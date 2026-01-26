"""
Email service using Resend.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from ..core.config import settings


def generate_verification_token() -> str:
    """Generate a secure verification token."""
    return secrets.token_urlsafe(32)


def get_verification_expiry() -> datetime:
    """Get expiry time for verification token (24 hours from now)."""
    return datetime.utcnow() + timedelta(hours=24)


async def send_verification_email(email: str, token: str, name: Optional[str] = None) -> bool:
    """
    Send verification email using Resend.

    Returns True if email was sent successfully, False otherwise.
    """
    if not settings.RESEND_API_KEY:
        # Email not configured - skip sending (development mode)
        return True

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        verification_url = f"{settings.APP_URL}/verify-email?token={token}"
        greeting = f"Hi {name}," if name else "Hi,"

        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Verify your xBasis account",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #1a1a1a; font-size: 24px; margin-bottom: 24px;">Welcome to xBasis!</h1>

  <p style="color: #4a4a4a; font-size: 16px; line-height: 1.6;">
    {greeting}
  </p>

  <p style="color: #4a4a4a; font-size: 16px; line-height: 1.6;">
    Thanks for signing up. Please verify your email address by clicking the button below:
  </p>

  <div style="text-align: center; margin: 32px 0;">
    <a href="{verification_url}"
       style="background-color: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block;">
      Verify Email Address
    </a>
  </div>

  <p style="color: #6a6a6a; font-size: 14px; line-height: 1.6;">
    Or copy and paste this link into your browser:
    <br>
    <a href="{verification_url}" style="color: #2563eb;">{verification_url}</a>
  </p>

  <p style="color: #6a6a6a; font-size: 14px; line-height: 1.6;">
    This link will expire in 24 hours.
  </p>

  <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 32px 0;">

  <p style="color: #9a9a9a; font-size: 12px;">
    If you didn't create an account on xBasis, you can safely ignore this email.
  </p>
</body>
</html>
            """,
        })
        return True
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {e}")
        return False


async def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset email using Resend.

    Returns True if email was sent successfully, False otherwise.
    """
    if not settings.RESEND_API_KEY:
        return True

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        reset_url = f"{settings.APP_URL}/reset-password?token={token}"

        resend.Emails.send({
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Reset your xBasis password",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;">
  <h1 style="color: #1a1a1a; font-size: 24px; margin-bottom: 24px;">Password Reset</h1>

  <p style="color: #4a4a4a; font-size: 16px; line-height: 1.6;">
    We received a request to reset your xBasis password. Click the button below to create a new password:
  </p>

  <div style="text-align: center; margin: 32px 0;">
    <a href="{reset_url}"
       style="background-color: #2563eb; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block;">
      Reset Password
    </a>
  </div>

  <p style="color: #6a6a6a; font-size: 14px; line-height: 1.6;">
    Or copy and paste this link into your browser:
    <br>
    <a href="{reset_url}" style="color: #2563eb;">{reset_url}</a>
  </p>

  <p style="color: #6a6a6a; font-size: 14px; line-height: 1.6;">
    This link will expire in 1 hour.
  </p>

  <hr style="border: none; border-top: 1px solid #e5e5e5; margin: 32px 0;">

  <p style="color: #9a9a9a; font-size: 12px;">
    If you didn't request a password reset, you can safely ignore this email.
  </p>
</body>
</html>
            """,
        })
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False
