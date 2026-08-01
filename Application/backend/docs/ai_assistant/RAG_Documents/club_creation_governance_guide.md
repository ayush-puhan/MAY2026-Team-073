# Club Creation & Governance Guide

## Purpose

Explains how a new club gets created on ClubConnect, how the proposal review process works, and how club-level status (active/suspended/archived) is governed afterward. Serves club creation, proposal status, and club governance questions. This document covers proposing and governing a club itself — for joining an existing club, see the membership process guide.

## Overview

A new club does not exist as a `clubs` row until a proposal has been reviewed and approved. The proposal is tracked separately from the resulting club, preserving the review trail even if the request is rejected.

## Definitions

- **Club creation request (`club_creation_requests`)**: a student-submitted proposal for a new club, reviewed by staff before an actual club record is created.
- **Resulting club**: the `clubs` row created only upon approval of a request; this link is empty while a request is pending or if it's rejected.
- **Club status**: the lifecycle state of an existing club — pending, active, suspended, or archived.
- **Faculty advisor**: a user optionally assigned to a club to provide oversight; a club can exist with no faculty advisor assigned.

## Proposing a New Club

1. A student submits a proposal: proposed name, proposed category, and a description of the club's purpose.
2. The request is created with status "submitted."
3. Staff move the request into "under_review."
4. A reviewer records a decision: approved or rejected, with optional review comments.
5. If approved, a new `clubs` row is created and linked back to the request as its resulting club.
6. If rejected, no club record is created; the request remains as a historical record with the review comments explaining the outcome.

## Proposal Status Values

- **Submitted** — proposal received, not yet reviewed.
- **Under review** — a reviewer is actively evaluating the proposal.
- **Approved** — proposal accepted; a corresponding club record now exists.
- **Rejected** — proposal declined; no club record is created.

## Club Lifecycle Status

Once a club exists, it carries its own separate status distinct from the creation request that produced it:

- **Pending** — club record exists but is not yet fully active (e.g. awaiting final setup).
- **Active** — club is operating normally and open to activity such as membership applications and events.
- **Suspended** — club's normal activity is paused, typically pending a governance review.
- **Archived** — club is no longer active; historical data is retained via soft-delete rather than removed.

A club's status is independent of any single creation request — status changes over a club's lifetime (e.g. active to suspended) are separate governance actions, not new creation requests.

## Frequently Asked Questions

**Does submitting a club proposal create the club immediately?**
No. A `clubs` row is only created once the proposal is reviewed and approved.

**What happens to my proposal if it's rejected?**
It's marked "rejected" with optional review comments explaining the decision; no club record is created, and the request remains as a historical record.

**Can I resubmit after a rejected proposal?**
Yes, submitting a new proposal is the path to try again; a rejected request itself is not reopened or edited into a new submission.

**Does every club have a faculty advisor?**
Not necessarily — a club can exist with no faculty advisor currently assigned.

**What does "archived" mean for a club?**
The club is no longer active; its record and history are preserved via soft-delete rather than deleted outright.

## Common Mistakes

- Assuming a submitted proposal already functions as a club before approval.
- Confusing proposal status (submitted/under_review/approved/rejected) with club lifecycle status (pending/active/suspended/archived) — these are two separate status fields on two separate records.
- Assuming a suspended or archived club's history is deleted rather than retained.

## Edge Cases

- A club can be suspended even while otherwise fully set up, pending a governance review unrelated to the original creation request.
- An archived club's data is retained (soft-deleted), not physically removed, preserving historical records such as past memberships and events.
- A rejected proposal does not block a future new proposal with a similar or identical name, though naming conflicts may be a factor a reviewer considers.

## Best Practices

- Write a clear, complete proposal description, since this is the primary information a reviewer uses to evaluate the request.
- Check proposal status before assuming a rejection was final without reading the review comments.
- Understand that governance actions on an existing club (suspension, archiving) are separate from the original creation approval.

## Important Notes

- The creation request and the resulting club are separate records; only approval produces a club row.
- Club lifecycle status is tracked independently of the original creation request's status.
- Archiving uses soft-delete, preserving historical data rather than deleting it.

---

## Metadata

**Primary intents served:** Club Creation Proposal, Proposal Status, Club Governance/Lifecycle Status Q&A

**Related SQL tables:** `club_creation_requests`, `clubs`

**Related system documents:** `assistant_conversation_behavior.md`, `dashboard_redundancy_map.md`

**Related RAG documents:** `platform_getting_started.md`, `membership_process_guide.md`

**Keywords:** club creation, propose a club, club proposal, submitted, under review, approved, rejected, resulting club, club status, active, suspended, archived, soft-delete, faculty advisor, governance

**Chunking Notes:**
- Suggested Chunk Boundaries: split at each H2 heading (Overview, Definitions, Proposing a New Club, Proposal Status Values, Club Lifecycle Status, FAQ entries individually, Common Mistakes, Edge Cases, Best Practices, Important Notes).
- Keep "Proposal Status Values" and "Club Lifecycle Status" as separate chunks — they describe two distinct status fields and should not be merged during retrieval.
