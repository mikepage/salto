from datetime import datetime, date
from enum import Enum
from typing import Optional

from salto.message import Message


class AuditRecord:
    class Incident(Enum):
        OPEN = b"0"
        INVALID = b"2"
        ACCESS_DENIED = b"3"
        EXPIRED = b"4"
        ANTI_PASSBACK = b"5"

    class Direction(Enum):
        IN = b"1"
        OUT = b"2"

    # Format: 'day/month' (default) or 'month/day', depending on the configuration of the interface
    DATETIME_FORMAT: str = "%d/%m %H:%M"

    def __init__(self, message: Message):
        self.message: Message = message
        self._datetime: Optional[datetime] = None
        self._incident: Optional[AuditRecord.Incident] = None

    # General error: it is not possible to send the requested incidence. Possible causes could be:
    # - specified door or peripheral does not exist.
    # - database not accessible.
    # - etc.
    @property
    def is_error(self) -> bool:
        return self.message.str_field(0) == "WE"

    # Overflow error: there is no more incidence to be sent. Depending on the command, the meaning of this error is as follows:
    # - 'WF': the audit trail of the specified door or peripheral is empty, i. e., no opening or rejection has been produced in the last days.
    # - 'WN': the last incidence in the audit trail has already be sent to the PMS, so no more incidence is available.
    # - 'WR': this case only occurs when the 'WR' command has been sent before any actual incidence collection request ('WF' or 'WN'): the interface cannot repeat anything since not previous request has been made.
    @property
    def is_end_of_trail(self) -> bool:
        return self.message.str_field(0) == "WO"

    @property
    def door_identification(self) -> str:
        return self.message.str_field(1)

    @property
    def datetime(self) -> datetime:
        if self._datetime is not None:
            return self._datetime

        parsed_datetime = datetime.strptime(f"{self.message.str_field(2)} {self.message.str_field(3)}", AuditRecord.DATETIME_FORMAT)
        if parsed_datetime > datetime.now():
            parsed_datetime = add_years(parsed_datetime, -1)
        self._datetime = parsed_datetime
        return self._datetime

    @property
    def incident(self) -> "AuditRecord.Incident":
        if self._incident is not None:
            return self._incident

        self._incident = AuditRecord.Incident(self.message.fields[4])
        return self._incident

    # - 'I': input or entrance reader.
    # - 'O': output or exit reader.
    @property
    def direction(self) -> "AuditRecord.Direction":
        if self.message.str_field(5) == "I":
            return AuditRecord.Direction.IN
        return AuditRecord.Direction.OUT

    # The content of this field depends on the type of the card owner:
    # - Hotel guest: if the card corresponds to a hotel guest, this field will contain the name of the room to which the guest belongs.
    # - Staff: if the card corresponds to a staff user, this field will contain the word 'STAFF   ' (8 characters) and field #8 will contain the name of the user (see below).
    # - Special users: for other kind of users (such as spare card) this field is left empty (8 blank characters).
    @property
    def card_identification(self) -> str:
        return self.message.str_field(6).strip()

    # - '#0': original card.
    # - '#1': first copy.
    # - '#2': second copy.
    # - '#D': indefinite copy (third or successive).
    # - '@1': single opening card number 1 (one-shot key).
    # - 'S1': spare card.
    # - 'S2': opening caused by means of a switch, button, keypad, etc.
    # - 'S3': opening caused online from the computer.
    @property
    def copy_number(self) -> str:
        return self.message.str_field(7)

    @property
    def user(self) -> str:
        return self.message.str_field(8)


# https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python
def add_years(d: datetime, years: int) -> datetime:
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).
    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
