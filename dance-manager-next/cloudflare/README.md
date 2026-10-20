# Dance Manager Next — Cloudflare V10 Concierge

**Independent staging service.** Never deploy to the original Dance Manager. Do not edit GitHub `main` or the Century of Empires files. This project lives in `dance-manager-next/cloudflare/` on branch `dance-manager-next-preview`.

## Design

- Static marketing/studio prototype stays on the existing Render **static** site (`https://dance-manager-next-preview.onrender.com`). Static sites do not use Render's sleeping free web backend. No Render backend is required for the AI.
- Cloudflare Worker provides `GET /health`, `POST /api/chat`, `POST /api/lead`, optional `POST /api/handoff`, and `/api/owner/*` for secure staff operations; `GET /owner` is an independent owner interface.
- Worker has a Workers AI binding to a supported free-tier model, plus D1 for inquiries, conversation history, deduplication, delivery attempts, and rate windows.
- Resend handles outbound customer acknowledgments and owner email notifications using its available free tier. Cloudflare Email Routing can receive emails into the Worker's `email()` handler. SMS uses optional Twilio when approved. Calls are human follow-ups only, not AI robocalls.
- A fixed acknowledgment is generated immediately from an accepted form submission; external delivery occurs asynchronously. **A 202 response does not mean an email or SMS was delivered.** The ticket states show accepted/failed attempts (provider acceptance is not guaranteed inbox delivery).

## IMPORTANT: before account setup

Do not put any actual contact records into the public demo before the studio owner approves it, a privacy notice is present, Cloudflare Access is configured, and provider delivery has been tested with fictional data. Do not store actual children's records here.

## Account-level deployment checklist (for ChatGPT Work)

1. Confirm `dance-manager-next-preview` is the selected GitHub branch. Inspect `src/worker.mjs`, `src/helpers.mjs`, `src/owner.mjs`, migrations, and `.toml` before enabling any external service.
2. In user's existing Cloudflare account, enable Workers AI; create new D1 database `dance-manager-next-inquiries` (not an existing database). Put the generated database ID into `wrangler.toml` **on this isolated branch only**. Don't paste API keys/tokens into files or the chat.
3. In `dance-manager-next/cloudflare/`, install dependencies (`npm install`); apply migrations (`npx wrangler d1 migrations apply dance-manager-next-inquiries --remote`); deploy Worker (`npx wrangler deploy`). Its route should be a new `workers.dev` address unless a dedicated demo domain is approved.
4. Set Worker secrets with Cloudflare secrets (never GitHub/plain vars): `RATE_SALT` (random), `OWNER_API_TOKEN` (random, >=32 characters), `RESEND_API_KEY`, `LEAD_FROM_EMAIL` (verified, controlled by studio owner), `LEAD_TO_EMAIL` (approved owner email). `ALLOWED_ORIGINS` must include the exact independent preview origin. The current project's `wrangler.toml` includes the independent Render preview domains only. `AI_MODEL` defaults to `@cf/meta/llama-3.1-8b-instruct-fp8`.
5. If provider setup is not complete, deploy only for fake AI testing. `/health` should show `aiConfigured:true` and `leadsConfigured:false`; contact forms must **not** claim that requests are being delivered.
6. Configure Resend free email sending with a verified studio-owned sender domain (or an approved separate sender). Verify one owner and one visitor inbox with test data. Do not activate paid subscriptions without approval. Resend free limits and sender restrictions must be checked during setup.
7. Check `GET https://<the-actual-worker>/health`; verify `POST /api/chat` from the approved preview origin using mock questions; submit a fake test inquiry to `/api/lead` only after email delivery is configured. Inspect D1 logs and actual owner/customer email delivery.
8. **Only after those tests pass**, update `dance-manager-next/v7-config.json` on `dance-manager-next-preview` from the old Render web backend URL to the exact new Worker HTTPS origin: `{"apiBase":"https://<actual-worker-host>"}`. Leave the existing Render **static** website service unchanged. Trigger/test the static site deployment if automatic deploy doesn't occur. The old sleeping Render **web** backend can remain disabled or idle—it is not needed.
9. Protect both `/owner` and `/api/owner/*` with Cloudflare Access (approved staff login) before using actual contact information. The owner UI requires the `OWNER_API_TOKEN` too; this token is deliberately **not** stored in localStorage, cookies, or the frontend repository. Use secret management to retrieve it and never publish it. Test ticket list, resolution, and actual staff replies.
10. **Optional email routing:** configure a Cloudflare-managed demo domain, an exact inbound address and Email Routing rule targeting this Worker; set `INBOUND_EMAIL_ENABLED=true` and `INBOUND_EMAIL_ADDRESS=the-routed-address`. Cloudflare reply requirements include a valid DMARC result. Check mailer loop protection, duplicate messages, owner alert and receipt in the real inbox.
11. **Optional SMS (costs vary):** use an approved Twilio account/number. Worker secrets: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`; set `TWILIO_WEBHOOK_URL` equal to the exact public HTTPS `/webhooks/twilio/sms` URL if proxying. Point the Twilio webhook there, verify signed requests, STOP/START handling, duplicates and owner follow-up. Keep this disabled if no authorized provider exists.
12. Open the website on iPhone: premium dancer graphics, dancer/competition tabs, responsive contact fields and chat remain intact. Verify there are no console errors, no old Render AI URL and no personal data stored in the static demo.

## Source and tests

- Worker: `src/worker.mjs`
- Pure validation: `src/helpers.mjs`
- Staff UI: `src/owner.mjs`
- D1 migration: `migrations/0001_init.sql`
- Cloudflare deployment configuration: `wrangler.toml`
- Local tests: `npm run check` (Node.js >=22 for built-in SQLite mocks)

All 18 tests are **local simulations**, not Cloudflare/Wrangler builds or real provider delivery. They cover Worker chat, CORS checks, adult/phone/consent validation, D1 persistence, owner notification acceptance, owner token gate, SMS signature/STOP, inbound email reply/dedupe and owner console rendering. Live installation and provider setup still require authorized access.

## Free-tier and safety reality

Cloudflare Workers and Workers AI have quotas. Resend currently has a free email allowance; it requires sender verification and may restrict trial recipients until configured. SMS requires a separate provider and may have per-message/number costs. Fast acknowledgment is a design goal, not a guaranteed response SLA. Do not make promises about human response times or bookings.

## Next-step order with minimal Work time

**One continuous Work run:** Cloudflare login -> create D1/Worker -> add secrets -> run fake AI and inquiry test -> connect frontend config -> confirm new behavior on iPhone. Skip SMS and inbound email setup if those require new paid accounts, a customer-owned domain, or approvals. Leave a concise status report with Worker URL, test outcomes, blockers and next command; no generic research or redesign.
