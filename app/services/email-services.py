
import resend
from core.config import EmailConfig
from core.logging_config import get_logger
from core.exceptions import ServerError
from app.template import email_template

configs = EmailConfig()
logging = get_logger(__name__)

class EmailService:
    def __init__(self) -> None:
        pass

    def send_email(self):
        pass