# This is the configuration file that adds the constraints to the parameters
# used in the code
# e.g. database_hostname needs to be a string, or access token expiration time needs to be an int
# We get the values to these parameters from the .env file

from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()
