# Financial Operations Guide

## Purpose

Explains how club-level financial operations work on ClubConnect: budgets, expense claims, and the embedded expense-approval process. Serves treasurer and faculty financial-process questions. This document is role-filtered to treasurer and faculty contexts — general students do not need this content.

## Overview

Club finances are organized around budgets, each covering a defined period, against which individual expenses are claimed. Each expense carries its own embedded approval outcome rather than relying on a separate approvals table — approval status, approver, approval date, and remarks all live directly on the expense record.

## Definitions

- **Budget (`budgets`)**: a club's planned allocation of funds for a defined period, with a title and an allocated amount.
- **Expense (`expenses`)**: an itemized cost claimed against a specific budget, with its own embedded approval outcome.
- **Approval status**: the outcome recorded directly on an expense row (rather than in a separate table), reflecting whether it has been approved, rejected, or is still pending.
- **Receipt**: an optional supporting document attached to an expense.

## Creating a Budget

1. A club treasurer (or authorized officer) creates a budget: a title, a period (start and end), and an allocated amount.
2. The budget period must be chronologically valid — its end cannot precede its start.
3. The allocated amount cannot be negative.
4. The budget is created with status "draft" and moves through submission and review before becoming active for the period it covers.

## Budget Status Lifecycle

Budget status progresses through: draft → submitted → approved (or rejected) → closed once the period ends or the budget is no longer active. A rejected budget does not have expenses claimed against it in an approved sense; a closed budget represents a completed, no-longer-active planning period.

## Submitting an Expense

1. A club member with the appropriate role submits an expense against an existing budget: a description, an amount, and optionally a category and a receipt document.
2. The claimed amount must be strictly positive.
3. The expense is created with its own status and an initial approval status (e.g. pending).
4. A reviewer evaluates the expense and records the approval outcome directly on that expense row: approval status, who approved it, when, and any remarks.

## Expense Approval — Embedded, Not a Separate Table

Unlike some workflows in ClubConnect, expense approval is not tracked in a separate approvals table. The approval status, the approver, the approval date, and any approval remarks are all fields directly on the `expenses` row itself. This is a deliberate design choice: an expense's current approval state is always read directly from that one row, not joined from elsewhere.

## Frequently Asked Questions

**Can an expense exist without being tied to a budget?**
No, every expense is claimed against a specific existing budget; there is no standalone expense record.

**Is expense approval tracked in a separate table from the expense itself?**
No — approval status, approver, approval date, and remarks are all embedded directly on the expense record.

**Can an expense amount be zero or negative?**
No, the claimed amount must be strictly greater than zero.

**Can a budget's end date be before its start date?**
No, a budget's period must be chronologically valid, with the end at or after the start.

**Is a receipt required to submit an expense?**
No, a receipt document is optional on an expense claim.

**What happens once a budget's period ends?**
It's expected to move toward a "closed" status, representing a completed planning period no longer open to new activity.

## Common Mistakes

- Looking for a separate "expense approvals" table — approval fields live directly on the expense row.
- Assuming an expense can be submitted without referencing an existing budget.
- Assuming a rejected budget can still have approved expenses claimed under it.

## Edge Cases

- A budget can be closed even if not fully spent; closure reflects the end of the planning period, not necessarily full utilization.
- An expense can be submitted with no receipt attached, though this may affect how a reviewer evaluates the approval.
- A negative or zero-amount expense submission is rejected outright by the underlying data constraint, not merely discouraged.

## Best Practices

- Ensure a budget is fully approved before relying on it to plan expense submissions against it.
- Attach a receipt to expense claims where possible to support faster or clearer approval review.
- Treasurers should track budget period end dates to anticipate when a budget will move toward closure.

## Important Notes

- Expense approval fields are embedded directly on the expense record — there is no separate expense-approvals table to query or reference.
- Budgets and expenses both enforce strict validation: chronologically valid periods, non-negative allocations, and strictly positive expense amounts.
- This guide covers club-level financial process only; individual live figures (actual budget balances, specific expense amounts) come from the user's own SQL-backed financial context, not from this document.

---

## Metadata

**Primary intents served:** Financial Operations Process (Budget Creation, Expense Submission, Expense Approval)

**Related SQL tables:** `budgets`, `expenses`, `documents`

**Related system documents:** `assistant_conversation_behavior.md` (Section 8, SQL vs RAG Usage — financial content is role-filtered to treasurer/faculty), `dashboard_redundancy_map.md`

**Related RAG documents:** `club_creation_governance_guide.md`

**Keywords:** budget, expense, treasurer, financial operations, allocated amount, budget period, expense approval, approval status, receipt, draft, submitted, approved, rejected, closed, embedded approval

**Chunking Notes:**
- Suggested Chunk Boundaries: split at each H2 heading (Overview, Definitions, Creating a Budget, Budget Status Lifecycle, Submitting an Expense, Expense Approval — Embedded Not a Separate Table, FAQ entries individually, Common Mistakes, Edge Cases, Best Practices, Important Notes).
- Keep "Expense Approval — Embedded, Not a Separate Table" as an isolated chunk, since it corrects a schema assumption an LLM might otherwise make (a separate approvals table) and should surface intact whenever expense-approval questions are retrieved.
