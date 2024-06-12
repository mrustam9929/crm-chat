from loguru import logger
import os

from core.settings.base import *

SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(' ')

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(BASE_DIR).joinpath('media')
STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR).joinpath('static')

logger.add(f'{BASE_DIR}/logs/project/info.log', level='INFO', rotation='00:00', compression='zip')
