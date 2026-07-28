"""
This file maintain configs like secretkeys,passwords, and database related info
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, Field
from sqlalchemy import URL


# Here we define class for database connection info
class DatabaseConfig(BaseSettings):
    # take database connection info from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True, 
        extra="ignore",env_prefix="DB_"
    )

    drivername: str = Field(alias="DB_DRIVERNAME")
    username: str = Field(alias="DB_USERNAME")
    password: str = Field(alias="DB_PASSWORD")
    host: str = Field(alias="DB_HOST")
    port: int = Field(alias="DB_PORT")
    database: str = Field(alias="DB_DATABASE")

    database_url: str | None = None
    redis_url: str | None = None
    secret_key: str | None = None
    debug: bool = False

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
        env_file=".key", env_file_encoding="utf-8", case_sensitive=True, extra="ignore" 
    )

    password_secret_key: str  # for password, makes passwords more secure by adding this key to the password before hashing
    dummy_pass: str = "$argon2i$v=19$m=16,t=2,p=1$ZGRkc2ZzZGZzc2Rm$rVCuSiAq61E9DtMfNk1Z7Q" # dummy hash for password comaprison
    secret_key: str  # for jwt token, should be long and random
    algorithm: str  # for jwt token

class EmailConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",case_sensitive=False, extra="ignore" )
    MAIL_SERVER:str
    MAIL_PORT:int
    MAIL_FROM:str
    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    FRONTEND_BASE_URL:str
