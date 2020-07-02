from typing import List

from salto.audit.audit_record import AuditRecord
from salto.client import Client
from salto.message import Message


class AuditTrail:
    # Fetches the audit trail for a given door. Audit retention is based on configuration in Salto.
    @staticmethod
    def fetch(client: Client, door_identification: str) -> List[AuditRecord]:
        audit_records: List[AuditRecord] = []
        end_of_trail = False

        with client.create_connection() as conn:
            next_message = Message([b"WF", Message.encode_str(door_identification)])
            while not end_of_trail:
                response = client._send_request(conn, client.encode_message(next_message))

                audit_record = AuditRecord(response.message)
                audit_records.append(audit_record)

                next_message = Message([b"WN", Message.encode_str(door_identification)])
                end_of_trail = audit_record.is_error or audit_record.is_end_of_trail

        return audit_records
