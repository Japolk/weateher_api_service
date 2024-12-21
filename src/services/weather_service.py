from datetime import timedelta
from typing import Optional

from src.config import settings
from src.services.aws_client import AWSClient
from src.services.openweather_client import OpenWeatherClient
from src.misc.utils import (
    get_logger,
    now_utc_time,
    now_timestamp_seconds,
    format_city_name,
)


class WeatherService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

            self._aws_client = AWSClient()
            self._weather_client = OpenWeatherClient()
            self._cache_time_minutes = settings.CACHE_EXPIRY_MINUTES
            self._logger = get_logger(__name__)

    def initialize(self):
        self._aws_client.initialize(
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            access_key_secret=settings.AWS_SECRET_ACCESS_KEY,
            aws_region=settings.AWS_REGION,
            bucket_name=settings.S3_BUCKET_NAME,
            dynamodb_table=settings.DYNAMODB_TABLE,
        )
        self._weather_client.initialize(
            api_key=settings.OPENWEATHER_API_KEY,
            max_cals_per_min=settings.MAX_CALLS_PER_MIN,
        )
        self._logger.info('WeatherService initialized')

    async def close(self):
        await self._weather_client.close()
        self._logger.info('WeatherService cleared')

    async def fetch_weather(self, city: str) -> dict:
        self._logger.info(f'Fetching weather from openweather for {city}')
        return await self._weather_client.get_city_weather(city)

    async def check_cache(self, city: str) -> Optional[dict]:
        """
        Check for a recent cache file of a city.

        """
        city_name = format_city_name(city)
        self._logger.info(f'Checking for a recent cache, city: {city_name}')
        cutoff_time = now_utc_time() - timedelta(minutes=self._cache_time_minutes)
        cache_file = await self._aws_client.find_recent_s3_file(city_name, cutoff_time=cutoff_time)

        if cache_file is not None:
            self._logger.info(f'Cache found for {city_name}')
            return await self._aws_client.get_s3_file(cache_file['Key'])
        else:
            self._logger.info(f'No cache for {city_name}')
            return None

    async def store_weather(self, city: str, weather: dict):
        """
        Store weather to S3 Bucket and log weather event to dynamodb

        """
        city_name = format_city_name(city)
        timestamp = now_timestamp_seconds()
        filename = f'{city_name}_{timestamp}.json'
        s3_file_url = await self._aws_client.put_s3_file(filename, weather)
        await self._aws_client.log_to_dynamodb(city_name, timestamp, s3_file_url)
