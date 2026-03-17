# Email Notification Service for Accountrix
# Uses SMTP (works with Gmail, SendGrid, any provider)
# Falls back to logging if not configured

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

# Email config from environment
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")


def is_email_configured() -> bool:
    return bool(SMTP_USER and SMTP_PASSWORD)


def send_email_sync(to: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """Send email via SMTP. Returns True if sent, False if failed/not configured."""
    if not is_email_configured():
        logger.info(f"[EMAIL NOT CONFIGURED] To: {to} | Subject: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to, msg.as_string())

        logger.info(f"Email sent to {to}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


async def notify_admin_new_registration(user_name: str, user_email: str, role: str):
    """Notify admin when a new accountant registers."""
    if not ADMIN_EMAIL:
        logger.info(f"[ADMIN NOTIFICATION] New registration: {user_name} ({user_email})")
        return

    subject = f"🆕 New Registration: {user_name} — Accountrix"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #0F766E; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 20px;">New User Registration</h1>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0;">
            <p style="color: #333; font-size: 16px;">A new accountant has registered on Accountrix:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #666;">Name:</td><td style="padding: 8px; font-weight: bold;">{user_name}</td></tr>
                <tr style="background: #f0f0f0;"><td style="padding: 8px; color: #666;">Email:</td><td style="padding: 8px; font-weight: bold;">{user_email}</td></tr>
                <tr><td style="padding: 8px; color: #666;">Role:</td><td style="padding: 8px; font-weight: bold;">{role}</td></tr>
            </table>
            <a href="https://accountrix.norabot.ai/app/admin" 
               style="display: inline-block; background: #0F766E; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
                View in Admin Panel →
            </a>
            <p style="color: #999; font-size: 12px; margin-top: 24px;">
                Go to Admin Panel → Subscriptions to activate their account when ready.
            </p>
        </div>
    </div>
    """
    text = f"New registration: {user_name} ({user_email}) - Role: {role}\n\nView at: https://accountrix.norabot.ai/app/admin"
    send_email_sync(ADMIN_EMAIL, subject, html, text)


async def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new user."""
    subject = "Welcome to Accountrix — Your AI Accounting Copilot"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #0F766E; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">Welcome to Accountrix</h1>
            <p style="color: #a7f3d0; margin: 8px 0 0 0;">Professional Control Across Your Entire Client Portfolio</p>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0;">
            <p style="color: #333; font-size: 16px;">Hi {user_name},</p>
            <p style="color: #555;">You've successfully registered on Accountrix. Here's how to get started:</p>
            <ol style="color: #555; line-height: 1.8;">
                <li><strong>Connect your e-conomic account</strong> — Go to Settings and click "Connect E-conomic"</li>
                <li><strong>Sync your clients</strong> — Your client portfolio will populate automatically</li>
                <li><strong>Review exceptions</strong> — See flagged transactions across all clients</li>
                <li><strong>Pre-VAT review</strong> — Check readiness before submission deadlines</li>
            </ol>
            <a href="https://accountrix.norabot.ai/login" 
               style="display: inline-block; background: #0F766E; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 8px;">
                Log in to Accountrix →
            </a>
            <p style="color: #999; font-size: 12px; margin-top: 24px;">
                Questions? Reply to this email and we'll help you get set up.
            </p>
        </div>
    </div>
    """
    text = f"Hi {user_name}, welcome to Accountrix! Log in at https://accountrix.norabot.ai/login"
    send_email_sync(user_email, subject, html, text)


async def send_economic_connected_email(user_email: str, user_name: str, client_count: int):
    """Notify user when their e-conomic sync is complete."""
    subject = f"✅ E-conomic Connected — {client_count} clients synced"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #0F766E; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 20px;">E-conomic Connected!</h1>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0;">
            <p style="color: #333;">Hi {user_name},</p>
            <p style="color: #555;">Your e-conomic account has been connected successfully.</p>
            <div style="background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <p style="color: #065f46; font-size: 24px; font-weight: bold; margin: 0;">{client_count} clients synced</p>
                <p style="color: #047857; margin: 4px 0 0 0;">Your portfolio dashboard is ready</p>
            </div>
            <a href="https://accountrix.norabot.ai/app/portfolio" 
               style="display: inline-block; background: #0F766E; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
                View Your Portfolio →
            </a>
        </div>
    </div>
    """
    text = f"Hi {user_name}, your e-conomic account is connected. {client_count} clients synced. View at https://accountrix.norabot.ai/app/portfolio"
    send_email_sync(user_email, subject, html, text)


async def send_subscription_activated_email(user_email: str, user_name: str, plan_name: str):
    """Notify user when their subscription is activated."""
    subject = f"✅ Subscription Activated — {plan_name}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #0F766E; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 20px;">Subscription Activated</h1>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0;">
            <p style="color: #333;">Hi {user_name},</p>
            <p style="color: #555;">Your <strong>{plan_name}</strong> subscription has been activated. You now have full access to Accountrix.</p>
            <p style="color: #555;">You will receive an invoice by email within 24 hours.</p>
            <a href="https://accountrix.norabot.ai/app/portfolio" 
               style="display: inline-block; background: #0F766E; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
                Go to Dashboard →
            </a>
        </div>
    </div>
    """
    text = f"Hi {user_name}, your {plan_name} subscription is active. View your dashboard at https://accountrix.norabot.ai/app/portfolio"
    send_email_sync(user_email, subject, html, text)


async def send_approval_email(user_email: str, user_name: str):
    """Notify user when their account is approved."""
    subject = "✅ Your Accountrix account is approved!"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #0F766E; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 20px;">Account Approved!</h1>
        </div>
        <div style="background: #f9f9f9; padding: 24px; border-radius: 0 0 8px 8px; border: 1px solid #e0e0e0;">
            <p style="color: #333;">Hi {user_name},</p>
            <p style="color: #555;">Great news! Your Accountrix account has been approved. You can now log in and start using the platform.</p>
            <a href="https://accountrix.norabot.ai/login"
               style="display: inline-block; background: #0F766E; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
                Log in to Accountrix →
            </a>
            <p style="color: #999; font-size: 12px; margin-top: 24px;">
                Connect your e-conomic account in Settings to sync your clients.
            </p>
        </div>
    </div>
    """
    text = f"Hi {user_name}, your Accountrix account is approved! Log in at https://accountrix.norabot.ai/login"
    send_email_sync(user_email, subject, html, text)
