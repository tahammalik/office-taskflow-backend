from fastapi_mail import ConnectionConfig,MessageSchema,FastMail,MessageType
from app.core.config import EmailConfig

settings = EmailConfig()

conf = ConnectionConfig(
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False, 
    USE_CREDENTIALS=True,
)

async def send_invite_email(receiver_email:str,token:str,workspace_name:str):
    invitation_link = f"{settings.FRONTEND_BASE_URL}/invites/accept?token={token}"

    message = MessageSchema(
        subject="Invite Link",
        recipients=[receiver_email],
        body=(f"""
            <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Our Platform</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f4f6f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="table-layout: fixed; background-color: #f4f6f8; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        <!-- Header Banner -->
                        <tr>
                            <td align="center" style="background-color: #4F46E5; padding: 40px 20px;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">Welcome Aboard!</h1>
                            </td>
                        </tr>
                        <!-- Content Body -->
                        <tr>
                            <td style="padding: 40px 30px; color: #333333; line-height: 1.6;">
                                <p style="font-size: 18px; margin-top: 0; font-weight: 600;">Hi {receiver_email},</p>
                                <p style="font-size: 16px; color: #4b5563;">Thank you for signing up. Your account is active and ready to go. Click the button below to access your new portal dashboard and complete your profile setup.</p>
                                
                                <!-- Call to Action Button -->
                                <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px auto;">
                                    <tr>
                                        <td align="center" bgcolor="#4F46E5" style="border-radius: 6px;">
                                            <a href="{invitation_link}" target="_blank" style="display: inline-block; padding: 14px 30px; font-size: 16px; color: #ffffff; font-weight: 600; text-decoration: none;">Accept</a>>
                                        </td>
                                    </tr>
                                </table>

                                <p style="font-size: 14px; color: #6b7280; margin-bottom: 0;">If the button doesn't work, copy and paste this link into your browser:<br>
                                <a href="{invitation_link}" style="color: #4F46E5; word-break: break-all;">{invitation_link}</a></p>
                            </td>
                        </tr>
                        <!-- Footer -->
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
        """
        ),
    subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)