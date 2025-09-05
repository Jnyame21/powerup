import os
import sys
from datetime import datetime, timedelta

# django
from django.core.validators import EmailValidator
from django.conf import settings

import phonenumbers
from phonenumbers import NumberParseException
import pusher
from timezonefinder import TimezoneFinder
import pytz
from haversine import haversine, Unit
import logging


logger = logging.getLogger(__name__)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {  # This handler writes logs to standard output
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
    },
    'root': {  # Root logger configuration
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # You can configure other loggers here as needed
    },
}

# Base url
def base_url(value):
    scheme = value.scheme
    host = value.get_host()
    return f"{scheme}://{host}"


def valid_phone_number(number:str):
    try:
        phone_number = phonenumbers.parse(number, None)
        if not phonenumbers.is_valid_number(phone_number):
            return False
    except NumberParseException:
        return False
    return True


def valid_email(email:str):
    email_validator = EmailValidator()
    try:
        email_validator(email)
    except Exception:
        return False
    return True


# Configure logging
def configure_logging():
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set log level to capture debug messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler and set level to debug
    if not settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Initialize the logger
def log_error(error_message:str):
    logger = configure_logging()
    logger.debug(error_message)
    logger.info(error_message)


def use_pusher():
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
    )
    return pusher_client


class ErrorMessageException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    def __str__(self) -> str:
        return self.message 


# Convert datetime
def format_relative_date_time(utc_date, day_name, time):
    # Convert the UTC string to a datetime object
    utc_datetime = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Get the current UTC datetime
    current_utc_datetime = datetime.now()

    # Check if it's today
    if utc_datetime.date() == current_utc_datetime.date():
        if day_name and time:
            return f"Today, {utc_datetime.strftime('%B %d, %Y at %H:%M')}"
        elif day_name and not time:
            return f"Today, {utc_datetime.strftime('%B %d, %Y')}"
        elif not day_name and time:
            return utc_datetime.strftime('%B %d, %Y at %H:%M')
        elif not day_name and not time:
            return utc_datetime.strftime('%B %d, %Y')

    elif utc_datetime.date() == (current_utc_datetime - timedelta(days=1)).date():
        if day_name and time:
            return f"Yesterday, {utc_datetime.strftime('%B %d, %Y at %H:%M')}"
        elif day_name and not time:
            return f"Yesterday, {utc_datetime.strftime('%B %d, %Y')}"
        elif not day_name and time:
            return utc_datetime.strftime('%B %d, %Y at %H:%M')
        elif not day_name and not time:
            return utc_datetime.strftime('%B %d, %Y')

    else:
        if day_name and time:
            return utc_datetime.strftime('%A, %B %d, %Y at %H:%M')
        elif day_name and not time:
            return utc_datetime.strftime('%A, %B %d, %Y')
        elif not day_name and time:
            return utc_datetime.strftime('%B %d, %Y at %H:%M')
        elif not day_name and not time:
            return utc_datetime.strftime('%B %d, %Y')


def is_within_radius(user_lat, user_lon, office_lat, office_lon, radius_m):
    user_location = (user_lat, user_lon)
    office_location = (office_lat, office_lon)
    distance_m = haversine(user_location, office_location, unit=Unit.METERS)

    return distance_m <= radius_m


def get_timezone(lat:float, lon:float):
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lng=lon, lat=lat)
    return timezone


def convert_to_local_datetime(utc_datetime, user_timezone):
    user_tz = pytz.timezone(user_timezone)
    return utc_datetime.replace(tzinfo=pytz.utc).astimezone(user_tz)


def get_current_user_utc_datetime(user_timezone):
    user_tz = pytz.timezone(user_timezone)
    user_local_time = datetime.now(user_tz)
    utc_datetime = user_local_time.astimezone(pytz.utc)
    return utc_datetime


def delete_file(File):
    if hasattr(File, 'url') and hasattr(File.url, 'name') and hasattr(File.url, 'storage'):
        storage = File.url.storage
        path = File.url.name
        if storage.exists(path):
            storage.delete(path)



