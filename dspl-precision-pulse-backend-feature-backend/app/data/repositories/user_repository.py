from ..models.user import User
from ..models import db

class UserRepository:

    @staticmethod
    def create(username, password_hash, role):
        user = User(
            username=username,
            password_hash=password_hash,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
