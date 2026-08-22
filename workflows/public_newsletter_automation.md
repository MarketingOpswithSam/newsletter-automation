# Public Newsletter Subscription System (marketingopswithsam.com)

## What this is

A separate system from the daily "AI in Marketing" digest (`workflows/newsletter_automation.md`). This one is public: anyone who subscribes via the "Get my notes on marketing ops and AI automation" box on the live site gets a real welcome email that doubles as that month's newsletter issue, written in Sam's own voice (marketing ops, automation, workflows — not AI news). Built 2026-08-22.

## Where subscriber data actually lives

Two places, both private, neither ever touches git:

1. **Supabase Postgres**, table `newsletter_subscribers` (project `212580ea-2034-47df-804b-9002ca64dd5b`, "marketingopswithsam"). Row-level security: public can only INSERT, nobody can SELECT. This is the durable signup record, already existed before this build.
2. **Resend contacts.** Resend needs its own copy to manage sending, segmentation, and unsubscribe state. Gated by API key only, viewable at resend.com/audiences.

## Resend configuration (IDs, so this is inspectable without digging through the dashboard)

- Segment "Newsletter Subscribers": `81e552ae-7cb3-4a48-a9b0-8cc6d77d765e`
- Topic "Monthly Newsletter" (opt_in default): `d4ae2bbc-5f74-4590-9411-0e29414abac3`
- Event "newsletter.signup": `01a026b8-5f15-7549-a510-a7c2783a9137`
- Automation "Public Newsletter Welcome": `01a026c2-665e-722e-b036-ce772842bf52` — trigger on `newsletter.signup` → send the "Current Issue" template. Enabled.
- Template "Public Newsletter — Current Issue", alias `public-newsletter-current-issue`: `f749c9da-e4f4-4848-bf47-e93a68ce0350`. Whatever this template holds is what fires on every new signup **and** what the monthly broadcast sends to everyone else. Update this one place, both paths stay in sync.
- Sending domain: `marketingopswithsam.com` (verified, same domain the daily digest uses), sent as `Marketing Ops With Sam <hello@marketingopswithsam.com>`.

## How signup → welcome email actually happens

1. Visitor submits the site's subscribe form (`src/components/ui/NewsletterSignupForm.tsx`).
2. Supabase edge function `newsletter-signup` upserts the row into `newsletter_subscribers` (unchanged, pre-existing).
3. **Next step, not yet built (Part B):** that same edge function needs to also create/update the contact in Resend and fire the `newsletter.signup` event, which triggers the automation above. Until this edit ships, new signups land in Supabase but do not yet get a real welcome email — the legacy Mailchimp call currently in that function does nothing meaningful (no real content, just double opt-in noise) and is being removed as part of the same edit.

## Content: issue #1, built and sent

Subject: "The $40,000 'automation' that was actually a guy named Dave" (revised from an earlier "chatbot vs agent" draft per user feedback: more entertaining, more of a narrative journey). Voice calibrated from real first-person posts on the site (`src/pages/BlogRapidCircle.tsx`, `src/pages/BlogPersonalNewsletter.tsx`): short declarative sentences, skeptical-then-converted arc, no em dashes, no corporate softening. Hero image: illustrated "fake automation reveal" scene with integrated text banner, matching the site's real brand tokens (violet `#6039E6`, pink, amber gradient, Poppins), generated via Canva, committed to `assets/public_newsletter_images/2026-08-issue1-hero-v2.png`. Header logo: the user's real supplied logo asset, committed to `assets/public_newsletter_images/logo.png`, both served via `raw.githubusercontent.com` (same trick the daily digest uses, Canva's own URLs expire in ~a day).

**Personalization:** template has a custom variable `NAME_PART` (fallbackValue `"there"`), merged into the HTML as `Hey {{{NAME_PART}}},`. The automation's `send_email` step sets `NAME_PART` to `{"var": "contact.first_name"}`. **Gotcha found by testing:** the automation engine expects **snake_case** field references (`contact.first_name`), not the camelCase used everywhere else in the Resend API (`firstName`) — camelCase silently resolves to nothing and always falls through to the fallback, no error thrown. Verified both branches for real: a contact with `firstName: "Sam"` produced "Hey Sam,", a contact with no first name produced "Hey there,".

Resend does **not** support Handlebars-style `{{#if}}` blocks in template HTML despite the triple-brace variable syntax looking like Handlebars — attempting one fails template validation outright ("improperly formatted variables"). Personalization has to be done with a plain merge variable plus a dynamic `{"var": ...}` reference at the automation step, not conditional logic inside the template.

**Note for future months:** this first issue's opening line ("Hey, thanks for signing up...") is written for a true first-time welcome. Since the automation always sends whatever the current template holds, future months' opening lines should be neutral enough to work for both a brand-new subscriber and someone who's been reading for a year — don't write "welcome" framing into every month's issue.

## Verification done (guardrail, per the incident logged in `feedback_newsletter_writing_style` memory)

- Fired a real test signup event, automation ran (`get-automation-runs` → completed).
- Pulled the actual sent email via `get-email`: real rendered HTML, no escaping, image and unsubscribe link both resolved correctly.
- Followed the real unsubscribe link: lands on Resend's hosted unsubscribe page, correctly shows the exact contact and the "Monthly Newsletter" topic, `isSubscribed: true`. It requires a genuine button click to confirm (a Next.js server action, not a plain GET) before it actually unsubscribes — this is correct, deliberate behavior (prevents email-scanner prefetches from silently unsubscribing people), not a bug. Could not script the actual confirm click via curl since it isn't a plain form POST; a real click in a browser is what a subscriber would do, and the page it lands on is correct.

## Still to build

- **Part B**: edit `supabase/functions/newsletter-signup/index.ts` (via Lovable's own AI agent, since this repo doesn't contain that code) to drop Mailchimp and call Resend (create-contact + send-event) instead. Needs a `RESEND_API_KEY` Supabase secret. Requires explicit user confirmation before sending, since it changes live production code behind a real public form.
- **Part C**: a second cloud routine (monthly cron, separate from the daily digest routine) that drafts each new month's issue, updates the "Current Issue" template, and sends a broadcast to the "Newsletter Subscribers" segment.
- One-time backfill already done: the 3 pre-existing rows in `newsletter_subscribers`, plus a test contact ([redacted]), all created as Resend contacts, opted into the Monthly Newsletter topic, added to the segment.
