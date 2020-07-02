from datetime import datetime
from enum import Enum
from typing import List, Optional

from salto.message import Message
from salto.support.card_details import CardDetails


# Example: cn_message = EncodeCard(amount=1, encoder="Online Encoder 1", rooms=["Room 1"], valid_from=datetime.now(), valid_till=datetime.now() + timedelta(days=2), print_info="John Doe\nAnonymousville")
class EncodeCard(Message):
    class SerialNumberReturns(Enum):
        NONE = b"0"  # No serial number is returned
        LAST = b"1"  # Last written card serial number is returned
        ALL = b"2"  # All written card serial numbers are returned

    COMMAND_NAME: str = "CN"

    def __init__(self,
                 amount: int,
                 encoder: str,
                 rooms: List[str],
                 eject_strategy: CardDetails.EjectStrategies = CardDetails.EjectStrategies.RETAIN,
                 granted_authorizations: Optional[List[int]] = None,
                 denied_authorizations: Optional[List[int]] = None,
                 valid_from: Optional[datetime] = None,
                 valid_till: Optional[datetime] = None,
                 operator: Optional[str] = None,
                 print_info: Optional[str] = None,
                 serial_number_return: SerialNumberReturns = SerialNumberReturns.ALL):
        fields: List[bytes] = [b""] * 16
        fields[0] = self.encode_str(f"{self.COMMAND_NAME}{str(amount) if amount > 0 else ''}")
        fields[1] = self.encode_str(encoder)
        fields[2] = eject_strategy.value

        for index, room in enumerate(rooms[:4]):
            fields[3 + index] = self.encode_str(room)

        if granted_authorizations:
            fields[7] = CardDetails.encode_authorizations(granted_authorizations)
        if denied_authorizations:
            fields[8] = CardDetails.encode_authorizations(denied_authorizations)
        if valid_from:
            fields[9] = self.encode_str(valid_from.strftime(CardDetails.DATETIME_FORMAT))
        if valid_till:
            fields[10] = self.encode_str(valid_till.strftime(CardDetails.DATETIME_FORMAT))
        if operator:
            fields[11] = self.encode_str(operator)[:24]
        if print_info:
            for index, line in enumerate(print_info.split("\n")[:3]):
                fields[12 + index] = self.sanitize_text(line)[:24]
        fields[15] = serial_number_return.value

        super().__init__(fields)
