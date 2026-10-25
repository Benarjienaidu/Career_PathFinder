
from app import app
from models import User

with app.app_context():
    users = User.query.all()

    if not users:
        print("No registered users found.")
    else:
        for user in users:
            print("ID:", user.id)
            print("Name:", user.name)
            print("Email:", user.email)
            print("Created at:", user.created_at)
            print("-" * 30)
