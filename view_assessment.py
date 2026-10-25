
from app import app
from models import Assessment

with app.app_context():
    assessments = Assessment.query.all()

    if not assessments:
        print("No assessments saved yet.")

    for item in assessments:
        print("Assessment ID:", item.id)
        print("User ID:", item.user_id)
        print("Education:", item.education)
        print("Interest:", item.interest)
        print("Python level:", item.python_level)
        print("Math level:", item.math_level)
        print("Coding level:", item.coding_level)
        print("Daily hours:", item.daily_hours)
        print("Goal:", item.goal)
        print("-" * 30)
