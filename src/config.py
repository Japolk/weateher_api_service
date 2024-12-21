import os

import dotenv

dotenv.load_dotenv()

class Settings:
    #OpenWeather API settings
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    MAX_CALLS_PER_MIN = int(os.getenv('MAX_CALLS_PER_MIN'))

    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE')

    # Caching Configuration
    CACHE_EXPIRY_MINUTES = int(os.getenv('CACHE_EXPIRY_MINUTES'))


settings = Settings()