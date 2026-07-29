# Membership Process Guide

## Purpose

Explains how joining a club works on ClubConnect: applying, review, status outcomes, club-scoped roles, committees, and leaving a club. Serves membership application, status, and process questions.

## Overview

Club membership on ClubConnect is a two-record process: a student submits an application, and a review decision produces (or does not produce) an actual membership record. The application preserves the review history; the membership record is the single source of truth for whether someone is currently in a club and what role they hold there.

## Definitions

- **Application (`club_join_applications`)**: a student's submitted request to join a specific club, including motivation, relevant skills, prior experience, portfolio link, resume, and weekly availability.
- **Membership (`club_memberships`)**: the actual record of a user belonging to a club, including their status and their club-scoped role.
- **Club-scoped role (`role_in_club`)**: the member's role within that specific club — for example member, treasurer, or president. Distinct from the user's platform-level role.
- **Committee**: a named sub-group within a club (e.g. "Events Committee") that a member can additionally be assigned to.
- **Withdrawn**: a status meaning the person was previously an approved member but has since left the club.

## One Membership Per Club

A user can hold at most one membership record per club — a student cannot apply to or hold two separate memberships in the same club at once. A student can, however, hold independent memberships across multiple different clubs, each with its own status and role.

## Application Workflow

1. Student selects a club to apply to.
2. Student completes the application: motivation, contribution/skills, previous experience, portfolio link (optional), resume upload (optional), and weekly availability.
3. Application is submitted with status "pending" and an `applied_at` timestamp.
4. A club officer with review authority evaluates the application.
5. The officer records a decision: approved or rejected, with optional review comments.
6. If approved, a corresponding membership record is created with status "approved" and the assigned `role_in_club` (typically "member" by default).
7. If rejected, the application is marked "rejected" with an optional rejection reason; no membership record is created.

## Membership Status Lifecycle

Membership status follows this progression:

- **Pending** — application submitted, awaiting review (reflected on the application, before a membership record exists).
- **Approved** — application accepted; an active membership record now exists with an assigned club-scoped role.
- **Rejected** — application declined; no membership record is created.
- **Withdrawn** — a previously approved member has left the club; the historical membership record is retained with this status rather than deleted.

Once a membership reaches "Withdrawn," it is a terminal historical record for that membership row; a person who wants to rejoin later submits a new application.

## Club-Scoped Roles

`role_in_club` values include member and officer-level roles such as treasurer and president. Officer-level roles carry additional capabilities scoped to that specific club only, such as reviewing applications, managing events, or handling that club's finances. Holding an officer role in one club has no effect on a person's role in any other club or on their platform-level role.

## Committees

Committees are optional sub-groups within a club that an existing member can be assigned to (e.g. "Events Committee," "Outreach Committee"). Committee assignment requires an existing approved membership in the parent club — committee membership is not a substitute for or an alternative path to club membership. Committee names are unique within a club but can repeat across different clubs.

## Withdrawing From a Club

A member who wants to leave a club has their membership status changed to "Withdrawn." This preserves the historical record of their prior membership and role rather than deleting it. A withdrawn member is no longer counted as an active member of the club and loses any officer-level capabilities they held there.

## Frequently Asked Questions

**Can I apply to the same club twice at the same time?**
No — a user can have only one membership record per club, so a second simultaneous application to the same club is not a separate, independent path.

**What happens to my application if it's rejected?**
It's marked rejected, optionally with a reason. No membership record is created. You may submit a new application later if you wish to try again.

**Does becoming a club treasurer or president change my overall account role?**
No. Club-scoped roles like treasurer or president only apply within that specific club and do not change your platform-level role.

**Can I join a committee without being a club member first?**
No. Committee assignment requires an existing approved membership in that club.

**What happens if I leave a club and want to rejoin later?**
Your prior membership is marked "Withdrawn" as a historical record. Rejoining requires submitting a new application, which goes through review again.

## Common Mistakes

- Assuming an application counts as membership before it is reviewed and approved — only an approved membership record confers member status.
- Assuming committee membership can be obtained without first being an approved club member.
- Confusing "Rejected" (application declined, never a member) with "Withdrawn" (was previously an approved member, then left).

## Edge Cases

- A resume attached to an application is optional; applications can be submitted without one.
- A rejected application does not block a future new application to the same club.
- A withdrawn member's historical role and tenure remain on record even though they are no longer active.

## Best Practices

- Complete the motivation and skills fields thoughtfully, since these are the primary information reviewers see when deciding on an application.
- Check application status before submitting a duplicate application to the same club.
- Officers should record clear review comments or rejection reasons to keep the process transparent for applicants.

## Important Notes

- The application record and the membership record are separate rows; only an approved application produces a membership record.
- `role_in_club` is always club-specific and never affects the platform-level `users.role`.
- Withdrawn memberships are retained as historical records, not deleted.

---

## Metadata

**Primary intents served:** Membership Application, Application Status ("why"/"what next"), Club-Scoped Roles Q&A, Committees Q&A, Leaving a Club

**Related SQL tables:** `club_join_applications`, `club_memberships`, `committees`, `committee_memberships`, `clubs`

**Related system documents:** `assistant_conversation_behavior.md`, `dashboard_redundancy_map.md`

**Related RAG documents:** `platform_getting_started.md`, `event_lifecycle_guide.md`

**Keywords:** join a club, apply to club, membership application, application status, pending, approved, rejected, withdrawn, role_in_club, treasurer, president, member, committee, committee membership, leaving a club, rejoin, resume, motivation, review comments, rejection reason
