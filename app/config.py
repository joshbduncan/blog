import os

from dotenv import load_dotenv

from .markdown_div import MarkdownDiv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY", "")

    # flatpages configuration
    FLATPAGES_AUTO_RELOAD = "DEBUG"
    FLATPAGES_EXTENSION = [".md", ".html", ".js"]
    FLATPAGES_ROOT = "../content"
    FLATPAGES_MARKDOWN_EXTENSIONS = [
        "codehilite",
        "fenced_code",
        "attr_list",
        "tables",
        MarkdownDiv(),
    ]
    FLATPAGES_EXTENSION_CONFIGS = {"codehilite": {"guess_lang": False}}

    POST_DIR = "posts"
    PAGE_DIR = "pages"

    # freezer static files destination
    FREEZER_DESTINATION = "../build"
    FREEZER_BASE_URL = "https://joshbduncan.com/"

    # Ignore MIME warning for type application/xml (sitemap, rss)
    FREEZER_IGNORE_MIMETYPE_WARNINGS = True
