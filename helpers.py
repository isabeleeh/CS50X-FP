import re

from flask import render_template
from datetime import datetime
from typing import Any, Dict, Optional


ALLOWED_EXTENSIONS = {'csv'}
EASILY_COMBINDED = {'生龙骨', '生牡蛎', '煅龙骨', '煅牡蛎', '石决明', '赤芍', '生白芍', '炒神曲', '炒麦芽', '炒山楂'}


"""apology function herits that of CS50X Problem Set 9, Finance
https://cs50.harvard.edu/x/2023/psets/9/finance/
"""
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

"""check if an extension is valid.
From https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/?highlight=downloading 
"""
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess(text):
    # To change "龙骨" "牡蛎" to "生龙骨" "生牡蛎"
    # To change "赤白芍" to "赤芍" "白芍"
    tmp = text
    if ("龙骨" in text) and ("生龙骨" not in text) and ("煅龙骨" not in text):
        tmp = tmp.replace("龙骨", "生龙骨")
    if ("牡蛎" in text) and ("生牡蛎" not in text) and ("煅牡蛎" not in text):
        tmp = tmp.replace("牡蛎", "生牡蛎")
    if ("赤白芍" in text):
        tmp = tmp.replace("赤白芍", "赤芍生白芍")
    if ("焦三仙" in text) or ("炒三仙" in text):
        tmp = tmp.replace("焦三仙", "炒麦芽炒神曲炒山楂")
        tmp = tmp.replace("炒三仙", "炒麦芽炒神曲炒山楂")
    if ("生地" in text) and ("生地黄" not in text):
        tmp = tmp.replace("生地", "生地黄")
    if ("熟地" in text) and ("熟地黄" not in text):
        tmp = tmp.replace("熟地", "熟地黄")
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
        else:
            continue

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

def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True  

def generate_download_headers(
        extension: str, filename: Optional[str] = None
)  -> Dict[str, Any]:
    filename = filename if filename else datetime.now().strftime("%Y%m%d_%H%M%S")
    # Set headers: attachment means download by default
    content_disp = f"attachment; filename={filename}.{extension}"
    headers = {"Content-Disposition": content_disp}
    return headers


