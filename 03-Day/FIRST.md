# Day 3 - FIRST HALF (FINAL ENTERPRISE VERSION)

## 9:00 AM - 12:00 PM

# Histograms, Skewed Data, SQL Plan Management, Bind Peeking & Plan Control

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* explain skewed data using banking branch and payment examples
* explain why histograms help Oracle estimate uneven data correctly
* identify when poor estimates can lead to poor execution plans
* explain why a good SQL can suddenly become slow without SQL text changes
* capture and inspect SQL plan baselines
* understand when SQL Plan Management helps and when it hides the real issue
* distinguish SQL plan baselines, SQL Profiles, hints, indexes, and histograms
* inspect bind-sensitive and bind-aware cursors
* understand why one execution plan may not fit every bind value
* use hints carefully for diagnosis, not as the first production fix

## Half-Day Storyline

The whole morning follows one banking incident pattern:

```text
A payment or branch transaction query was fast yesterday.
Today it is slow.
The application team says the SQL text did not change.
The DBA must first understand the data pattern:

Are all values evenly distributed?
Or are a few branches, statuses, or customers much larger than the rest?

Only after that can the DBA decide whether the issue is bad estimates, plan change, bind values, or unsafe plan forcing.
```

We use two connected labs:

| Topic | Banking story | DBA skill |
| ----- | ------------- | --------- |
| Histograms and skew | Branches and payment statuses are not evenly distributed | Understand why estimates and plans can change |
| Lab 9 | Payment settlement query needs plan stability | Capture and verify a SQL plan baseline |
| Lab 10 | Same branch report SQL behaves differently for big and small branches | Diagnose bind peeking, ACS, and hint risk |

---

# HALF-DAY DESIGN PHILOSOPHY

This half day is intentionally:

* production-stability focused
* practical
* optimizer-behavior oriented
* cautious about forcing plans
* honest about environment-dependent behavior

NOT:

* theoretical SPM definitions only
* "baseline everything"
* "hint everything"
* pretending adaptive cursor sharing always appears immediately

---

# FINAL TIME STRUCTURE

| Time          | Section                                            |
| ------------- | -------------------------------------------------- |
| 9:00 - 9:15   | Histograms and skewed banking data                 |
| 9:15 - 9:25   | Why skew changes optimizer choices                 |
| 9:25 - 9:45   | Demo Lab: histogram on failed transactions         |
| 9:45 - 9:50   | Plan regression scenario                           |
| 9:50 - 10:00  | SQL Plan Management mental model                   |
| 10:00 - 10:10 | Lab setup: payment workload                        |
| 10:10 - 10:25 | Lab 9: capture and inspect SQL plan baseline       |
| 10:25 - 10:30 | Plan evolution, fixed baselines, production safety |
| 10:45 - 11:00 | Bind peeking and skewed data                       |
| 11:00 - 11:35 | Lab 10: bind variables and adaptive cursor sharing |
| 11:35 - 11:50 | Hints, profiles, baselines, indexes comparison     |
| 11:50 - 12:00 | Morning summary and transition                     |

---

# LICENSING AND PRIVILEGE NOTE

SQL Plan Management is available in Oracle, but some views and package operations may require privileges.

Confirm access to:

```text
DBMS_SPM
V$SQL
DBA_SQL_PLAN_BASELINES
DBMS_XPLAN
DBMS_STATS
```

If `DBA_SQL_PLAN_BASELINES` is not accessible, ask the training DBA to query it or grant catalog access for the lab.

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
ALTER SESSION SET optimizer_use_sql_plan_baselines = TRUE;
```

---

# SLOT 1 - HISTOGRAMS, SKEWED DATA AND SQL PLAN MANAGEMENT

## 9:00 AM - 10:30 AM

# SECTION 1 - HISTOGRAMS AND SKEWED BANKING DATA (9:00 - 9:15)

Banking scenario:

```text
The bank has 50 branches.
Branch 1 is a city branch with very high payment volume.
Branch 3 is a small branch with very low payment volume.

If Oracle assumes every branch has the same number of rows, it may choose the wrong access path.
```

# Slide 1 - Day 3 Opening (9:00 AM - 9:05 AM)

## Time: 9:00 AM - 9:05 AM

## Slide Content

# Start With Data Distribution

Before tuning a SQL plan, ask:

```text
Is the data evenly distributed?
Or are some values much bigger than others?
```

Banking examples:

* one branch processes most transactions
* most payments are SETTLED, fewer are PENDING
* a few corporate customers have very large account activity
* month-end creates unusual volume for salary branches

DBA message:

```text
Bad estimates often start with misunderstood data distribution.
```

---

## Trainer Delivery

"Before we talk about SQL Plan Management or bind peeking, we need one foundation:

Oracle chooses plans based on estimates.

Estimates come from statistics.

If the data is uneven and Oracle does not understand that unevenness, the plan can be wrong even when the SQL text is simple."

---

# Slide 2 - What Skewed Data Means (9:05 AM - 9:15 AM)

## Time: 9:05 AM - 9:15 AM

## Slide Content

# Skewed Data

Skew means:

```text
Some values appear much more often than others.
```

Banking example:

| Value | Meaning | Row pattern |
| ----- | ------- | ----------- |
| branch_id = 1 | city branch | very many rows |
| branch_id = 2 | normal branch | moderate rows |
| branch_id = 3 | small branch | very few rows |

Why it matters:

```text
The best plan for a small branch may be bad for a large branch.
```

DBA benefit:

```text
You learn when one average estimate is not good enough.
```

---

# SECTION 2 - WHY HISTOGRAMS MATTER (9:15 - 9:25)

Banking scenario:

```text
The optimizer knows a table has 305,500 branch transaction rows.
Without a histogram, it may estimate branch_id values too evenly.
With a histogram, Oracle can understand that branch 1 is much larger than branch 3.
```

# Slide 3 - What A Histogram Tells Oracle (9:15 AM - 9:20 AM)

## Time: 9:15 AM - 9:20 AM

## Slide Content

# Histogram

A histogram is column statistics that describe value distribution.

Simple idea:

```text
Not every value has the same row count.
```

Without histogram:

```text
Oracle may estimate each branch as roughly average.
```

With histogram:

```text
Oracle can estimate common and rare values more accurately.
```

Banking benefit:

```text
Better estimates for branch, status, product, or customer segments that are uneven.
```

---

# Slide 4 - Why DBAs Check Histograms (9:20 AM - 9:25 AM)

## Time: 9:20 AM - 9:25 AM

## Slide Content

# DBA Decision Point

When a query filters on a skewed column:

```text
WHERE branch_id = :b_branch_id
WHERE status = 'PENDING'
WHERE customer_segment = 'CORPORATE'
```

The DBA checks:

* is the column skewed?
* are statistics fresh?
* does a histogram exist?
* are estimated rows close to actual rows?
* does the access path make sense for common and rare values?

Practical rule:

```text
Histograms do not tune SQL by themselves.
They help Oracle make better choices when data is uneven.
```

---

# SECTION 3 - DEMO LAB: HISTOGRAM ON FAILED TRANSACTIONS (9:25 - 9:45)

Banking scenario:

```text
A bank has a transaction monitoring table.
Most transactions are successful.
Only a small percentage fail.

Operations wants failed transactions quickly because failed transactions may need investigation or retry.
The DBA wants Oracle to understand that FAILED is rare and SUCCESS is common.
```

# Slide 5 - Histogram Demo Story (9:25 AM - 9:45 AM)

## Time: 9:25 AM - 9:45 AM

## Slide Content

# Banking Histogram Demo

We will compare the same query before and after a histogram.

Data pattern:

```text
SUCCESS = 95,000 rows
FAILED  =  5,000 rows
```

This is skewed data.

DBA question:

```text
Does Oracle understand that FAILED is much less common than SUCCESS?
```

What to compare:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

Final teaching line:

```text
Histogram helps Oracle understand uneven banking data, so it can estimate rows better and choose a smarter execution plan.
```

---

# Part 0 - Setup Bank Table

Why this step matters:

```text
The table models a realistic banking pattern: most transactions succeed, only some fail.
```

```sql
DROP TABLE bank_txn_demo PURGE;

CREATE TABLE bank_txn_demo AS
SELECT
  LEVEL txn_id,
  CASE
    WHEN LEVEL <= 95000 THEN 'SUCCESS'
    ELSE 'FAILED'
  END txn_status,
  ROUND(DBMS_RANDOM.VALUE(100, 50000), 2) amount
FROM dual
CONNECT BY LEVEL <= 100000;
```

Meaning:

```text
SUCCESS = 95,000 rows
FAILED  = 5,000 rows
```

---

# Part 1 - Create Index

Why this step matters:

```text
The failed-transaction query filters by transaction status.
The index gives Oracle an access path if it decides the filter is selective enough.
```

```sql
CREATE INDEX idx_bank_txn_status
ON bank_txn_demo(txn_status);
```

---

# Part 2 - Gather Stats Without Histogram

Why this step matters:

```text
This creates normal column statistics but intentionally prevents a histogram.
SIZE 1 means no histogram.
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'BANK_TXN_DEMO',
    method_opt => 'FOR COLUMNS SIZE 1 txn_status'
  );
END;
/
```

---

# Part 3 - Confirm Histogram Is None

Why this step matters:

```text
The DBA verifies the test condition before running the query.
Oracle has basic stats, but it does not know SUCCESS is very common and FAILED is rare.
```

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

Expected:

```text
TXN_STATUS    NONE
```

---

# Part 4 - Run Failed Transaction Query Before Histogram

Why this step matters:

```text
This shows how Oracle estimates and executes the failed-transaction lookup before it has value-distribution detail.
```

```sql
SELECT /* hist_demo_failed_before */
       *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

Find the exact cursor:

```sql
COLUMN hist_sql_id NEW_VALUE hist_sql_id
COLUMN hist_child_no NEW_VALUE hist_child_no

SELECT sql_id AS hist_sql_id,
       child_number AS hist_child_no,
       plan_hash_value,
       executions,
       buffer_gets,
       rows_processed,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%hist_demo_failed_before%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC
FETCH FIRST 1 ROW ONLY;
```

Check the runtime plan:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&hist_sql_id',
    &&hist_child_no,
    'ALLSTATS LAST'
  )
);
```

Explain:

```text
Before histogram, Oracle may estimate rows wrongly because it assumes values are evenly spread.
Compare E-Rows with A-Rows.
```

---

# Part 5 - Create Histogram

Why this step matters:

```text
Now Oracle learns the real distribution of transaction status values.
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'BANK_TXN_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 txn_status'
  );
END;
/
```

---

# Part 6 - Confirm Histogram Created

Why this step matters:

```text
The DBA confirms the optimizer has frequency information before comparing the second plan.
```

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

Expected:

```text
TXN_STATUS    FREQUENCY
```

---

# Part 7 - Run Same Query After Histogram

Why this step matters:

```text
The SQL is logically the same, but Oracle now has better information about the status distribution.
```

```sql
SELECT /* hist_demo_failed_after */
       *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

Find the exact cursor:

```sql
COLUMN hist_sql_id NEW_VALUE hist_sql_id
COLUMN hist_child_no NEW_VALUE hist_child_no

SELECT sql_id AS hist_sql_id,
       child_number AS hist_child_no,
       plan_hash_value,
       executions,
       buffer_gets,
       rows_processed,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%hist_demo_failed_after%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC
FETCH FIRST 1 ROW ONLY;
```

Check the runtime plan:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&hist_sql_id',
    &&hist_child_no,
    'ALLSTATS LAST'
  )
);
```

Compare:

```text
Before histogram: Oracle guessed distribution.
After histogram : Oracle knows FAILED is rare.
```

---

# SECTION 4 - PLAN REGRESSION SCENARIO (9:45 - 9:50)

Banking scenario:

```text
The overnight payment settlement job normally finishes before branches open.
After a statistics refresh, the same payment query takes much longer and delays operational reporting.
```

# Slide 6 - Banking Plan Regression Scenario (9:45 AM - 9:50 AM)

## Time: 9:45 AM - 9:50 AM

## Slide Content

# Payment Settlement Regression

Payment settlement query:

```text
Yesterday: 1 second
Today:    40 seconds
```

Possible causes:

* statistics refresh
* data growth
* data skew
* new or missing histogram
* new index or dropped index
* bind value change
* optimizer parameter change
* database patch or upgrade

Technical question:

```text
Did Oracle choose a different plan, and why?
```

---

## Trainer Delivery

"This is one of the most serious production problems.

Nothing obvious changed in the application.

But Oracle may have chosen a different plan.

SQL Plan Management helps us stabilize known good plans for critical SQL."

---

# SECTION 5 - SQL PLAN MANAGEMENT MENTAL MODEL (9:50 - 10:00)

Banking scenario:

```text
The DBA finds yesterday's plan was good and today's plan is risky.
The bank needs a controlled way to keep using the known good plan while investigating the root cause.
```

# Slide 7 - What SPM Does (9:50 AM - 9:53 AM)

## Time: 9:50 AM - 9:53 AM

## Slide Content

# SQL Plan Management For Critical Banking SQL

SPM is a safety control for important SQL:

* capture known plans
* store accepted plans
* avoid unverified plan changes
* evolve better plans safely
* stabilize critical SQL

Core idea:

```text
Do not let critical payment SQL suddenly switch to an untested plan.
```

DBA benefit:

```text
stabilize production first, then tune with evidence
```

---

# Slide 8 - Key Terms (9:53 AM - 9:56 AM)

## Time: 9:53 AM - 9:56 AM

## Slide Content

Real example:

```text
One payment settlement SQL can have one SQL handle and multiple possible plan names.
```

| Term | Meaning |
| ---- | ------- |
| SQL handle | identifier for the SQL statement |
| Plan name | identifier for one plan |
| Enabled | plan is available for use |
| Accepted | plan is approved for use |
| Fixed | stronger preference for a specific plan |
| Evolved | tested and accepted as better or safe |

---

## Trainer Delivery

"Enabled means Oracle can consider the plan.

Accepted means the plan is approved.

Fixed means stronger preference.

In production, fixed plans can be useful during emergencies, but they can also block better plans later."

---

# Slide 9 - When To Use Baselines (9:56 AM - 10:00 AM)

## Time: 9:56 AM - 10:00 AM

## Slide Content

Use SPM when plan stability protects the business.

Good candidates:

* payment settlement
* fund transfer posting
* end-of-day batch
* regulatory reports
* critical dashboard SQL
* SQL that regressed after stats refresh or upgrade

Poor candidates:

* badly written SQL that should be fixed
* queries returning unnecessary data
* locking problems
* I/O bottlenecks unrelated to plan
* every SQL in the database

DBA rule:

```text
Baseline critical SQL, not every SQL.
```

---

# SECTION 6 - LAB SETUP: PAYMENT WORKLOAD (10:00 - 10:10)

Banking scenario:

```text
We create a small version of a payment settlement table.
Most payments are already settled, while a smaller set is pending or failed.
The pending-today query represents the SQL operations staff cares about.
```

# Slide 10 - Lab Objective (10:00 AM - 10:10 AM)

## Time: 10:00 AM - 10:10 AM

## Slide Content

Lab 9 story:

```text
Build a payment workload, prove the important query has a good plan, then preserve that plan.
```

What each setup step means:

1. Create the table so we have a controlled payment workload.
2. Insert realistic status distribution: mostly settled, some pending and failed.
3. Create the index a DBA would expect for status/date lookup.
4. Gather histogram stats so Oracle understands the status distribution.
5. Validate the setup before trusting any plan result.

DBA benefit:

```text
You learn to build evidence before touching production SQL.
```

---

# Step 1 - Drop And Create Payments Table

Why this step matters:

```text
The table represents payment settlement records that operations query during the day.
Dropping and recreating keeps every classroom run predictable.
```

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE payments PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE payments (
    payment_id       NUMBER PRIMARY KEY,
    customer_id      NUMBER,
    account_id       NUMBER,
    branch_id        NUMBER,
    settlement_date  DATE,
    amount           NUMBER(12,2),
    status           VARCHAR2(20),
    created_date     DATE
);
```

---

# Step 2 - Insert Payment Data

This is sized to work on normal classroom machines.

Why this step matters:

```text
Most banking payments are already settled; only a smaller subset needs active investigation.
That status imbalance lets us discuss selectivity and histograms later.
```

```sql
BEGIN
  FOR i IN 1..200000 LOOP
    INSERT INTO payments (
      payment_id,
      customer_id,
      account_id,
      branch_id,
      settlement_date,
      amount,
      status,
      created_date
    )
    VALUES (
      i,
      MOD(i,5000) + 1,
      MOD(i,20000) + 1,
      MOD(i,50) + 1,
      TRUNC(SYSDATE) - MOD(i,30),
      ROUND(DBMS_RANDOM.VALUE(100,100000),2),
      CASE
        WHEN MOD(i,20) = 0 THEN 'PENDING'
        WHEN MOD(i,20) = 1 THEN 'FAILED'
        ELSE 'SETTLED'
      END,
      SYSDATE - MOD(i,60)
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;
```

Expected distribution:

```text
SETTLED = most rows
PENDING = around 5%
FAILED  = around 5%
```

---

# Step 3 - Create Supporting Index

Why this step matters:

```text
The business query filters by payment status and settlement date.
A DBA checks whether an index supports the business access pattern.
```

```sql
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);
```

---

# Step 4 - Gather Statistics With Histogram

Why this step matters:

```text
Without fresh stats, Oracle may guess incorrectly.
The histogram helps Oracle understand that SETTLED is common while PENDING and FAILED are less common.
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'PAYMENTS',
    method_opt => 'FOR COLUMNS SIZE 254 status',
    cascade    => TRUE
  );
END;
/
```

---

# Step 5 - Validate Setup

Why this step matters:

```text
Before discussing plans, the DBA first proves the data pattern and statistics are what the lab expects.
```

```sql
SELECT status, COUNT(*) AS row_count
FROM payments
GROUP BY status
ORDER BY status;

SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'PAYMENTS'
AND column_name = 'STATUS';
```

---

# SECTION 7 - LAB 9: CAPTURE SQL PLAN BASELINE (10:10 - 10:25)

Banking scenario:

```text
The payment query is business-critical.
The DBA wants to capture the known good plan so a future stats refresh, patch, or index change does not silently replace it with a bad plan.
```

# Slide 11 - Critical SQL (10:10 AM - 10:25 AM)

## Time: 10:10 AM - 10:25 AM

## Slide Content

# Payment Query To Protect

Operations asks:

```text
How many payments are still pending for today's settlement date?
```

```sql
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE)
```

Why the DBA cares:

```text
If this query slows down, payment monitoring and settlement confirmation slow down.
```

---

# Step 1 - Run Critical SQL

Use `COUNT(*)` first to avoid printing many rows.

Why this step matters:

```text
First execute the exact SQL shape we want to protect.
Oracle can only capture a plan that has actually been parsed and executed.
```

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

Expected:

```text
The index IDX_PAYMENTS_STATUS_DATE should be a good candidate access path.
```

Trainer note:

The exact operation may vary, but with this data and index Oracle should usually use the status/date index or an efficient index-based path.

---

# Step 2 - Find SQL ID, Child Number And Plan Hash

Do this before displaying the runtime plan. In SQL Developer, `DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,...)` may pick an internal SQL Developer cursor instead of the payment query.

Why this step matters:

```text
SQL ID identifies the statement.
Child number identifies the specific cursor.
Plan hash identifies the execution plan.
Together they let the DBA point at the exact plan, not a guess.
```

```sql
COLUMN spm_sql_id NEW_VALUE spm_sql_id
COLUMN spm_child_no NEW_VALUE spm_child_no
COLUMN spm_plan_hash NEW_VALUE spm_plan_hash

SELECT sql_id AS spm_sql_id,
       child_number AS spm_child_no,
       plan_hash_value AS spm_plan_hash,
       executions,
       buffer_gets,
       disk_reads,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%day3_spm_payment_pending%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC
FETCH FIRST 1 ROW ONLY;
```

Confirm:

```sql
SELECT '&&spm_sql_id' AS sql_id,
       '&&spm_child_no' AS child_number,
       '&&spm_plan_hash' AS plan_hash_value
FROM dual;
```

---

# Step 3 - Display Captured Runtime Plan

Use the captured cursor values instead of `NULL,NULL`.

Why this step matters:

```text
The DBA must inspect the actual runtime plan before preserving it.
Never baseline a plan just because the SQL is important.
```

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&spm_sql_id',
    &&spm_child_no,
    'ALLSTATS LAST +PREDICATE +NOTE'
  )
);
```

---

# Step 4 - Load Plan From Cursor Cache

Why this step matters:

```text
This is the moment we tell Oracle: this observed plan is approved for this SQL.
```

```sql
DECLARE
  l_plans_loaded PLS_INTEGER;
BEGIN
  l_plans_loaded := DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(
    sql_id          => '&&spm_sql_id',
    plan_hash_value => &&spm_plan_hash
  );

  DBMS_OUTPUT.PUT_LINE('Plans loaded: ' || l_plans_loaded);
END;
/
```

Expected:

```text
Plans loaded: 1
```

If plans loaded is `0`:

* rerun the SQL
* confirm SQL ID
* confirm plan hash value
* check package privileges
* avoid changing SQL text between execution and capture

---

# Step 5 - View SQL Plan Baseline

Why this step matters:

```text
Production DBAs verify every change.
The baseline view proves whether the plan was captured, enabled, accepted, and fixed or not fixed.
```

```sql
SELECT sql_handle,
       plan_name,
       enabled,
       accepted,
       fixed,
       created,
       last_executed
FROM dba_sql_plan_baselines
WHERE creator = USER
ORDER BY created DESC
FETCH FIRST 10 ROWS ONLY;
```

If `CREATOR` column is unavailable in your environment, use:

```sql
SELECT sql_handle,
       plan_name,
       enabled,
       accepted,
       fixed,
       created,
       last_executed
FROM dba_sql_plan_baselines
ORDER BY created DESC
FETCH FIRST 10 ROWS ONLY;
```

Record:

* SQL handle
* plan name
* enabled
* accepted
* fixed

---

# Step 6 - Rerun Same SQL And Check Baseline Note

Why this step matters:

```text
The rerun proves Oracle can still execute the SQL and that the accepted baseline is available.
```

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

Refresh the captured cursor values:

```sql
COLUMN spm_sql_id NEW_VALUE spm_sql_id
COLUMN spm_child_no NEW_VALUE spm_child_no
COLUMN spm_plan_hash NEW_VALUE spm_plan_hash

SELECT sql_id AS spm_sql_id,
       child_number AS spm_child_no,
       plan_hash_value AS spm_plan_hash,
       executions,
       buffer_gets,
       disk_reads,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%day3_spm_payment_pending%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC
FETCH FIRST 1 ROW ONLY;
```

Then display the exact cursor:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&spm_sql_id',
    &&spm_child_no,
    'ALLSTATS LAST +PREDICATE +NOTE'
  )
);
```

Look for note:

```text
SQL plan baseline
```

Trainer note:

The note text can vary by version. The important check is that the baseline exists and the accepted plan is available for the SQL.

---

# Step 7 - SPM Worksheet

| Item | Observation |
| ---- | ----------- |
| SQL ID | |
| Child number | |
| Plan hash value | |
| Plans loaded | |
| SQL handle | |
| Plan name | |
| Enabled | |
| Accepted | |
| Fixed | |
| Baseline note visible? | |

---

# SECTION 8 - EVOLUTION, FIXED BASELINES & SAFETY (10:25 - 10:30)

Banking scenario:

```text
Two weeks later, a new index is added for payment reporting.
Oracle discovers a new plan for the settlement query.
The DBA must decide whether the new plan is actually better before allowing production to use it.
```

# Slide 12 - Plan Evolution (10:25 AM - 10:27 AM)

## Time: 10:25 AM - 10:27 AM

## Slide Content

# Plan Evolution

```text
Test new candidate plan before accepting it.
```

Banking example:

```text
The old plan is stable.
The new plan might be faster after a new reporting index.
SPM lets the DBA test before trusting it.
```

Use when:

* new plan appears after stats refresh
* new index creates a possible better plan
* upgrade introduces new optimizer choices
* you want improvement without surprise regression

DBA benefit:

```text
improvement without surprise regression
```

---

# Optional - Evolve Report

Use a SQL handle from the baseline query.

Why this step matters:

```text
The evolve report shows whether Oracle considers another plan safe to accept.
It is a review artifact a DBA can attach to a change ticket.
```

```sql
SET LONG 1000000

SELECT DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
         sql_handle => 'sql_handle_here'
       ) AS evolve_report
FROM dual;
```

Trainer note:

This is optional because the lab may not have a second candidate plan. Use it to show the workflow and report format.

---

# Slide 13 - Fixed Baselines (10:27 AM - 10:30 AM)

## Time: 10:27 AM - 10:30 AM

## Slide Content

# Fixed Baselines

```text
stronger preference for a specific accepted plan
```

Banking emergency example:

```text
A salary credit batch is running slowly after a patch.
The DBA temporarily fixes the known good plan to restore service.
```

Use carefully for:

* emergency regression stabilization
* critical payment or batch SQL
* short-term production containment

Risk:

```text
May block better future plans.
```

DBA rule:

```text
Use fixed baselines as containment, not as permanent tuning by default.
```

---

# Production Safety Checklist

Before using SPM in production:

* confirm SQL is business-critical
* capture known good plan
* compare old and new plans
* verify required indexes exist
* test in non-production
* document SQL handle and plan name
* define rollback
* review baselines periodically

Banking change-control note:

```text
For payment, ledger, or regulatory SQL, document why the baseline exists and how to remove it safely.
```

---

# Optional - Baseline Rollback Example

Use the SQL handle and plan name from the baseline view.

Why this step matters:

```text
Every production plan-control change needs a rollback path.
```

```sql
DECLARE
  l_dropped PLS_INTEGER;
BEGIN
  l_dropped := DBMS_SPM.DROP_SQL_PLAN_BASELINE(
    sql_handle => 'sql_handle_here',
    plan_name  => 'plan_name_here'
  );

  DBMS_OUTPUT.PUT_LINE('Baselines dropped: ' || l_dropped);
END;
/
```

Trainer note:

Do not run this unless you intentionally want to remove the lab baseline. It is included because production SPM changes need rollback planning.

---

# SLOT 2 - BIND PEEKING, ADAPTIVE CURSOR SHARING, HINTS & SQL PROFILES

## 10:45 AM - 12:00 PM

# SECTION 9 - BIND PEEKING MENTAL MODEL (10:45 - 11:00)

Banking scenario:

```text
The application uses one branch report SQL with a bind variable.
For the head-office branch it returns many rows.
For a small rural branch it returns very few rows.
The SQL text is the same, but the best plan may be different.
```

# Slide 14 - Same SQL, Different Values (10:45 AM - 10:52 AM)

## Time: 10:45 AM - 10:52 AM

## Slide Content

# Same SQL, Different Branch Size

```sql
SELECT ...
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

Banking example:

```text
branch_id = 1 -> head office branch, many transactions
branch_id = 3 -> small branch, few transactions
```

Problem:

```text
One plan may not be good for every value.
```

DBA benefit:

```text
understand why a query can be fast for one branch and slow for another
```

---

## Trainer Delivery

"Bind variables are good for scalability.

They reduce hard parsing and help SQL reuse.

But if data is skewed, different bind values may need different plans.

That is where bind peeking and adaptive cursor sharing become important."

---

# Slide 15 - Key Concepts (10:52 AM - 11:00 AM)

## Time: 10:52 AM - 11:00 AM

## Slide Content

What the DBA is trying to prove:

```text
Is Oracle choosing one reusable plan, or can it adapt when bind values return very different row counts?
```

| Concept | Meaning |
| ------- | ------- |
| Bind peeking | optimizer looks at bind value during hard parse |
| Skewed data | values are not evenly distributed |
| Bind sensitive | Oracle notices bind values may matter |
| Bind aware | Oracle may use different child cursors/plans |
| Histogram | stats object showing value distribution |

Banking translation:

```text
Histograms help Oracle know that not every branch_id has the same transaction volume.
```

---

# SECTION 10 - LAB 10: BIND VARIABLES AND ADAPTIVE CURSOR SHARING (11:00 - 11:35)

Banking scenario:

```text
The branch transaction report is parameterized.
Users pass one branch_id at a time.
The DBA must explain why a query for a large branch needs a different access pattern than a query for a small branch.
```

# Slide 16 - Lab Objective (11:00 AM - 11:35 AM)

## Time: 11:00 AM - 11:35 AM

## Slide Content

Lab 10 story:

```text
Create one large branch, one medium branch, and one small branch.
Then run the same bind SQL for different branches and inspect Oracle's cursor behavior.
```

What each step means:

1. create skewed branch transaction data
2. gather stats with histogram
3. run the same bind SQL for rare and common values
4. inspect plans
5. inspect child cursors
6. discuss hints and why one forced plan can be unsafe

DBA benefit:

```text
recognize when the problem is not the SQL text, but the bind value and data distribution
```

---

# Step 1 - Drop And Create Branch Transactions

Why this step matters:

```text
This table models transaction activity by branch.
It gives us a clean place to demonstrate skew without depending on prior lab data.
```

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE branch_transactions PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE branch_transactions (
    transaction_id    NUMBER PRIMARY KEY,
    branch_id         NUMBER NOT NULL,
    customer_id       NUMBER,
    account_id        NUMBER,
    transaction_date  DATE,
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(100)
);
```

---

# Step 2 - Insert Skewed Data

This uses set-based inserts for speed.

Why this step matters:

```text
Real banks do not have equal traffic in every branch.
Head office or city branches may process hundreds of times more transactions than small branches.
```

Branch 1: large branch.

```sql
INSERT /*+ APPEND */ INTO branch_transactions
SELECT LEVEL,
       1,
       MOD(LEVEL,50000) + 1,
       MOD(LEVEL,100000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       CASE WHEN MOD(LEVEL,5) = 0 THEN 'FAILED' ELSE 'SUCCESS' END,
       'large branch'
FROM dual
CONNECT BY LEVEL <= 300000;

COMMIT;
```

Branch 2: medium branch.

```sql
INSERT /*+ APPEND */ INTO branch_transactions
SELECT 300000 + LEVEL,
       2,
       MOD(LEVEL,50000) + 1,
       MOD(LEVEL,100000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       'SUCCESS',
       'medium branch'
FROM dual
CONNECT BY LEVEL <= 5000;

COMMIT;
```

Branch 3: small branch.

```sql
INSERT /*+ APPEND */ INTO branch_transactions
SELECT 305000 + LEVEL,
       3,
       MOD(LEVEL,50000) + 1,
       MOD(LEVEL,100000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       'SUCCESS',
       'small branch'
FROM dual
CONNECT BY LEVEL <= 500;

COMMIT;
```

---

# Step 3 - Create Index And Gather Histogram Stats

Why this step matters:

```text
The index gives Oracle an efficient path for selective branch lookups.
The histogram tells Oracle that branch_id values are not evenly distributed.
```

```sql
CREATE INDEX idx_branch_txn_branch
ON branch_transactions(branch_id);
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'BRANCH_TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 254 branch_id',
    cascade    => TRUE
  );
END;
/
```

---

# Step 4 - Verify Distribution And Histogram

Why this step matters:

```text
Before blaming bind peeking or ACS, the DBA proves the data is actually skewed.
```

```sql
SELECT branch_id,
       COUNT(*) AS txn_count
FROM branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

Expected:

```text
BRANCH_ID 1 = 300000 rows
BRANCH_ID 2 =   5000 rows
BRANCH_ID 3 =    500 rows
```

Check histogram:

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

Expected:

```text
HISTOGRAM = FREQUENCY
```

---

# Step 5 - Prepare Bind Variable

Why this step matters:

```text
Applications normally send bind variables, not hard-coded branch values.
This step makes the lab behave more like application SQL.
```

```sql
VARIABLE b_branch_id NUMBER
```

Run the same SQL shape with different values. Use aggregate queries to avoid printing rows while still requiring table access.

---

# Step 6 - Rare Value First

Why this step matters:

```text
Branch 3 has few rows.
An index access path may be efficient because Oracle can find a small subset quickly.
```

```sql
EXEC :b_branch_id := 3;

SELECT /* day3_bind_branch_demo */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

Expected:

```text
Branch 3 is selective. Index access may be appropriate.
```

---

# Step 7 - Common Value

Why this step matters:

```text
Branch 1 has many rows.
A full scan may be cheaper than using an index to visit many table rows one by one.
```

```sql
EXEC :b_branch_id := 1;

SELECT /* day3_bind_branch_demo */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

Expected:

```text
Branch 1 returns most rows. Full scan may be better than many table lookups.
```

Trainer note:

Oracle may reuse the first plan initially. Adaptive cursor sharing may require repeated executions before creating alternate child cursors.

---

# Step 8 - Repeat Executions To Encourage ACS

Use this simple repeatable SQL*Plus script:

Why this step matters:

```text
Adaptive Cursor Sharing may need repeated executions before Oracle decides bind values deserve different child cursors.
```

```sql
EXEC :b_branch_id := 3
SELECT /* day3_bind_branch_demo */ SUM(amount) FROM branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 1
SELECT /* day3_bind_branch_demo */ SUM(amount) FROM branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 3
SELECT /* day3_bind_branch_demo */ SUM(amount) FROM branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 1
SELECT /* day3_bind_branch_demo */ SUM(amount) FROM branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 2
SELECT /* day3_bind_branch_demo */ SUM(amount) FROM branch_transactions WHERE branch_id = :b_branch_id;
```

---

# Step 9 - Inspect Child Cursors

Why this step matters:

```text
Child cursors show whether Oracle is treating the same SQL differently for different bind patterns.
This is key evidence in a production bind-sensitivity investigation.
```

```sql
SELECT sql_id,
       child_number,
       plan_hash_value,
       executions,
       is_bind_sensitive,
       is_bind_aware,
       buffer_gets,
       rows_processed,
       SUBSTR(sql_text,1,90) sql_text
FROM v$sql
WHERE sql_text LIKE '%day3_bind_branch_demo%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY sql_id, child_number;
```

If multiple child cursors appear, inspect each:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    'sql_id_here',
    child_number_here,
    'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

---

# Step 10 - If Bind Aware Does Not Appear

This is normal in short labs.

DBA lesson:

```text
Do not force a conclusion.
If ACS does not appear, use the evidence available: row counts, histogram, plan shape, buffers, and peeked binds.
```

Possible reasons:

* not enough executions
* optimizer chose one acceptable plan
* ACS did not need another child cursor
* cursor cache behavior changed
* environment settings differ
* data volume is still too small

Do not fake it.

Use the evidence you do have:

* branch 1 row count vs branch 3 row count
* E-Rows vs A-Rows
* buffers
* peeked binds
* child cursor flags

---

# Step 11 - Bind Lab Worksheet

Why this step matters:

```text
The worksheet turns the lab into a production-style evidence record.
```

| Item | Observation |
| ---- | ----------- |
| Branch 1 rows | |
| Branch 2 rows | |
| Branch 3 rows | |
| Histogram exists? | |
| Plan for branch 3 | |
| Plan for branch 1 | |
| SQL ID | |
| Child cursors | |
| Bind sensitive? | |
| Bind aware? | |
| Peeked bind visible? | |

---

# SECTION 11 - HINTS, PROFILES, BASELINES, INDEXES (11:35 - 11:50)

Banking scenario:

```text
An application team asks the DBA to add an INDEX hint because the small-branch report is fast with the index.
The DBA must test whether that same hint damages the head-office branch report.
```

# Slide 17 - Why Hints Are Risky With Skew (11:35 AM - 11:43 AM)

## Time: 11:35 AM - 11:43 AM

## Slide Content

# Hint Risk With Uneven Branch Traffic

Forced index plan:

```sql
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

May help:

```text
small branch -> few rows -> index can be efficient
```

May hurt:

```text
large branch -> many rows -> index can cause excessive table lookups
```

DBA rule:

```text
A hint that fixes one bind value can break another bind value.
```

---

# Hint Demonstration

Compare forced full scan and forced index for both branch values:

Why this step matters:

```text
The DBA proves that hints are not magic.
The same forced access path can be good for one data pattern and bad for another.
```

```sql
EXEC :b_branch_id := 3

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_branch_id := 1

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

Then compare full scan hint:

```sql
EXEC :b_branch_id := 3

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_branch_id := 1

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

Ask:

* Which hint helps the rare value?
* Which hint helps the common value?
* Why can one forced plan be unsafe?

Banking discussion:

```text
Would you hard-code an INDEX hint into a shared branch report used by every branch?
What happens on month-end when large branches process even more rows?
```

---

# Slide 18 - Tool Selection Table (11:43 AM - 11:50 AM)

## Time: 11:43 AM - 11:50 AM

## Slide Content

# Choose The Tool Based On Root Cause

| Problem | Better Tool |
| ------- | ----------- |
| Missing access path | Index |
| Wrong estimate from skew | Histogram or SQL Profile |
| Sudden plan regression | SQL Plan Baseline |
| Need emergency plan control | Baseline or targeted hint |
| Application SQL cannot change | Profile or baseline |
| Bad query logic | Rewrite SQL |
| Different bind values need different plans | ACS, histogram, query design |

Banking examples:

| Banking symptom | Better DBA response |
| --------------- | ------------------- |
| Payment query changed plan after stats refresh | Consider SQL plan baseline |
| Branch report wrong estimate because one branch is huge | Check histogram and bind behavior |
| Query returns too much history | Rewrite SQL with business filters |
| Emergency batch must finish tonight | Temporary baseline or targeted hint with rollback |

---

## Trainer Delivery

"Do not use one tool for every problem.

Hints, profiles, baselines, indexes, and histograms solve different problems.

The senior DBA skill is matching the tool to the root cause."

---

# SECTION 12 - MORNING SUMMARY (11:50 - 12:00)

Banking scenario:

```text
The incident bridge asks for a clear DBA recommendation.
The DBA must explain whether the issue is plan regression, bind skew, missing stats, unsafe hints, or bad SQL design.
```

# Slide 19 - Key Takeaways (11:50 AM - 12:00 PM)

## Time: 11:50 AM - 12:00 PM

## Slide Content

# DBA Decision Framework

For banking SQL:

1. Confirm the business impact.
2. Identify the exact SQL ID and child cursor.
3. Read the runtime plan before changing anything.
4. Check whether the problem is plan regression or bind-value skew.
5. Use histograms to help Oracle understand uneven data.
6. Use baselines for critical plan stability.
7. Use hints mainly for diagnosis or short-term containment.
8. Document rollback for every plan-control change.

Main lesson:

```text
Do not guess. Preserve stability, prove the root cause, then choose the smallest safe fix.
```

---

## Trainer Delivery

"The main message is stability with evidence.

Do not baseline everything.

Do not hint everything.

Do not assume one plan is good for every bind value.

Read the data distribution, runtime plan, and cursor behavior.

In a bank, tuning is not just about making SQL faster.

It is about protecting settlement, reporting, customer service, and audit reliability."

---

# TRANSITION TO DAY 3 SECOND HALF

## Next Topics

* locking
* blocking sessions
* concurrency
* short-lived performance problems
* final banking case study

Closing line:

```text
Plan stability solves plan surprises.
Bind diagnosis solves value-specific surprises.
Concurrency diagnosis solves waiting-on-other-sessions surprises.
```
