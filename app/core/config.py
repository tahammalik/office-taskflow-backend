"""
This file maintain configs like secretkeys,passwords, and database related info
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


# Here we define class for database connection info
class DatabaseConfig(BaseSettings):
    # take database connection info from .env file
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    drivername: str
    username: str
    password: str
    host: str
    port: int
    database: str

    # build connection with database
    def build_connection(self) -> URL:
        return URL.create(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


# Here we define class for secrete keys and passwords
class SecretConfig(BaseSettings):
    # take secret keys and passwords from .key file
    model_config = SettingsConfigDict(
        env_file=".key", env_file_encoding="utf-8", case_sensitive=False
    )

    password_secret_key: str  # for password, makes passwords more secure by adding this key to the password before hashing
    dummy_hash: str  # dummy hash for password comaprison
    secret_key: str  # for jwt token, should be long and random
    algorithm: str  # for jwt token
