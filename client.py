import io
import socket
from logging import Logger
from time import sleep
from typing import Optional

from salto import common
from salto.message import Message
from salto.response import Response


class Client:
    MAX_RETRIES = 3

    CONNECT_TIMEOUT = 10  # seconds to connect the server
    WRITE_TIMEOUT = 10  # seconds to write a request
    READ_TIMEOUT = 30  # seconds to read some bytes. Must including waiting time to place the card

    class InvalidAcknowledgement(Exception):
        pass

    # client = Client("192.168.1.120:8090")
    def __init__(self, endpoint: str, logger: Optional[Logger] = None, lrc_skip: bool = False):
        host, _, port = endpoint.partition(":")
        self.host: str = host
        self.port: int = int(port)
        self.logger = logger
        self.lrc_skip = lrc_skip

    @property
    def is_ready(self) -> bool:
        return self.send_request(common.ENQ).is_ack

    def create_connection(self) -> socket.socket:
        return socket.create_connection((self.host, self.port), Client.CONNECT_TIMEOUT)

    def send_request(self, request: bytes) -> Response:
        with self.create_connection() as conn:
            return self._send_request(conn, request)

    def send_message(self, message: Message) -> Response:
        return self.send_request(self.encode_message(message))

    def encode_message(self, message: Message) -> bytes:
        message_bytes = bytes(message)
        lrc = common.LRC_SKIP if self.lrc_skip else common.lrc(message_bytes)
        return common.STX + message_bytes + common.ETX + lrc

    def _send_request(self, conn: socket.socket, request: bytes, attempt: int = 1) -> Response:
        self._debug("out", request)
        conn.settimeout(Client.WRITE_TIMEOUT)
        conn.sendall(request)

        conn.settimeout(Client.READ_TIMEOUT)
        acknowledgement = conn.recv(1)
        self._debug("in", acknowledgement)

        if request == common.ENQ and acknowledgement in [common.ACK, common.NAK]:
            return Response(acknowledgement)
        elif acknowledgement == common.ACK:
            return self.read_stx(conn)
        elif acknowledgement == common.NAK:
            if attempt < Client.MAX_RETRIES:
                self.await_ready(conn)
                return self._send_request(conn, request, attempt + 1)
            else:
                return Response(acknowledgement)
        else:
            raise Client.InvalidAcknowledgement(f"Invalid SALTO acknowledgement: {acknowledgement!r}")

    def read_stx(self, conn: socket.socket) -> Response:
        with io.BytesIO() as buffer:
            while True:
                conn.settimeout(Client.READ_TIMEOUT)
                current_control_char = conn.recv(1)
                buffer.write(current_control_char)

                # Read until ETX
                if current_control_char == common.ETX:
                    break

            # Read the LCR char
            conn.settimeout(Client.READ_TIMEOUT)
            buffer.write(conn.recv(1))

            response = buffer.getvalue()
            self._debug("in", response)

            return Response(response)

    def await_ready(self, conn: socket.socket) -> None:
        attempt = 1
        while True:
            self._debug("out", common.ENQ)
            conn.settimeout(Client.WRITE_TIMEOUT)
            conn.sendall(common.ENQ)

            conn.settimeout(Client.READ_TIMEOUT)
            acknowledgement = conn.recv(1)
            self._debug("in", acknowledgement)

            if acknowledgement == common.ACK or attempt >= Client.MAX_RETRIES:
                break

            attempt += 1
            sleep(0.2)

    def _debug(self, direction: str, message: bytes) -> None:
        if self.logger is None:
            return

        message = message.replace(common.STX, b"STX ")
        message = message.replace(common.ETX, b" ETX")
        message = message.replace(common.ENQ, b"ENQ")
        message = message.replace(common.ACK, b"ACK")
        message = message.replace(common.NAK, b"NAK")
        message = message.replace(common.LRC_SKIP, b"LRC_SKIP")
        message = message.replace(Message.FIELD_DELIMITER, b"|")

        self.logger.debug(f"[SALTO][{self.host}:{self.port}] {'->' if direction == 'out' else '<-'} {message!r}")
