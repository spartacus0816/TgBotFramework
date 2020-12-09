"""
协议适配基类
============

各协议请继承以下基类，并使用 ``driver.register_adapter`` 注册适配器
"""

import abc
from typing_extensions import Literal
from functools import reduce, partial
from dataclasses import dataclass, field
from typing import Any, Dict, Union, Optional, Callable, Iterable, Awaitable, TYPE_CHECKING

from pydantic import BaseModel

from nonebot.config import Config

if TYPE_CHECKING:
    from nonebot.drivers import Driver, WebSocket


class Bot(abc.ABC):
    """
    Bot 基类。用于处理上报消息，并提供 API 调用接口。
    """

    @abc.abstractmethod
    def __init__(self,
                 driver: "Driver",
                 connection_type: str,
                 config: Config,
                 self_id: str,
                 *,
                 websocket: Optional["WebSocket"] = None):
        """
        :参数:

          * ``driver: Driver``: Driver 对象
          * ``connection_type: str``: http 或者 websocket
          * ``config: Config``: Config 对象
          * ``self_id: str``: 机器人 ID
          * ``websocket: Optional[WebSocket]``: Websocket 连接对象
        """
        self.driver = driver
        """Driver 对象"""
        self.connection_type = connection_type
        """连接类型"""
        self.config = config
        """Config 配置对象"""
        self.self_id = self_id
        """机器人 ID"""
        self.websocket = websocket
        """Websocket 连接对象"""

    def __getattr__(self, name: str) -> Callable[..., Awaitable[Any]]:
        return partial(self.call_api, name)

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """Adapter 类型"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def check_permission(cls, driver: "Driver", connection_type: str,
                               headers: dict, body: Optional[dict]) -> str:
        """
        :说明:

          检查连接请求是否合法的函数，如果合法则返回当前连接 ``唯一标识符``，通常为机器人 ID；如果不合法则抛出 ``RequestDenied`` 异常。

        :参数:

          * ``driver: Driver``: Driver 对象
          * ``connection_type: str``: 连接类型
          * ``headers: dict``: 请求头
          * ``body: Optional[dict]``: 请求数据，WebSocket 连接该部分为空

        :返回:

          - ``str``: 连接唯一标识符

        :异常:

          - ``RequestDenied``: 请求非法
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def handle_message(self, message: dict):
        """
        :说明:

          处理上报消息的函数，转换为 ``Event`` 事件后调用 ``nonebot.message.handle_event`` 进一步处理事件。

        :参数:

          * ``message: dict``: 收到的上报消息
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def call_api(self, api: str, **data):
        """
        :说明:

          调用机器人 API 接口，可以通过该函数或直接通过 bot 属性进行调用

        :参数:

          * ``api: str``: API 名称
          * ``**data``: API 数据

        :示例:

        .. code-block:: python

            await bot.call_api("send_msg", message="hello world"})
            await bot.send_msg(message="hello world")
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, event: "Event",
                   message: Union[str, "Message", "MessageSegment"], **kwargs):
        """
        :说明:

          调用机器人基础发送消息接口

        :参数:

          * ``event: Event``: 上报事件
          * ``message: Union[str, Message, MessageSegment]``: 要发送的消息
          * ``**kwargs``
        """
        raise NotImplementedError


class Event(abc.ABC, BaseModel):

    class Config:
        extra = "allow"

    @abc.abstractmethod
    def get_type(self) -> Literal["message", "notice", "request", "meta_event"]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_event_name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_event_description(self) -> str:
        raise NotImplementedError

    def get_log_string(self) -> str:
        return f"[{self.get_event_name()}]: {self.get_event_description()}"

    @abc.abstractmethod
    def get_user_id(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_session_id(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_message(self) -> "Message":
        raise NotImplementedError

    @abc.abstractmethod
    def get_plaintext(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def is_tome(self) -> bool:
        raise NotImplementedError


@dataclass
class MessageSegment(abc.ABC):
    """消息段基类"""
    type: str
    """
    - 类型: ``str``
    - 说明: 消息段类型
    """
    data: Dict[str, Any] = field(default_factory=lambda: {})
    """
    - 类型: ``Dict[str, Union[str, list]]``
    - 说明: 消息段数据
    """

    @abc.abstractmethod
    def __str__(self) -> str:
        """该消息段所代表的 str，在命令匹配部分使用"""
        raise NotImplementedError

    @abc.abstractmethod
    def __add__(self, other) -> "Message":
        """你需要在这里实现不同消息段的合并：
        比如：
            if isinstance(other, str):
                ...
            elif isinstance(other, MessageSegment):
                ...
        注意：不能返回 self，需要返回一个新生成的对象
        """
        raise NotImplementedError

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    @abc.abstractmethod
    def is_text(self) -> bool:
        raise NotImplementedError


class Message(list, abc.ABC):
    """消息数组"""

    def __init__(self,
                 message: Union[str, dict, list, BaseModel, MessageSegment,
                                "Message"] = None,
                 *args,
                 **kwargs):
        """
        :参数:

          * ``message: Union[str, dict, list, BaseModel, MessageSegment, Message]``: 消息内容
        """
        super().__init__(*args, **kwargs)
        if isinstance(message, (str, dict, list, BaseModel)):
            self.extend(self._construct(message))
        elif isinstance(message, Message):
            self.extend(message)
        elif isinstance(message, MessageSegment):
            self.append(message)

    def __str__(self):
        return ''.join((str(seg) for seg in self))

    @classmethod
    def __get_validator__(cls):
        yield cls._validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            examples=["foo", {
                "type": "text",
                "data": {
                    "text": "bar"
                }
            }])

    @classmethod
    def _validate(cls, value):
        return cls(value)

    @staticmethod
    @abc.abstractmethod
    def _construct(
            msg: Union[str, dict, list, BaseModel]) -> Iterable[MessageSegment]:
        raise NotImplementedError

    def __add__(self, other: Union[str, MessageSegment,
                                   "Message"]) -> "Message":
        result = self.__class__(self)
        if isinstance(other, str):
            result.extend(self._construct(other))
        elif isinstance(other, MessageSegment):
            result.append(other)
        elif isinstance(other, Message):
            result.extend(other)
        return result

    def __radd__(self, other: Union[str, MessageSegment, "Message"]):
        result = self.__class__(other)
        return result.__add__(self)

    def append(self, obj: Union[str, MessageSegment]) -> "Message":
        """
        :说明:

          添加一个消息段到消息数组末尾

        :参数:

          * ``obj: Union[str, MessageSegment]``: 要添加的消息段
        """
        if isinstance(obj, MessageSegment):
            super().append(obj)
        elif isinstance(obj, str):
            self.extend(self._construct(obj))
        else:
            raise ValueError(f"Unexpected type: {type(obj)} {obj}")
        return self

    def extend(self, obj: Union["Message",
                                Iterable[MessageSegment]]) -> "Message":
        """
        :说明:

          拼接一个消息数组或多个消息段到消息数组末尾

        :参数:

          * ``obj: Union[Message, Iterable[MessageSegment]]``: 要添加的消息数组
        """
        for segment in obj:
            self.append(segment)
        return self

    def reduce(self) -> None:
        """
        :说明:

          缩减消息数组，即按 MessageSegment 的实现拼接相邻消息段
        """
        index = 0
        while index < len(self):
            if index > 0 and self[index -
                                  1].is_text() and self[index].is_text():
                self[index - 1] += self[index]
                del self[index]
            else:
                index += 1

    def extract_plain_text(self) -> str:
        """
        :说明:

          提取消息内纯文本消息
        """

        def _concat(x: str, y: MessageSegment) -> str:
            return f"{x} {y}" if y.is_text() else x

        plain_text = reduce(_concat, self, "")
        return plain_text[1:] if plain_text else plain_text
