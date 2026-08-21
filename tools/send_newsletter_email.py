#!/usr/bin/env python3
"""Send an email via the Resend HTTPS API, either a rendered newsletter HTML file or a plain-text note.

Usage:
    python tools/send_newsletter_email.py --to recipient@example.com \\
        --subject "Subject line" --html-file path/to/newsletter.html

    python tools/send_newsletter_email.py --to recipient@example.com \\
        --subject "Subject line" --body "Plain text message, e.g. a failure notice"

Reads RESEND_API_KEY from the project .env file. Sends as hello@marketingopswithsam.com.
Uses Resend's HTTPS API (not SMTP) because raw SMTP (port 587) is not reachable from
the cloud routine's sandboxed network, which only allows outbound HTTPS.
"""
import argparse
import json
import re
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SENDER_NAME = "Marketing Ops With Sam"
SENDER_EMAIL = "hello@marketingopswithsam.com"
RESEND_API_URL = "https://api.resend.com/emails"


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
    parser = argparse.ArgumentParser(description="Send a newsletter HTML file, or a plain-text note, via Resend.")
    parser.add_argument("--to", required=True, action="append", help="Recipient email address (repeatable)")
    parser.add_argument("--subject", required=True, help="Email subject line")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html-file", help="Path to a rendered HTML file to send")
    group.add_argument("--body", help="Plain-text message body (for simple notices, e.g. a failure notification)")
    args = parser.parse_args()

    env = load_env()
    api_key = env.get("RESEND_API_KEY")

    if not api_key:
        raise SystemExit("Missing RESEND_API_KEY in .env. Add it before sending.")

    payload = {
        "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to": args.to,
        "subject": args.subject,
    }

    if args.html_file:
        html_content = Path(args.html_file).read_text(encoding="utf-8")
        payload["html"] = html_content
        payload["text"] = html_to_plain_text(html_content)
    else:
        payload["text"] = args.body

    request = urllib.request.Request(
        RESEND_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "newsletter-automation/1.0 (+https://github.com/MarketingOpswithSam/newsletter-automation)",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise SystemExit(f"Resend API error {e.code}: {error_body}")

    print(f"Sent to {', '.join(args.to)} from {SENDER_EMAIL} via Resend, id={result.get('id')}")


if __name__ == "__main__":
    main()
