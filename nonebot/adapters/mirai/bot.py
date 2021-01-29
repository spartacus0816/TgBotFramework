from pprint import pprint
from typing import Optional

from nonebot.adapters import Bot as BaseBot
from nonebot.drivers import Driver, WebSocket
from nonebot.typing import overrides


class MiraiBot(BaseBot):

    def __init__(self,
                 connection_type: str,
                 self_id: str,
                 *,
                 websocket: Optional["WebSocket"] = None):
        super().__init__(connection_type, self_id, websocket=websocket)

    @property
    @overrides(BaseBot)
    def type(self) -> str:
        return "mirai"

    @classmethod
    @overrides(BaseBot)
    async def check_permission(cls, driver: "Driver", connection_type: str,
                               headers: dict, body: Optional[dict]) -> str:
        return ''

    @overrides(BaseBot)
    async def handle_message(self, message: dict):
        pprint(message)

    @overrides(BaseBot)
    async def call_api(self, api: str, **data):
        return super().call_api(api, **data)

    @overrides(BaseBot)
    async def send(self, event: "Event", message: str, **kwargs):
        return super().send(event, message, **kwargs)
