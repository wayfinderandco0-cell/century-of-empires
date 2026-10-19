# Dance Manager Next — V7 secure AI / lead backend

**Status:** Source code only. Not deployed or connected to actual credentials yet. The public V7 preview continues to use its guided demo until the secure backend is configured.

This server is **independent of the owner's existing Dance Manager site** and independent of the historical strategy game that shares the GitHub test repository.

## How it works

- Public site: \`/dance-manager-next/preview-v7.html\` (on GitHub Pages)
- Public configuration: \`/dance-manager-next/v7-config.json\` contains only the backend HTTPS origin. **No secrets.**
- Backend: \`/dance-manager-next/backend/server.cjs\` (Node 20+, no extra npm dependencies).
- AI: \`POST /api/chat\` sends bounded chat history to OpenAI Responses API with a server-only key. The model is selected with \`OPENAI_MODEL\`; default \`gpt-4o-mini\`.
- Inquiry: \`POST /api/lead\` sends a direct email through Resend only if the provider accepts it. Nothing is stored on the backend; public browsing is not tied to real student records.
- Check: \`GET /health\` reports \`aiConfigured\` and \`leadsConfigured\`. It does not validate the credentials.
- If AI or mail credentials are absent, those endpoints return 503 instead of pretending they worked.

## Hosting

GitHub Pages is a static host and **cannot safely run this backend**.

Deploy the \`main\` branch on a trusted Node server such as Render as a *new, independent web service*:

- Build command: not needed (no dependencies).
- Start command: \`node dance-manager-next/backend/server.cjs\`
- Root directory: repository root (or set start command appropriately if a custom root is chosen).
- Bind: the server listens on \`process.env.PORT\`, default 10000.
- Environment variables (server-only):

| Variable | Purpose |
| --- | --- |
| \`OPENAI_API_KEY\` | OpenAI API project key; enables live AI |
| \`OPENAI_MODEL\` | Optional; default \`gpt-4o-mini\` |
| \`ALLOWED_ORIGINS\` | Set to \`https://wayfinderandco0-cell.github.io\` for the current preview |
| \`RESEND_API_KEY\` | Resend server key; required for real inquiry delivery |
| \`LEAD_TO_EMAIL\` | Authorized company inbox to receive inquiries |
| \`LEAD_FROM_EMAIL\` | Verified sender address/domain controlled by the company |

**Never** put private API keys in the GitHub repository, HTML, client JS, \`v7-config.json\`, or chat messages. Enter them through your deployment provider's private environment-variable controls.

When a backend is deployed and \`/health\` responds correctly, replace the empty \`apiBase\` in \`v7-config.json\` with the backend origin, e.g. \`https://YOUR-CHOSEN-BACKEND.example.com\`. The frontend checks \`/health\` and enables live AI / real inquiries only for configured features.

## Safety, cost and privacy

- AI requests are capped by message/history length and output tokens. Server-side in-memory rate limits reduce accidental or abusive volume; add a managed edge rate limiter and bot challenge before high-traffic production.
- The system prompt states only verified *prototype* features and instructs the AI not to invent prices, product integrations, event records, or appointments.
- AI questions are processed by an external AI provider. Add a privacy notice and obtain the business owner's approval before real customers use the chatbot.
- Real lead submissions need explicit consent; sample requests remain local when mail isn't enabled.
- Resend requires sender-domain verification. Configure the correct business-owned inbox; never silently route visitors' data to a developer's personal address.
- Don't solicit real minors' names, photos or addresses in the public chatbot. Secure child/guardian features require additional access controls and policy review.
- Model API usage and production hosting may incur **separate costs** from a ChatGPT subscription. Set spending budgets and alarms; consider prepaid API credits with auto-recharge off.
- Requests are **not stored** by this Node server; the outgoing providers have their own terms and retention. Do not market this as guaranteed end-to-end privacy.
- For production, add durable monitoring/log aggregation that avoids personal data, managed CAPTCHA/Turnstile, stronger per-client throttling, verified ownership of the sender and receiving inbox, a privacy policy and retention/deletion procedures.

## Test without any real keys

\`\`\`sh
node dance-manager-next/backend/server.cjs
curl http://localhost:10000/health
\`\`\`

With no keys, expected health properties: \`aiConfigured: false\`, \`leadsConfigured: false\`. No real AI request or email delivery is possible until the server credentials are configured.

## What remains

1. Obtain the business owner's approval to collect real inquiries and identify the intended receiving email inbox.
2. Select a hosting service/workspace and deploy the independent backend.
3. Configure server-only OpenAI API and email credentials; make a controlled test transaction.
4. Set the public backend URL in \`v7-config.json\`, verify browser CORS and iPhone experience.
5. Deploy managed spam protection and appropriate privacy notices before wider rollout.

**Nothing in V7 changes the existing Dance Manager website.**


## V8 visitor-conversion decisions (2026-10-19)

- Independent Render API created: \`https://dance-manager-next-ai-v7.onrender.com\` in workspace \`Stan's workspace\` (\`srv-dbb7rq9jfumc73er36ug\`), free tier, manual deploy. Do **not** change the existing game server or original Dance Manager domain.
- The public \`v7-config.json\` links only to the HTTPS API hostname. No secrets or private information are in GitHub.
- The V8 chat begins as a navigation guide. It offers relevant feature demos, and may offer an optional demo request to clearly interested adults. It must not interrupt, pester, or request a contact address inside the conversation.
- Adults must affirm they are 18+ and authorize follow-up before live inquiry delivery.
- Promotional email consent is a separate, unchecked opt-in. The server includes that decision in the lead notification for authorized staff. This does **not** establish a production mailing list or an automated marketing campaign.
- Live AI requires a dedicated server-side \`OPENAI_API_KEY\`; live lead delivery requires \`RESEND_API_KEY\`, \`LEAD_FROM_EMAIL\` (verified sender), and \`LEAD_TO_EMAIL\`. The UI must truthfully remain a scripted demo when either service is not configured.
- IP addresses: **do not store or export visitor IPs for advertising in this prototype**. Temporary in-memory hashed network data are used solely for coarse abuse throttling, not behavioral profiling. A service provider may still process normal network/request logs according to its policies. Before any future first-party analytics or ads audience feature: create a real privacy notice, set a retention period, obtain applicable consent, ensure audience restrictions for minors, and assess account/platform eligibility.
- If authorized later, consider consent-based website retargeting and adult first-party email lists as the primary customer acquisition paths. Google Ads Customer Match has conditional IP support, but IP targeting is not equivalent to reliably identifying individuals; eligibility, geography, consent, and match-rate limitations apply.
- Do not assume a ChatGPT subscription includes OpenAI API usage. Limit API spend and enable alerts before adding real credentials.
- The test repo also contains an unrelated strategy game. Use a narrowly scoped backend deploy for this Dance Manager API; do not alter other services.


## Cloudflare Workers AI (free alternative)

Preferred zero-dollar chatbot option for small demo: Cloudflare Workers AI includes a 10,000 Neurons/day Free allocation, subject to its terms. Once exhausted, requests fail until reset; select a free-eligible model.

The existing separate Render API can now call Cloudflare Workers AI **directly via REST**, avoiding any need for another hosting service.

1. Open Cloudflare dashboard > Workers AI > Use REST API; create a scoped Workers AI API token and find the 32-character Account ID.
2. Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_AI_TOKEN as **private** Render service environment variables for dance-manager-next-ai-v7. Never share them in chat or commit them to GitHub.
3. Optional CLOUDFLARE_AI_MODEL defaults to @cf/google/gemma-4-26b-a4b-it. Other permitted choices: @cf/zai-org/glm-4.7-flash; @cf/meta/llama-3.1-8b-instruct-fp8.
4. Redeploy the new backend service if not automatic. The public v7-config.json already references its HTTPS origin; V8 checks /health to decide whether to enable live AI.

When both Cloudflare variables are configured, the server prefers Workers AI even if an OpenAI key exists. The response is still an AI-generated answer. A 429 free-tier limit error is shown as a temporary unavailable message.

Real inquiry emails remain separate and disabled until email delivery is configured. No IP-based ad tracking is installed. Only adults may submit inquiries, and consent for promotional marketing is separate.


## V9 Communication Concierge (2026-10-19)

The **separate Render staging website** now serves Dance Manager Next V9 at \`https://dance-manager-next-v2.onrender.com\`; it uses the \`dance-manager-next-preview\` GitHub branch, with \`index.html\` loading V4 student progress and V9 response-center assets. **It does not update the existing Dance Manager website.** The API uses \`main\` and \`node dance-manager-next/backend/server.cjs\`.

V9 adds \`backend/operations.cjs\`. Its endpoints:

- \`POST /api/lead\`: adult-authorized inquiries, **required message**, optional chat excerpt, optional one-time text opt-in, owner notification and visitor acknowledgment. No provider acceptance means **no success confirmation**. Externally accepted messages can still fail after provider acceptance; configure delivery monitoring in production.
- \`POST /api/handoff\`: same as \`/api/lead\` with handoff source recorded; must be triggered only with explicit consent.
- \`POST /webhooks/resend/inbound\`: verifies signed \`email.received\` events, fetches the received email by ID, sends staff notification, optionally replies with short AI-assisted information and an automated receipt.
- \`POST /webhooks/twilio/sms\`: validates the Twilio signature, notifies staff, optionally sends a brief AI-assisted text via TwiML within a bounded timeout, then awaits human follow-up. Handles STOP/HELP.
- \`GET /api/owner/inquiries\` and \`POST /api/owner/resolve\`: bearer-authenticated API-only access to the last 50 tickets and a basic human-takeover flag; only available with durable storage. This is **not** yet a secure staff login/UI.
- \`GET /health\`: non-secret booleans \`aiConfigured\`, \`leadsConfigured\`, \`smsConfigured\`, \`inboxConfigured\`, \`inboundEmailConfigured\`, \`inboundSmsConfigured\`, \`ownerAlertsConfigured\`.

**Live observation at implementation:** Latest Render boot logs on October 19, 2026 printed \`AI off, leads off\`. Website and backend deployments succeeding **does not** mean real AI answers, emails, or SMS have been activated. Need actual account-owner credentials, domain ownership, sender/recipient authorization, and a test end-to-end. Never enter credentials into website content, GitHub, or chat.

### Private Render service configuration (only required for enabled features)

| Variable(s) | Function |
| --- | --- |
| \`CLOUDFLARE_ACCOUNT_ID\`, \`CLOUDFLARE_AI_TOKEN\` OR \`OPENAI_API_KEY\` | Server-only live AI; Cloudflare option uses Workers AI REST and has a free daily allocation. |
| \`RESEND_API_KEY\`, \`LEAD_FROM_EMAIL\`, \`LEAD_TO_EMAIL\` | A verified business-owned sender and authorized owner inbox; owner lead alerts plus acknowledgment emails. |
| \`RESEND_WEBHOOK_SECRET\`, \`RESEND_INBOUND_ADDRESS\` | Signed inbound email processing. Configure Resend \`email.received\` webhook to \`https://dance-manager-next-ai-v7.onrender.com/webhooks/resend/inbound\`. |
| \`TWILIO_ACCOUNT_SID\`, \`TWILIO_AUTH_TOKEN\`, \`TWILIO_FROM_NUMBER\`, \`OWNER_MOBILE\` | Optional SMS owner notification and customer one-time acknowledgment. Configure a registered/approved sender and texting rules. |
| \`PUBLIC_API_BASE\` | Exactly \`https://dance-manager-next-ai-v7.onrender.com\` for Twilio signature validation. Configure the inbound SMS webhook on the owned Twilio number at \`.../webhooks/twilio/sms\`. |
| \`UPSTASH_REDIS_REST_URL\`, \`UPSTASH_REDIS_REST_TOKEN\` | Optional private ticket persistence (30-day records). If not configured, **no durable queue**. |
| \`CONVERSATION_HMAC_SECRET\` | Private random secret; enables short email/phone-matched conversation context with the Upstash credentials. |
| \`ADMIN_API_TOKEN\` | Strong private bearer token needed to list or resolve tickets via backend API; not to be placed in the browser demo. |
| \`ALLOWED_ORIGINS\` | Comma-separated exact origins. Include approved Render staging origins and/or GitHub Pages. |

The role selector on the studio demonstration is **not authorization**. No real student records belong in that preview. A production site needs authenticated studio staff, guardian privacy controls, verified domain, production legal notices, audit logs, queue retry handling, provider delivery status, escalation routing and message consent. Do not assume 24/7 service availability or any guaranteed human response time from a staging server. Inbound emails and SMS must be tested end-to-end and monitored before launch.

### Test plan

1. Verify \`/health\` shows the expected channel booleans after credential setup; inspect Render boot logs.
2. Test short general questions in the website AI widget, with strict source-grounded navigation.
3. Submit an adult opt-in inquiry with an owner-authorized test email; confirm receipt in the owner inbox and the visitor inbox before announcing email capture is live.
4. For texting, first use a provider-approved test number. Verify owner alert, STOP, HELP, consent, inbound webhook validation and the default fallback if AI is slow.
5. For inbox memory, use a private ticket test, then mark it resolved through an authenticated admin API call and verify automated responses stop. Do not expose the admin bearer token on a public website.
