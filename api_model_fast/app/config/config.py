import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    DEBUG = os.environ.get("DEBUG", False)

    # PostgreSQL
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    DB_NAME = os.environ.get("DB_NAME")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")

    # AWS Bedrock
    PROFILE_ARN = os.environ.get("PROFILE_ARN", "tu_profile_arn_here")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")

    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    CONVERSATIONS_URL = os.getenv("CONVERSATIONS_URL")
