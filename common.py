STX: bytes = b"\x02"  # Start of text, indicates the start of a message.
ETX: bytes = b"\x03"  # End of text, indicates the end of a message
ENQ: bytes = b"\x05"  # Enquiry about the PC interface being ready to receive a new message.
ACK: bytes = b"\x06"  # Positive acknowledgement to a PMS message or enquiry (ENQ).
NAK: bytes = b"\x15"  # Negative acknowledgement to a PMS message or enquiry (ENQ).

LRC_SKIP: bytes = b"\x0D"  # The PMS can avoid LRC calculation by sending a 0DH value (return character)


def lrc(message: bytes) -> bytes:
    result = 0
    for b in message + ETX:  # LRC message must not include STX and should include ETX
        result ^= b
    return bytes([result])
