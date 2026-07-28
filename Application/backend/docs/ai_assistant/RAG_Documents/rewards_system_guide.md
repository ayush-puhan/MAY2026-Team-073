# Rewards System Guide

## Purpose

Explains how the ClubConnect rewards system works: earning points, the redemption process, task completion, and the store catalog. Serves rewards mechanics, balance explanation, and redemption process questions.

## Overview

Points are earned through an append-only ledger, never through an editable running total. Points can be spent through redemption requests against either a free-text reward description or, separately, catalog items in the rewards store. Points can also be earned by completing catalog-listed tasks.

## Definitions

- **Points ledger (`reward_points_ledger`)**: an append-only record of every point grant or deduction for a user, each with a reason and an optional source event.
- **Balance**: the sum of a user's ledger rows. There is no separate stored "balance" field — it is always derived by adding up ledger entries.
- **Redemption (`reward_redemptions`)**: a user's request to spend accumulated points on a reward.
- **Reward task (`reward_tasks`)**: a catalog entry describing a completable action that awards a fixed number of points.
- **Task completion (`reward_task_completions`)**: a log entry recording that a user completed a given reward task.
- **Store item (`reward_store_items`)**: a catalog entry describing something redeemable for points, with stock and per-user limits.

## How Points Are Earned

Points can be added to a user's ledger for various reasons — for example, attending an event, or completing a listed reward task. Each ledger entry records the number of points, a reason, and, if applicable, the event that generated them. Because the ledger is append-only, a full history of how a balance was built up is always preserved; points are never silently adjusted by editing a past entry.

## How Balance Is Calculated

A user's current point balance is not stored as a single number — it is calculated by summing every entry in that user's ledger. This means the balance is always a derived value reflecting complete history, not a cached figure that could drift out of sync with the underlying entries.

## Completing Reward Tasks

1. User views the catalog of active reward tasks.
2. User completes the described action for a task.
3. A task completion record is logged.
4. Points for that task are added to the user's ledger, tied to the reason described by the task.

A reward task can allow repeat completions up to a configured maximum; some tasks may additionally require the user's account to meet a verification requirement before they can be completed.

## Redeeming Points

1. User submits a redemption request, spending a chosen number of accumulated points on a reward.
2. The request is created with status "requested."
3. A reviewer evaluates and either approves, fulfills, or rejects the request.
4. If rejected, spent points are not deducted from the ledger for that request (no ledger entry is created without an approved outcome).

Redemption requests describe the reward being requested in free text; they are not required to reference a specific catalog store item, since the redemption record and the store catalog are tracked independently.

## The Rewards Store Catalog

The rewards store lists items available for redemption, each with a points cost, available stock, and a maximum number a single user may claim. Some store items may require the user's account to meet a verification requirement before they can be claimed. The store catalog is a separate reference list from individual redemption requests — browsing the store does not itself create a redemption.

## Frequently Asked Questions

**Where does my point balance come from?**
It's calculated by summing all entries in your points ledger — there's no separate editable balance field.

**Can I lose points I've already earned?**
Points are only removed through a new ledger entry recording a deduction; past entries themselves are never edited or erased.

**Can I complete the same reward task more than once?**
Some tasks allow repeat completions up to a set maximum; this depends on how that specific task is configured.

**Does redeeming points always reference a store item?**
No — a redemption request describes the reward in free text and is not required to link to a specific catalog store item.

**What happens if my redemption request is rejected?**
No points are deducted for a rejected request; your ledger and balance are unaffected.

## Common Mistakes

- Assuming your balance is a single stored number rather than a sum of ledger entries.
- Assuming a redemption request automatically corresponds to a specific store catalog item.
- Assuming a rejected redemption still deducts the requested points.

## Edge Cases

- A reward task marked as requiring verification cannot be completed by an account that hasn't met that requirement, regardless of how many times the user attempts it.
- A store item with limited stock or a per-user cap may become unavailable to a given user even if they have enough points.
- Because the ledger is append-only, correcting an erroneous point grant is done with a new offsetting entry, not by editing the original one.

## Best Practices

- Check the rewards catalog periodically, since tasks and store items are separate lists that can each change independently.
- Review your ledger history, not just your balance, if you want to understand exactly how your points were earned.

## Important Notes

- Balance is always derived, never directly stored or edited.
- Reward tasks and store items are independent catalogs; completing a task earns points, while browsing the store does not.
- Redemption requests are free-text and do not require a formal link to a store catalog item.

---

## Metadata

**Primary intents served:** Rewards Mechanics, Balance Explanation, Redemption Process, Reward Task Completion

**Related SQL tables:** `reward_points_ledger`, `reward_redemptions`, `reward_tasks`, `reward_task_completions`, `reward_store_items`

**Related system documents:** `assistant_conversation_behavior.md`, `dashboard_redundancy_map.md`

**Related RAG documents:** `platform_getting_started.md`, `event_lifecycle_guide.md`

**Keywords:** rewards, points, points ledger, balance, redemption, redeem points, reward task, task completion, reward store, store item, points cost, stock, max per user, requires verification, append-only ledger

**Chunking Notes:**
- Suggested Chunk Boundaries: split at each H2 heading (Overview, Definitions, How Points Are Earned, How Balance Is Calculated, Completing Reward Tasks, Redeeming Points, The Rewards Store Catalog, FAQ entries individually, Common Mistakes, Edge Cases, Best Practices, Important Notes).
- FAQ entries are independently retrievable question/answer pairs and should not be split mid-answer.
