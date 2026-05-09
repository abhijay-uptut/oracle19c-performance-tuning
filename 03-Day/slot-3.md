# Day 3 — Slot 3

## 1:00 PM to 2:30 PM

# Concurrency, Locking and Short-Lived Performance Problems

## Slot Objective

By the end of this slot, trainees should understand:

* Difference between concurrency and locking
* Why sessions block each other
* How row-level locks work
* How to identify blocking and waiting sessions
* What deadlocks and long transactions are
* Why banking systems face concurrency issues
* How to use Oracle views for lock diagnosis
* Safe steps before killing or resolving sessions

---

# Suggested Slot Flow

| Time        | Section                         |
| ----------- | ------------------------------- |
| 1:00 - 1:10 | Concurrency vs locking          |
| 1:10 - 1:25 | Row locks, blocking, deadlocks  |
| 1:25 - 1:40 | Hot blocks, waits, short spikes |
| 1:40 - 2:10 | Lab 11: Locking simulation      |
| 2:10 - 2:25 | Diagnosis and safe resolution   |
| 2:25 - 2:30 | Summary                         |

---

# Slide 1: Slot Title

## Concurrency, Locking and Short-Lived Performance Problems

**Slide content:**

In this slot, we will learn:

* Concurrency vs locking
* Row-level locks
* Blocking sessions
* Deadlocks
* Long-running transactions
* Hot blocks and buffer busy waits
* Short-lived spikes
* Lock diagnosis views

---

## Trainer Explanation

“Until now, we focused mostly on SQL plans and optimizer behavior.

But sometimes SQL is not slow because of a bad plan.

Sometimes SQL is slow because it is waiting.

In banking systems, many users may update accounts, payments, balances, and loan records at the same time.

That creates concurrency and locking issues.”

---

# Slide 2: What is Concurrency?

## Slide content:

Concurrency means many users or sessions work at the same time.

Example:

* Multiple users doing fund transfers
* Multiple tellers updating accounts
* Batch job posting payments
* Reports reading transaction data
* API services updating payment status

---

## Trainer Explanation

“Concurrency is normal.

A banking database must support many users at the same time.

If 500 users are working, Oracle must manage all their reads and writes safely.

Concurrency is not bad by itself. The problem starts when sessions compete for the same data or same resource.”

---

# Slide 3: What is Locking?

## Slide content:

Locking protects data consistency.

When one session changes a row, Oracle locks that row until transaction ends.

Example:

```sql
UPDATE accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

The row remains locked until:

```sql
COMMIT;
```

or

```sql
ROLLBACK;
```

---

## Trainer Explanation

“Locking is Oracle’s way of protecting data.

If one session updates account 101, another session should not update the same row at the same time without control.

So Oracle locks the row until the first session commits or rolls back.

This protects correctness, but it can also make other sessions wait.”

---

# Slide 4: Concurrency vs Locking

## Slide content:

| Concept     | Meaning                                      |
| ----------- | -------------------------------------------- |
| Concurrency | Many sessions working together               |
| Locking     | Mechanism to protect changed data            |
| Blocking    | One session waits because another holds lock |
| Deadlock    | Two sessions wait for each other             |

---

## Trainer Explanation

“Concurrency is the situation.

Locking is the protection mechanism.

Blocking happens when one session is waiting because another session holds a lock.

Deadlock is more serious: two sessions are waiting for each other, and neither can continue.”

---

# Slide 5: Why Banking Apps Face Concurrency Problems

## Slide content:

Banking apps face concurrency issues because many sessions update:

* Account balances
* Payment status
* Transaction records
* Loan EMI status
* Wallet balances
* Ledger entries
* Audit records
* Settlement batches

High-risk areas:

* Fund transfer
* Payment posting
* Reversal
* End-of-day batch
* Loan collection

---

## Trainer Explanation

“Banking systems are write-heavy in critical areas.

Fund transfer updates balances.

Payment posting updates payment status.

Loan EMI collection updates loan accounts.

If many sessions try to update the same account, branch batch, or payment record, blocking can happen.”

---

# Slide 6: Row-Level Locks

## Slide content:

Oracle uses row-level locking for DML.

DML examples:

```sql
INSERT
UPDATE
DELETE
MERGE
```

Important:

* Readers usually do not block writers
* Writers can block writers
* Lock is held until commit or rollback

---

## Trainer Explanation

“Oracle locking is generally efficient because it locks rows, not the whole table for normal updates.

A SELECT usually does not block an UPDATE.

But if two sessions update the same row, the second session waits.

The lock is released only when the first session commits or rolls back.”

---

# Slide 7: Blocking Session

## Slide content:

A blocking session holds a lock.

A waiting session needs the same locked row.

Example:

```text
Session 1 updates account_id = 101
Session 1 does not commit

Session 2 updates account_id = 101
Session 2 waits
```

---

## Trainer Explanation

“This is the most common locking situation.

Session 1 updates a row and forgets to commit.

Session 2 tries to update the same row.

Session 2 is now stuck waiting.

From the user side, it looks like the application is slow or hanging.”

---

# Slide 8: Deadlocks

## Slide content:

Deadlock happens when sessions wait for each other.

Example:

```text
Session 1 locks Account A
Session 2 locks Account B

Session 1 tries to lock Account B
Session 2 tries to lock Account A
```

Result:

```text
Both sessions wait
Oracle detects deadlock
One statement fails with ORA-00060
```

---

## Trainer Explanation

“Deadlock is different from normal blocking.

In blocking, one session waits and can continue after the blocker commits.

In deadlock, two sessions wait for each other.

Oracle detects this and cancels one statement with ORA-00060.

Deadlocks usually indicate application transaction order problems.”

---

# Slide 9: Long-Running Transactions

## Slide content:

Long-running transaction means session holds locks for too long.

Common causes:

* User opens screen and does not commit
* Application waits before commit
* Batch job updates many rows
* Error handling misses rollback
* Network/API delay inside transaction

Impact:

* Blocking sessions
* Undo growth
* Poor user experience

---

## Trainer Explanation

“Long transactions are dangerous in banking systems.

If a transaction updates an account and waits for external API response before commit, locks can remain open.

Other sessions may then wait.

Good application design keeps transactions short.”

---

# Slide 10: Hot Blocks

## Slide content:

Hot block means many sessions frequently access the same data block.

Can happen with:

* Sequence-heavy inserts
* Same account row updates
* Same branch summary row
* Same status table
* High-frequency ledger inserts

Possible symptom:

```text
buffer busy waits
```

---

## Trainer Explanation

“Hot blocks happen when many sessions compete for the same block.

Even if they are not updating the exact same row, they may access rows stored in the same block.

This can create contention.

In high-volume banking systems, hot blocks can appear in ledger, transaction, or summary tables.”

---

# Slide 11: Buffer Busy Waits

## Slide content:

`buffer busy waits` means sessions are waiting for a data block in buffer cache.

Possible causes:

* Hot blocks
* Concurrent inserts
* Concurrent updates
* Segment contention
* Poor physical design

---

## Trainer Explanation

“Buffer busy waits means sessions want access to a block, but another session is using it in a conflicting way.

This is not always a SQL plan problem.

It can be a concurrency or data layout problem.

We usually investigate hot objects, segment stats, and workload pattern.”

---

# Slide 12: Library Cache Contention

## Slide content:

Library cache contention happens when sessions compete for shared SQL/PLSQL objects.

Possible causes:

* Too much hard parsing
* Not using bind variables
* Frequent object recompilation
* Invalidations
* Many similar SQL statements

Symptoms may include:

* library cache lock
* library cache pin
* mutex waits

---

## Trainer Explanation

“Library cache contention is related to shared SQL and object metadata.

If application creates many unique SQL statements instead of using bind variables, parsing pressure can increase.

If packages or objects are frequently recompiled, sessions may wait.

This is another type of short-lived performance issue.”

---

# Slide 13: Short-Lived Performance Spikes

## Slide content:

Short-lived spikes are problems that happen briefly.

Examples:

* 5-minute fund transfer slowness
* Batch job blocks users
* Report suddenly consumes I/O
* One session locks payment table
* CPU spike during dashboard refresh

Challenge:

```text
Problem may disappear before DBA checks it.
```

---

## Trainer Explanation

“Short-lived issues are difficult because by the time DBA checks, the problem may be gone.

That is why AWR, ASH, alerts, and monitoring are useful.

But for active locking, dynamic views like v$session and dba_blockers are very useful.”

---

# Slide 14: Tools and Views

## Slide content:

Important views:

* `v$session`
* `v$lock`
* `v$locked_object`
* `dba_blockers`
* `dba_waiters`
* ASH, if licensed

Use them to find:

* Blocking session
* Waiting session
* Wait event
* Locked object
* SQL causing lock

---

## Trainer Explanation

“These are the main views for diagnosing locking and concurrency.

v$session shows session status and blocking information.

v$lock shows low-level lock details.

v$locked_object shows objects locked by sessions.

dba_blockers and dba_waiters show blocker-waiter relationship.

ASH is useful for historical active session analysis if licensed.”

---

# Slide 15: v$session

## Slide content:

Useful query:

```sql
SELECT sid,
       serial#,
       username,
       blocking_session,
       wait_class,
       event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

Shows:

* Waiting session
* Blocking session
* Wait class
* Wait event

---

## Trainer Explanation

“This is one of the most practical queries.

If a session is blocked, blocking_session tells us who is blocking it.

The wait event tells us what it is waiting for.

For row lock waits, we may see events like `enq: TX - row lock contention`.”

---

# Slide 16: dba_blockers and dba_waiters

## Slide content:

Find blockers:

```sql
SELECT *
FROM dba_blockers;
```

Find waiters:

```sql
SELECT *
FROM dba_waiters;
```

Purpose:

* Identify blocking sessions
* Identify waiting sessions
* Understand blocker-waiter chain

---

## Trainer Explanation

“These views make lock diagnosis easier.

dba_blockers shows sessions blocking others.

dba_waiters shows sessions waiting for locks.

In a real issue, we use these views to quickly identify who is causing the wait.”

---

# Slide 17: v$locked_object

## Slide content:

```sql
SELECT lo.session_id,
       o.object_name,
       o.object_type,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id;
```

Shows:

* Which session locked which object
* Object name
* Object type
* Lock mode

---

## Trainer Explanation

“v$locked_object helps us identify the object involved.

For example, maybe the ACCOUNTS table is locked by one session.

This does not always mean whole table is blocked, but it helps us know which object is involved in the transaction.”

---

# Slide 18: v$lock

## Slide content:

```sql
SELECT sid,
       type,
       id1,
       id2,
       lmode,
       request,
       block
FROM v$lock
WHERE block = 1 OR request > 0;
```

Purpose:

* Low-level lock details
* Shows holders and waiters
* Useful for advanced diagnosis

---

## Trainer Explanation

“v$lock is lower-level.

It shows lock type, mode held, requested mode, and whether the session is blocking.

For beginners, v$session and dba_blockers are easier.

But v$lock is useful for deeper analysis.”

---

# Slide 19: ASH, If Licensed

## Slide content:

ASH = Active Session History

Useful for short-lived issues.

Can answer:

* What sessions were active?
* What were they waiting for?
* Which SQL was running?
* Which object was involved?
* What happened during the spike?

Important:

```text
Use only if properly licensed.
```

---

## Trainer Explanation

“ASH is very useful for short-lived performance spikes.

If the problem happened for 5 minutes and disappeared, ASH may help reconstruct what happened.

But ASH usage requires proper Oracle licensing, so always follow the bank’s license policy.”

---

# Slide 20: Banking Scenario

## Slide content:

Multiple users update same account balance.

Session 1:

```sql
UPDATE accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

Session 2:

```sql
UPDATE accounts
SET balance = balance + 1000
WHERE account_id = 101;
```

If Session 1 does not commit, Session 2 waits.

---

## Trainer Explanation

“Now we move to our lab scenario.

Two sessions update the same account.

Session 1 updates the balance but does not commit.

Session 2 tries to update the same account.

Oracle protects consistency, so Session 2 waits.”

---

# Slide 21: Lab 11 Objective

## Slide content:

## Locking Simulation

Participants will:

1. Open two database sessions
2. Update same account row in Session 1
3. Do not commit
4. Try update in Session 2
5. Observe waiting behavior
6. Diagnose blocker and waiter
7. Safely resolve the lock

---

## Trainer Explanation

“This lab requires two SQL sessions.

It can be two SQL Developer worksheets with separate connections, or two SQL*Plus terminals.

The key is that Session 1 must keep the transaction open.

Session 2 will then wait.”

---

# Slide 22: Lab Setup Check

## Slide content:

Confirm account exists:

```sql
SELECT account_id, account_number, balance
FROM accounts
WHERE account_id = 101;
```

If not found:

```sql
INSERT INTO accounts (
  account_id, account_number, customer_id, branch_id,
  account_type, balance, status, opened_date
)
VALUES (
  101, '1000000101', 101, 1,
  'SAVINGS', 50000, 'ACTIVE', SYSDATE
);

COMMIT;
```

---

## Trainer Explanation

“Before starting, make sure account_id 101 exists.

If it does not exist, insert it.

Then commit, so both sessions can see the row.

Now we are ready for locking simulation.”

---

# Slide 23: Session 1 — Create Lock

## Slide content:

In Session 1, run:

```sql
UPDATE accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

Important:

```text
Do not commit.
Do not rollback.
Keep session open.
```

---

## Trainer Explanation

“Session 1 updates account 101.

Now this row is locked.

Do not commit.

Do not rollback.

Keep the session open.

This simulates an application transaction that has not completed yet.”

---

# Slide 24: Session 2 — Waiting Update

## Slide content:

In Session 2, run:

```sql
UPDATE accounts
SET balance = balance + 1000
WHERE account_id = 101;
```

Expected behavior:

```text
Session 2 waits.
```

Why?

```text
Session 1 holds lock on account_id = 101.
```

---

## Trainer Explanation

“Now Session 2 tries to update the same account.

It will wait because Session 1 holds the row lock.

This is exactly how users experience hanging or slow transactions in banking applications.”

---

# Slide 25: Diagnosis Query 1 — Find Waiting Sessions

## Slide content:

Run in third session or new worksheet:

```sql
SELECT sid,
       serial#,
       username,
       blocking_session,
       wait_class,
       event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

Expected:

* Waiting session visible
* Blocking session ID visible
* Wait event likely row lock contention

---

## Trainer Explanation

“Now we diagnose.

This query shows sessions that are blocked.

blocking_session tells us which session is causing the wait.

The event tells us what kind of wait it is.”

---

# Slide 26: Diagnosis Query 2 — Find Blockers

## Slide content:

```sql
SELECT *
FROM dba_blockers;
```

Expected:

```text
Blocking session appears here.
```

---

## Trainer Explanation

“This view shows sessions that are blocking others.

In our lab, Session 1 should appear as the blocker.

If the view shows no rows, check whether Session 2 is still waiting.”

---

# Slide 27: Diagnosis Query 3 — Find Waiters

## Slide content:

```sql
SELECT *
FROM dba_waiters;
```

Expected:

```text
Waiting session appears here.
```

---

## Trainer Explanation

“This view shows sessions that are waiting.

In our lab, Session 2 should appear here.

Together, dba_blockers and dba_waiters help us understand the blocker-waiter relationship.”

---

# Slide 28: Diagnosis Query 4 — Locked Object

## Slide content:

```sql
SELECT lo.session_id,
       o.object_name,
       o.object_type,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id;
```

Expected:

```text
ACCOUNTS table appears as locked object.
```

---

## Trainer Explanation

“This query tells us which object is involved.

We expect to see ACCOUNTS.

Remember, Oracle locks the row, but the object appears in this view as part of the transaction lock information.”

---

# Slide 29: Diagnosis Query 5 — SQL Causing Lock

## Slide content:

```sql
SELECT s.sid,
       s.serial#,
       s.username,
       s.status,
       s.blocking_session,
       s.event,
       q.sql_text
FROM v$session s
LEFT JOIN v$sql q
  ON s.sql_id = q.sql_id
WHERE s.sid IN (
  SELECT blocking_session
  FROM v$session
  WHERE blocking_session IS NOT NULL
)
OR s.blocking_session IS NOT NULL;
```

---

## Trainer Explanation

“This query tries to show the SQL text for blocker and waiter.

Sometimes the blocker’s current SQL may not show the original update because it is now idle.

That is important.

A session can be idle but still blocking because it has an uncommitted transaction.”

---

# Slide 30: Important Production Lesson

## Slide content:

A blocker may appear as:

```text
INACTIVE
```

But still block others.

Why?

* It updated data
* Did not commit
* Did not rollback
* Transaction is still open

Important:

```text
Inactive does not always mean harmless.
```

---

## Trainer Explanation

“This is a very important real-world point.

Many DBAs see inactive session and think it is not doing anything.

But an inactive session can still hold locks if it has an uncommitted transaction.

So always check blocking and transaction status, not only active/inactive status.”

---

# Slide 31: Safe Resolution Steps

## Slide content:

Before killing a session:

1. Identify blocker
2. Identify waiting sessions
3. Identify locked object
4. Check SQL/module/user
5. Check transaction duration
6. Contact application/user/team
7. Ask for commit or rollback
8. Kill session only with approval

---

## Trainer Explanation

“In production, do not immediately kill sessions.

A blocking session may be processing an important payment.

Killing it can rollback work or create business issues.

First identify owner, module, SQL, and impact.

Then follow bank’s incident process.”

---

# Slide 32: Resolving Lab Lock

## Slide content:

To release lock, go to Session 1.

Option 1:

```sql
COMMIT;
```

Option 2:

```sql
ROLLBACK;
```

After that, Session 2 continues.

---

## Trainer Explanation

“In the lab, we resolve the lock by committing or rolling back Session 1.

Once Session 1 releases the lock, Session 2 can continue.

This demonstrates how waiting sessions depend on blocker completion.”

---

# Slide 33: Emergency Kill Command

## Slide content:

Only with approval:

```sql
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;
```

Example:

```sql
ALTER SYSTEM KILL SESSION '123,4567' IMMEDIATE;
```

Use carefully.

---

## Trainer Explanation

“This is an emergency option.

Do not use it casually.

Killing a session can rollback work and affect application behavior.

In a bank, this should follow approval and incident process.”

---

# Slide 34: Lab Task Worksheet

## Slide content:

Participants should record:

| Item                        | Observation |
| --------------------------- | ----------- |
| Blocking session SID        |             |
| Blocking session serial#    |             |
| Waiting session SID         |             |
| Wait event                  |             |
| Locked object               |             |
| SQL involved                |             |
| Is blocker active/inactive? |             |
| Safe resolution step        |             |

---

## Trainer Explanation

“This worksheet is the lab output.

They should not only run commands.

They should identify blocker, waiter, object, event, and safe action.

This is exactly what DBAs do during real incidents.”

---

# Slide 35: Short-Lived Issue Diagnosis Flow

## Slide content:

For short-lived problems:

```text
1. Check current sessions
2. Identify waits
3. Check blockers/waiters
4. Capture SQL ID
5. Check AWR/ASH if issue passed
6. Check application logs
7. Document time window
8. Compare with baseline
```

---

## Trainer Explanation

“If the issue is happening now, use dynamic views.

If the issue already passed, use AWR or ASH if available.

Always capture time window.

Without time window, short-lived issues are difficult to investigate.”

---

# Slide 36: Common Tuning Problems Covered

## Slide content:

This slot covers:

## Concurrency Issues

Many sessions competing for same data/resource.

## Locking Issues

One session blocks another due to uncommitted transaction.

## Short-Lived Performance Problems

Brief spikes due to locks, waits, batch jobs, or hot objects.

---

## Trainer Explanation

“This slot maps to three important production problems.

Concurrency issues are normal in banking, but they must be managed.

Locking issues often look like slow application performance.

Short-lived spikes require quick diagnosis and good monitoring.”

---

# Slide 37: Slot 3 Summary

## Slide content:

In this slot, we learned:

* Concurrency means many sessions working together
* Locking protects data consistency
* Writers can block writers
* Blocking happens when one session holds a needed lock
* Deadlocks happen when sessions wait for each other
* Long transactions increase blocking risk
* Dynamic views help identify blockers and waiters
* Safe resolution needs approval and validation

---

## Trainer Explanation

“Let’s summarize.

Not every performance issue is a bad SQL plan.

Sometimes SQL is waiting for locks or resources.

A good DBA must identify whether the problem is execution time or wait time.

For locking, find blocker, waiter, object, SQL, and safe resolution.”

---

# Slide 38: Transition to Slot 4

## Slide content:

Next slot:

# Final Capstone: End-to-End Banking Performance Tuning Case

We will combine:

* AWR
* ADDM
* Execution plans
* Indexing
* SQL Advisor thinking
* Plan regression
* Locking diagnosis
* Final root cause analysis

---

## Trainer Explanation

“In the final slot, we will combine all three days.

We will take a banking performance case and diagnose it end-to-end.

The goal is to think like a production DBA: gather evidence, identify root cause, apply safe fix, and validate improvement.”

---

# Final Trainer Message for Slot 3

Use this line:

> “If a query is slow, first ask: is it working slowly, or is it waiting?”
