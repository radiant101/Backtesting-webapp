from passlib.context import CryptContext
# basically telling what hashing algo using across code
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password : str):
    return pwd_context.hash(password)

# verification for login
def verify(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)