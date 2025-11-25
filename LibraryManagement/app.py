# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection
db = mysql.connector.connect(
    host="digitallibrary.cirn2jekr1ft.eu-west-1.rds.amazonaws.com",
    user="root",
    password="Ujwal2016",
    database="digital_library"
)
cursor = db.cursor(dictionary=True)

# -------------------- AUTH SERVICE --------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("books"))
    return redirect(url_for("signin"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, password))
        db.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["id"]
            flash("Welcome back, " + user["name"], "success")
            return redirect(url_for("books"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("signin.html")


# -------------------- BOOK SERVICE --------------------
@app.route("/books")
def books():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    cursor.execute("SELECT * FROM books")
    all_books = cursor.fetchall()
    return render_template("books.html", books=all_books)


# -------------------- BORROW SERVICE --------------------
@app.route("/borrow/<int:book_id>")
def borrow(book_id):
    if "user_id" not in session:
        return redirect(url_for("signin"))

    cursor.execute("INSERT INTO borrow_records (user_id, book_id) VALUES (%s, %s)",
                   (session["user_id"], book_id))
    db.commit()
    flash("Book borrowed successfully!", "success")
    return redirect(url_for("books"))

@app.route("/mybooks")
def mybooks():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    cursor.execute("""
        SELECT b.title, b.author, br.borrow_date
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.user_id=%s
    """, (session["user_id"],))
    my_books = cursor.fetchall()

    return render_template("borrow.html", books=my_books)


# -------------------- LOGOUT --------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("signin"))


if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)
