import aiohttp
from fastapi import HTTPException
from asyncio_throttle import Throttler

from src.misc.utils import get_logger


class OpenWeatherClient:
    API_URL = 'https://api.openweathermap.org'
    GEO_ENDPOINT = API_URL + '/geo/1.0/direct'
    WEATHER_ENDPOINT = API_URL + '/data/2.5/weather'

    def __init__(self):
        self._api_key = None
        self._aiohttp_session = None
        self._throttler = None
        self._logger = get_logger(__name__)

    def initialize(self, api_key: str, max_cals_per_min: int):
        self._api_key = api_key
        self._aiohttp_session = aiohttp.ClientSession()
        self._throttler = Throttler(rate_limit= max_cals_per_min, period=60)
        self._logger.info("OpenWeatherClient initialized")

    async def close(self):
        if self._aiohttp_session:
            await self._aiohttp_session.close()
            self._aiohttp_session = None
        self._logger.info('OpenWeatherClient Cleared')

    async def get_city_weather(self, city_name) -> dict:
        """
        this is the life

        """
        geo_result = await self.query_url(
            url = self.GEO_ENDPOINT,
            query_parameters = {'q': city_name, 'appid': self._api_key}
        )
        if not geo_result:
            raise HTTPException(
                status_code=404,
                detail='City not found. '
                       'Either your city is not on our maps or you are using the wrong city name.'
            )
        city = geo_result[0]
        weather_result = await self.query_url(
            url=self.WEATHER_ENDPOINT,
            query_parameters={'lat': city['lat'], 'lon': city['lon'], 'appid': self._api_key}
        )
        return weather_result

    async def query_url(self, url: str, query_parameters: dict) -> dict:
        """
        this is the life

        """
        async with self._throttler:
            async with self._aiohttp_session.get(url=url, params=query_parameters) as response:
                if response.status == 404:
                    raise HTTPException(
                        status_code=404,
                        detail='City not found. '
                               'Either your city is not on our maps or you are using the wrong city name.'
                    )
                if response.status in (500, 502, 503, 504, 401):
                    self._logger.error(f'Openweather API error: {await response.text()}')
                    raise HTTPException(status_code=500, detail=f'Something went wrong, please try again later')
                result = await response.json()
        return result
