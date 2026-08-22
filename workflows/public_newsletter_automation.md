# Public Newsletter Subscription System (marketingopswithsam.com)

## What this is

A separate system from the daily "AI in Marketing" digest (`workflows/newsletter_automation.md`). This one is public: anyone who subscribes via the "Get my notes on marketing ops and AI automation" box on the live site gets a real welcome email that doubles as that month's newsletter issue, written in Sam's own voice (marketing ops, automation, workflows — not AI news). Built 2026-08-22, revised 2026-08-22/23 per user feedback rounds.

## Where subscriber data actually lives

Two places, both private, neither ever touches git:

1. **Supabase Postgres**, table `newsletter_subscribers` (project `212580ea-2034-47df-804b-9002ca64dd5b`, "marketingopswithsam"). Row-level security: public can only INSERT, nobody can SELECT. This is the durable signup record, already existed before this build.
2. **Resend contacts.** Resend needs its own copy to manage sending, segmentation, and unsubscribe state. Gated by API key only, viewable at resend.com/audiences.

## Resend configuration (IDs, so this is inspectable without digging through the dashboard)

- Segment "Newsletter Subscribers": `81e552ae-7cb3-4a48-a9b0-8cc6d77d765e`
- Topic "Monthly Newsletter" (opt_in default): `d4ae2bbc-5f74-4590-9411-0e29414abac3`
- Event "newsletter.signup": `01a026b8-5f15-7549-a510-a7c2783a9137`
- Automation "Public Newsletter Welcome": `01a026c2-665e-722e-b036-ce772842bf52` — trigger on `newsletter.signup` → send the "Current Issue" template. Enabled. **Its step config hardcodes its own `from` and `subject`, which override the template's own values** — if the template's subject changes, the automation step must be updated too, or live sends use the stale subject silently.
- Template "Public Newsletter — Current Issue", alias `public-newsletter-current-issue`: `f749c9da-e4f4-4848-bf47-e93a68ce0350`. Whatever this template holds is what fires on every new signup **and** what the monthly broadcast will send to everyone else once Part C exists. Update this one place, both paths stay in sync. **The user has also hand-edited this template directly in the Resend dashboard at times** — if content looks different from what's described below, the dashboard is the current source of truth, not this doc; pull it via `get-template` before assuming.
- Sending domain: `marketingopswithsam.com` (verified, same domain the daily digest uses), sent as `Marketing Ops With Sam <hello@marketingopswithsam.com>`.

## How signup → welcome email actually happens

1. Visitor submits the site's subscribe form (`src/components/ui/NewsletterSignupForm.tsx`).
2. Supabase edge function `newsletter-signup` upserts the row into `newsletter_subscribers` (unchanged, pre-existing).
3. **Next step, not yet built (Part B):** that same edge function needs to also create/update the contact in Resend and fire the `newsletter.signup` event, which triggers the automation above. Until this edit ships, new signups land in Supabase but do not yet get a real welcome email — the legacy Mailchimp call currently in that function does nothing meaningful (no real content, just double opt-in noise) and is being removed as part of the same edit. **Asked about explicitly, still awaiting the user's go-ahead** — do not make this edit without it, it changes live production code behind a real public form.

## Content formula (standing rule for every future issue, not just this one)

User's explicit direction, given after seeing the first draft:

- **Structure**: open with an explicit, warm welcome + expectation-setting (cadence, why, the "if it doesn't teach you something or make you laugh, it doesn't go out" promise), then straight into a story. Every issue should have a story, not just analysis.
- **60% personal experience**: first person, direct. "I saw this," "I encountered this," "I had a client do this."
- **40% observation, drawn from three sources**: a friend, a former colleague (**never just "colleague" — always "former colleague," user's explicit, repeated instruction**), and someone from the industry generally. Short supporting beats reinforcing the same theme as the main story, not separate topics.
- **Subject line and preview text**: subject should hook with curiosity, a specific number, or a pattern interrupt, plus a blunt, concrete edge, not a plain "Welcome!" Preview text carries the warmth/welcome framing the subject doesn't have room for.
- **Voice**: no "super serious AI language," write like a friend telling a story they actually want to hear, casual but sharp, no em dashes (standing rule, [[feedback-newsletter-writing-style]]).

## Content: issue #1, current version

Subject: "The $40k 'automation' I've now found four times." Preview text: "Welcome. Also, meet Dave, and the three other people just like him." Headline in-body: "Meet Dave. He's not the only one."

Structure: welcome + expectations, then the main story (Sam's own client experience: a "fully automated" lead-routing system that turns out to be one guy named Dave doing everything manually), then three short observation vignettes in the same theme (a friend's manual "automated" reporting, a former colleague whose process broke when he left because it only lived in his head, someone from the industry whose "AI-powered growth engine" demo hit a long silent pause at the first hard question), a 3-question actionable test readers can run on their own team, a pull-quote, and a close.

Hero image: illustrated "fake automation reveal" scene with integrated text banner, matching the site's real brand tokens (violet `#6039E6`, pink, amber gradient, Poppins), generated via Canva, committed to `assets/public_newsletter_images/2026-08-issue1-hero-v2.png`. Header logo: the user's real supplied logo asset (`brand_assets/MarketingOpswithSam.png`, navy wordmark, matches the site's actual live logo), committed to `assets/public_newsletter_images/logo.png`. Both served via `raw.githubusercontent.com` (Canva's own URLs expire in ~a day, so chosen images always get downloaded and re-hosted, never linked directly).

**Personalization:** template has a custom variable `NAME_PART` (fallbackValue `"there"`), merged into the HTML as `Hey {{{NAME_PART}}},`. The automation's `send_email` step sets `NAME_PART` to `{"var": "contact.first_name"}`. **Gotcha found by testing:** the automation engine expects **snake_case** field references (`contact.first_name`), not the camelCase used everywhere else in the Resend API (`firstName`) — camelCase silently resolves to nothing and always falls through to the fallback, no error thrown. Verified both branches for real against actual sent emails: a contact with `firstName: "Sam"` produced "Hey Sam,", a contact with none produced "Hey there,".

Resend does **not** support Handlebars-style `{{#if}}` blocks in template HTML despite the triple-brace variable syntax looking like Handlebars — attempting one fails template validation outright ("improperly formatted variables"). Personalization has to be done with a plain merge variable plus a dynamic `{"var": ...}` reference at the automation step, not conditional logic inside the template.

## Verification done (guardrail, per the incident logged in `feedback_newsletter_writing_style` memory)

Every content revision in this system has been tested the same way before being reported as done, never just assumed to work:

- Fire a real `send-event` test, confirm the automation run completed (`get-automation-runs`).
- Pull the actual sent email via `get-email`: confirm real rendered HTML (no escaping), correct subject, correct image URLs, correct personalization branch.
- Unsubscribe link verified once by actually following it: lands on Resend's hosted unsubscribe page, correctly shows the exact contact and the "Monthly Newsletter" topic. Requires a genuine button click to confirm (a Next.js server action, not a plain GET) before it actually unsubscribes — this is correct, deliberate behavior (prevents email-scanner prefetches from silently unsubscribing people), not a bug.

## Still to build

- **Part B**: edit `supabase/functions/newsletter-signup/index.ts` (via Lovable's own AI agent, since this repo doesn't contain that code) to drop Mailchimp and call Resend (create-contact + send-event) instead. Needs a `RESEND_API_KEY` Supabase secret. **Explicitly asked about twice, still no go-ahead from the user** — do not proceed without it.
- **Part C**: a second cloud routine (monthly cron, separate from the daily digest routine) that drafts each new month's issue, updates the "Current Issue" template, and sends a broadcast to the "Newsletter Subscribers" segment. Not started.
- One-time backfill already done: the 3 pre-existing rows in `newsletter_subscribers`, plus a personal test address (not recorded here, this file is public), all created as Resend contacts, opted into the Monthly Newsletter topic, added to the segment.
