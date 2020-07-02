from typing import List

from salto.message import Message
from salto.support.card_details import CardDetails


class WriteTrack(Message):
    COMMAND_NAME: str = "P"

    def __init__(self,
                 track: int,
                 encoder: str,
                 text: str,
                 eject_strategy: CardDetails.EjectStrategies = CardDetails.EjectStrategies.RETAIN):
        fields: List[bytes] = [
            self.encode_str(f"{self.COMMAND_NAME}{track}"),
            self.encode_str(encoder),
            eject_strategy.value,
            self.sanitize_text(text),
        ]
        super().__init__(fields)
