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
