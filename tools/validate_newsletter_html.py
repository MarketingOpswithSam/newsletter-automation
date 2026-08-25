#!/usr/bin/env python3
"""Validate a rendered newsletter HTML file before it is ever handed to send-email.

This exists because the post-send guardrail in workflows/newsletter_automation.md
(call get-email after send-email and inspect the result) only catches problems
*after* a broken or placeholder email has already landed in the recipient's inbox.
On 2026-08-25/26 an automation run sent a literal "<PLACEHOLDER>" string as the
email body before catching the mistake and sending a corrected follow-up, i.e. the
recipient still received the broken email first. This script is a pre-send check:
if it fails, do NOT call send-email at all, treat it as a step 3-6a tool error and
go to the workflow's step 6b failure path instead.

Usage:
    python tools/validate_newsletter_html.py --input path/to/rendered.html

Exits 0 and prints "OK" if the file looks like a real rendered newsletter.
Exits 1 and prints the specific reason(s) otherwise.
"""
import argparse
import re
import sys

MIN_LENGTH = 3000
REQUIRED_TAGS = ("<!doctype html", "<table", "<td", "<body")
SUSPECT_MARKERS = ("placeholder", "todo", "lorem ipsum", "tbd", "xxx", "insert content here")


def validate(text):
    reasons = []
    stripped = text.strip()
    lower = stripped.lower()

    if len(stripped) < MIN_LENGTH:
        reasons.append(f"content is only {len(stripped)} chars, expected a full rendered "
                        f"newsletter of at least {MIN_LENGTH} chars")

    if not lower.startswith("<!doctype html"):
        reasons.append("does not start with a real <!DOCTYPE html> (escaped or missing)")

    for tag in REQUIRED_TAGS:
        if tag not in lower:
            reasons.append(f"missing expected tag {tag!r} (HTML may be escaped or truncated)")

    escaped_tags = ("&lt;!doctype", "&lt;table", "&lt;td", "&lt;body", "&lt;html")
    if any(tag in lower for tag in escaped_tags):
        reasons.append("contains escaped structural tags (e.g. &lt;table), HTML was likely double-escaped")

    for marker in SUSPECT_MARKERS:
        # word-boundary match so "placeholder" inside a real sentence about
        # placeholders (unlikely, but be precise) isn't a false trigger on its own,
        # while a bare "<PLACEHOLDER>"-style stand-in for real content is caught.
        if re.search(rf"\b{re.escape(marker)}\b", lower):
            reasons.append(f"contains suspect placeholder marker {marker!r}")

    return reasons


def main():
    parser = argparse.ArgumentParser(description="Validate rendered newsletter HTML before sending.")
    parser.add_argument("--input", required=True, help="Path to the rendered HTML file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    reasons = validate(text)

    if reasons:
        print("INVALID - do not send. Reasons:")
        for r in reasons:
            print(f"  - {r}")
        sys.exit(1)

    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
