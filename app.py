"""StudentHub: a small Flask and SQLite student records application."""
import math
import os
import re
import secrets
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent


def calculate_grade(marks):
    """Grade scale: A+ 90+, A 80+, B 70+, C 60+, D 40+, F below 40."""
    if marks >= 90: return "A+"
    if marks >= 80: return "A"
    if marks >= 70: return "B"
    if marks >= 60: return "C"
    if marks >= 40: return "D"
    return "F"


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("STUDENTHUB_DATABASE", str(BASE_DIR / "students.db")),
        DEBUG=os.environ.get("FLASK_DEBUG", "0").lower() in {"1", "true"},
        PAGE_SIZE=10,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "0").lower() in {"1", "true"},
    )
    if test_config:
        app.config.update(test_config)
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def init_db():
        connection = db()
        connection.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age BETWEEN 1 AND 120),
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            course TEXT NOT NULL,
            marks REAL NOT NULL CHECK(marks BETWEEN 0 AND 100),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            gender TEXT NOT NULL DEFAULT '',
            registration_date TEXT NOT NULL DEFAULT '',
            phone TEXT NOT NULL DEFAULT ''
        )""")
        # Keep databases created by earlier StudentHub versions usable.
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(students)")}
        for name, declaration in (("gender", "TEXT NOT NULL DEFAULT ''"),
                                  ("registration_date", "TEXT NOT NULL DEFAULT ''"),
                                  ("phone", "TEXT NOT NULL DEFAULT ''")):
            if name not in columns:
                connection.execute(f"ALTER TABLE students ADD COLUMN {name} {declaration}")
        connection.execute("UPDATE students SET registration_date = substr(created_at, 1, 10) WHERE registration_date = ''")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email_nocase ON students(email COLLATE NOCASE)")
        connection.commit()

    with app.app_context():
        init_db()

    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return session["csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token
    app.jinja_env.globals["today"] = lambda: date.today().isoformat()

    @app.before_request
    def protect_forms():
        if request.method == "POST":
            supplied = request.form.get("csrf_token", "")
            expected = session.get("csrf_token", "")
            if not expected or not secrets.compare_digest(supplied, expected):
                abort(400, description="The form expired or could not be verified. Please try again.")

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("error.html", code=400, message=getattr(error, "description", "Invalid request.")), 400

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="The page or student record could not be found."), 404

    @app.errorhandler(500)
    def server_error(_error):
        app.logger.exception("Unexpected application error")
        return render_template("error.html", code=500, message="Something went wrong. Please try again."), 500

    app.jinja_env.globals["calculate_grade"] = calculate_grade

    def validate_student(form):
        data = {key: form.get(key, "").strip() for key in
                ("name", "age", "email", "phone", "gender", "course", "marks", "registration_date")}
        errors = []
        if not data["name"] or len(data["name"]) > 100:
            errors.append("Enter a full name between 1 and 100 characters.")
        if not data["age"].isdigit() or not 1 <= int(data["age"] or 0) <= 120:
            errors.append("Enter a valid age between 1 and 120.")
        if len(data["email"]) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", data["email"]):
            errors.append("Enter a valid email address.")
        if not data["course"] or len(data["course"]) > 100:
            errors.append("Enter a course name between 1 and 100 characters.")
        if data["gender"] not in ("", "Female", "Male", "Non-binary", "Prefer not to say"):
            errors.append("Choose a valid gender option.")
        phone = re.sub(r"[\s()+.-]", "", data["phone"])
        if data["phone"] and (not phone.isdigit() or not 7 <= len(phone) <= 15):
            errors.append("Enter a valid phone number (7 to 15 digits).")
        try:
            marks = float(data["marks"])
            if not math.isfinite(marks) or not 0 <= marks <= 100:
                raise ValueError
        except ValueError:
            marks = 0.0
            errors.append("Marks must be a number between 0 and 100.")
        try:
            reg_date = date.fromisoformat(data["registration_date"])
            if reg_date > date.today(): raise ValueError
        except ValueError:
            errors.append("Enter a valid registration date that is not in the future.")
        data["email"] = data["email"].lower()
        data["age"] = int(data["age"]) if data["age"].isdigit() else 0
        data["marks"] = marks
        return data, errors

    @app.route("/")
    def index():
        search = request.args.get("search", "").strip()[:100]
        course = request.args.get("course", "").strip()[:100]
        sort_options = {"newest": "id DESC", "oldest": "id ASC", "name": "name COLLATE NOCASE ASC",
                        "marks_high": "marks DESC", "marks_low": "marks ASC"}
        sort = request.args.get("sort", "newest")
        order = sort_options.get(sort, sort_options["newest"])
        page = max(1, request.args.get("page", 1, type=int) or 1)
        conn = db()
        clauses, params = [], []
        if search:
            clauses.append("(name LIKE ? OR email LIKE ? OR course LIKE ?")
            params.extend([f"%{search}%"] * 3)
            if search.isdigit():
                clauses[-1] += " OR id = ?"
                params.append(int(search))
            clauses[-1] += ")"
        if course:
            clauses.append("course = ?"); params.append(course)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        total_filtered = conn.execute("SELECT COUNT(*) FROM students" + where, params).fetchone()[0]
        pages = max(1, math.ceil(total_filtered / app.config["PAGE_SIZE"]))
        page = min(page, pages)
        students = conn.execute(f"SELECT * FROM students{where} ORDER BY {order} LIMIT ? OFFSET ?",
                                (*params, app.config["PAGE_SIZE"], (page - 1) * app.config["PAGE_SIZE"])).fetchall()
        stats = conn.execute("""SELECT COUNT(*) total, COALESCE(ROUND(AVG(marks), 2), 0) average,
            COALESCE(MAX(marks), 0) highest, COALESCE(MIN(marks), 0) lowest,
            COALESCE(SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END), 0) passed FROM students""").fetchone()
        courses = [r[0] for r in conn.execute("SELECT DISTINCT course FROM students ORDER BY course COLLATE NOCASE")]
        grade_counts = {grade: 0 for grade in ("A+", "A", "B", "C", "D", "F")}
        for row in conn.execute("SELECT marks FROM students"):
            grade_counts[calculate_grade(row[0])] += 1
        recent = conn.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5").fetchall()
        return render_template("index.html", students=students, stats=stats, search=search, course=course,
            courses=courses, sort=sort, page=page, pages=pages, total_filtered=total_filtered,
            grade_counts=grade_counts, recent=recent)

    @app.route("/students/add", methods=["GET", "POST"])
    def add_student():
        if request.method == "POST":
            data, errors = validate_student(request.form)
            if errors:
                for error in errors: flash(error, "error")
                return render_template("student_form.html", student=request.form, page_title="Add Student"), 400
            try:
                db().execute("""INSERT INTO students (name, age, email, course, marks, gender, registration_date, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", tuple(data[k] for k in ("name", "age", "email", "course", "marks", "gender", "registration_date", "phone")))
                db().commit()
            except sqlite3.IntegrityError:
                flash("A student with this email already exists.", "error")
                return render_template("student_form.html", student=request.form, page_title="Add Student"), 400
            flash("Student added successfully.", "success")
            return redirect(url_for("index"))
        return render_template("student_form.html", student={"registration_date": date.today().isoformat()}, page_title="Add Student")

    @app.route("/students/<int:student_id>")
    def student_detail(student_id):
        student = db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if student is None: abort(404)
        return render_template("student_detail.html", student=student, grade=calculate_grade(student["marks"]))

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def edit_student(student_id):
        student = db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if student is None: abort(404)
        if request.method == "POST":
            data, errors = validate_student(request.form)
            if errors:
                for error in errors: flash(error, "error")
                return render_template("student_form.html", student=request.form, page_title="Edit Student"), 400
            try:
                db().execute("""UPDATE students SET name=?, age=?, email=?, course=?, marks=?, gender=?, registration_date=?, phone=? WHERE id=?""",
                    (*[data[k] for k in ("name", "age", "email", "course", "marks", "gender", "registration_date", "phone")], student_id))
                db().commit()
            except sqlite3.IntegrityError:
                flash("Another student already uses this email.", "error")
                return render_template("student_form.html", student=request.form, page_title="Edit Student"), 400
            flash("Student updated successfully.", "success")
            return redirect(url_for("student_detail", student_id=student_id))
        return render_template("student_form.html", student=dict(student), page_title="Edit Student")

    @app.route("/students/<int:student_id>/delete", methods=["POST"])
    def delete_student(student_id):
        cursor = db().execute("DELETE FROM students WHERE id = ?", (student_id,))
        db().commit()
        flash("Student deleted." if cursor.rowcount else "Student not found.", "success" if cursor.rowcount else "error")
        return redirect(url_for("index"))

    @app.route("/about")
    def about(): return render_template("about.html")

    @app.route("/contact")
    def contact(): return render_template("contact.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
