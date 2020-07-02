from datetime import datetime
from typing import List, Optional

from salto.messages.encode_card import EncodeCard


class EncodeMobile(EncodeCard):
    COMMAND_NAME: str = "CNM"

    def __init__(self,
                 phone_number: str,
                 text_message: str,
                 rooms: List[str],
                 granted_authorizations: Optional[List[int]] = None,
                 denied_authorizations: Optional[List[int]] = None,
                 valid_from: Optional[datetime] = None,
                 valid_till: Optional[datetime] = None,
                 operator: Optional[str] = None,
                 print_info: Optional[str] = None):
        super().__init__(
            amount=0,
            encoder=phone_number,
            rooms=rooms,
            granted_authorizations=granted_authorizations,
            denied_authorizations=denied_authorizations,
            valid_from=valid_from,
            valid_till=valid_till,
            operator=operator,
            print_info=print_info,
        )
        self.fields.pop(2)  # Delete eject strategy
        self.fields[14] = self.sanitize_text(text_message)[:256]
