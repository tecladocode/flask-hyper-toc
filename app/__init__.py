from flask import Flask, render_template
from slugify import slugify

app = Flask(__name__)


@app.template_filter("slug")
def slugify_filter(string_):
    """
    Slugify a string. This is here so that you don't have to pass a unique ID
    to each section."""
    return slugify(string_)


@app.get('/')
def home():
    return render_template("usage.html")