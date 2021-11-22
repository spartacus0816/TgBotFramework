import logging

from nonebot.log import LoguruHandler, logger

aiocache_logger = logging.getLogger("aiocache.serializers.serializers")
aiocache_logger.setLevel(logging.DEBUG)
aiocache_logger.handlers.clear()
aiocache_logger.addHandler(LoguruHandler())

from .event import *
from .bot import Bot as Bot
from .message import Message as Message
from .message import MessageSegment as MessageSegment
