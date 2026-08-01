# Helpdesk & Support Guide

## Purpose

Explains how support tickets and emergency reports work on ClubConnect: raising a ticket, the response thread, resolution, and the separate emergency-reporting path. Serves support-ticket and emergency-reporting process questions.

## Overview

ClubConnect has two distinct channels for raising an issue: support tickets, for general platform, club, or account issues, and emergency reports, for harassment, medical, accessibility, or other urgent safety concerns. These are separate systems with separate workflows and are never treated as interchangeable.

## Definitions

- **Support ticket (`support_tickets`)**: a helpdesk request raised by a user, optionally scoped to a specific club or university.
- **Ticket response (`ticket_responses`)**: a reply on a ticket's message thread, potentially from the user or an assigned agent.
- **Resolution response**: the specific ticket response flagged as the one that closed the ticket.
- **Emergency report (`emergency_reports`)**: a report of harassment, a medical situation, a wheelchair-assistance need, or another urgent concern, optionally tied to a specific event, and optionally submitted anonymously.

## Raising a Support Ticket

1. User submits a ticket: a title, a description, a ticket type, and a priority level.
2. The ticket is optionally scoped to a specific club or university if relevant.
3. The ticket is created with status "open" (or equivalent starting status) and may be assigned to a support agent.
4. The user or the assigned agent can add responses to the ticket's thread.
5. When the issue is resolved, a response is flagged as the resolution, and the ticket's status is updated to reflect closure.
6. The user may optionally leave a resolution rating after closure.

## Ticket Status Progression

A ticket generally moves through: submission → assignment (optional) → active thread of responses → resolution → closure. The exact set of status values reflects this progression; a ticket can also be marked to flag moderation concerns if its content is found to be offensive.

## Ticket Response Thread

Responses on a ticket form a running thread, similar to a conversation. Any response can be added by either the user or the assigned agent. Exactly one response is designated the resolution — the one that closed the ticket — distinguishing it from ordinary back-and-forth replies.

## Emergency Reporting — A Separate Path

Emergency reports are never handled the same way as ordinary support tickets. An emergency report can be submitted anonymously (no reporter identity required), can optionally reference a specific event it occurred at, and progresses through: reported → acknowledged → in_progress → resolved. Emergency content is never resolved conversationally — it is always routed for direct human handling, regardless of how it is phrased or requested.

## Frequently Asked Questions

**What's the difference between a support ticket and an emergency report?**
A support ticket covers general platform, club, or account issues handled through a normal reply thread. An emergency report covers harassment, medical, accessibility, or other urgent safety concerns and is always routed for direct human handling rather than conversational resolution.

**Can I submit an emergency report anonymously?**
Yes, the reporter identity on an emergency report is optional, supporting anonymous submission.

**Can a support ticket be tied to a specific club?**
Yes, a ticket can optionally be scoped to a specific club, or left unscoped for a general platform issue.

**How do I know a ticket has been resolved?**
One response in the ticket's thread is flagged as the resolution; the ticket's status also reflects closure at that point.

**Can I rate how my ticket was resolved?**
Yes, a resolution rating can optionally be left after a ticket is closed.

**Can an emergency report be tied to an event?**
Yes, optionally — an emergency report may reference the specific event where the situation occurred, but this link is not required.

## Common Mistakes

- Raising an emergency situation as a general support ticket rather than through the dedicated emergency-report path.
- Assuming every reply on a ticket thread counts as its resolution — only the response specifically flagged as such does.
- Assuming an emergency report requires identifying yourself — anonymous submission is supported.

## Edge Cases

- A ticket flagged as offensive is a moderation concern distinct from its ordinary open/resolved progression.
- An emergency report with no reporter identity (anonymous) can still be acknowledged and resolved by a handler.
- A ticket with no club or university scoping is treated as a general platform-level issue.

## Best Practices

- Use the emergency-report path immediately for any harassment, medical, or safety concern rather than a general ticket.
- Provide a clear title and description when raising a ticket, since this is the primary information an agent sees first.
- Leave a resolution rating after closure to help improve support quality.

## Important Notes

- Support tickets and emergency reports are always treated as separate systems with separate workflows — never as interchangeable channels.
- Emergency reports are never resolved through conversational assistance; they are always routed to a human handler.
- Anonymous emergency reporting is explicitly supported by the data model.

---

## Metadata

**Primary intents served:** Support Ticket Status, Support Ticket Process, Emergency Reporting

**Related SQL tables:** `support_tickets`, `ticket_responses`, `emergency_reports`

**Related system documents:** `assistant_conversation_behavior.md` (Section 6, Escalation Rules), `dashboard_redundancy_map.md`

**Related RAG documents:** `platform_getting_started.md`, `event_lifecycle_guide.md`

**Keywords:** support ticket, helpdesk, ticket status, ticket response, resolution, resolution rating, priority, ticket type, emergency report, harassment, medical, wheelchair assistance, anonymous report, escalation

**Chunking Notes:**
- Suggested Chunk Boundaries: split at each H2 heading (Overview, Definitions, Raising a Support Ticket, Ticket Status Progression, Ticket Response Thread, Emergency Reporting — A Separate Path, FAQ entries individually, Common Mistakes, Edge Cases, Best Practices, Important Notes).
- Keep "Emergency Reporting — A Separate Path" as its own standalone retrievable chunk, since it is the section most likely to be retrieved under time pressure and should not be diluted by surrounding ticket-process content.
