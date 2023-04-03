from glob import glob
from importlib import import_module
from traceback import format_exc

from . import *

try:
    bot.start(bot_token=Var.BOT_TOKEN)
except Exception as err:
    LOGS.exception(str(err))

async def sync_redis_into_local(db: Redis, cache: dict):
    try:
        keys = await db.keys()
        for key in keys:
            data = (eval((await db.get(key)) or "{}"))
            cache.update({key: data})
    except Exception as er:
        LOGS.exception(str(er))

plugins = sorted(glob("bot/plugins/*.py"))
for plugin in plugins:
    try:
        if plugin.endswith("_.py"):
            continue
        plugin = plugin.replace(".py", "").replace("/", ".").replace("\\", ".")
        import_module(plugin)
        LOGS.info(f"Successfully Loaded {plugin}")
    except BaseException:
        LOGS.info(format_exc())

LOGS.info("Syncing Redis Into Local Database.")
bot.loop.run_until_complete(sync_redis_into_local(dB, CACHE))
LOGS.info("Successfully Synced Redis Into Local Database.")

LOGS.info("Bot Started...")

try:
    bot.run_until_disconnected()
except KeyboardInterrupt:
    LOGS.info("Stopoing The Bot!")
    LOGS.info("Going Offline!")
    exit()