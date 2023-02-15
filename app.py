import os, csv, re, pinyin as py

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response
from io import StringIO


from helpers import apology, allowed_file, split_herbs, is_all_chinese, generate_download_headers

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

    return render_template("index.html", rows=rows)


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
            filename = secure_filename(py.get(file.filename, format = "strip"))
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # return redirect(url_for('uploaded_file', filename=filename))

            # Read the attachment content into a var myherbs as dict type
            # encoding='utf-8-sig' to remove the BOM /ufeff
            with open(filepath, "r", encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    
                    # In case the "Amount" field is blank
                    if row["Amount"] == '':
                        amount = 0;
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

        flash("Succeeded!")
        

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
            return apology("The amount cannot be blank")
        amount = int(amount)
        # item_db = db.execute("SELECT * FROM herbs WHERE id = ?", item_id)
        #if (item_db[0]["amount"] + amount) < 0:
        #    flash("Insufficient amount!")
        #    return redirect("/")
        
        db.execute("UPDATE herbs SET amount = ? WHERE id = ?", (amount), item_id)

        flash("Succeeded!")
        return redirect("/")


@app.route("/replenish", methods = ["GET", "POST"])
def replenish():
    # Replenish one by one
    if request.method == "POST":
        # To show the existing herbs listed from db for users to edit amount
        # To indicate whether it is add amount for existing herb or add new herb
        add_others = request.form.get("addothers")
        if add_others == 'false':

            herb = request.form.get("herb")
            amount = request.form.get("amount")

            # To add new herb that does not exist in db yet
            if herb == "Add Others":
                add_others = True
                return render_template("replenish.html", add_others = add_others)

            if not herb or not amount:
                return apology("Herb or amount cannot be blank")

            item_db = db.execute("SELECT * FROM herbs WHERE Chinese_ch = ?", herb)
            amount_db = item_db[0]["amount"]

            # - means minus. So there is the possibility for user to input a bigger amount number to minus than the existing amount
            if (amount_db + int(amount)) < 0:
                return apology("No sufficient amount")

            # Update the amount into db
            db.execute("UPDATE herbs SET amount = ? WHERE Chinese_ch = ?", amount_db + int(amount), herb)
            flash("Added Successfully!")
        
        # To handle adding new herb
        elif add_others == 'true':
            new_herb = request.form.get("newherb")
            amount = request.form.get("amount")
            if not new_herb or not amount:
                return apology("Herb or amount cannot be blank")

            if not is_all_chinese(new_herb):
                return apology("Please input Chinese name of the herb")

            amount = int(amount)
            pinyin_herb = (py.get(new_herb, format='strip', delimiter=" ")).title()

            item_db = db.execute("SELECT * FROM herbs WHERE Chinese_ch = ?", new_herb)
            if item_db:
                return apology("The herb exists!")
                
            db.execute("INSERT INTO herbs (Chinese_ch, pinyin, amount) VALUES (?, ?, ?)",
                new_herb,
                pinyin_herb,
                amount)
            flash("Added Successfully!")
            
        return redirect("/replenish")
    else:
        herbs = db.execute("SELECT * FROM herbs ORDER BY pinyin")
        return render_template("replenish.html", herbs = herbs)

@app.route("/remove", methods = ["GET", "POST"])
def remove():
    if request.method == "POST":
        id = request.form.get("id")
        if id:
            db.execute("DELETE FROM herbs WHERE id = ?", id)
            flash("Successfully removed!")
        
        return redirect("/")
    
@app.route("/export", methods = ["POST"])
def export():
    def generate():
        # place holder for path
        os_path = ''
        db_row = db.execute("SELECT * FROM herbs ORDER BY pinyin")
        
        # Use StringIO to write into memory instead of creating actual file
        data = StringIO()
        # Specify field names because I do not need all the fields in db to be reflected in csv file
        fieldnames = ['Name', 'Amount']
        # According to python docs usage example of csv.DictWriter
        w = csv.DictWriter(data, fieldnames=fieldnames)

        w.writeheader()
        # To save memory: 返回写入的值，然后让io流指针回到起点，删去指针后的部分，即清空所有写入的内容，准备下一行的写入
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # write each line item
        for item in db_row:
            # Here use three variables to avoid ' or " conflicts 
            chinese_ch = item["Chinese_ch"]
            pinyin = item["pinyin"]
            name = f"{chinese_ch} {pinyin}"
            w.writerow(
                {'Name': name,
                    'Amount': item["amount"]}
                )
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
    if request.method == "POST":
        # Export/download file from server
        return Response(generate(), 
                        headers = generate_download_headers("csv"),
                        mimetype = "text/csv",
                        )
@app.route("/removeall", methods = ["POST"])
def removeall():
    db.execute("DELETE FROM herbs")
    flash("Remove All Herbs!")
    return redirect("/")
