from passlib.context import CryptContext

from src.core.config import PASSWORD_PEPPER

class HashService:

    
    def __init__(self, pwd_context : CryptContext):
        self.pwd_context = pwd_context
    
    
    def hash_password(self, password : str) -> str:
        password_concat = password + PASSWORD_PEPPER
        return self.pwd_context.hash(password_concat)
    
    
    def verify_hash_password(self, password : str, hash_password : str) -> bool:
        password_concat = password + PASSWORD_PEPPER
        return self.pwd_context.verify(password_concat, hash_password)