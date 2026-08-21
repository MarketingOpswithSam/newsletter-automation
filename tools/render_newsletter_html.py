#!/usr/bin/env python3
"""Render a newsletter content JSON spec into email-safe HTML.

Usage:
    python tools/render_newsletter_html.py --input path/to/content.json --output path/to/out.html

Input JSON schema:
{
  "subject": "...",
  "preheader": "...",
  "hero_headline": "...",
  "hero_intro": "...",
  "sections": [
    {"heading": "...", "eyebrow": "short label, e.g. WHAT'S CHANGING (optional)",
     "lead": "one bold short takeaway sentence (optional)",
     "analysis": "short paragraphs separated by blank lines, no walls of text",
     "bullets": ["optional short bullet points, good for action steps"],
     "example": "concrete example/case study (optional, pull-quote style)",
     "image_url": "https://...", "source_url": "https://...", "source_label": "..."},
    ...
  ],
  "video_idea": {"hook": "...", "shot_idea": "...", "caption_angle": "..."},
  "quick_links": [{"label": "...", "url": "..."}, ...],
  "footer": {"address": "...", "unsubscribe_url": "..."}
}

Everything renders inside ONE continuous card (logo, hero, every section, the video
idea, quick links, footer) so the issue reads as a single document, with thin rule
dividers between sections rather than separate boxed-off blocks.
"""
import argparse
import html
import json

LOGO_URL = "https://marketingopswithsam.com/brand-logo.png"
NAVY = "#003E80"
PRIMARY = "#0078D4"
ACCENT = "#3a9bff"
BG_TINT = "#F0F6FF"
PAGE_BG = "#f0f2f5"
TEXT = "#1a1a1a"
BORDER = "#e5e7eb"
MUTED = "#7b8794"
FONT_STACK = "'Poppins', 'Segoe UI', Arial, Helvetica, sans-serif"


def esc(s):
    return html.escape(s or "", quote=True)


def paragraphs_html(text, size=15, line_height=1.7, color=None):
    color = color or TEXT
    paras = [p.strip() for p in (text or "").split("\n\n") if p.strip()]
    if not paras:
        paras = [text or ""]
    return "".join(
        f"""<tr>
          <td style="font-family:{FONT_STACK};font-size:{size}px;line-height:{line_height};color:{color};padding:0 0 12px 0;">
            {esc(p)}
          </td>
        </tr>"""
        for p in paras
    )


def divider():
    return f"""
  <tr>
    <td style="padding:6px 32px;">
      <div style="border-top:1px solid {BORDER};font-size:0;line-height:0;">&nbsp;</div>
    </td>
  </tr>"""


def render_header(hero_headline):
    return f"""
  <tr>
    <td style="padding:26px 32px 20px 32px;text-align:center;background-color:#ffffff;">
      <a href="https://marketingopswithsam.com" style="display:inline-block;">
        <img src="{LOGO_URL}" alt="Marketing Ops With Sam" width="180" height="180" border="0"
             style="width:180px;max-width:50%;height:auto;display:inline-block;border:0;" />
      </a>
    </td>
  </tr>
  <tr>
    <td bgcolor="{PRIMARY}" style="background-color:{PRIMARY};background:linear-gradient(135deg,{PRIMARY},{ACCENT});padding:26px 32px 30px 32px;">
      <div style="font-family:{FONT_STACK};font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#ffffff;opacity:0.9;padding-bottom:10px;">
        AI in Marketing Daily
      </div>
      <div style="font-family:{FONT_STACK};font-size:25px;font-weight:700;color:#ffffff;line-height:1.3;">
        {esc(hero_headline)}
      </div>
    </td>
  </tr>"""


def render_intro(hero_intro):
    return f"""
        <tr>
          <td style="padding:26px 32px 4px 32px;font-family:{FONT_STACK};font-size:16px;line-height:1.65;color:{TEXT};">
            {esc(hero_intro)}
          </td>
        </tr>"""


def render_section(section, index):
    eyebrow = esc(section.get("eyebrow") or section.get("heading"))
    heading = esc(section.get("heading"))
    lead = esc(section.get("lead"))
    analysis = section.get("analysis") or section.get("body") or ""
    bullets = section.get("bullets") or []
    example = esc(section.get("example"))
    image_url = section.get("image_url")
    source_url = section.get("source_url")
    source_label = esc(section.get("source_label") or "Source")

    lead_html = ""
    if lead:
        lead_html = f"""
        <tr>
          <td style="font-family:{FONT_STACK};font-size:16px;font-weight:600;line-height:1.5;color:{NAVY};padding:0 0 10px 0;">
            {lead}
          </td>
        </tr>"""

    image_html = ""
    if image_url:
        side = "padding:18px 32px 4px 32px;"
        image_html = f"""
        <tr>
          <td style="{side}">
            <img src="{esc(image_url)}" alt="{heading}" width="536" height="302"
                 style="width:100%;max-width:536px;height:auto;border-radius:10px;display:block;" />
          </td>
        </tr>"""

    bullets_html = ""
    if bullets:
        items = "".join(
            f"""<tr>
              <td style="padding:0 0 8px 0;font-family:{FONT_STACK};font-size:15px;line-height:1.6;color:{TEXT};">
                <span style="color:{PRIMARY};font-weight:700;">&#8594;</span>&nbsp; {esc(b)}
              </td>
            </tr>"""
            for b in bullets
        )
        bullets_html = f"""
        <tr>
          <td style="padding:2px 0 6px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              {items}
            </table>
          </td>
        </tr>"""

    example_html = ""
    if example:
        example_html = f"""
        <tr>
          <td style="padding:8px 0 6px 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background-color:{BG_TINT};border-radius:8px;">
              <tr>
                <td style="padding:14px 16px;font-family:{FONT_STACK};font-size:14px;line-height:1.55;color:{TEXT};">
                  <strong style="color:{NAVY};">In practice:</strong> {example}
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    source_html = ""
    if source_url:
        source_html = f"""
        <tr>
          <td style="padding:10px 0 0 0;font-family:{FONT_STACK};font-size:13px;">
            <a href="{esc(source_url)}" style="color:{PRIMARY};text-decoration:none;">Read more: {source_label} &rarr;</a>
          </td>
        </tr>"""

    return f"""{image_html}
  <tr>
    <td style="padding:20px 32px 22px 32px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="font-family:{FONT_STACK};font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{PRIMARY};padding:0 0 6px 0;">
            {eyebrow}
          </td>
        </tr>
        <tr>
          <td style="font-family:{FONT_STACK};font-size:21px;font-weight:700;color:{NAVY};padding:0 0 10px 0;">
            {heading}
          </td>
        </tr>
        {lead_html}
        {paragraphs_html(analysis)}
        {bullets_html}
        {example_html}
        {source_html}
      </table>
    </td>
  </tr>"""


def render_video_idea(video_idea):
    if not video_idea:
        return ""
    hook = esc(video_idea.get("hook"))
    shot_idea = esc(video_idea.get("shot_idea"))
    caption_angle = esc(video_idea.get("caption_angle"))
    return f"""
  <tr>
    <td style="padding:8px 32px 26px 32px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"
             style="background-color:{BG_TINT};border-radius:10px;">
        <tr>
          <td style="padding:20px 22px;">
            <div style="font-family:{FONT_STACK};font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:{PRIMARY};padding-bottom:10px;">
              &#127909; 30-Second Video Idea, LinkedIn / Instagram
            </div>
            <div style="font-family:{FONT_STACK};font-size:15px;line-height:1.6;color:{TEXT};padding-bottom:8px;">
              <strong>Hook:</strong> {hook}
            </div>
            <div style="font-family:{FONT_STACK};font-size:15px;line-height:1.6;color:{TEXT};padding-bottom:8px;">
              <strong>Shot idea:</strong> {shot_idea}
            </div>
            <div style="font-family:{FONT_STACK};font-size:15px;line-height:1.6;color:{TEXT};">
              <strong>Caption angle:</strong> {caption_angle}
            </div>
          </td>
        </tr>
      </table>
    </td>
  </tr>"""


def render_quick_links(quick_links):
    if not quick_links:
        return ""
    items = "".join(
        f"""<tr>
          <td style="padding:0 0 8px 0;font-family:{FONT_STACK};font-size:14px;">
            &bull; <a href="{esc(l.get('url'))}" style="color:{PRIMARY};text-decoration:none;">{esc(l.get('label'))}</a>
          </td>
        </tr>"""
        for l in quick_links
    )
    return f"""
  <tr>
    <td style="padding:0 32px 26px 32px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="font-family:{FONT_STACK};font-size:14px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:{NAVY};padding:0 0 12px 0;">
            Further reading
          </td>
        </tr>
        {items}
      </table>
    </td>
  </tr>"""


def render_footer(footer):
    footer = footer or {}
    address = esc(footer.get("address") or "Melbourne, Australia")
    unsubscribe_url = footer.get("unsubscribe_url") or "#"
    return f"""
  <tr>
    <td bgcolor="{BG_TINT}" style="background-color:{BG_TINT};padding:20px 32px;">
      <div style="font-family:{FONT_STACK};font-size:12px;line-height:1.6;color:{MUTED};text-align:center;">
        {address}<br/>
        <a href="{esc(unsubscribe_url)}" style="color:{MUTED};text-decoration:underline;">Unsubscribe</a>
      </div>
    </td>
  </tr>"""


def render(spec):
    subject = esc(spec.get("subject"))
    preheader = esc(spec.get("preheader"))

    header_html = render_header(spec.get("hero_headline"))
    intro_html = render_intro(spec.get("hero_intro"))
    sections = spec.get("sections", [])
    sections_html = divider().join(render_section(s, i) for i, s in enumerate(sections))
    video_idea_html = render_video_idea(spec.get("video_idea"))
    quick_links_html = render_quick_links(spec.get("quick_links"))
    footer_html = render_footer(spec.get("footer"))

    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="color-scheme" content="light dark" />
<meta name="supported-color-schemes" content="light dark" />
<title>{subject}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
<style>
  @media only screen and (max-width: 600px) {{
    .container {{ width: 100% !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background-color:{PAGE_BG};">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:{PAGE_BG};">
  {preheader}
</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{PAGE_BG};">
<tr>
<td align="center" style="padding:24px 12px;">
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0"
       style="width:600px;max-width:600px;background-color:#ffffff;border:1px solid {BORDER};border-radius:16px;overflow:hidden;">
  {header_html}
  {intro_html}
  {divider()}
  {sections_html}
  {divider()}
  {video_idea_html}
  {quick_links_html}
  {footer_html}
</table>
</td>
</tr>
</table>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Render newsletter content JSON into email-safe HTML.")
    parser.add_argument("--input", required=True, help="Path to input JSON content spec")
    parser.add_argument("--output", required=True, help="Path to write output HTML")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        spec = json.load(f)

    html_out = render(spec)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
