from abc import ABC, abstractmethod
from enum import Enum, EnumMeta


class DefaultEnumMeta(EnumMeta):
    default = object()

    def __call__(cls, value=default, *args, **kwargs):
        if value is DefaultEnumMeta.default:
            # Assume the first enum is default
            return next(iter(cls))
        return super().__call__(value, *args, **kwargs)


class MessageCode(Enum):
    INITIALIZE = "INIT",
    DISCONNECT = "DISC"


class TCPMessage():

    @property
    @abstractmethod
    def message_code(self):
        return None

    @property
    @abstractmethod
    def content(self):
        return None

    @abstractmethod
    def format(self):
        pass


class StringMessage(TCPMessage, ABC):

    def __init__(self, message_code: MessageCode, content: str):
        self.__message_code = message_code
        self.__content = content

    @property
    def message_code(self):
        return self.__message_code

    @property
    def content(self):
        return self.__content

    def format(self):
        return self.message_code.value
