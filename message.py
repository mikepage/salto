import codecs
import translitcodec  # used to provide "translit/short" encoding
from typing import List, Optional

from salto.i18n import localized


class Message:
    ENCODING: str = "Latin-1"
    FIELD_DELIMITER: bytes = b"\xB3"  # Each field in a message is delimited by this separator character
    ERRORS: List[bytes] = [b"ES", b"NC", b"NF", b"OV", b"EP", b"EF", b"TD", b"ED", b"EA", b"OS", b"EO", b"EV", b"EG"]  # Error message keys

    def __init__(self, fields: List[bytes]):
        self.fields: List[bytes] = fields

    # Example: Message.encode('|CN|Online Encoder 1|R|Room 1|')
    @staticmethod
    def encode(message_string: str) -> "Message":
        return Message([Message.sanitize_text(field) for field in message_string.split("|")[1:-1]])

    @staticmethod
    def decode(raw_message: bytes) -> "Message":
        return Message(raw_message.split(Message.FIELD_DELIMITER)[1:-1])

    @staticmethod
    def sanitize_text(text: str) -> bytes:
        return codecs.encode(text, "translit/short/" + Message.ENCODING, "replace").replace(Message.FIELD_DELIMITER, b"|").replace(b"\r", b"")

    @staticmethod
    def encode_str(text: str) -> bytes:
        return text.encode(Message.ENCODING)

    @property
    def command(self) -> Optional[str]:
        return None if self.is_error else self.str_field(0)

    @property
    def details(self) -> List[str]:
        return [field.decode(Message.ENCODING) for field in self.fields[1:]]

    @property
    def is_error(self) -> bool:
        return self.fields[0] in Message.ERRORS

    @property
    def error(self) -> Optional[str]:
        if not self.is_error:
            return None

        if self.fields[0] == b"EG":
            # Yields an encoder or phone number, followed by an error message
            return self.str_field(-1) if len(self.fields) > 1 else localized('salto.errors.EG')
        else:
            return localized("salto.errors." + self.str_field(0))

    def __bytes__(self) -> bytes:
        return Message.FIELD_DELIMITER + Message.FIELD_DELIMITER.join(self.fields) + Message.FIELD_DELIMITER

    def str_field(self, field_index: int) -> str:
        return self.fields[field_index].decode(Message.ENCODING)
