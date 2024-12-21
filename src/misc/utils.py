import logging
from datetime import datetime, UTC


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def now_utc_time() -> datetime:
    return datetime.now(UTC)


def now_timestamp_seconds() -> int:
    return int(now_utc_time().timestamp())


def format_city_name(city_name: str) -> str:
    formatted_name = '_'.join([part.strip() for part in city_name.split(',')])
    formatted_name = formatted_name.lower().replace(' ', '_')
    return formatted_name