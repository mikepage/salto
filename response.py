import re
from typing import Optional

from salto import common
from salto.message import Message


class Response:
    class InvalidMessage(Exception):
        pass

    RAW_MESSAGE_RE = re.compile(rb"^" + common.STX + rb"(.*)" + common.ETX + rb"(.*)$")

    def __init__(self, raw_response: bytes):
        self.raw_response = raw_response
        self._lrc: Optional[bytes] = None
        self._raw_message: Optional[bytes] = None

        if self.is_message:
            self.verify()

    @property
    def is_ack(self) -> bool:
        return self.raw_response == common.ACK

    @property
    def is_nak(self) -> bool:
        return self.raw_response == common.NAK

    @property
    def is_message(self) -> bool:
        return self.raw_response.startswith(common.STX)

    def verify(self) -> None:
        if self.lrc != common.LRC_SKIP and common.lrc(self.raw_message) != self.lrc:
            raise Response.InvalidMessage("LRC is incorrect!")

    @property
    def lrc(self) -> bytes:
        if self._lrc is not None:
            return self._lrc

        match = Response.RAW_MESSAGE_RE.search(self.raw_response)
        self._lrc = match[2] if match is not None else b""
        return self._lrc

    @property
    def raw_message(self) -> bytes:
        if self._raw_message is not None:
            return self._raw_message

        match = Response.RAW_MESSAGE_RE.search(self.raw_response)
        self._raw_message = match[1] if match is not None else b""
        return self._raw_message

    @property
    def message(self) -> Message:
        return Message.decode(self.raw_message)
