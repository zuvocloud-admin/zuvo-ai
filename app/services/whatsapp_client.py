from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.message import MessageDispatchResult


class BaseMessagingClient(ABC):
    """
    Abstract Messaging Gateway interface adhering to Open/Closed (OCP)
    and Dependency Inversion (DIP) principles.
    """

    @abstractmethod
    async def send_text_message(
        self,
        phone_number_id: str,
        recipient_phone: str,
        text_body: str
    ) -> MessageDispatchResult:
        pass


class MetaWhatsAppClient(BaseMessagingClient):
    """
    Official Meta WhatsApp Cloud API Client.
    Sends session and template messages via Meta Graph API v20.0+.
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = base_url or settings.whatsapp.base_url
        self.api_version = settings.whatsapp.meta_api_version
        self._custom_token = token
        self.timeout = settings.whatsapp.request_timeout_seconds

    @property
    def token(self) -> str:
        return self._custom_token or settings.whatsapp.system_user_token

    async def send_text_message(
        self,
        phone_number_id: str,
        recipient_phone: str,
        text_body: str
    ) -> MessageDispatchResult:
        """
        Dispatches a 24-hour session text message to a customer.
        """
        # If in mock testing mode or token is placeholder, simulate successful dispatch
        if self.token.startswith("mock_") or settings.app.env == "test":
            simulated_wamid = f"wamid.SIMULATED_{recipient_phone}_{int(httpx._utils.get_environment_proxies().get('time', 0)) or 1001}"
            logger.info(f"[SIMULATED OUTBOUND] To={recipient_phone} From={phone_number_id}: '{text_body}'")
            return MessageDispatchResult(
                success=True,
                wamid=simulated_wamid,
                recipient_phone=recipient_phone,
                meta_response={"messaging_product": "whatsapp", "messages": [{"id": simulated_wamid}]}
            )

        # Fallback to configured Meta phone number ID if a mock or non-numeric PNID was passed
        actual_phone_number_id = phone_number_id
        if not str(phone_number_id).isdigit():
            actual_phone_number_id = settings.whatsapp.phone_number_id or "1312713255253790"

        url = f"{self.base_url}/{self.api_version}/{actual_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone.replace("+", "").replace("-", "").strip(),
            "type": "text",
            "text": {"body": text_body}
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code in (200, 201):
                    res_json = response.json()
                    wamid = res_json.get("messages", [{}])[0].get("id")
                    logger.info(f"Successfully sent WhatsApp message to {recipient_phone} (wamid: {wamid})")
                    return MessageDispatchResult(
                        success=True,
                        wamid=wamid,
                        recipient_phone=recipient_phone,
                        meta_response=res_json
                    )
                else:
                    error_msg = f"Meta API Error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return MessageDispatchResult(
                        success=False,
                        recipient_phone=recipient_phone,
                        error_message=error_msg,
                        meta_response=response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    )

        except Exception as e:
            error_msg = f"Exception sending WhatsApp message to {recipient_phone}: {str(e)}"
            logger.error(error_msg)
            return MessageDispatchResult(
                success=False,
                recipient_phone=recipient_phone,
                error_message=error_msg
            )


# Default client singleton
whatsapp_client = MetaWhatsAppClient()
