# Day 3 - SECOND HALF (FINAL ENTERPRISE VERSION)

## 1:00 PM - 5:00 PM

# Concurrency, Locking, Short-Lived Problems & Final Banking Capstone

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* distinguish slow execution from waiting/blocking
* simulate row-level locking using two business sessions and one DBA diagnosis session
* identify blockers, waiters, locked objects, and wait events
* understand why inactive sessions can still block
* resolve locks safely in a banking production mindset
* diagnose short-lived performance problems using current views and AWR/ASH concepts
* complete an end-to-end banking performance case
* produce a final evidence-based DBA recommendation

---

# HALF-DAY DESIGN PHILOSOPHY

This half day is intentionally:

* incident-response focused
* multi-session practical
* evidence-driven
* safety-oriented
* capstone-based

NOT:

* locking theory only
* "kill session" training
* one-command tuning
* vague final recap

---

# HALF-DAY STORYLINE

Real-life banking incident:

```text
It is month-end salary day.
Branch 10 is processing a high transaction volume.

The operations team reports two symptoms:

1. The branch transaction dashboard is slow.
2. One customer balance correction is stuck.

As the DBA, your job is not to guess.
Your job is to prove whether the problem is:

* slow SQL execution,
* waiting because of a lock,
* too much data requested by the business query,
* a missing access path,
* or a mix of these.
```

Why this storyline matters:

```text
In production, users normally say "the system is slow".
They rarely know whether the database is executing, waiting, blocked, sorting,
reading too much data, or suffering from a poor access path.

This half day teaches DBAs how to separate those possibilities using evidence.
```

---

# FINAL TIME STRUCTURE

| Time          | Section                                      |
| ------------- | -------------------------------------------- |
| 1:00 - 1:15   | Concurrency vs locking                       |
| 1:15 - 1:35   | Lock diagnosis views                         |
| 1:35 - 2:10   | Lab 11: account row lock incident simulation |
| 2:10 - 2:25   | Safe resolution and short-lived incidents    |
| 2:25 - 2:30   | Slot 3 summary                               |
| 2:45 - 3:05   | Final capstone briefing                      |
| 3:05 - 3:35   | Capstone Part 1: workload evidence           |
| 3:35 - 4:10   | Capstone Part 2: plan diagnosis and SQL fix  |
| 4:10 - 4:35   | Capstone Part 3: locking diagnosis           |
| 4:35 - 4:55   | Capstone Part 4: validation and report       |
| 4:55 - 5:00   | Final training close                         |

---

# COMMON SESSION SETTINGS

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET SERVEROUTPUT ON
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

---

# BEFORE STARTING

This file assumes earlier labs created:

```text
ACCOUNTS
TRANSACTIONS
CUSTOMERS
```

Validate:

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('ACCOUNTS','TRANSACTIONS','CUSTOMERS')
ORDER BY table_name;
```

If `ACCOUNTS` or `TRANSACTIONS` is missing, run `01-Day/SECOND.md` setup first.

---

# SLOT 3 - CONCURRENCY, LOCKING AND SHORT-LIVED PERFORMANCE PROBLEMS

## 1:00 PM - 2:30 PM

# SECTION 1 - CONCURRENCY VS LOCKING (1:00 - 1:15)

## Banking Scenario

A teller starts a balance correction for account `1000000101` and leaves the transaction uncommitted while checking paperwork.

At the same time, an ATM withdrawal, mobile transfer, or branch posting tries to update the same account.

To the business user, it looks like:

```text
The transaction is slow.
```

To the DBA, the real question is:

```text
Is the SQL slow because it is doing work,
or is it slow because it is waiting for another session?
```

## DBA Benefit

This section teaches the DBA to avoid the most common wrong reaction:

```text
Do not tune SQL before checking whether it is blocked.
```

If the SQL is waiting on a lock, adding an index will not fix the immediate problem.

---

# Slide 1 - Core Idea

## Slide Content

# Slow Does Not Always Mean Bad SQL

When a banking screen is slow, SQL may be:

```text
executing work
```

or:

```text
waiting for another session
```

Common wait reason:

```text
another session holds a lock
```

---

## Trainer Delivery

"Until now we focused heavily on execution plans.

But a query can have a good plan and still appear slow.

Why?

Because it may be waiting for another session.

In banking systems, this is common during balance updates, payment posting, reversals, settlement jobs, and end-of-day corrections.

The DBA benefit is simple:

Before recommending an index, SQL rewrite, or session kill, first prove whether the session is working or waiting."

---

# Slide 2 - Definitions

## Slide Content

| Concept | Banking Example | DBA Meaning |
| ------- | --------------- | ----------- |
| Concurrency | ATM, mobile app, teller, and batch job use the same database | many sessions work at the same time |
| Locking | one teller updates an account balance | Oracle protects changed data until commit/rollback |
| Blocking | another transaction wants the same account row | one session waits for another session |
| Deadlock | two sessions hold what the other needs | Oracle detects and cancels one statement |
| Hot block | many transactions hit the same popular branch/account range | many sessions compete for the same data block |

---

# Slide 3 - Banking Risk Areas

## Slide Content

High-risk banking data:

* account balances
* payment status
* ledger rows
* loan EMI status
* reversal records
* settlement batches
* audit rows

Production warning:

```text
Writers can block writers.
Readers usually do not block writers in Oracle.
```

DBA action:

```text
When the complaint mentions stuck posting, stuck reversal, or stuck balance update,
check locks and waiters before changing SQL.
```

---

# SECTION 2 - LOCK DIAGNOSIS VIEWS (1:15 - 1:35)

## Banking Scenario

The call center says:

```text
Customer account 1000000101 cannot be updated.
The teller screen keeps spinning.
```

The application team asks the DBA:

```text
Which session is blocking it?
Which object is locked?
Is the blocker still active?
Can we safely resolve it?
```

## DBA Benefit

These views help the DBA move from complaint to evidence:

```text
complaint -> waiting session -> blocking session -> locked object -> open transaction -> safe action
```

This is the production skill that prevents blind session killing.

---

# Slide 4 - Views We Use

## Slide Content

| DBA Question | View To Use | Why It Matters |
| ------------ | ----------- | -------------- |
| Who is waiting? | `V$SESSION` | shows waiter, wait event, and `BLOCKING_SESSION` |
| Who is blocking? | `DBA_BLOCKERS` / `DBA_WAITERS` | gives blocker/waiter relationship |
| Which table is involved? | `V$LOCKED_OBJECT` | proves the object, such as `ACCOUNTS` |
| Is there an open transaction? | `V$TRANSACTION` | shows the blocker still has uncommitted work |
| What SQL was involved? | `V$SQL` | helps identify the application action if SQL is still available |

Banking example:

```text
If ACCOUNTS is locked, the incident may affect balance update, withdrawal,
deposit posting, reversal, or interest correction.
```

---

# Query 1 - Blocked Sessions

Why this step exists:

```text
Start with the waiting session.
If BLOCKING_SESSION is populated, this is not just "slow SQL".
It is a blocking incident.
```

```sql
SELECT sid,
       serial#,
       username,
       status,
       blocking_session,
       wait_class,
       event,
       seconds_in_wait,
       sql_id
FROM v$session
WHERE blocking_session IS NOT NULL;
```

Expected during lab:

```text
Waiting session shows BLOCKING_SESSION.
```

---

# Query 2 - Blocker/Waiter Relationship

Why this step exists:

```text
This gives a quick incident map:
which session is causing the queue, and which session is stuck behind it.
```

```sql
SELECT *
FROM dba_blockers;

SELECT *
FROM dba_waiters;
```

If these views are not accessible:

```text
Use V$SESSION blocking_session instead.
```

---

# Query 3 - Locked Objects

Why this step exists:

```text
The business needs to know what is affected.
Lock on ACCOUNTS is more urgent than a lock on a temporary training table.
```

```sql
SELECT lo.session_id,
       s.serial#,
       s.username,
       o.object_name,
       o.object_type,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id
JOIN v$session s
  ON lo.session_id = s.sid
ORDER BY lo.session_id, o.object_name;
```

Expected during lab:

```text
ACCOUNTS should appear as locked object.
```

---

# Query 4 - Blocker Details

Why this step exists:

```text
The blocker may be INACTIVE but still dangerous.
In banking, an inactive blocker can still hold an uncommitted balance update.
```

```sql
SELECT s.sid,
       s.serial#,
       s.username,
       s.status,
       s.module,
       s.action,
       s.event,
       s.sql_id,
       t.start_time,
       t.used_ublk,
       t.used_urec
FROM v$session s
LEFT JOIN v$transaction t
  ON s.taddr = t.addr
WHERE s.sid IN (
  SELECT blocking_session
  FROM v$session
  WHERE blocking_session IS NOT NULL
);
```

Trainer note:

The blocker may show `INACTIVE` but still hold an open transaction. That is a key production lesson.

---

# Query 5 - SQL Text For Waiter And Blocker

Why this step exists:

```text
SQL text helps connect database evidence to the application module,
such as teller correction, payment posting, or settlement update.
```

```sql
SELECT s.sid,
       s.serial#,
       s.username,
       s.status,
       s.blocking_session,
       s.event,
       s.sql_id,
       SUBSTR(q.sql_text,1,120) AS sql_text
FROM v$session s
LEFT JOIN v$sql q
  ON s.sql_id = q.sql_id
WHERE s.blocking_session IS NOT NULL
OR s.sid IN (
  SELECT blocking_session
  FROM v$session
  WHERE blocking_session IS NOT NULL
);
```

Trainer note:

The blocker's current SQL may be null or unrelated if the blocker is now idle. The session can still hold locks.

---

# SECTION 3 - LAB 11: ACCOUNT ROW LOCK INCIDENT SIMULATION (1:35 - 2:10)

## Banking Scenario

Incident story:

```text
A teller starts a manual correction on account 1000000101.
The teller updates the balance but forgets to commit.

A second operation tries to update the same account.
This could represent an ATM withdrawal, mobile transfer, fee reversal, or branch posting.

The second operation waits.
The customer sees a stuck transaction.
The DBA must prove who is blocking, what is locked, and how to resolve safely.
```

## DBA Benefit

After this lab, the DBA should be able to:

* identify the waiting session
* identify the blocking session
* prove the locked object
* recognize that an `INACTIVE` session can still block
* choose commit, rollback, or escalation based on business risk

---

# Slide 5 - Lab Requirement

## Slide Content

# Lab 11: Account Balance Update Is Stuck

Open three database sessions:

| Session | Role In Story | What It Does |
| ------- | ------------- | ------------ |
| Session 1 | Teller correction | updates the account and does not commit |
| Session 2 | ATM/mobile/branch posting | tries to update the same account and waits |
| Session 3 | DBA investigator | finds blocker, waiter, locked object, and safe resolution |

Use separate SQL Developer worksheets or separate SQL*Plus terminals.

Learning goal:

```text
Do not guess. Use database evidence to explain why the transaction is stuck.
```

---

# Step 1 - Setup Account Row

Run once before the lock simulation.

Why this step exists:

```text
We need one known customer account so every trainee blocks the same row.
This removes setup confusion and keeps the lab focused on diagnosis.
```

Banking meaning:

```text
Account 1000000101 is the customer account involved in the incident.
```

```sql
MERGE INTO accounts a
USING (
  SELECT 101 AS account_id,
         '1000000101' AS account_number,
         101 AS customer_id,
         1 AS branch_id,
         'SAVINGS' AS account_type,
         50000 AS balance,
         'ACTIVE' AS status,
         SYSDATE AS opened_date
  FROM dual
) src
ON (a.account_id = src.account_id)
WHEN MATCHED THEN
  UPDATE SET a.balance = src.balance,
             a.status = src.status
WHEN NOT MATCHED THEN
  INSERT (
    account_id,
    account_number,
    customer_id,
    branch_id,
    account_type,
    balance,
    status,
    opened_date
  )
  VALUES (
    src.account_id,
    src.account_number,
    src.customer_id,
    src.branch_id,
    src.account_type,
    src.balance,
    src.status,
    src.opened_date
  );

COMMIT;
```

Validate:

```sql
SELECT account_id, account_number, balance, status
FROM accounts
WHERE account_id = 101;
```

---

# Step 2 - Session 1 Creates The Lock

In Session 1:

Business meaning:

```text
The teller has started a correction and changed the balance.
Because there is no COMMIT or ROLLBACK, Oracle must protect this uncommitted row.
```

DBA significance:

```text
This session becomes the blocker.
It may later look idle, but the transaction is still open.
```

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'DAY3_LOCK_LAB',
    action_name => 'BLOCKER_SESSION'
  );
END;
/

UPDATE /* day3_lock_blocker */
       accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

Important:

```text
Do not COMMIT.
Do not ROLLBACK.
Keep Session 1 open.
```

---

# Step 3 - Session 2 Becomes The Waiter

In Session 2:

Business meaning:

```text
Another banking operation now tries to update the same customer account.
It cannot continue until the first transaction commits or rolls back.
```

DBA significance:

```text
This session becomes the waiter.
The wait proves the issue is blocking, not necessarily a bad execution plan.
```

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'DAY3_LOCK_LAB',
    action_name => 'WAITER_SESSION'
  );
END;
/

UPDATE /* day3_lock_waiter */
       accounts
SET balance = balance + 1000
WHERE account_id = 101;
```

Expected:

```text
Session 2 waits.
```

Do not cancel it yet.

Trainer checkpoint:

```text
Ask trainees what the user would report.
Expected answer: "The transaction is hanging" or "the screen is slow".

Then ask what the DBA must prove.
Expected answer: whether it is executing or waiting.
```

---

# Step 4 - Session 3 Diagnoses The Block

In Session 3, run:

Business meaning:

```text
The DBA checks the live database instead of asking users to retry blindly.
```

DBA significance:

```text
This query names the waiter and shows the blocking session ID.
It also shows whether the blocker is ACTIVE or INACTIVE.
```

```sql
SELECT sid,
       serial#,
       username,
       status,
       blocking_session,
       wait_class,
       event,
       seconds_in_wait,
       module,
       action
FROM v$session
WHERE blocking_session IS NOT NULL
OR module = 'DAY3_LOCK_LAB'
ORDER BY sid;
```

Expected:

```text
WAITER_SESSION shows blocking_session.
BLOCKER_SESSION may be INACTIVE but still blocking.
```

Key lesson:

```text
Inactive does not mean harmless.
An inactive session with an open transaction can still block production work.
```

---

# Step 5 - Session 3 Finds Locked Object

Business meaning:

```text
The DBA identifies the impacted business object.
In this lab, the locked object is ACCOUNTS, which means customer balance work is affected.
```

DBA significance:

```text
Object evidence helps decide priority and escalation.
A lock on ACCOUNTS during business hours is more serious than a lock on a report staging table.
```

```sql
SELECT lo.session_id,
       s.serial#,
       s.module,
       s.action,
       o.object_name,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id
JOIN v$session s
  ON lo.session_id = s.sid
WHERE o.object_name = 'ACCOUNTS';
```

Expected:

```text
ACCOUNTS appears with blocking session.
```

---

# Step 6 - Session 3 Checks Transaction Age

Business meaning:

```text
The DBA checks how long the correction has been open and whether it used undo.
Long open transactions increase risk because rollback can take time and business state may be unclear.
```

DBA significance:

```text
This prevents unsafe action.
Before killing or rolling back anything, understand the transaction age and module.
```

```sql
SELECT s.sid,
       s.serial#,
       s.status,
       s.module,
       s.action,
       t.start_time,
       t.used_ublk,
       t.used_urec
FROM v$session s
JOIN v$transaction t
  ON s.taddr = t.addr
WHERE s.module = 'DAY3_LOCK_LAB';
```

Ask:

* Which session has open transaction?
* Is the blocker active or inactive?
* What business module does it belong to?
* Should we kill it immediately?

Expected DBA answer:

```text
Do not kill immediately.
First contact the application owner, teller supervisor, or batch owner.
Confirm whether the transaction should commit or roll back.
```

---

# Step 7 - Resolve The Lab Lock

In Session 1, choose one:

Business meaning:

```text
The owner of the teller correction decides the outcome.
COMMIT means the correction is valid.
ROLLBACK means the correction should be cancelled.
```

DBA significance:

```text
The safest fix is usually to complete or cancel the blocker through the owning session or application.
Killing the session is an escalation path, not the default.
```

```sql
COMMIT;
```

or:

```sql
ROLLBACK;
```

Expected:

```text
Session 2 completes.
```

Then commit or rollback Session 2:

```sql
COMMIT;
```

---

# Optional Emergency Command

Only with approval in production:

```sql
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;
```

Trainer note:

In a bank, killing a session can rollback payment or settlement work. Do not teach this as the default fix.

---

# Locking Worksheet

| Item | Observation |
| ---- | ----------- |
| Blocking SID | |
| Blocking serial# | |
| Waiting SID | |
| Wait event | |
| Locked object | |
| Blocker module/action | |
| Blocker active or inactive? | |
| Safe resolution | |

---

# SECTION 4 - SHORT-LIVED INCIDENTS (2:10 - 2:25)

## Banking Scenario

The operations team reports:

```text
Between 2:05 PM and 2:08 PM, payment posting was slow.
Now everything is normal.
```

This is common in banking:

* salary upload spikes
* short settlement bursts
* blocked sessions that resolve before the DBA connects
* slow reports during branch closing
* brief storage or network pressure

## DBA Benefit

This section teaches the DBA what to capture when the problem is temporary.

The key production habit:

```text
If the issue has disappeared, do not say "nothing is wrong".
Ask for the exact time window and check historical evidence if available.
```

---

# Slide 6 - If The Problem Disappears

## Slide Content

# Short-Lived Incidents Need Time Evidence

Banking example:

```text
Payment posting was slow from 2:05 PM to 2:08 PM,
but it is normal by the time the DBA logs in.
```

Use:

* exact complaint time window
* AWR if the interval is captured
* ASH if licensed
* application logs
* alerting/monitoring history
* SQL IDs from logs

DBA goal:

```text
Reconstruct what happened using snapshots, samples, logs, and SQL IDs.
```

---

# Active Session Snapshot Query

Run during an active issue:

Why this step exists:

```text
If the issue is happening now, capture active sessions immediately.
This is the DBA equivalent of taking a production incident photo before it disappears.
```

```sql
SELECT sid,
       serial#,
       username,
       status,
       wait_class,
       event,
       blocking_session,
       sql_id,
       module,
       action,
       seconds_in_wait
FROM v$session
WHERE username IS NOT NULL
AND wait_class <> 'Idle'
ORDER BY seconds_in_wait DESC;
```

ASH option, if licensed:

Why this step exists:

```text
If the issue already disappeared, ASH may show what sessions were active,
what they waited on, and who blocked them during the complaint window.
```

```sql
SELECT sample_time,
       session_id,
       session_serial#,
       sql_id,
       event,
       blocking_session,
       module,
       action
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (15/1440)
ORDER BY sample_time DESC;
```

Trainer note:

Only use ASH where Diagnostic Pack licensing is approved.

---

# SLOT 3 SUMMARY

```text
If SQL is slow, ask:

Is it executing slowly?
Or is it waiting?
```

Banking DBA takeaway:

```text
For stuck balance updates and payment postings, prove waiting/blocking first.
For slow reports and dashboards, prove workload and plan behavior.
```

---

# SLOT 4 - FINAL CAPSTONE: END-TO-END BANKING PERFORMANCE CASE

## 2:45 PM - 5:00 PM

# SECTION 5 - CAPSTONE BRIEFING (2:45 - 3:05)

## Banking Scenario

End-of-day branch operations incident:

```text
Branch 10 has very high transaction volume today.

The branch manager opens the transaction dashboard to review recent activity.
The screen is slow.

At the same time, one account balance update is stuck because another session
has not committed.
```

This capstone combines two real production patterns:

* one SQL query asks for too much data and needs a better access path
* one account update is blocked by an uncommitted transaction

## DBA Benefit

This final lab teaches the complete DBA response:

```text
understand complaint -> collect evidence -> fix SQL/access path -> diagnose lock -> validate -> report
```

---

# Slide 7 - Business Scenario

## Slide Content

# Branch 10 Dashboard And Account Update Incident

Symptoms:

* dashboard slow during business hours
* branch transaction report takes too long
* AWR may show high reads or high SQL elapsed time
* one query scans too much transaction data
* one account update is blocked

Goal:

```text
Diagnose, fix, validate, and explain the business risk like a production DBA.
```

DBA questions:

```text
Is the dashboard slow because it reads too much data?
Is the plan doing unnecessary work?
Is the stuck account update blocked?
What evidence proves the fix helped?
```

---

## Trainer Delivery

"This is the final lab.

You will combine all three days:

* SQL plan reading,
* indexing,
* AWR thinking,
* advisor judgment,
* plan stability,
* bind awareness,
* locking diagnosis,
* before/after validation."

---

# SECTION 6 - CAPSTONE SETUP (3:05 - 3:20)

## Banking Scenario

To make the incident realistic, we create a high-volume branch:

```text
Branch 10 handled most of today's transaction traffic.
The dashboard query for Branch 10 now has much more data to read and sort.
```

## DBA Benefit

This setup teaches an important production lesson:

```text
Performance problems often appear only when data distribution changes.
A query that looked fine for a small branch may become expensive for a hot branch.
```

---

# Step 1 - Create Hot Branch Pattern

This makes the dashboard query visibly problematic.

Why this step exists:

```text
We intentionally make Branch 10 the busy branch.
This lets trainees see how data volume affects query cost.
```

```sql
UPDATE transactions
SET branch_id = 10
WHERE transaction_id <= 80000;

COMMIT;
```

Gather stats:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/
```

Validate:

```sql
SELECT branch_id, COUNT(*) AS row_count
FROM transactions
WHERE branch_id IN (10, 11, 12)
GROUP BY branch_id
ORDER BY branch_id;
```

Expected:

```text
BRANCH_ID 10 has a large row count.
```

Banking meaning:

```text
Branch 10 is now the branch under pressure.
Reports and dashboards for this branch have more work to do.
```

---

# Step 2 - Make Before Plan Clean

If a previous run created the final tuning index, make it invisible so the before plan shows the problem.

Why this step exists:

```text
The before test must show the original problem.
If the final index already exists from a previous run, the lab would hide the issue.
```

DBA significance:

```text
Good performance work needs a clean before/after comparison.
```

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_BRANCH_DATE_CAP';

  IF v_count > 0 THEN
    EXECUTE IMMEDIATE 'ALTER INDEX idx_txn_branch_date_cap INVISIBLE';
  END IF;
END;
/

ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
```

---

# Optional - AWR Start Snapshot

Use only if AWR privileges/license are available.

Why this step exists:

```text
In production, AWR can preserve workload evidence across a time window.
For this training, it is optional because not every environment has the license or privileges.
```

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Trainer note:

The capstone can be completed without AWR. If AWR is available, use snapshots for stronger before/after evidence.

---

# SECTION 7 - CAPSTONE PART 1: WORKLOAD EVIDENCE (3:20 - 3:35)

## Banking Scenario

The branch manager says:

```text
I only need to see the latest transactions for Branch 10,
but the dashboard is taking too long.
```

The current SQL asks for all rows for Branch 10 and sorts them by date.

## DBA Benefit

This section teaches the DBA to prove the problem before changing anything:

* how many rows are processed
* how many logical reads happen
* whether a large sort is present
* whether the query asks for more data than the business needs

---

# Problem Query

Dashboard query:

Why this step exists:

```text
This is the inefficient version of the dashboard query.
It represents a common production problem: the screen only needs recent rows,
but the SQL asks for all historical rows.
```

```sql
SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;
```

Problems to notice:

* `SELECT *`
* no date range
* large branch
* large sort
* likely excessive reads/buffers

Banking example:

```text
The manager wants recent Branch 10 transactions.
The SQL asks Oracle to fetch and sort every Branch 10 transaction first.
```

---

# Run Before Query Safely

Use `AUTOTRACE TRACEONLY` so rows are not printed.

Why this step exists:

```text
The DBA needs runtime evidence without flooding the screen with thousands of rows.
AUTOTRACE TRACEONLY lets us capture work done by the SQL.
```

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SET AUTOTRACE OFF
```

Record:

* elapsed time
* consistent gets
* physical reads
* rows processed

---

# Capture Before Plan

```sql
EXPLAIN PLAN FOR
SELECT /* capstone_dashboard_before_plan */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected issue:

```text
Large row set and sort operation.
```

DBA significance:

```text
The plan explains why the dashboard is slow.
The metrics prove how much work the SQL actually did.
Both are needed before recommending a fix.
```

Trainer note:

Do not wrap this specific before-plan query in `COUNT(*)`. Oracle may remove the sort because sorting is unnecessary for a count. Use `AUTOTRACE TRACEONLY` for runtime metrics and `EXPLAIN PLAN` to show the original dashboard plan shape.

---

# SECTION 8 - CAPSTONE PART 2: FIX SQL AND ACCESS PATH (3:35 - 4:10)

## Banking Scenario

After speaking with the branch manager, we learn the screen does not need all history.

The real business requirement is:

```text
Show the latest 100 Branch 10 transactions from the last 3 months.
```

## DBA Benefit

This section teaches two DBA habits:

* fix the business query first so it asks for the right data
* then create the smallest useful index to support that query

---

# Better Business Query

The dashboard should show recent rows, not unlimited history.

Why this step exists:

```text
This changes the SQL from "return everything" to "return the data the screen needs".
This is often safer and more effective than only adding an index.
```

```sql
SELECT /* capstone_dashboard_after */
       transaction_id,
       account_id,
       customer_id,
       branch_id,
       transaction_date,
       amount,
       status
FROM transactions
WHERE branch_id = 10
AND transaction_date >= ADD_MONTHS(SYSDATE,-3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

---

# Create Supporting Index Safely

Why this step exists:

```text
The query filters by BRANCH_ID and sorts by TRANSACTION_DATE descending.
The composite index supports that access pattern.
```

DBA significance:

```text
The index is tied to a clear business query.
It is not a random index created because the system felt slow.
```

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_BRANCH_DATE_CAP';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_branch_date_cap ON transactions(branch_id, transaction_date DESC)';
  ELSE
    EXECUTE IMMEDIATE
      'ALTER INDEX idx_txn_branch_date_cap VISIBLE';
  END IF;
END;
/
```

Gather stats:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );
END;
/
```

---

# Run After Query

Why this step exists:

```text
A fix is not complete until it is measured.
The DBA compares after metrics against before metrics.
```

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* capstone_dashboard_after */
       transaction_id,
       account_id,
       customer_id,
       branch_id,
       transaction_date,
       amount,
       status
FROM transactions
WHERE branch_id = 10
AND transaction_date >= ADD_MONTHS(SYSDATE,-3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;

SET AUTOTRACE OFF
```

Record:

* elapsed time
* consistent gets
* physical reads
* rows processed

---

# Capture After Runtime Plan

Why this step exists:

```text
The runtime plan confirms whether Oracle used the improved access path
and whether fewer rows and buffers were processed.
```

```sql
SELECT /* capstone_dashboard_after_plan */
       COUNT(*)
FROM (
  SELECT transaction_id,
         account_id,
         customer_id,
         branch_id,
         transaction_date,
         amount,
         status
  FROM transactions
  WHERE branch_id = 10
  AND transaction_date >= ADD_MONTHS(SYSDATE,-3)
  ORDER BY transaction_date DESC
  FETCH FIRST 100 ROWS ONLY
);

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +NOTE'
  )
);
```

Expected improvement:

```text
Fewer rows processed.
Lower buffers.
Possible use of IDX_TXN_BRANCH_DATE_CAP.
Reduced sort pressure or STOPKEY behavior.
```

Banking benefit:

```text
The branch manager gets the recent transactions faster.
The database avoids wasting work on old rows the screen does not need.
```

---

# SECTION 9 - CAPSTONE PART 3: LOCKING DIAGNOSIS (4:10 - 4:35)

## Banking Scenario

While the dashboard issue is being handled, another user reports:

```text
Account 1000000101 balance update is stuck.
```

This proves a critical production point:

```text
A real incident can have more than one database symptom.
One part may be SQL workload.
Another part may be locking.
```

## DBA Benefit

This section checks whether trainees can reuse the lock diagnosis method inside a larger incident.

The DBA must not assume every symptom has the same root cause.

---

# Create A Controlled Lock

Use the same lock lab pattern from Slot 3.

Why this step exists:

```text
We add a locking symptom to the capstone so trainees diagnose both:
1. slow dashboard SQL
2. stuck account update
```

Ensure account row exists:

```sql
MERGE INTO accounts a
USING (
  SELECT 101 AS account_id,
         '1000000101' AS account_number,
         101 AS customer_id,
         1 AS branch_id,
         'SAVINGS' AS account_type,
         50000 AS balance,
         'ACTIVE' AS status,
         SYSDATE AS opened_date
  FROM dual
) src
ON (a.account_id = src.account_id)
WHEN MATCHED THEN
  UPDATE SET a.balance = src.balance,
             a.status = src.status
WHEN NOT MATCHED THEN
  INSERT (
    account_id,
    account_number,
    customer_id,
    branch_id,
    account_type,
    balance,
    status,
    opened_date
  )
  VALUES (
    src.account_id,
    src.account_number,
    src.customer_id,
    src.branch_id,
    src.account_type,
    src.balance,
    src.status,
    src.opened_date
  );

COMMIT;
```

Session 1:

Business meaning:

```text
One session starts an account adjustment and leaves it uncommitted.
```

```sql
UPDATE /* capstone_lock_blocker */
       accounts
SET balance = balance - 500
WHERE account_id = 101;
```

Do not commit.

Session 2:

Business meaning:

```text
Another operation tries to update the same account and becomes blocked.
```

```sql
UPDATE /* capstone_lock_waiter */
       accounts
SET balance = balance + 500
WHERE account_id = 101;
```

Expected:

```text
Session 2 waits.
```

---

# Diagnose Capstone Lock

Session 3:

Why this step exists:

```text
The DBA proves the account update is waiting on another session.
This avoids mixing up the locking problem with the dashboard SQL problem.
```

```sql
SELECT sid,
       serial#,
       username,
       status,
       blocking_session,
       wait_class,
       event,
       seconds_in_wait,
       sql_id
FROM v$session
WHERE blocking_session IS NOT NULL;
```

Then:

Why this step exists:

```text
This proves the affected object is ACCOUNTS.
Now the DBA can explain the business impact clearly.
```

```sql
SELECT lo.session_id,
       s.serial#,
       o.object_name,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id
JOIN v$session s
  ON lo.session_id = s.sid
WHERE o.object_name = 'ACCOUNTS';
```

Resolve:

Why this step exists:

```text
Rollback releases the blocker in the lab.
In production, the DBA would coordinate with the application or business owner first.
```

```sql
-- In Session 1
ROLLBACK;
```

Trainer note:

This proves the capstone has both SQL workload problem and locking symptom. Real incidents often have more than one issue.

---

# SECTION 10 - CAPSTONE PART 4: VALIDATION AND REPORT (4:35 - 4:55)

## Banking Scenario

The incident is not finished when the SQL runs faster or the lock disappears.

The operations manager asks:

```text
What was the root cause?
What did you change?
How much did it improve?
What is the risk?
Can we roll it back?
```

## DBA Benefit

This section teaches the professional finish:

```text
DBAs must produce evidence, not just fixes.
```

Before/after numbers and a short incident report help the business trust the recommendation.

---

# Optional - AWR End Snapshot

Use only if AWR was started earlier:

Why this step exists:

```text
The ending snapshot closes the measurement window for before/after comparison.
Use only where licensing and privileges allow.
```

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Then generate/report with your normal AWR workflow if privileges allow.

---

# Before/After Worksheet

Why this step exists:

```text
This forces evidence-based validation.
If the numbers did not improve, the fix is not proven.
```

| Metric | Before | After |
| ------ | -----: | ----: |
| Elapsed time | | |
| Consistent gets | | |
| Physical reads | | |
| Rows returned | | |
| Main access path | | |
| Sort operation | | |
| Predicate type | | |

---

# Final Incident Report Template

Participants should present:

Why this step exists:

```text
Production DBAs must communicate clearly to non-DBA stakeholders.
This template turns technical findings into an incident explanation.
```

| Section | Finding |
| ------- | ------- |
| Business complaint | |
| Evidence source | AWR / SQL plan / session views |
| Top SQL or query | |
| Plan issue | |
| Locking issue | |
| Root cause | |
| Fix applied | |
| Before metrics | |
| After metrics | |
| Production risk | |
| Rollback plan | |

---

# Example Final Finding

```text
Root cause:
Dashboard query requested all historical transactions for a high-volume branch and sorted a large row set.
One account update was also blocked by an uncommitted transaction.

Evidence:
Before plan showed large row processing and sort.
Runtime statistics showed high logical reads.
V$SESSION showed row lock wait on ACCOUNTS.

Fix:
Changed dashboard SQL to use required columns, 3-month date filter, and FETCH FIRST 100 ROWS.
Created composite index on (branch_id, transaction_date DESC).
Resolved lock by rolling back the blocker in the lab.

Validation:
After query processed fewer rows and reduced logical reads.
Lock wait disappeared after blocker rollback.
```

Trainer checkpoint:

```text
Ask each participant to explain the incident in one minute:
What was slow?
What was blocked?
What evidence proved each issue?
What changed?
What improved?
```

---

# SECTION 11 - FINAL TRAINING CLOSE (4:55 - 5:00)

## Banking Scenario

The day ends with the DBA presenting a clear production-style conclusion:

```text
The Branch 10 dashboard was inefficient because it requested too much historical data.
The account update was blocked by an uncommitted transaction.
Both were diagnosed with evidence and resolved with controlled actions.
```

## DBA Benefit

The final takeaway is the working method DBAs should use after the training.

---

# Slide 8 - Three-Day Framework

## Slide Content

Use this framework for banking performance incidents:

```text
1. Understand complaint
2. Confirm time window
3. Check workload evidence
4. Identify top SQL and waits
5. Read runtime plan
6. Check locks and sessions
7. Choose the smallest safe fix
8. Validate before and after
9. Document risk and rollback
10. Monitor after change
```

---

# Final Message

```text
Performance tuning is investigation.

Do not guess.
Do not blindly create indexes.
Do not blindly kill sessions.
Do not blindly accept advisor output.

Follow evidence:
workload, plans, waits, locks, and before/after validation.
```

Banking translation:

```text
A slow banking screen may be slow SQL.
A stuck banking transaction may be a lock.
A serious incident may contain both.

The DBA's value is proving the difference and choosing the safest fix.
```
