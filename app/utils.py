from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hash the password
def hash_function(password: str):
    return pwd_context.hash(password)


# compare the two hashes
def verify_password(input_pass, db_pass):
    # pwd_context has a built-in function called verify that
    # verifies/compares if the input pass and the db stores hash pass are the same
    return pwd_context.verify(input_pass, db_pass)



