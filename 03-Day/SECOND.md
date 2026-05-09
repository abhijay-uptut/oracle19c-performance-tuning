# Day 3 - SECOND HALF (FINAL ENTERPRISE VERSION)

## 1:00 PM - 5:00 PM

# Concurrency, Locking, Short-Lived Problems & Final Banking Capstone

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* distinguish slow execution from waiting/blocking
* simulate row-level locking using two sessions
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

# FINAL TIME STRUCTURE

| Time          | Section                                      |
| ------------- | -------------------------------------------- |
| 1:00 - 1:15   | Concurrency vs locking                       |
| 1:15 - 1:35   | Lock diagnosis views                         |
| 1:35 - 2:10   | Lab 11: two-session row lock simulation      |
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

# Slide 1 - Core Idea

## Slide Content

# Not Every Slow SQL Is Executing

Sometimes SQL is:

```text
waiting
```

not:

```text
working
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

In banking systems, this is common during balance updates, payment posting, reversals, and settlement jobs."

---

# Slide 2 - Definitions

## Slide Content

| Concept | Meaning |
| ------- | ------- |
| Concurrency | many sessions working at the same time |
| Locking | mechanism to protect changed data |
| Blocking | one session waits for another session |
| Deadlock | sessions wait for each other |
| Hot block | many sessions compete for the same block |

---

# Slide 3 - Banking Risk Areas

## Slide Content

High-risk objects:

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

---

# SECTION 2 - LOCK DIAGNOSIS VIEWS (1:15 - 1:35)

# Slide 4 - Views We Use

## Slide Content

| View | Use |
| ---- | --- |
| `V$SESSION` | blocker, waiter, wait event |
| `DBA_BLOCKERS` | blocking sessions |
| `DBA_WAITERS` | waiting sessions |
| `V$LOCKED_OBJECT` | object involved |
| `V$TRANSACTION` | open transaction details |
| `V$SQL` | SQL text if still available |

---

# Query 1 - Blocked Sessions

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

# SECTION 3 - LAB 11: TWO-SESSION LOCKING SIMULATION (1:35 - 2:10)

# Slide 5 - Lab Requirement

## Slide Content

Open three sessions:

* Session 1: creates the lock
* Session 2: waits on the lock
* Session 3: diagnoses the lock

Use separate SQL Developer worksheets or separate SQL*Plus terminals.

---

# Step 1 - Setup Account Row

Run once before the lock simulation.

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

---

# Step 4 - Session 3 Diagnoses The Block

In Session 3, run:

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

---

# Step 5 - Session 3 Finds Locked Object

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

---

# Step 7 - Resolve The Lab Lock

In Session 1, choose one:

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

# Slide 6 - If The Problem Disappears

## Slide Content

Short-lived problems may disappear before the DBA checks.

Use:

* exact complaint time window
* AWR if the interval is captured
* ASH if licensed
* application logs
* alerting/monitoring history
* SQL IDs from logs

---

# Active Session Snapshot Query

Run during an active issue:

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

---

# SLOT 4 - FINAL CAPSTONE: END-TO-END BANKING PERFORMANCE CASE

## 2:45 PM - 5:00 PM

# SECTION 5 - CAPSTONE BRIEFING (2:45 - 3:05)

# Slide 7 - Business Scenario

## Slide Content

# Core Transaction Dashboard Is Slow

Symptoms:

* dashboard slow during business hours
* branch transaction report takes too long
* AWR may show high reads or high SQL elapsed time
* one query scans too much transaction data
* one account update is blocked

Goal:

```text
Diagnose, fix, and validate like a production DBA.
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

# Step 1 - Create Hot Branch Pattern

This makes the dashboard query visibly problematic.

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

---

# Step 2 - Make Before Plan Clean

If a previous run created the final tuning index, make it invisible so the before plan shows the problem.

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

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Trainer note:

The capstone can be completed without AWR. If AWR is available, use snapshots for stronger before/after evidence.

---

# SECTION 7 - CAPSTONE PART 1: WORKLOAD EVIDENCE (3:20 - 3:35)

# Problem Query

Dashboard query:

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

---

# Run Before Query Safely

Use `AUTOTRACE TRACEONLY` so rows are not printed.

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

Trainer note:

Do not wrap this specific before-plan query in `COUNT(*)`. Oracle may remove the sort because sorting is unnecessary for a count. Use `AUTOTRACE TRACEONLY` for runtime metrics and `EXPLAIN PLAN` to show the original dashboard plan shape.

---

# SECTION 8 - CAPSTONE PART 2: FIX SQL AND ACCESS PATH (3:35 - 4:10)

# Better Business Query

The dashboard should show recent rows, not unlimited history.

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

---

# SECTION 9 - CAPSTONE PART 3: LOCKING DIAGNOSIS (4:10 - 4:35)

# Create A Controlled Lock

Use the same lock lab pattern from Slot 3.

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

```sql
UPDATE /* capstone_lock_blocker */
       accounts
SET balance = balance - 500
WHERE account_id = 101;
```

Do not commit.

Session 2:

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

```sql
-- In Session 1
ROLLBACK;
```

Trainer note:

This proves the capstone has both SQL workload problem and locking symptom. Real incidents often have more than one issue.

---

# SECTION 10 - CAPSTONE PART 4: VALIDATION AND REPORT (4:35 - 4:55)

# Optional - AWR End Snapshot

Use only if AWR was started earlier:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Then generate/report with your normal AWR workflow if privileges allow.

---

# Before/After Worksheet

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

---

# SECTION 11 - FINAL TRAINING CLOSE (4:55 - 5:00)

# Slide 8 - Three-Day Framework

## Slide Content

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
