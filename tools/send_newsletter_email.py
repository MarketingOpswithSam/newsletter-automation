#!/usr/bin/env python3
"""Send an email via IONOS SMTP, either a rendered newsletter HTML file or a plain-text note.

Usage:
    python tools/send_newsletter_email.py --to recipient@example.com \\
        --subject "Subject line" --html-file path/to/newsletter.html

    python tools/send_newsletter_email.py --to recipient@example.com \\
        --subject "Subject line" --body "Plain text message, e.g. a failure notice"

Reads IONOS_SMTP_HOST, IONOS_SMTP_PORT, IONOS_SMTP_USER, IONOS_SMTP_PASSWORD
from the project .env file. IONOS_SMTP_USER is also used as the From address.
"""
import argparse
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SENDER_NAME = "Marketing Ops With Sam"


def load_env():
    env_path = PROJECT_ROOT / ".env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


def html_to_plain_text(html_content):
    text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html_content)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|td|tr|h[1-6])>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Send a newsletter HTML file, or a plain-text note, via IONOS SMTP.")
    parser.add_argument("--to", required=True, action="append", help="Recipient email address (repeatable)")
    parser.add_argument("--subject", required=True, help="Email subject line")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html-file", help="Path to a rendered HTML file to send")
    group.add_argument("--body", help="Plain-text message body (for simple notices, e.g. a failure notification)")
    args = parser.parse_args()

    env = load_env()
    smtp_host = env.get("IONOS_SMTP_HOST", "smtp.ionos.com")
    smtp_port = int(env.get("IONOS_SMTP_PORT", "587"))
    smtp_user = env.get("IONOS_SMTP_USER")
    smtp_password = env.get("IONOS_SMTP_PASSWORD")
    sender_name = env.get("SENDER_NAME", DEFAULT_SENDER_NAME)

    if not smtp_user or not smtp_password:
        raise SystemExit(
            "Missing IONOS_SMTP_USER / IONOS_SMTP_PASSWORD in .env. "
            "Add them before sending."
        )

    msg_headers = {
        "Subject": args.subject,
        "From": formataddr((sender_name, smtp_user)),
        "To": ", ".join(args.to),
    }

    if args.html_file:
        html_content = Path(args.html_file).read_text(encoding="utf-8")
        plain_text = html_to_plain_text(html_content)
        msg = MIMEMultipart("alternative")
        for key, value in msg_headers.items():
            msg[key] = value
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
    else:
        msg = MIMEText(args.body, "plain", "utf-8")
        for key, value in msg_headers.items():
            msg[key] = value

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, args.to, msg.as_string())

    print(f"Sent to {', '.join(args.to)} from {smtp_user} via {smtp_host}:{smtp_port}")


if __name__ == "__main__":
    main()
