import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User

# Password hashing using bcrypt
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Check password against hash
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Add a new user to the database
def add_user(db: Session, username: str, email: str, password: str) -> User:
    hashed_pw = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Authenticate user by username and password
def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None