from typing import Any

resources = {
    "en": {
        "salto": {
            "errors": {
                "ES": "Syntax error. The received message from the PMS is not correct (unknown command, nonsense parameters, prohibited characters, etc.)",
                "NC": "No communication. The specified encoder does not answer (encoder is switched off, disconnected from the PC interface, etc.)",
                "NF": "No files. Database file in the PC interface is damaged, corrupted or not found.",
                "OV": "Overflow. The encoder is still busy executing a previous task and cannot accept a new one.",
                "EP": "Card error. Card not found or wrongly inserted in the encoder.",
                "EF": "Format error. The card has been encoded by another system or may be damaged.",
                "TD": "Unknown room. This error occurs when trying to encode a card for a non-existing room.",
                "ED": "Timeout error. The encoder has been waiting too long for a card to be inserted. The operation is cancelled.",
                "EA": "This error occurs when the PC interface cannot execute the ‘CC’ command (encode copies of a guest card) because the room is checked out.",
                "OS": "This error occurs when the requested room is out of service.",
                "EO": "The requested guest card is being encoded by another station.",
                "EV": "Card validity error. This error occurs when the inserted card for a 'CN', 'CC' or 'CA' command belongs to a valid staff user.",
                "EG": "General error",
            }
        }
    }
}

LANGUAGE = "en"


def localized(resource_path: str) -> str:
    parts = resource_path.split(".")
    parts.insert(0, LANGUAGE)
    current: Any = resources
    for part in parts:
        if part not in current:
            return resource_path
        current = current[part]
        parts = parts[1:]
    return current
