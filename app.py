import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from extensions import db
from models import User, Assessment
from services.auth_service import register_user, authenticate_user
import requests
from services.llm_service import generate_career_analysis
from sqlalchemy import inspect, text


app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(
    os.path.join(app.root_path, "instance"),
    exist_ok=True
)

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to continue.", "error")
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("dashboard/index.html", user=user)




@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    if "user_id" not in session:
        flash("Please log in to take the assessment.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        allowed = {
            "education": {
                "school", "diploma", "undergraduate",
                "graduate", "postgraduate", "other"
            },
            "interest": {
                "software", "ai_ml", "data", "hardware",
                "mechanical", "business", "government",
                "creative", "research", "healthcare", "undecided"
            },
            "situation": {
                "studying", "working", "job_seeking",
                "career_change", "exploring"
            },
            "favorite_subject": {
                "logical", "technology", "numbers", "design",
                "people", "business", "science", "reading",
                "practical", "unsure"
            },
            "work_style": {
                "independent", "team", "people_facing",
                "hands_on", "mixed", "unsure"
            },
            "priority": {
                "income", "stability", "flexibility", "impact",
                "creativity", "interest", "growth", "entrepreneurship"
            },
            "dislike": {
                "coding", "math", "people", "physical",
                "routine", "uncertainty", "none"
            },
            "goal": {
                "internship", "job", "higher_studies",
                "entrepreneurship", "exploration", "government_exam"
            }
        }

        answers = {
            field: request.form.get(field, "").strip()
            for field in allowed
        }

        for field, permitted_values in allowed.items():
            if answers[field] not in permitted_values:
                flash("Please complete every field correctly.", "error")
                return redirect(url_for("assessment"))

        try:
            daily_hours = int(request.form.get("daily_hours", ""))
        except (ValueError, TypeError):
            flash("Please select your available study time.", "error")
            return redirect(url_for("assessment"))

        if daily_hours not in {1, 2, 4, 6, 8}:
            flash("Invalid study time. Please try again.", "error")
            return redirect(url_for("assessment"))

        new_assessment = Assessment(
            user_id=session["user_id"],
            education=answers["education"],
            interest=answers["interest"],
            situation=answers["situation"],
            favorite_subject=answers["favorite_subject"],
            work_style=answers["work_style"],
            priority=answers["priority"],
            dislike=answers["dislike"],
            goal=answers["goal"],
            daily_hours=daily_hours,

            # Temporary placeholders until Step 2 measures ability.
            python_level=0,
            math_level=0,
            coding_level=0
        )

        try:
            db.session.add(new_assessment)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not save discovery answers")
            flash("We couldn't save your answers. Please try again.", "error")
            return redirect(url_for("assessment"))

        flash("Discovery answers saved successfully!", "success")
        return redirect(url_for("assessment_results"))

    return render_template("assessment/start.html")




@app.route("/careers")
def careers():
    return render_template("careers/discover.html")


@app.route("/roadmap")
def roadmap():
    return render_template("roadmap/index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name","")
        email = request.form.get("email","")
        password = request.form.get("password","")

        try:
            success, message = register_user(name, email, password)
        except Exception:
            db.session.rollback()
            app.logger,exception("Registration failed")
            flash("Registartion failed. Please try again.","error")
            return render_template("auth/register.html"),500
        if success:
            flash(message + " Please login in.", "success")
            return redirect(url_for("login"))
        flash(message, "error")

    return render_template("auth/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        user = authenticate_user(email, password)

        if user:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))





@app.route("/assessment/results")
def assessment_results():
    if "user_id" not in session:
        flash("Please log in to view results.", "error")
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    assessment = (
        Assessment.query
        .filter_by(user_id=user.id)
        .order_by(Assessment.id.desc())
        .first()
    )

    if assessment is None:
        flash("Please complete the assessment first.", "error")
        return redirect(url_for("assessment"))

    recommendation = None
    analysis_error = False

    
    try:
         recommendation = generate_career_analysis(assessment)
         print("Career analysis generated successfully.")

    except Exception as exc:
        app.logger.exception("Career analysis generation failed")
        print("ACTUAL ERROR:", repr(exc))
        analysis_error = True


    skill_labels = {
        0: "Not started",
        1: "Beginner",
        2: "Intermediate",
        3: "Advanced"
    }

    interest_names = {
        "software": "Software Development",
        "ai_ml": "AI and Machine Learning",
        "data": "Data Science and Analytics",
        "hardware": "Hardware and Electronics",
        "mechanical": "Mechanical Engineering",
        "business": "Business and Management",
        "creative": "Creative Careers",
        "research": "Research",
        "government": "Government Services",
        "healthcare": "Healthcare and Life Sciences",
        "undecided": "Still exploring"
    }

    goal_names = {
        "internship": "Get an internship",
        "job": "Get a job",
        "higher_studies": "Pursue higher studies",
        "entrepreneurship": "Build a startup",
        "exploration": "Explore career options",
        "government_exam": "Prepare for government exams"
    }

    return render_template(
        "assessment/result.html",
        user=user,
        assessment=assessment,
        skill_labels=skill_labels,
        interest_name=interest_names.get(
            assessment.interest, "Other"
        ),
        goal_name=goal_names.get(
            assessment.goal, "Other"
        ),
        recommendation=recommendation,
        analysis_error=analysis_error
    )





@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404



with app.app_context():
    db.create_all()

    # Add new discovery columns to an existing SQLite database.
    existing_columns = {
        column["name"]
        for column in inspect(db.engine).get_columns("assessments")
    }

    new_columns = {
        "situation": "VARCHAR(50)",
        "favorite_subject": "VARCHAR(50)",
        "work_style": "VARCHAR(50)",
        "priority": "VARCHAR(50)",
        "dislike": "VARCHAR(50)",
    }

    for column_name, column_type in new_columns.items():
        if column_name not in existing_columns:
            db.session.execute(
                text(
                    f"ALTER TABLE assessments "
                    f"ADD COLUMN {column_name} {column_type}"
                )
            )

    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
