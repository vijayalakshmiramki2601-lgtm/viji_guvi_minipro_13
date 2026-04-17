from flask import Flask, render_template, request, redirect, session
import sqlite3, json

app = Flask(__name__)
app.secret_key = "food_health_secret"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS food_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        food TEXT,
        calories INTEGER,
        protein INTEGER,
        fat INTEGER,
        health_score INTEGER,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- FOOD ENGINE ----------
def get_food_data(food):
    food = food.lower()

    foods = {
        "burger": (300, 10, 20, "burger.jpg"),
        "pizza": (280, 12, 18, "pizza.jpg"),
        "apple": (80, 1, 0, "apple.jpg"),
        "salad": (120, 5, 3, "salad.jpg"),
        "rice": (200, 4, 1, "rice.jpg"),
        "chicken": (250, 25, 10, "chicken.jpg"),
        "egg": (70, 6, 5, "egg.jpg"),
        "milk": (100, 8, 4, "milk.jpg"),
        "banana": (90, 1, 0, "banana.jpg"),
        "sandwich": (220, 8, 10, "sandwich.jpg"),
        "fries": (320, 4, 25, "fries.jpg"),
        "cake": (350, 3, 15, "cake.jpg"),
        "juice": (110, 1, 0, "juice.jpg"),
        "dosa": (180, 4, 6, "dosa.jpg"),
        "idli": (120, 3, 1, "idli.jpg")
    }

    if food in foods:
        cal, pro, fat, img = foods[food]
        score = max(20, 100 - cal // 5)
        return cal, pro, fat, score, img

    return 150, 4, 5, 60, "default.jpg"

# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        food = request.form["food"]
        cal, pro, fat, score, img = get_food_data(food)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("""INSERT INTO food_log
        (username, food, calories, protein, fat, health_score, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session["user"], food, cal, pro, fat, score, img))
        conn.commit()
        conn.close()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""SELECT id, food, calories, protein, fat, health_score, image
                 FROM food_log WHERE username=?""",
              (session["user"],))
    data = c.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        data=data,
        user=session["user"],
        chart_data=json.dumps(data)
    )

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM food_log WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    if "user" in session:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("DELETE FROM food_log WHERE username=?", (session["user"],))
        conn.commit()
        conn.close()

    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)