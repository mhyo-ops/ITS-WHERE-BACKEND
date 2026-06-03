import asyncio
from functools import partial

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import random
import os
from dotenv import load_dotenv

load_dotenv()


def generate_code() -> str:
    return str(random.randint(100000, 999999))


def _get_api() -> sib_api_v3_sdk.TransactionalEmailsApi:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY", "")
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


async def send_verification_email(email: str, code: str) -> None:
    try:
        api = _get_api()
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": "dinmhy732@gmail.com", "name": "ODEJ Platform"},
            subject="Verify your ODEJ account",
            text_content=f"Your verification code is: {code}\n\nExpires in 10 minutes.",
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(api.send_transac_email, send_smtp_email),
        )
        print(f"✅ Verification email sent to {email}")
    except Exception as e:
        print(f"⚠️ Email send failed: {e}")


async def send_reset_email(email: str, code: str) -> None:
    try:
        api = _get_api()
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": "dinmhy732@gmail.com", "name": "ODEJ Platform"},
            subject="ODEJ — Password Reset Code",
            text_content=(
                f"Your password reset code is: {code}\n\nExpires in 10 minutes.\n"
                "If you didn't request this, ignore this email."
            ),
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(api.send_transac_email, send_smtp_email),
        )
        print(f"✅ Reset email sent to {email}")
    except Exception as e:
        print(f"⚠️ Email send failed: {e}")


async def send_reminder_email(email: str, event_title: str, event_date: str, address: str) -> None:
    try:
        api = _get_api()
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={"email": "dinmhy732@gmail.com", "name": "ODEJ Platform"},
            subject=f"Reminder: {event_title} is tomorrow!",
            text_content=(
                f"Hello,\n\n"
                f"This is a reminder that you are registered for:\n\n"
                f"Event: {event_title}\n"
                f"Date: {event_date}\n"
                f"Location: {address}\n\n"
                f"We look forward to seeing you there!\n\n"
                f"— ODEJ Platform"
            ),
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(api.send_transac_email, send_smtp_email),
        )
        print(f"✅ Reminder email sent to {email} for event {event_title}")
    except Exception as e:
        print(f"⚠️ Reminder email failed: {e}")
