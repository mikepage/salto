from typing import List

from salto.message import Message


# Example: mc_message = Checkout(room="Room 1")
class Checkout(Message):
    COMMAND_NAME: str = "CO"

    def __init__(self, room: str):
        fields: List[bytes] = [
            self.encode_str(self.COMMAND_NAME),
            b"0",
            self.encode_str(room),
        ]
        super().__init__(fields)
