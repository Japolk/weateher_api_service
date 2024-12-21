from typing import Annotated, Type
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from src.misc.utils import get_logger
from src.services.weather_service import WeatherService


api_logger = get_logger('fastapi')

@asynccontextmanager
async def lifespan(app: FastAPI):
    weather_service = get_weather_service()
    weather_service.initialize()
    yield
    await weather_service.close()


def get_weather_service() -> WeatherService:
    return WeatherService()

WeatherServiceDep = Annotated[Type[WeatherService], Depends(get_weather_service)]

app = FastAPI(lifespan=lifespan)

@app.get('/weather')
async def get_weather(
        city: str,
        weather_service: WeatherServiceDep,
        background_tasks: BackgroundTasks,
):
    cached_weather = await weather_service.check_cache(city)
    if cached_weather is not None:
        return cached_weather

    city_weather = await weather_service.fetch_weather(city)
    background_tasks.add_task(weather_service.store_weather, city, city_weather)
    return city_weather


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    api_logger.critical(f'Unhandled exception: {exc}')
    return JSONResponse(status_code=500, content={'message': 'Service Unavailable, please try again later'})
