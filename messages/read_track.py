from typing import List

from salto.message import Message
from salto.support.card_details import CardDetails


# Example: l1_message = ReadTrack(track=1, encoder="Online Encoder 1")
class ReadTrack(Message):
    COMMAND_NAME: str = "L"

    def __init__(self,
                 track: int,
                 encoder: str,
                 eject_strategy: CardDetails.EjectStrategies = CardDetails.EjectStrategies.RETAIN):
        fields: List[bytes] = [
            self.encode_str(f"{self.COMMAND_NAME}{track}"),
            self.encode_str(encoder),
            eject_strategy.value,
        ]
        super().__init__(fields)
