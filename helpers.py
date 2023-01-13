import os, string
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

ALLOWED_EXTENSIONS = {'csv'}


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_words(text):
    words = []
    for word in text.split():
        if word.isalpha():
            words.append(word)
    return " ".join(words)