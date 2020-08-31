from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import googletrans
from helpers import apology, login_required, selLanguages
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

app = Flask(__name__)

# Initializing SQLite3 and Google Translate Library
db = sqlite3.connect("translate.db", check_same_thread=False)
db.row_factory = sqlite3.Row
cur = db.cursor()
translator = googletrans.Translator()
languages = dict(map(reversed, googletrans.LANGUAGES.items()))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # User reached route via POST
    if request.method == "POST":
        # If user presses button on index page, redirect them to the respective pages
        nextPage = request.form.get("nextPage")
        # To Voice Page
        if nextPage == "voice":
            return redirect("/voice")
        # To Text Page
        elif nextPage == "text":
            return redirect("/text")
        # To the Saved Translations Page
        elif nextPage == "saved":
            return redirect("/saved")
        # To user's history page
        else:
            return redirect("/history")
    # User reached route via GET
    else:
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    # User reached route via POST
    if request.method == "POST":
        # Get user's username and password
        username = request.form.get("username")
        password = request.form.get("password")
        # if one or the other are not provided, return apology
        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)
        # Select from Database
        cur.execute("SELECT * FROM users WHERE username = :username", {"username":username})
        users = cur.fetchall()
        # If password does not match, return apology
        if len(users) != 1 or not check_password_hash(users[0]["hash"], password):
            return apology("invalid username and/or password", 403)
        # Save user session, and redirect to index page
        session["user_id"] = users[0]["id"]
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # User reached route via POST
    if request.method == "POST":
        # Get username, password, confirmed password from user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        cur.execute("SELECT username FROM users")
        usernamesExist = cur.fetchall()
        # If user did not enter a username, return apology
        if not username:
            return apology("must enter a username", 403)
        # If user did not enter a password, return apology
        elif not password:
            return apology("must enter a password", 403)
        # If user did not confirm their password, return apology
        elif not confirmation:
            return apology("confirm your password", 403)
        # If password and confirmation does not match, return apology
        elif password != confirmation:
            return apology("passwords do not match", 403)
        counter1 = 0
        # Check database if username exists already, if it does, return apology
        while counter1 < len(usernamesExist):
            if username in (usernamesExist[counter1]["username"]):
                return apology("username already exists", 403)
            counter1 += 1
        # Hash password, and then insert it to the database and redirect user to index page
        passwordHash = generate_password_hash(password)
        userid = len(usernamesExist) + 1
        cur.execute("INSERT INTO users (id, username, hash) VALUES (:id, :username, :passwordHash)", {"id":userid, "username":username, "passwordHash":passwordHash})
        db.commit()
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("register.html")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    # User reached route via POST
    if request.method == "POST":
        # Take in user input from form
        currentPass = request.form.get("currentPass")
        changedPass = request.form.get("changedPass")
        confirm = request.form.get("confirm")
        cur.execute("SELECT hash FROM users WHERE id=@id", {"id":session["user_id"]})
        oldPassDB = cur.fetchall()
        oldPassDB = oldPassDB[0]['hash']
        # If user did not enter current password, return apology
        if not currentPass:
            return apology("must enter current password", 403)
        # If user did not enter new password, return apology
        elif not changedPass:
            return apology("must enter new password", 403)
        # If user did not confirm new password, return apology
        elif not confirm:
            return apology("must confirm new password", 403)
        # If confirmed password does not match with new password, return apology
        elif changedPass != confirm:
            return apology("new passwords must match", 403)
        # If user did not enter the correct current password, return apology
        elif not check_password_hash(oldPassDB, currentPass):
            return apology("wrong current password", 403)
        # Else, continue with changing the password (hashing new password, inserting it into database)
        else:
            changedPassHash = generate_password_hash(changedPass)
            db.execute("UPDATE users SET hash=@hash WHERE id=@id", {"hash":changedPassHash, "id":session["user_id"]})
            return redirect("/")
    # User reached route via GET
    else:
        return render_template("password.html")

@app.route("/voice", methods=["GET", "POST"])
@login_required
def voice():
    # User reached route via POST
    if request.method == "POST":
        # Variable to check if user has inputted their voice
        inputTrue = request.form.get("inputTrue")
        # If not, redirect user to input their voice (did this to get language of origin + language they want to translate to)
        if inputTrue == "False":
            destination = request.form.get("destination")
            source = request.form.get("source")
            # If no language is selected, return apology
            if source == "default" or destination == "default":
                return apology("select a valid language", 403)
            srcLower = source.lower()
            destLower = destination.lower()
            srcSymbol = languages[srcLower]
            return render_template("userInput.html", srcSymbol=srcSymbol, destination=destination, source=source)
        # If yes, redirect user to their translated text
        else:
            userInput = request.form.get("userInput")
            destination = request.form.get("destination")
            source = request.form.get("source")
            srcLower = source.lower()
            destLower = destination.lower()
            # Translate user input
            translated = translator.translate(userInput, dest=languages[destLower], src=languages[srcLower])
            translated = translated.text
            # Insert to history table, get user translated text
            cur.execute("INSERT INTO history (userid, src, dest, userInput, translated) VALUES (@userid, @src, @dest, @userInput, @translated)", {"userid":(session["user_id"]), "src":source, "dest":destination, "userInput":userInput, "translated":translated})
            db.commit()
            return render_template("textTranslated.html", userInput=userInput, destination=destination, source=source, translated=translated)
    # User reached route via GET
    else:
        listLanguages = selLanguages(languages)
        return render_template("voice.html", listLanguages=listLanguages)

@app.route("/text", methods=["GET", "POST"])
@login_required
def text():
    # User reached route via POST
    if request.method == "POST":
        # Getting user input, and language of origin + destination
        destination = request.form.get("destination")
        userInput = request.form.get("userInput")
        source = request.form.get("source")
        # If user did not provide either one of the variables, return apology
        if not userInput:
            return apology("must enter something to translate", 403)
        elif source == "default" or destination == "default":
            return apology("select a valid language", 403)
        destLower = destination.lower()
        srcLower = source.lower()
        # Translate User Input
        translated = translator.translate(userInput, dest=languages[destLower], src=languages[srcLower])
        translated = translated.text
        # Insert to history table, get user translated text
        cur.execute("INSERT INTO history (userid, src, dest, userInput, translated) VALUES (@userid, @src, @dest, @userInput, @translated)", {"userid":(session["user_id"]), "src":source, "dest":destination, "userInput":userInput, "translated":translated})
        db.commit()
        return render_template("textTranslated.html", userInput=userInput, destination=destination, source=source, translated=translated)
    # User reached route via GET
    else:
        listLanguages = selLanguages(languages)
        return render_template("text.html", listLanguages=listLanguages)

@app.route("/saved", methods=["GET", "POST"])
@login_required
def saved():
    # User reached route via POST
    if request.method == "POST":
        # Get the translated values from the Text Translated page
        userInput = request.values.get("userInput")
        source = request.values.get("source")
        destination = request.values.get("destination")
        translated = request.values.get("translated")
        # Insert values into a different table in database, show user their saved translations
        cur.execute("INSERT INTO saved (userid, src, dest, userInput, translated) VALUES (@userid, @src, @dest, @userInput, @translated)", {"userid":(session["user_id"]), "src":source, "dest":destination, "userInput":userInput, "translated":translated})
        db.commit()
        cur.execute("SELECT * FROM saved WHERE userid = @userid", {"userid":session["user_id"]})
        saved = cur.fetchall()
        flash("Saved!")
        return render_template("saved.html", saved=saved)
    # User reached route via GET
    else:
        # Show user their saved translations from database
        cur.execute("SELECT * FROM saved WHERE userid = @userid", {"userid":session["user_id"]})
        saved = cur.fetchall()
        return render_template("saved.html", saved=saved)

@app.route("/history")
@login_required
def history():
    # Show user their translation history from database
    cur.execute("SELECT * FROM history WHERE userid = @userid", {"userid":session["user_id"]})
    userHistory = cur.fetchall()
    return render_template("history.html", userHistory=userHistory)

@app.route("/privacy", methods=["GET", "POST"])
@login_required
def privacy():
    # User reached route via POST
    if request.method == "POST":
        # Get what user chose from their options
        userChoice = request.form.get("userChoice")
        # Clear user history
        if userChoice == "history":
            cur.execute("DELETE FROM history WHERE userid=@userid", {"userid":(session["user_id"])})
            db.commit()
        # Clear saved user history
        else:
            cur.execute("DELETE FROM saved WHERE userid=@userid", {"userid":(session["user_id"])})
            db.commit()
        flash("Done!")
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("privacy.html")
