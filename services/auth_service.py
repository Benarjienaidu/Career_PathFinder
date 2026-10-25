from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User



def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    if len(password)<8:
        return False, "Password must be at least 8 characters."

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return False,"An account with this email already exists."

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )


    db.session.add(user)
    db.session.commit()

    return True, "registration successful"

def authenticate_user(email, password):
    email=email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        return user
    return None
