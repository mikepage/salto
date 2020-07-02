from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from salto.message import Message


class CardDetails:
    DATETIME_FORMAT: str = "%H%M%d%m%y"

    class EjectStrategies(Enum):
        EJECT = b"E"  # Ejection. The PC interface waits for the key to be removed from the encoder.
        RETAIN = b"R"  # Retention. The PC interface does not wait for the key to be removed.
        REAR = b"T"  # Ejection by the rear side (not used). Same effect as 'E'.

    class CardType(Enum):
        STAFF_CARD = 1
        SPARE_GUEST_CARD = 2
        INVALID_GUEST_CARD = 3
        UNIDENTIFIED_CARD = 4
        GUEST_CARD = 5

    AUTHORIZATION_MAPPINGS: Dict[int, bytes] = {
        1: b"1", 2: b"2", 3: b"3", 4: b"4", 5: b"5", 6: b"6", 7: b"7", 8: b"8",
        9: b"9", 10: b"a", 11: b"b", 12: b"c", 13: b"d", 14: b"e", 15: b"f",
        16: b"g", 17: b"h", 18: b"i", 19: b"j", 20: b"k", 21: b"l", 22: b"m",
        23: b"n", 24: b"o", 25: b"p", 26: b"q", 27: b"r", 28: b"s", 29: b"t",
        30: b"u", 31: b"v", 32: b"w", 33: b"x", 34: b"y", 35: b"z", 36: b"!",
        37: b"#", 38: b"$", 39: b"%", 40: b"&", 41: b"(", 42: b")", 43: b"*",
        44: b"+", 45: b",", 46: b"-", 47: b".", 48: b"/", 49: b":", 50: b";",
        51: b"<", 52: b"=", 53: b">", 54: b"?", 55: b"@", 56: b"[", 57: b"\\",
        58: b"]", 59: b"^", 60: b"_", 61: b"{", 62: b"}"
    }

    AUTHORIZATION_MAPPINGS_INVERTED: Dict[int, int] = {v[0]: k for k, v in AUTHORIZATION_MAPPINGS.items()}

    # Can be initialized as the result of a ReadCard (LT) message
    def __init__(self, message: Message):
        self.message = message

    @classmethod
    def encode_authorizations(cls, authorizations: List[int]) -> bytes:
        return b"".join(cls.AUTHORIZATION_MAPPINGS[auth] for auth in authorizations)

    @classmethod
    def decode_authorizations(cls, authorization_field: bytes) -> List[int]:
        return [cls.AUTHORIZATION_MAPPINGS_INVERTED[b] for b in authorization_field]

    @classmethod
    def decode_datetime(cls, datetime_field: bytes) -> datetime:
        return datetime.strptime(datetime_field.decode(Message.ENCODING), cls.DATETIME_FORMAT)

    @property
    def encoder(self) -> str:
        return self.message.str_field(1)

    @property
    def card_type(self) -> CardType:
        ct = self.message.str_field(2)
        if ct == "LM":
            return CardDetails.CardType.STAFF_CARD
        elif ct == "LR":
            return CardDetails.CardType.SPARE_GUEST_CARD
        elif ct == "LC":
            return CardDetails.CardType.INVALID_GUEST_CARD
        elif ct == "LD":
            return CardDetails.CardType.UNIDENTIFIED_CARD
        else:
            return CardDetails.CardType.GUEST_CARD

    @property
    def is_quest_card(self) -> bool:
        return self.card_type == CardDetails.CardType.GUEST_CARD

    @property
    def rooms(self) -> List[str]:
        if self.is_quest_card:
            return [room for room in (self.message.str_field(2), self.message.str_field(3), self.message.str_field(4), self.message.str_field(5)) if room != ""]
        return []

    @property
    def is_valid_for_main_room(self) -> bool:
        if self.is_quest_card:
            return self.message.str_field(6) == "CI"
            # Otherwise 'CO'
        return False

    # '0' - original card.
    # '1' - first copy.
    # '2' - second copy.
    # 'I' - undefined copy (third and successive).
    # 'A' - one-shot key.
    @property
    def copy_number(self) -> str:
        if self.is_quest_card:
            return self.message.str_field(7)
        return ""

    @property
    def granted_authorizations(self) -> List[int]:
        if self.is_quest_card:
            return self.decode_authorizations(self.message.fields[8])
        return []

    @property
    def valid_from(self) -> Optional[datetime]:
        if self.is_quest_card and self.message.fields[9]:
            return self.decode_datetime(self.message.fields[9])
        return None

    @property
    def valid_till(self) -> Optional[datetime]:
        if self.is_quest_card and self.message.fields[10]:
            return self.decode_datetime(self.message.fields[10])
        return None

    @property
    def operator(self) -> str:
        if self.is_quest_card:
            return self.message.str_field(11)
        return ""
