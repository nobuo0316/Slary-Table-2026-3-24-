from sqlalchemy.orm import Session
from .models import User
from .auth import hash_password

def seed_admin(db: Session):
    if db.query(User).count() > 0:
        return
    admin = User(email="admin@example.com", password_hash=hash_password("admin123"), role="admin")
    editor = User(email="editor@example.com", password_hash=hash_password("editor123"), role="editor")
    viewer = User(email="viewer@example.com", password_hash=hash_password("viewer123"), role="viewer")
    db.add_all([admin, editor, viewer])
    db.commit()
