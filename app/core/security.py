import hmac
import hashlib
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


class SecurityService:
    """
    Security service enforcing cryptographic verification and PII protection.
    Follows Single Responsibility Principle (SRP).
    """

    @staticmethod
    def verify_meta_signature(raw_payload: bytes, signature_header: Optional[str]) -> bool:
        """
        Validates the SHA256 HMAC signature sent by Meta in the X-Hub-Signature-256 header.
        """
        if not settings.security.require_hmac_verification:
            return True

        if not signature_header or not signature_header.startswith("sha256="):
            logger.warning("Missing or malformed X-Hub-Signature-256 header.")
            return False

        expected_signature = signature_header.split("sha256=")[1]
        secret = settings.whatsapp.app_secret.encode("utf-8")
        
        computed_hash = hmac.new(secret, raw_payload, hashlib.sha256).hexdigest()
        
        is_valid = hmac.compare_digest(computed_hash, expected_signature)
        if not is_valid:
            logger.warning("Invalid HMAC-SHA256 signature detected.")
        return is_valid

    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """Masks sensitive customer phone number for compliant logging."""
        if not phone or len(phone) < 6:
            return "******"
        return f"{phone[:3]}****{phone[-3:]}"
