from typing import List

from salto.message import Message
from salto.support.card_details import CardDetails


# Example: lt_message = ReadCard("Online Encoder 1")
class ReadCard(Message):
    COMMAND_NAME: str = "LT"

    def __init__(self,
                 encoder: str,
                 eject_strategy: CardDetails.EjectStrategies = CardDetails.EjectStrategies.RETAIN):
        fields: List[bytes] = [
            self.encode_str(self.COMMAND_NAME),
            self.encode_str(encoder),
            eject_strategy.value,
        ]
        super().__init__(fields)
