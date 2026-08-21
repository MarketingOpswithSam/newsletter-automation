# Workflow: Daily "AI in Marketing" Newsletter

## Objective
Every morning at 08:00 Australia/Melbourne, autonomously research how AI in marketing is changing, draft a short newsletter, generate on-brand images, render polished HTML, and **send** it from hello@marketingopswithsam.com to the recipient in `NEWSLETTER_TO_EMAIL` (see `.env` locally, or the routine's own prompt config in the cloud, this file is public so the literal recipient address is deliberately kept out of it). Fully autonomous — no human approval step.

## Required Inputs
None from the user at run time — this workflow is self-contained and triggered by a daily schedule. Fixed theme: "how AI in marketing is changing, what to focus on, what to learn, and concrete action steps."

## Brand Style (derived from marketingopswithsam.com on 2026-08-22 — re-derive if the site is redesigned)
- Font: Poppins (Google Fonts, weights 300–800), sans-serif fallback
- Primary: `#0078D4`, gradient/accent: `#3a9bff`
- Background tint: `#F0F6FF`, text: `#0a0a0a`
- Neutral borders/grays: `#e5e7eb`, `#DDDDDD`, `#9ca3af`
- Sender name: "Marketing Ops With Sam" (set via the `from` field on the Resend MCP `send-email` call, matches the logo/site brand exactly)

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
Use the **Canva** MCP tool `generate-design` (free, no credits, this replaced a paid Higgsfield-based approach on 2026-08-22 after Higgsfield's monthly credits ran out): `design_type: "youtube_thumbnail"` (16:9, matches the email's image slot) for each of the 3 sections.

**Every image combines a fun, memorable illustrated scene or character AND a bold text banner, not typography alone on a flat background.** The scene should be specific to that section's point, genuinely fun/memorable, exaggerated expressions, a bit of humor or tension, a small visual story, not generic decorative clipart. Pull the banner text from the section's `lead` or a number in its `analysis`/`example`, don't invent a new claim for the image that isn't already in the copy.

Query pattern for `generate-design`: `Fun bold flat illustration, <specific character/scene description with exaggerated expressions or a bit of visual tension/humor, tied directly to the section's point>, modern editorial character illustration style, muted blue and navy color palette. Large bold white text banner across the bottom reading "<SHORT TEXT>" on a solid dark blue strip. High contrast poster style.` **Describe colors in words** ("muted blue and navy"), never as hex codes in the query text, Canva has rendered literal hex codes as garbled on-image text when they were included.

`generate-design` returns 4 candidates, each with a `thumbnail.url`. Canva is noticeably less reliable than the old Higgsfield path: expect occasional garbled/duplicated words in the banner text or off-brand colors. View all 4 (fetch each `thumbnail.url`, e.g. via a browser screenshot) and pick the one with the cleanest, most accurate banner text and the closest match to the brand's blue palette. If literally none of the 4 are acceptable, regenerate once with a shorter banner phrase, then take the best of the second batch regardless, don't loop more than once.

**Canva's `thumbnail.url` is a signed URL that expires in about a day, so it cannot be used directly as the email's `image_url`.** Instead, for each chosen image: download it (`curl -sL "<thumbnail.url>" -o assets/newsletter_images/<date>-section<N>.png`, creating the `assets/newsletter_images/` folder if needed), then `git add`, commit, and push it to the repo (the repo is public specifically so these images resolve without auth). Use the resulting permanent URL as `image_url` in the JSON spec: `https://raw.githubusercontent.com/MarketingOpswithSam/newsletter-automation/main/assets/newsletter_images/<date>-section<N>.png`. Push this before step 5 so the URL is live before the email that references it goes out.

### 5. Render HTML
Run:
```
python tools/render_newsletter_html.py --input .tmp/newsletter_content_<date>.json --output .tmp/newsletter_<date>.html
```

### 6a. Send
Send using the **Resend MCP tool** (`send-email`), NOT `tools/send_newsletter_email.py` and NOT raw SMTP or a direct HTTPS call. MCP tool calls are the only send path that reliably works from the cloud routine's sandboxed network, direct network calls (SMTP or straight `curl`/`urllib` to any email API) get blocked there, confirmed the hard way on 2026-08-22.

Call `send-email` with:
- `from`: `Marketing Ops With Sam <hello@marketingopswithsam.com>`
- `to`: `[the address in NEWSLETTER_TO_EMAIL]`
- `subject`: the chosen subject line
- `html`: the **raw, unescaped** contents of the rendered `.tmp/newsletter_<date>.html` file (read it first). Pass the file's exact contents, character for character, do NOT re-type, re-format, or HTML-escape it while passing it as the tool argument, that turns real `<table>` markup into literal `&lt;table&gt;` text and the recipient gets a wall of visible tags instead of a formatted email. This happened once (2026-08-22) and must not happen again.
- `text`: a short plain-text fallback (a few sentences summarizing the issue is enough, the HTML is what actually gets read)

**Mandatory guardrail, every single send, no exceptions:** immediately after calling `send-email`, call `get-email` with the returned id and inspect the `HTML Content` field it returns.
- It must start with a real `<!DOCTYPE html>` (an actual less-than sign), not the literal text `&lt;!DOCTYPE`.
- It must contain real `<table`, `<td`, `<img` tags, not `&lt;table`, `&lt;td`, `&lt;img`.
- If it looks escaped (literal `&lt;`/`&gt;` visible instead of real tags), the send is broken. Immediately send a corrected email (same subject is fine, Gmail and most clients will just show both, better a duplicate than a broken one going unnoticed) with the HTML passed correctly, verify that one with `get-email` too, and only log success once a verified-good email has gone out.
- Only proceed to step 7 after this check passes on a real send.

This is a real send, no draft, no approval step otherwise. Then go to step 7.

(`tools/send_newsletter_email.py` still exists and still works, useful for quick local testing from a machine with normal network access, but the cloud routine must use the Resend MCP tool, not that script.)

### 6b. Failure path
If step 2's safety check failed, or any tool call in steps 3-6a errored: don't leave it silent, since nobody is reviewing this run each morning. Send a short plain-text heads-up via the same Resend MCP tool so the skip is visible immediately instead of only discoverable by checking the log file: `send-email` with `from`/`to` as above, `subject`: "Newsletter skipped today", `text`: "Today's AI in Marketing newsletter did not send.\n\nReason: <what happened>" (and `html` can repeat the same text, plain text is low risk for the escaping mistake above, but the same raw-content rule still applies).

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
- Never hardcode the recipient email address in this file or in any tracked code file, this repo is public. Reference `NEWSLETTER_TO_EMAIL` instead. The sender address (hello@marketingopswithsam.com) is fine to hardcode, it's already public on the site itself.
- Always verify a send with `get-email` before trusting it (see step 6a). A send that "succeeds" at the API level can still have gone out with broken/escaped HTML, success only means the guardrail check passed too.

## Edge Cases
- **Fewer than 3 sources found:** skip send, log failure (step 6b). Don't send a thin/weak issue.
- **Image generation fails for a section:** proceed without that section's image rather than blocking the whole send; the render tool handles missing `image_url` gracefully (image block is simply omitted).
- **Repeated topic:** if today's best story overlaps heavily with the last 7 log entries, actively look for a different angle or a more recent development before falling back to it.
