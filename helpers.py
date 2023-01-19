import os, string, re
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

ALLOWED_EXTENSIONS = {'csv'}
EASILY_COMBINDED = {'生龙骨', '生牡蛎', '煅龙骨', '煅牡蛎', '石决明'}


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

def preprocess(text):
    # To change "龙骨" "牡蛎" to "生龙骨" "生牡蛎"
    tmp = text
    if ("龙骨" in text) and ("生龙骨" not in text) and ("煅龙骨" not in text):
        tmp = tmp.replace("龙骨", "生龙骨")
    if ("牡蛎" in text) and ("生牡蛎" not in text) and ("煅牡蛎" not in text):
        tmp = tmp.replace("牡蛎", "生牡蛎")
    return tmp

def split_herbs(prescript):
    # To take the whole prescription as input, and return a dict type with herb name and amount.
    # issue to solve: "牡蛎" and "煅牡蛎" could cause conflict
    rough_list = prescript.split("，") # a rough list, probably include information like "生龙骨煅牡蛎各30克先煎" "柴胡12克"
    item_list = []
    for item in rough_list:
        tmp = re.split(r"克", item)[0] # "生龙骨煅牡蛎各30克先煎" -> "生龙骨煅牡蛎各30"
        amount = "".join(list(filter(str.isdigit, tmp))) # Catch the amount value
        if amount:
            amount = int(amount)

        if '各' in tmp:
            # like "生龙骨煅牡蛎各30"
            tmp = re.split(r"各", item)[0] # "生龙骨煅牡蛎各30" -> "生龙骨煅牡蛎"
            tmp = preprocess(tmp)
            for chinese in EASILY_COMBINDED:
                if tmp == "":
                    break
                if chinese in tmp:
                    item_list.append({'Chinese_ch': chinese, 'amount': amount})
                    tmp = tmp.replace(chinese, '')

        else:
            
            # Catch the herb's Chinese name
            chinese = ''
            chinese = chinese.join(re.findall('[\u4e00-\u9fa5]', tmp)) 
            item_list.append({'Chinese_ch': chinese, 'amount': amount})
    return item_list   
