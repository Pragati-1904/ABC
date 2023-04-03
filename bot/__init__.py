from telethon import TelegramClient
from aioredis import Redis
from logging import INFO, basicConfig, getLogger
from .config import Var

basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] : %(message)s",
    level=INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
LOGS = getLogger(__name__)
TelethonLogger = getLogger("Telethon")
TelethonLogger.setLevel(INFO)

try:
    LOGS.info("Trying Connect With Telegram")
    bot = TelegramClient(None, Var.API_ID, Var.API_HASH)
    LOGS.info("Successfully Connected with Telegram")
except Exception as e:
    LOGS.critical(str(e))
    exit()

try:
    dB = Redis(
        username=Var.REDISUSER,
        host=Var.REDISHOST,
        port=Var.REDISPORT,
        password=Var.REDISPASSWORD,
        decode_responses=True,
    )
    CACHE = {}
except Exception as es:
    LOGS.critical(str(es))
    exit()