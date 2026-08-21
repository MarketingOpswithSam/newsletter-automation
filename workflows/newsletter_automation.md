# Workflow: Daily "AI in Marketing" Newsletter

## Objective
Every morning at 08:00 Australia/Melbourne, autonomously research how AI in marketing is changing, draft a short newsletter, generate on-brand images, render polished HTML, and **send** it from hello@marketingopswithsam.com to [redacted]. Fully autonomous — no human approval step.

## Required Inputs
None from the user at run time — this workflow is self-contained and triggered by a daily schedule. Fixed theme: "how AI in marketing is changing, what to focus on, what to learn, and concrete action steps."

## Brand Style (derived from marketingopswithsam.com on 2026-08-22 — re-derive if the site is redesigned)
- Font: Poppins (Google Fonts, weights 300–800), sans-serif fallback
- Primary: `#0078D4`, gradient/accent: `#3a9bff`
- Background tint: `#F0F6FF`, text: `#0a0a0a`
- Neutral borders/grays: `#e5e7eb`, `#DDDDDD`, `#9ca3af`
- Sender name: "Marketing Ops With Sam" (set by `tools/send_newsletter_email.py`, matches the logo/site brand exactly)

## Voice: Direct-Response Hooks, Still Professional
This should be genuinely fun to open, the kind of email someone thinks about during the day, not a flat news recap. Write with the punch of direct-response copywriting (think Sabri Suby: bold claims, pattern interrupts, open loops, curiosity) while staying credible for a professional B2B marketing ops audience. Concretely:
- **Subject line and preheader**: lead with curiosity, a bold claim, a specific number, or a pattern interrupt, not a flat headline. "Your competitors' AI agent just did your job for you" beats "AI Agents in Marketing This Week."
- **Section `lead`**: a provocative one-liner that makes the reader want the next sentence, not a summary. Think of it as the hook of a mini-story, not a topic sentence.
- **Rhythm**: mix short punchy sentences with longer ones. Don't let every sentence run the same length, that's what makes copy feel flat and reportorial instead of alive.
- **Stay grounded**: every bold claim still needs to be true and backed by the cited source. Entertaining does not mean exaggerated or clickbait, the credibility of a marketing ops professional's newsletter is the whole point.
- Keep everything else: no em dashes, plain simple words, cut filler/hedge phrases, short paragraphs, bullets for anything step-like.

## Steps

### 1. Read history
Read `logs/newsletter_history.jsonl` (create it if missing). Look at the last ~7 entries (date, subject, source URLs) so today's research doesn't rehash a story covered in the last week.

### 2. Research
Use native web search/fetch to find AI-in-marketing developments from roughly the last 24–48 hours: what's changing, notable tools, case studies, or news. Aim for **8–12 credible sources** (this is a deeper-analysis issue, not a thin digest — more sources means more to draw on for context, examples, and the further-reading list). Save raw notes to `.tmp/research_<date>.md` (disposable, regenerated daily).

**Safety check:** if fewer than 3 credible sources are found, stop here — skip straight to step 6b (log-only, no send).

### 3. Draft content
Synthesize research into a JSON content spec matching the schema `tools/render_newsletter_html.py` expects:
```json
{
  "subject": "...",
  "preheader": "...",
  "hero_headline": "...",
  "hero_intro": "...",
  "sections": [
    {"heading": "What's Changing", "eyebrow": "What's changing", "lead": "...", "analysis": "short paragraph\n\nshort paragraph", "example": "...", "image_url": "...", "source_url": "...", "source_label": "..."},
    {"heading": "What to Focus On", "eyebrow": "What to focus on", "lead": "...", "analysis": "short paragraph\n\nshort paragraph", "example": "...", "image_url": "...", "source_url": "...", "source_label": "..."},
    {"heading": "Action Steps", "eyebrow": "Action steps", "lead": "...", "analysis": "one short paragraph", "bullets": ["...", "...", "...", "..."], "example": "...", "image_url": "...", "source_url": "...", "source_label": "..."}
  ],
  "video_idea": {"hook": "...", "shot_idea": "...", "caption_angle": "..."},
  "quick_links": [{"label": "...", "url": "..."}],
  "footer": {"address": "Melbourne, Australia", "unsubscribe_url": "#"}
}
```
- Sections map to: what's changing, what to focus on / key lesson, and concrete action steps the reader can take today.
- The whole issue renders as **one continuous document** (single card, thin dividers between sections), so writing needs to carry that: readable and scannable, not a wall of text.
- Each section: a one-line bold `lead` takeaway up front, `analysis` as 2 short paragraphs (separate them with a blank line, each paragraph a few sentences, not 150+ word blocks), and a pull-quote style `example`. The Action Steps section should use `bullets` (3-4 short, concrete steps) instead of a dense paragraph, since steps are more readable as a list.
- `video_idea` is required every day: a 30-second LinkedIn/Instagram video prompt (hook, shot idea, caption angle) derived from that day's insight.
- `quick_links` should have **5-7 entries** drawn from the best research sources. Tighter is more readable than exhaustive.
- Cite sources near claims — don't state facts without a linked source.
- Write 2 subject line options internally, pick the stronger one, and always include a preheader (the inbox preview snippet). Apply the **Voice** guidance above to the subject, preheader, and every `lead`, these are the hooks that decide whether the email gets opened and read.
- Save the finished spec to `.tmp/newsletter_content_<date>.json` (disposable).

### 4. Generate images
Use the Higgsfield image generation tool (`generate_image_batch`, model `recraft_v4_1`, `model_type: "standard"`, **not** `"vector"`, vector mode outputs SVG which most email clients including Outlook don't render): exactly **one image per section** (3 total, no separate hero image).

**Every image combines a fun, memorable illustrated scene or character AND a bold text banner, not typography alone on a flat gradient.** Typography-only "quote cards" were tried and rejected as "just text, not enjoyable." The scene should be specific to that section's point and genuinely fun/memorable, exaggerated expressions, a bit of humor or tension, a small visual story, not generic decorative clipart. `recraft_v4_1` in standard mode handles this well: it can render a full illustrated scene together with a short (3-6 word) bold text banner integrated as a solid-color strip (top or bottom of the composition) without garbling the text, longer phrases still risk garbling so keep the banner text short and punchy. Pull the banner text from the section's `lead` or a number in its `analysis`/`example`, don't invent a new claim for the image that isn't already in the copy.

Prompt pattern: `Fun bold flat illustration, <specific character/scene description with exaggerated expressions or a bit of visual tension/humor, tied directly to the section's point>, modern editorial character illustration style. Across the bottom, a solid dark blue banner strip with large bold white sans-serif text reading exactly "<SHORT TEXT>". High contrast, poster style, no other text`. Pin `colors` to the brand hex palette (`#0078D4`, `#3a9bff`, `#F0F6FF`, `#003E80`).

Example scenes that worked well: a marketer relaxing feet-up with coffee while a grumpy little robot does the work behind them (for "AI agents already doing the work"), an EU-flag-headed regulator inspecting a nervous sweating chatbot with a magnifying glass (for "a compliance rule is already live"), three characters relay-racing a baton while holding a magnifying glass, pencil, and checkmark flag (for a research/draft/check pipeline). The bar: would someone actually remember this image, not just read past it.

After generating, quickly check each image (fetch and view it, e.g. via a browser screenshot) to confirm the baked-in text actually rendered correctly and isn't garbled before using it, since AI text rendering is usually clean at this length but isn't guaranteed. If a generation comes back with garbled/misspelled text, regenerate once with a shorter phrase; if it still fails, fall back to a plain content-specific illustration (no baked-in text) for that section rather than shipping garbled text.

Use the returned hosted image URLs directly in the JSON spec — do not download/re-host them.

### 5. Render HTML
Run:
```
python tools/render_newsletter_html.py --input .tmp/newsletter_content_<date>.json --output .tmp/newsletter_<date>.html
```

### 6a. Send
Send the rendered HTML file via IONOS SMTP, from hello@marketingopswithsam.com:
```
python tools/send_newsletter_email.py --to [redacted] --subject "<chosen subject>" --html-file .tmp/newsletter_<date>.html
```
This reads `IONOS_SMTP_HOST`/`IONOS_SMTP_PORT`/`IONOS_SMTP_USER`/`IONOS_SMTP_PASSWORD` from `.env` and sends a real email (HTML + a plain-text fallback the script generates automatically) — no draft, no approval step. Then go to step 7.

### 6b. Failure path
If step 2's safety check failed, or any tool call in steps 3-6a errored: don't leave it silent, since nobody is reviewing this run each morning. Send a short plain-text heads-up so the skip is visible immediately instead of only discoverable by checking the log file:
```
python tools/send_newsletter_email.py --to [redacted] --subject "Newsletter skipped today" --body "Today's AI in Marketing newsletter did not send.\n\nReason: <what happened>"
```
Then append a failure entry to `logs/newsletter_history.jsonl` (date, status: "skipped", reason) and stop.

### 7. Log
Append a success entry to `logs/newsletter_history.jsonl`: `{"date": "...", "status": "sent", "subject": "...", "headline": "...", "sources": ["..."]}`.

## Standing Guidance (don't re-derive these each run)
- Always include a preheader and 2 internally-considered subject line options.
- Cite sources inline near claims to avoid hallucinated facts.
- Every image needs `alt` text (handled by the render tool automatically from each section's `heading`, so keep headings meaningful and specific).
- Footer address is "Melbourne, Australia" (a city-level placeholder, fine for a self-only send). Keep the unsubscribe link too, so neither is forgotten if this ever expands to a real subscriber list, which would need a full street address for CAN-SPAM compliance.
- `.tmp/*` files are disposable and regenerated daily. `logs/newsletter_history.jsonl` is NOT disposable — it must persist across runs for the dedup check.
- The template renders as **one continuous document** (a single card with thin dividers), not separate boxed-off blocks per section. Don't reintroduce a full border/box around each individual section, that was tried and explicitly rejected as feeling disconnected.
- Readability over density: short paragraphs (2 per section, blank-line separated), a bold one-line takeaway (`lead`) at the top of each section, bullets for anything step-like, and a tighter quick-links list (5-7, not 8-10+). Enjoyable to read beats exhaustive.

## Edge Cases
- **Fewer than 3 sources found:** skip send, log failure (step 6b). Don't send a thin/weak issue.
- **Image generation fails for a section:** proceed without that section's image rather than blocking the whole send; the render tool handles missing `image_url` gracefully (image block is simply omitted).
- **Repeated topic:** if today's best story overlaps heavily with the last 7 log entries, actively look for a different angle or a more recent development before falling back to it.
