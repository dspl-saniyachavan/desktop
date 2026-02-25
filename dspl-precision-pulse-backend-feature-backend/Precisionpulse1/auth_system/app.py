from flask import Flask, render_template, request, redirect, session, flash
import psycopg2
import bcrypt
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


def get_db_connection():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    return conn


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_pw.decode("utf-8"))
            )
            conn.commit()
            cur.close()
            conn.close()

            flash("Registration successful! Please login.")
            return redirect("/login")

        except Exception as e:
            flash("User already exists!")
            
            return redirect("/register")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            user_id, stored_password = user
            if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                session["user_id"] = user_id
                session["username"] = username
                return redirect("/dashboard")

        flash("Invalid credentials")
        return redirect("/login")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", username=session["username"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)