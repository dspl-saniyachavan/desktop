from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)

def verify_password(password, hashed):
    try:
        return ph.verify(hashed, password)
    except:
        return False
