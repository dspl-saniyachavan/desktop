from ..data.repositories.user_repository import UserRepository
from ..security.hashing import hash_password, verify_password

class UserService:

    @staticmethod
    def register_user(username, password, role):
        password_hash = hash_password(password)
        return UserRepository.create(username, password_hash, role)

    @staticmethod
    def authenticate(username, password):
        user = UserRepository.get_by_username(username)
        if user and verify_password(password, user.password_hash):
            return user
        return None
