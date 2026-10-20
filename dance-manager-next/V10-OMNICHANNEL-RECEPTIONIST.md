# Dance Manager Next — V10 omnichannel AI receptionist requirements

Status: design / implementation specification. No live integrations are activated by this file.
Target branch: dance-manager-next-preview. Never modify the original production Dance Manager.

## Purpose
Provide a fast, courteous 24/7 front desk for inbound website chat, email, and SMS. Automatically acknowledge each new inquiry, notify the studio owner, assist with verified information, and hand off issues that need a human. Keep the premium V3 marketing design, dancer graphics, and mobile experience intact.

## Required message flow
1. Receive an authenticated/provider-verified inbound event from the website, Cloudflare Email Service, or an SMS provider such as Twilio. Reject unsolicited spoofed webhook requests.
2. Deduplicate events by channel provider ID, ticket/thread ID, and sender; prevent self-reply loops and mailer-daemon/autoresponder loops.
3. Persist receipt, minimal sender contact information, and thread status into secured storage (planned Cloudflare D1); protect staff endpoints via real authentication.
4. Immediately acknowledge new HUMAN-originated messages with a fixed, honest template that does not wait for an AI inference. For SMS, comply with opt-out, inbound help, consent and approved messaging routes. Only send one initial auto-ack per fresh conversation; avoid a repeated generic acknowledgment on every reply.
5. Notify the owner through configured email and optionally SMS/push, with channel, contact, message summary, timestamp, action-needed flag, and safe link to secure staff thread. Alert on new actionable inquiries; group routine follow-ups to avoid notification spam.
6. Generate an optional helpful AI reply from approved, studio-specific FAQ and live authoritative information. Be transparent the responder is automated. Never invent studio pricing, class places, booking confirmations, registration status or response-time SLAs.
7. If the AI cannot reliably help, route to a human queue. Visitor receives: "I've shared your message with our team. Someone will respond as soon as they're available. I can still help with general questions in the meantime."
8. After a staff member claims a conversation, stop unsolicited AI responses. Preserve owner-readable history and support staff replies in the original channel.
9. Record outcomes separately: received, acknowledged, owner-alert accepted, human-needed, delivery failed, closed; report failed deliveries instead of implying success.
10. Website can continue its guided demo when providers are unconfigured, but must never claim an email/SMS was delivered.

## Default wording
"Thanks for contacting Dance Manager. I'm the automated assistant and I've received your message. I can help with general questions now. I've also alerted our team; if a person is needed, someone will reply as soon as they're available. What would you like help with?"

## Targets (goals, not guarantees)
- Acknowledge via provider within seconds of receipt; do not wait for Workers AI.
- Studio-owner notification queued immediately; provider transit and delivery can vary.
- Automated human handoff and after-hours handling always available while backend is online.
- AI response can follow separately; if a model is delayed, the acknowledgment remains useful.

## Cloudflare integration notes
- Cloudflare Workers AI: studio FAQ assistant, only after deterministic acknowledgment; honor daily budget and rate limits.
- Cloudflare Email Service: use Workers email() route, message.reply() for qualifying incoming email, and outbound send_email/verified domain for staff alerts. Inbound auto-replies may fail DMARC checks; record that failure and retain the human ticket.
- Cloudflare D1: tickets, messages, delivery attempts, deduplication ids, and audit timestamps.
- SMS: a provider such as Twilio is separate from Workers AI; configure signed incoming webhook, compliant approved SMS senders and STOP/HELP/START handling. Do not send marketing or unsolicited messages without appropriate permission.
- Website: retain current /health, /api/chat, /api/lead semantics or coordinate a versioned API migration to avoid breaking V9.
- Child safety/privacy: receive adult guardian data where possible. Do not enter actual student/minor records in public preview. Use role-based staff login, access logs, limited retention, and minimal PII.
- Verify email DNS, sender reputation, rate limits, billing and actual send/receive before enabling live toggles.
- Do not embed API credentials in frontend JavaScript or GitHub.

## Acceptance tests before enabling live
- One inbound email receives one threaded ack and creates one ticket.
- One inbound SMS receives one ack, creates ticket, and complies with opt-outs.
- Studio owner is alerted once per new actionable ticket; further replies attach to the existing thread.
- AI answers routine approved questions; unknowns escalate honestly.
- Duplicate/replayed webhooks do not cause duplicate messages.
- Bot/self-messages do not trigger auto-reply loops.
- Staff takeover stops AI follow-up.
- Broken email/SMS provider does not display "sent"; retry/failure logged.
- Mobile owner view shows unread, urgent and awaiting-human tickets.
- Premium V3 homepage/competition graphics are restored and visually smoke-tested on an iPhone.
