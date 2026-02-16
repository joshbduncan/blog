import mimetypes

from flask import Flask
from flask_flatpages import FlatPages

from .config import Config

from flask_frozen import Freezer

app: Flask = Flask(import_name=__name__)
flatpages: FlatPages = FlatPages(app=app)
freezer: Freezer = Freezer(app=app)

app.config.from_object(Config)


@app.context_processor
def inject_site_url():
    return {"site_url": app.config.get("FREEZER_BASE_URL")}


mimetypes.add_type(type="application/manifest+json", ext=".webmanifest")

from . import routes  # noqa: F401 E402
