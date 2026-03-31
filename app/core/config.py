"""
    This file maintain configs like secretkeys,passwords, and database related info
"""
from pydantic_settings import BaseSettings,SettingsConfigDict
from sqlalchemy import URL

class DatabaseConfig(BaseSettings):
    # define components for database connection
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    drivername:str
    username:str
    password:str
    host:str
    port:int
    database:str

    # build connection with database
    def build_connection(self) -> str:
        return URL.create(
            drivername=self.drivername,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
# Here we define class for importent keys and passwords
class SecretConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.key',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    password_secret_key:str 
    dummy_hash:str
    secret_key:str
    algorithm:str 

