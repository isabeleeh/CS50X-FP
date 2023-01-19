import os, time, csv, re, logging

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename
from pypinyin import lazy_pinyin

from helpers import apology, allowed_file, split_herbs

UPLOAD_FOLDER = './uploads'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super secret key'

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
    rows = db.execute("SELECT * FROM herbs ORDER BY pinyin")

    if rows:
        return render_template("index.html", rows=rows)
    else:
        return apology("Error when accessing database")


@app.route("/importfile", methods = ["GET", "POST"])
def importfile():
    """Import .csv file which includes herbs inventory and write into herbs.db"""
    if request.method == "POST":
        # User reaches here via "POST"
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect("/")

            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect("/")
            
        if file and allowed_file(file.filename):
            filename = secure_filename(''.join(lazy_pinyin(file.filename)))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # return redirect(url_for('uploaded_file', filename=filename))

            # Read the attachment content into a var myherbs as dict type
            # encoding='utf-8-sig' to remove the BOM /ufeff
            with open(filepath, "r", encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    
                    if row["Amount"] == '':
                        amount = 100;
                    else:
                        amount = int(row["Amount"])
                    mixedname = row["Name"]
                    # Handle exceptions such as row in excel consists of character like ""
                    if mixedname == "":
                        continue
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

@app.route("/prescription", methods = ["GET", "POST"])
def prescription():
    """ Handle the prescription from the doctor and minus the amount of each herb from db"""
    if request.method == "POST":
        prescript = request.form.get("prescript")
        doses = request.form.get("doses")
        if not doses:
            doses = 3
        else:
            doses = int(doses)

        # divide the prescription into a list
        if not prescript or not doses:
            return apology("prescription or doses cannot be blank")
        # split_herbs function handles split and related scenarios
        herbs_list = split_herbs(prescript)
        
        # To store the herbs that are not in db
        invalid_herbs = []
        # To store the herbs that have no adequet amount in db
        insufficient_herbs = []
        
        for herb in herbs_list:            
            item_db = db.execute("SELECT * FROM herbs WHERE Chinese_ch = ?", herb["Chinese_ch"])
            # If cannot find the corresponding herb in db
            if len(item_db) != 1:
                invalid_herbs.append(herb)
                continue
            # if the amount in db is not sufficient for this time
            #amount = int(amount)
            amount_db = item_db[0]["amount"]
            if (amount_db - herb["amount"] * doses) < 0:
                insufficient_herbs.append(herb)
                continue

            db.execute("UPDATE herbs SET amount = ? WHERE Chinese_ch = ?", (amount_db - herb["amount"] * doses), herb["Chinese_ch"])

        if invalid_herbs or insufficient_herbs:
            # Show the listed herbs that have not been handled
            return render_template("prescription.html", invalid_herbs = invalid_herbs, insufficient_herbs = insufficient_herbs)

        #flash("Succeeded!")
        

    else:
        return render_template("prescription.html")

    return redirect("/")

@app.route("/manage", methods = ["POST"])
def manage():
    # Shortcut to manage amount in db on "index" page
    if request.method == "POST":
        amount = request.form.get("quantity")
        item_id = request.form.get("id")
        if not amount:
            apology("The amount cannot be blank")
        amount = int(amount)
        item_db = db.execute("SELECT * FROM herbs WHERE id = ?", item_id)
        if (item_db[0]["amount"] + amount) < 0:
            flash("Insufficient amount!")
            return redirect("/")
        
        db.execute("UPDATE herbs SET amount = ? WHERE id = ?", (item_db[0]["amount"] + amount), item_id)

        flash("Succeeded!")
        return redirect("/")

@app.route("/testonly", methods = ["GET", "POST"])
def testonly():
    if request.method == "POST":
        # SUDO
        i = request.form.get("id")
    else:
        
        return render_template("test.html")
