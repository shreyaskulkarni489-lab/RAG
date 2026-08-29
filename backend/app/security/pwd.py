import hashlib
import os

def get_password_hash(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{h}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False

    # 1. Salted SHA256 format (salt:hash)
    if ":" in hashed_password:
        salt, h = hashed_password.split(":", 1)
        test_h = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        if test_h == h:
            return True

    # 2. Try passlib/bcrypt if installed
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass

    # 3. Plaintext fallback (for dev/seeder edge-cases)
    if plain_password == hashed_password:
        return True

    return False


