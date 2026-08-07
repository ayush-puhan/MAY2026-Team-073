# Platform Getting Started

## Purpose

Explains what ClubConnect is, how a new or existing user gets oriented, what platform roles exist, how account verification works, where core features live, and what each role can do. Serves onboarding, navigation, account, and role-capability questions.

## Overview

ClubConnect is a university club management platform. It lets students discover and join clubs, register for and attend events, track reward points, raise support requests, and lets club officers, faculty advisors, and administrators manage clubs, approvals, and oversight from the same platform.

Every account belongs to one university tenant and authenticates with either a password or Google sign-in.

## Platform Roles

ClubConnect has two separate layers of role:

- **Platform role** (`users.role`): the account's permission tier across the whole platform. Values are student, faculty advisor, student affairs office, dean of student welfare, and system admin.
- **Club-scoped role** (`club_memberships.role_in_club`): a role held only within one specific club, such as member, treasurer, or president. A student's platform role stays "student" even while holding an officer-level club role.

These two role concepts are independent. A person's platform role does not change when they become a club officer.

## Signing In

An account signs in with either an email/password combination or Google sign-in (OAuth). The sign-in method is fixed per account at creation and does not change afterward. Each successful sign-in issues a session that stays valid until it expires or the user logs out.

## Institutional Email Verification

Students can add an institutional email address to their profile. Verification confirms that address belongs to a recognized university domain. An unverified institutional email does not block using the platform, but some university-specific features may depend on verification. Verification status is separate from whether the account itself is active.

## First-Time Orientation

A new user's first steps on ClubConnect are:

1. Complete the profile (name, and for students, academic program details).
2. Optionally add and verify an institutional email.
3. Browse or search clubs by category, name, or keyword.
4. Apply to join clubs of interest, or ask the assistant for personalized recommendations.
5. Explore upcoming events open to the university.

New users have no membership or activity history yet — recommendations and suggestions in this state rely on directly stated interests rather than past behavior.

## Where to Find Things

General navigation, by feature area:

| Feature | Where it lives |
|---|---|
| Club search and discovery | Explore/Search page |
| My memberships | Memberships tab |
| My applications | Applications tab |
| Events open to me | Events tab |
| My registrations and attendance | Events / My Events tab |
| Reward points and history | Rewards tab |
| Announcements | Announcement Center |
| Support requests | Support tab |
| Emergency reporting | Emergency Report action (always visible) |
| Profile and account settings | Profile / Account settings |
| Club management tools (officers only) | Club Management area |
| Approval queues (faculty/admin only) | Faculty Dashboard / Admin Dashboard |

## Role Capabilities: Student

A student can browse and search clubs and events, apply to join clubs, register for events, view their own membership and application status, track attendance and reward points, raise support tickets, and file emergency reports. A student cannot approve applications, manage a club's budget, or view other students' individual data.

## Role Capabilities: Club Officer (role_in_club)

A club member holding an officer-level `role_in_club` (such as president or treasurer) additionally manages that specific club: reviewing join applications, organizing events, assigning volunteer tasks, and — for a treasurer — submitting and tracking budgets and expenses for that club. Officer capabilities apply only to the club(s) where the person holds that role, not platform-wide.

## Role Capabilities: Faculty Advisor

A faculty advisor oversees the clubs they are assigned to advise: reviewing pending event or expense approvals, viewing engagement trends for those clubs, and answering governance questions for their advised clubs. A faculty advisor does not have platform-wide administrative access outside their advised clubs.

## Role Capabilities: Student Affairs Office / Dean of Student Welfare / System Admin

These platform-wide administrative roles review and approve club creation proposals, oversee platform-wide aggregate activity, and handle governance at the university level. Individual students' private data (applications, tickets, financial records) is not exposed to these roles as raw individual records outside authorized review contexts — administrative oversight here works at an aggregate or proposal level, not a per-student browsing level.

## Profile and Account Settings

A user's profile includes name, contact phone, profile photo, and accessibility preferences (including a color-blind display mode). Students additionally have an academic profile: program, academic year, semester, batch, and section. Profile fields can be updated at any time from account settings; changing them does not affect membership, application, or event history.

## Frequently Asked Questions

**What is ClubConnect?**
A university platform for discovering clubs, joining them, attending events, and tracking related activity, with tools for club officers, faculty advisors, and administrators to manage and oversee that activity.

**Do I need to verify my institutional email to use ClubConnect?**
No. Verification is optional and only affects features tied specifically to confirmed institutional status; general platform use does not require it.

**Can my platform role and my club role be different?**
Yes. Platform role (student, faculty advisor, etc.) and club-scoped role (member, treasurer, president, etc.) are tracked separately. A student can simultaneously be a club president.

**How do I switch between password and Google sign-in?**
The sign-in method is fixed to how the account was created; it is not something a user changes later.

**Can I see another student's application, ticket, or financial data?**
No, individual data belonging to another user is never exposed regardless of platform role, except through explicitly authorized aggregate or review contexts.

## Common Mistakes

- Assuming a club officer role changes the platform-level role shown on the account — it does not.
- Assuming institutional email verification is required before any platform feature can be used.
- Looking for administrative individual-student lookups on admin roles — these roles work at proposal/aggregate level, not individual browsing.

## Edge Cases

- A user can belong to more than one club simultaneously, each with its own independent `role_in_club`.
- A faculty advisor with no clubs currently assigned has no pending approvals to review; this is a normal empty state, not an error.
- A brand-new account has no interests, memberships, or history recorded yet; this is expected and does not indicate a broken profile.

## Best Practices

- Add and verify an institutional email early to ensure eligibility for university-specific features.
- Keep accessibility preferences (including color-blind mode) updated for the best display experience.
- Officers should be aware that their officer permissions are scoped only to the specific club(s) where they hold that role.

## Important Notes

- Platform role and club-scoped role are always tracked and reasoned about separately.
- Verification affects eligibility for certain features; it does not gate general platform access.
- Administrative roles operate on aggregates and proposals, not individual student records, in ordinary use.

---

## Metadata

**Primary intents served:** Getting Started, Navigation, Role Capabilities Q&A, Profile & Account

**Related SQL tables:** `users`, `student_profiles`, `auth_sessions`, `departments`, `programs`

**Related system documents:** `assistant_conversation_behavior.md`, `dashboard_redundancy_map.md`

**Related RAG documents:** `membership_process_guide.md`, `event_lifecycle_guide.md`

**Keywords:** onboarding, getting started, sign in, sign up, Google sign-in, institutional email, verification, platform role, club role, role_in_club, navigation, where do I find, profile, account settings, accessibility, color-blind mode, faculty advisor, student affairs office, dean of student welfare, system admin, club officer, president, treasurer
