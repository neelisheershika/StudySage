from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import auth, credentials, firestore
import datetime

# Initialize Firebase
cred = credentials.Certificate(r"C:\Users\neeli\OneDrive\Desktop\StudySage\App.py\serviceAccountkey.json.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a strong secret key

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        try:
            user = auth.get_user_by_email(email)
            session["user"] = user.uid
            # Redirect to the dashboard after login
            return redirect(url_for("dashboard"))
        except auth.UserNotFoundError:
            return "Invalid email! User not found in Firebase."
        except Exception as e:
            return f"Error: {e}"
    return render_template("login.html")

# Dashboard Route (Newly Added)
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    # You can customize this dashboard to show an overview or redirect further.
    return render_template("dashboard.html")  # Create dashboard.html in your templates folder.

# Personal Info Route
@app.route("/personal_info", methods=["GET", "POST"])
def personal_info():
    if "user" not in session:
        return redirect(url_for("login"))
    user_id = session["user"]
    if request.method == "POST":
        user_data = {
            "name": request.form["name"],
            "dob": request.form["dob"],
            "hobbies": request.form["hobbies"],
            "exam_name": request.form["exam_name"],
            "exam_duration": int(request.form["exam_duration"]),
            "description": request.form["description"]
        }
        db.collection("users").document(user_id).set(user_data)
        return redirect(url_for("assessment"))
    return render_template("personal_info.html")

# Assessment (Study Plan) Route
@app.route("/assessment", methods=["GET"])
def assessment():
    if "user" not in session:
        return redirect(url_for("login"))
    user_id = session["user"]
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return "User data not found. Please fill in personal info."
    user_data = user_doc.to_dict()
    exam_duration = user_data.get("exam_duration", 30)
    exam_name = user_data.get("exam_name", "General Exam")

    syllabus = {
        "Math": ["Algebra", "Geometry", "Calculus"],
        "Science": ["Physics", "Chemistry", "Biology"],
        "English": ["Grammar", "Comprehension", "Essay Writing"],
        "History": ["Ancient", "Medieval", "Modern"]
    }
    subjects = list(syllabus.keys())
    total_days = exam_duration
    study_plan = {}

    for day in range(1, total_days + 1):
        day_plan = {}
        for subject in subjects:
            topic_index = (day - 1) % len(syllabus[subject])
            day_plan[subject] = syllabus[subject][topic_index]
        study_plan[f"Day {day}"] = day_plan

    # Debug: print the study plan in the console
    print("Study Plan:", study_plan)
    
    return render_template("assessment.html", study_plan=study_plan, exam_name=exam_name)


# Progress Tracking Route
@app.route("/progress")
def progress():
    return render_template("progress.html")

# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)
