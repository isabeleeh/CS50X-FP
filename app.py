import os, time, csv, re, logging

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin

from helpers import apology, allowed_file, get_words

UPLOAD_FOLDER = './uploads'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///myherbs.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Show portfolio of all herbs"""
    rows = db.execute("SELECT * FROM herbs")

    if rows:
        return render_template("index.html", rows=rows)
    else:
        return apology("Error when accessing database")


@app.route("/importfile", methods = ["GET", "POST"])
def importfile():
    """Import .csv or excel file which includes herbs inventory and write into herbs.db"""
    if request.method == "POST":
        # User reaches here via "POST"
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/")

            # Read the attachment content into a var myherbs as dict type
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect("/")
            
        if file and allowed_file(file.filename):
            filename = secure_filename(''.join(lazy_pinyin(file.filename)))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # return redirect(url_for('uploaded_file', filename=filename))

            # encoding='utf-8-sig' to remove the BOM /ufeff
            with open(filepath, "r", encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    
                    if row["Amount"] == '':
                        amount = 0;
                    else:
                        amount = int(row["Amount"])
                    mixedname = row["Name"]
                    # Handle exceptions such as row in excel consists of character like ""
                    if mixedname == "":
                        continue
                    logging.info(row["Amount"])
                    chinese = ''
                    # Fetch the Chinese character from a string
                    chinese = chinese.join(re.findall('[\u4e00-\u9fa5]', mixedname))
                    # Remove the Chinese character from a string
                    pinyin = ((re.sub('[\u4e00-\u9fa5]', '', mixedname)).strip()).title()
                    # Before insert into table, check whether the herb already exists.
                    item_herbs = db.execute("SELECT * FROM  herbs WHERE Chinese_ch = ?", chinese)
                    if item_herbs:
                        # This herb exists, we just replace the amount value
                        db.execute("UPDATE herbs SET amount = ? WHERE Chinese_ch = ?", amount, chinese)
                    else:
                        # This herb does not exist, we need to insert one for it.
                        db.execute("INSERT INTO herbs (Chinese_ch, pinyin, amount) VALUES (?, ?, ?)", 
                            chinese,
                            pinyin,
                            amount)
                    
    
    else:
        return render_template("importfile.html")

    return redirect("/")