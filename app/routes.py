from datetime import datetime
import re

import html

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from zoneinfo import ZoneInfo
import xml.etree.cElementTree as ET

from flask import (
    Response,
    redirect,
    abort,
    render_template,
    request,
    url_for,
    send_from_directory,
)
from flask.typing import ResponseReturnValue
from flask_flatpages import Page

from app import app, flatpages, freezer

POST_DIR: str = app.config.get("POST_DIR", "posts")
PAGE_DIR: str = app.config.get("PAGE_DIR", "pages")


@app.errorhandler(404)
def page_not_found(e) -> str:
    return render_template("404.html")


@freezer.register_generator
def error_handlers():
    yield "/404.html"


ROOT_IMAGE_FILES: dict[str, str] = {
    "favicon.ico": "favicon.ico",
    "favicon.svg": "favicon.svg",
    "apple-touch-icon.png": "apple-touch-icon.png",
    "icon-192.png": "icon-192.png",
    "icon-512.png": "icon-512.png",
    "og-image.png": "og-image.png",
    "og-image-square.png": "og-image-square.png",
}


@freezer.register_generator
def root_image_files():
    for path in ROOT_IMAGE_FILES.values():
        yield f"/{path}"


##########
# ROUTES #
##########


@app.route("/")
def index():
    posts: list[Page] = get_live_posts()
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=posts)


@app.route("/<name>.html")
def post(name: str) -> str:
    path: str = f"{POST_DIR}/{name}"
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)


@app.get("/site.webmanifest")
def manifest() -> Response:
    directory: str | None = app.static_folder
    if directory is None:
        abort(404)

    assert directory is not None  # to fix type error for `send_from_directory`

    return send_from_directory(directory, "site.webmanifest")


@app.get("/<path:filename>")
def root_static(filename: str) -> Response:
    if filename not in ROOT_IMAGE_FILES:
        abort(404)

    directory: str | None = app.static_folder
    if directory is None:
        abort(404)

    assert directory is not None  # to fix type error for `send_from_directory`

    return send_from_directory(directory, ROOT_IMAGE_FILES[filename])


#########
# PAGES #
#########


@app.route("/about.html")
def about() -> str:
    path: str = f"{PAGE_DIR}/about"
    page = flatpages.get_or_404(path)
    return render_template("page.html", page=page, og_type="profile")


@app.route("/photography.html")
def photography() -> str:
    return render_template("photography.html", title="Photography")


@app.route("/search.html")
def search() -> str:
    posts: list[Page] = get_live_posts()
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("search.html", posts=posts, title="Search")


@app.route("/software.html")
def software() -> str:
    path: str = f"{PAGE_DIR}/software"
    page = flatpages.get_or_404(path)
    return render_template("page.html", page=page)


##############
# META PAGES #
##############


@app.route("/category/<category>.html")
def category(category: str) -> str:
    posts: list[Page] = [
        post for post in get_live_posts() if category == post.meta["category"]
    ]
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=posts, filter=category)


@app.route("/categories.html")
@app.route("/tags.html")
def tags() -> str:
    if request.path == "/categories.html":
        tags: list[str] = get_all_categories()
        title: str = "#categories"
        route = "category"
    else:
        tags: list[str] = get_all_tags()
        title: str = "#tags"
        route = "tag"

    if not tags:
        abort(404)

    return render_template("tags.html", title=title, tags=tags, route=route)


@app.route("/tag/<tag>.html")
def tag(tag: str) -> str:
    posts: list[Page] = [
        post for post in get_live_posts() if tag in get_post_tags(post)
    ]
    posts.sort(key=lambda item: item["date"], reverse=True)
    return render_template("posts.html", posts=posts, filter=tag)


##########
# ROUTES #
##########


@app.route("/projects/qrcoder/")
def qrcoder() -> str:
    return render_template("projects/qrcoder/index.html")


@app.route("/projects/qrcoder.html")
def qrcoder_legacy() -> ResponseReturnValue:
    return redirect(url_for("qrcoder"), code=301)


############
# XML DATA #
############


@app.route("/sitemap.xml")
def sitemap() -> Response:
    # get data for the sitemap
    posts: list[Page] = get_live_posts()
    categories: list[str] = get_all_categories()
    tags: list[str] | list = get_all_tags() or []

    # sort posts by date (oldest first)
    posts.sort(key=lambda item: item["date"], reverse=False)

    # define the XML namespace
    NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    XHTML_NS = "http://www.w3.org/1999/xhtml"

    # create the root <urlset> element with namespaces
    urlset = ET.Element("urlset", {"xmlns": NS, "xmlns:xhtml": XHTML_NS})

    # helper function to add a URL entry
    def add_url(loc: str, changefreq: str | None = None) -> None:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = loc
        if changefreq:
            ET.SubElement(url, "changefreq").text = changefreq

    # add the base website URL
    add_url(url_for("index", _external=True), "weekly")

    # add static pages
    add_url(url_for("about", _external=True), "monthly")
    add_url(url_for("software", _external=True), "monthly")

    # add posts
    for post in posts:
        post_url: str = url_for(
            "post", name=post.path.replace(post.folder, ""), _external=True
        )
        add_url(post_url)

    # add categories
    for category in categories:
        category_url: str = url_for("category", category=category, _external=True)
        add_url(category_url)

    # add tags
    for tag in tags:
        tag_url: str = url_for("tag", tag=tag, _external=True)
        add_url(tag_url)

    # convert the XML tree to a string
    xml_string = ET.tostring(urlset, encoding="utf-8", xml_declaration=True).decode(
        "utf-8"
    )

    return Response(xml_string, status=200, content_type="application/xml")


@app.route("/rss.xml")
def rss() -> Response:
    def get_rss_pubdate(date: datetime | None = None) -> str:
        """Format a datetime object to RFC-822 format for an RSS `pubDate`.

        Args:
            date (datetime | None): The datetime to format. Defaults to the current time in America/New_York.

        Returns:
            str: RFC-822-compliant date string.
        """
        zone = ZoneInfo("America/New_York")

        if date is None:
            date = datetime.now(zone)
        elif date.tzinfo is None:
            date = date.replace(tzinfo=zone)  # localize if naive

        return date.strftime("%a, %d %b %Y %H:%M:%S %z")

    def make_links_absolute(
        html: str, base_url: str = url_for("index", _external=True)
    ) -> str:
        """Convert all relative links in HTML to absolute URLs."""
        if not html:
            return html  # Return as-is if empty

        soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

        # convert relative <a href=""> links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            assert isinstance(href, str)  # for type checker
            a["href"] = urljoin(base_url, href)

        # convert relative <img src=""> links
        for img in soup.find_all("img", src=True):
            src = img["src"]
            assert isinstance(src, str)  # for type checker
            img["src"] = urljoin(base_url, src)

        return str(soup)

    def clean_html(html: str) -> str:
        """Remove `loading="lazy"` attributes from <img> tags in HTML content."""
        soup: BeautifulSoup = BeautifulSoup(html, "html.parser")

        # Find all <img> tags and remove the "loading" attribute
        for img in soup.find_all("img"):
            if "loading" in img.attrs:
                del img["loading"]

        return str(soup)  # Return cleaned HTML as a string

    def escape_xml(text: str) -> str:
        """Escape special XML characters to prevent parsing errors."""
        if text:
            return html.escape(text)  # Escapes &, <, >, " and '
        return text

    # get all posts sorted by date
    posts: list[Page] = sorted(
        get_live_posts(), key=lambda item: item["date"], reverse=True
    )

    # define namespaces
    ATOM_NS = "http://www.w3.org/2005/Atom"
    CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"

    # register namespaces
    ET.register_namespace("atom", ATOM_NS)
    ET.register_namespace("content", CONTENT_NS)

    # create root RSS element with required attributes
    root = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(root, "channel")

    # add site metadata
    ET.SubElement(channel, "title").text = "Josh Duncan - Blog"

    # correct `atom:link` (namespace handling)
    ET.SubElement(
        channel,
        f"{{{ATOM_NS}}}link",
        {
            "href": url_for("rss", _external=True),
            "rel": "self",
            "type": "application/rss+xml",
        },
    )

    ET.SubElement(channel, "link").text = url_for("index", _external=True)
    ET.SubElement(
        channel, "description"
    ).text = "just some random thoughts published on the internet..."
    ET.SubElement(channel, "lastBuildDate").text = get_rss_pubdate()
    ET.SubElement(channel, "language").text = "en-US"

    # add the last 10 posts
    for post in posts[:10]:
        post_url: str = url_for(
            "post", name=post.path.replace(post.folder, ""), _external=True
        )
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = escape_xml(post.meta["title"])
        ET.SubElement(item, "link").text = post_url
        pub_date = datetime.combine(
            post.meta["date"], datetime.min.time(), ZoneInfo("America/New_York")
        )
        ET.SubElement(item, "pubDate").text = get_rss_pubdate(pub_date)
        ET.SubElement(item, "guid").text = post_url

        # convert links to absolute in description & content
        description_html: str = make_links_absolute(post.meta["description"])
        content_html: str = make_links_absolute(post.html)

        # remove lazy loading tag from images
        content_html: str = clean_html(content_html)

        assert not re.search(r'href=["\'](?!https?:\/\/)[^"\']+', content_html), (
            "Found relative href link!"
        )
        assert not re.search(r'src=["\'](?!https?:\/\/)[^"\']+', content_html), (
            "Found relative src link!"
        )
        assert 'loading="lazy"' not in content_html, "Found a lazy loading img tag!"

        # add description (wrapped in CDATA)
        ET.SubElement(item, "description").text = f"<![CDATA[{description_html}]]>"

        # add content:encoded (wrapped in CDATA)
        content_encoded = ET.SubElement(
            item, "{http://purl.org/rss/1.0/modules/content/}encoded"
        )
        content_encoded.text = f"<![CDATA[{content_html}]]>"

    # convert XML to string
    xml_string = ET.tostring(root, encoding="utf-8").decode("utf-8")

    # fix the escaping of CDATA sections
    xml_string = xml_string.replace("&lt;![CDATA[", "<![CDATA[").replace(
        "]]&gt;", "]]>"
    )

    # ensure HTML inside CDATA remains untouched
    xml_string = (
        xml_string.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    )

    return Response(xml_string, status=200, content_type="application/rss+xml")


##########
# ROBOTS #
##########


@app.route("/robots.txt")
def robots() -> str:
    return render_template("robots.txt")


#############
# FUNCTIONS #
#############


def get_pages() -> list[Page]:
    return [page for page in flatpages if page.path.startswith(PAGE_DIR)]


def get_live_posts() -> list[Page]:
    return [post for post in flatpages if post.path.startswith(POST_DIR)]


def get_all_categories() -> list[str]:
    categories: set[str] = set()
    for post in get_live_posts():
        categories.add(post.meta["category"])
    return sorted(list(categories))


def get_post_tags(post: Page) -> list[str]:
    tags: str = post.meta.get("tags", "")
    return sorted(tags.split(", "))


def get_all_tags() -> list[str]:
    tags: set[str] = set()
    for post in get_live_posts():
        tags.update(set(get_post_tags(post)))
    return sorted(list(tags))
