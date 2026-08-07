# Event Lifecycle Guide

## Purpose

Explains how club events work on ClubConnect: creation, registration, multi-session structure, check-in/attendance, volunteer assignments, and external participants. Serves event discovery, registration, attendance, and process questions.

## Overview

An event is created and run by a club. Users register for events, are checked in via a unique QR token at attendance time, and events may include multiple sessions, assigned volunteers, and non-member external participants.

## Definitions

- **Event (`events`)**: a club-run event with a title, venue, start/end time, optional registration deadline, optional capacity, and a status.
- **Event session (`event_sessions`)**: an individual agenda item within a multi-part event, ordered by `session_order`.
- **Registration (`event_registrations`)**: a user's record of intent to attend a specific event.
- **Attendance record (`attendance_records`)**: confirmation that a registered user actually checked in at the event.
- **Volunteer assignment (`volunteer_assignments`)**: a task assigned to a club member (via their membership) to help run the event.
- **External participant (`external_participants`)**: a non-member attendee such as a guest speaker, another university's student, or a competition participant.

## Event Creation

A club creates an event with a title, description, venue, start and end time, and optionally a registration deadline and capacity. The event's end time can never be earlier than its start time. An event can be marked public (`is_public`) to control visibility, and can be marked as requiring external-participant registration if it involves attendees from outside the club's own membership.

## Registering for an Event

1. Student finds an event via search, browsing, or a recommendation.
2. Student registers before the registration deadline (if one is set) and before capacity (if set) is reached.
3. A registration record is created with status "registered" and a unique QR code token generated for check-in.
4. The student can view their registration under their event history at any time.

A user can register for a given event only once — a second registration attempt for the same event does not create a separate row.

## Registration Status Values

- **Registered** — an active registration; the user intends to attend.
- **Waitlisted** — the user registered after capacity was reached and is on hold pending an opening.
- **Cancelled** — the user (or the system) cancelled the registration; it no longer counts as active intent to attend.

## Multi-Session Events

Some events consist of multiple sessions (e.g. a conference with several talks). Each session has its own title, venue, and start/end time, and sessions are ordered within the parent event by `session_order`. Sessions belong to one parent event and are not independently registerable — registration happens at the event level, not per session.

## Check-In and Attendance

Attendance is recorded separately from registration. A registered user is checked in at the event, typically by scanning their unique QR code token, producing an attendance record with a `checked_in_at` timestamp and, optionally, who recorded the check-in. A user can have only one attendance record per event — check-in is a single confirmed occurrence, not a running log.

Registration and attendance are tracked independently: a user can be registered without ever being checked in (a no-show), and in some flows may be recorded as attending an event tied to a club they are not a formal member of.

## Volunteer Assignments

A club can assign tasks to its own members to help run an event — for example, registration-desk duty or logistics support. A volunteer assignment is tied to the member's club membership (not just their bare user account), links to a specific event, records who assigned the task, and includes a task description and optional due time. Assignment status follows: **assigned → in_progress → completed**, or **missed** if the task was not carried out.

## External Participants

An event that involves non-member attendees — a guest speaker, a student from another university, or a competition participant — records them as external participants rather than through the regular registration flow. An external participant may optionally be linked to an existing platform user account, or may be a fully external individual with no account at all. `participant_type` distinguishes the kind of external participant (other-university student, guest speaker, competition participant, etc.).

## Frequently Asked Questions

**Can I register for an event more than once?**
No, a user can register for a given event only once; the platform does not create duplicate registrations.

**What happens if an event reaches capacity?**
New registrations after capacity is reached are marked "Waitlisted" rather than "Registered," pending an opening.

**Is attendance automatically recorded when I register?**
No. Registration and attendance are separate steps — attendance is only recorded when you're actually checked in at the event, generally via your unique QR code token.

**Can I register for one session of a multi-session event only?**
No, registration is at the event level. Individual sessions are agenda items within the event, not separately registerable units.

**Do I need to be a club member to attend that club's event?**
Not necessarily — many events are open for registration to any eligible user, and non-members can also be recorded as external participants where applicable.

**What does a "missed" volunteer assignment mean?**
It means the assigned task was not carried out, as opposed to "completed."

## Common Mistakes

- Assuming registering for an event automatically means you're marked as having attended — attendance requires a separate check-in.
- Trying to register separately for each session of a multi-session event instead of registering once at the event level.
- Assuming a cancelled registration can simply be "reactivated" — a new registration is generally needed instead.

## Edge Cases

- An event with no capacity set has no waitlisting mechanism — all registrations remain "Registered."
- A user can be recorded as attending (via `attendance_records`) an event whose hosting club they are not a formal member of, since attendance is tracked independently of club membership.
- A volunteer assignment always references a club membership, so only current club members (not arbitrary platform users) can be assigned volunteer tasks for that club's events.

## Best Practices

- Register early for events with a set capacity to avoid being waitlisted.
- Check the registration deadline before assuming you can register at any time up to the event start.
- Club organizers should set clear task descriptions and due times on volunteer assignments to avoid ambiguity about what's expected.

## Important Notes

- Registration and attendance are two distinct records; neither implies the other automatically.
- Multi-session structure is for agenda organization only — registration and capacity apply at the event level.
- External participants may or may not have a linked platform account.

---

## Metadata

**Primary intents served:** Event Discovery, Event Registration, Attendance/Check-In Questions, Volunteer Assignment Questions, External Participant Questions

**Related SQL tables:** `events`, `event_sessions`, `event_registrations`, `attendance_records`, `volunteer_assignments`, `external_participants`

**Related system documents:** `assistant_conversation_behavior.md`, `dashboard_redundancy_map.md`, `recommendation_logic_playbook.md`

**Related RAG documents:** `platform_getting_started.md`, `membership_process_guide.md`

**Keywords:** event registration, register for event, capacity, waitlisted, cancelled registration, check-in, QR code, attendance record, multi-session event, event session, session_order, volunteer assignment, assigned, in_progress, completed, missed, external participant, guest speaker, registration deadline
