# Day 3 - FIRST HALF (FINAL ENTERPRISE VERSION)

## 9:00 AM - 12:00 PM

# SQL Plan Management, Bind Peeking, Adaptive Cursor Sharing & Plan Control

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* explain why a good SQL can suddenly become slow without SQL text changes
* capture and inspect SQL plan baselines
* understand when SQL Plan Management helps and when it hides the real issue
* distinguish SQL plan baselines, SQL Profiles, hints, indexes, and histograms
* demonstrate skewed data with bind variables
* inspect bind-sensitive and bind-aware cursors
* understand why one execution plan may not fit every bind value
* use hints carefully for diagnosis, not as the first production fix

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
| 9:00 - 9:10   | Day 3 opening and plan regression scenario         |
| 9:10 - 9:25   | SQL Plan Management mental model                   |
| 9:25 - 9:45   | Lab setup: payment workload                        |
| 9:45 - 10:15  | Lab 9: capture and inspect SQL plan baseline       |
| 10:15 - 10:30 | Plan evolution, fixed baselines, production safety |
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

# SLOT 1 - SQL PLAN MANAGEMENT

## 9:00 AM - 10:30 AM

# SECTION 1 - PLAN REGRESSION SCENARIO (9:00 - 9:10)

# Slide 1 - Day 3 Opening

## Slide Content

# Advanced Production Tuning

Day 3 focuses on:

* plan regression
* plan stability
* SQL Plan Management
* bind peeking
* adaptive cursor sharing
* hints and SQL Profiles
* locking and concurrency later today

---

## Trainer Delivery

"Day 1 taught us how to read SQL and plans.

Day 2 taught us how to diagnose workload with AWR, ADDM, and advisors.

Day 3 is about production behavior:

SQL was fast yesterday.

SQL is slow today.

The SQL text did not change.

Now we need to understand plan stability, bind values, and concurrency."

---

# Slide 2 - Banking Plan Regression Scenario

## Slide Content

# Scenario

Payment settlement query:

```text
Yesterday: 1 second
Today:    40 seconds
```

Possible cause:

```text
Same SQL, different execution plan
```

Why plan may change:

* statistics refresh
* new index
* dropped index
* data growth
* data skew
* bind value change
* optimizer parameter change
* database patch or upgrade

---

## Trainer Delivery

"This is one of the most serious production problems.

Nothing obvious changed in the application.

But Oracle may have chosen a different plan.

SQL Plan Management helps us stabilize known good plans for critical SQL."

---

# SECTION 2 - SQL PLAN MANAGEMENT MENTAL MODEL (9:10 - 9:25)

# Slide 3 - What SPM Does

## Slide Content

# SQL Plan Management

SPM helps Oracle:

* capture known plans
* store accepted plans
* avoid unverified plan changes
* evolve better plans safely
* stabilize critical SQL

Core idea:

```text
Use approved plans unless a better plan is verified.
```

---

# Slide 4 - Key Terms

## Slide Content

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

# Slide 5 - When To Use Baselines

## Slide Content

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

---

# SECTION 3 - LAB SETUP: PAYMENT WORKLOAD (9:25 - 9:45)

# Slide 6 - Lab Objective

## Slide Content

We will:

1. create a payment table
2. create a useful index
3. run a critical payment query
4. capture its SQL ID and plan
5. load the plan into SPM
6. verify the baseline exists
7. rerun and check plan notes

---

# Step 1 - Drop And Create Payments Table

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

```sql
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);
```

---

# Step 4 - Gather Statistics With Histogram

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

# SECTION 4 - LAB 9: CAPTURE SQL PLAN BASELINE (9:45 - 10:15)

# Slide 7 - Critical SQL

## Slide Content

Payment settlement query:

```sql
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE)
```

This represents a business-critical settlement workload.

---

# Step 1 - Run Critical SQL

Use `COUNT(*)` first to avoid printing many rows.

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

# SECTION 5 - EVOLUTION, FIXED BASELINES & SAFETY (10:15 - 10:30)

# Slide 8 - Plan Evolution

## Slide Content

Plan evolution means:

```text
Test new candidate plan before accepting it.
```

Use when:

* new plan appears after stats refresh
* new index creates a possible better plan
* upgrade introduces new optimizer choices
* you want improvement without surprise regression

---

# Optional - Evolve Report

Use a SQL handle from the baseline query.

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

# Slide 9 - Fixed Baselines

## Slide Content

Fixed baseline:

```text
stronger preference for a specific accepted plan
```

Use carefully for:

* emergency regression stabilization
* critical payment or batch SQL
* short-term production containment

Risk:

```text
May block better future plans.
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

---

# Optional - Baseline Rollback Example

Use the SQL handle and plan name from the baseline view.

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

# SECTION 6 - BIND PEEKING MENTAL MODEL (10:45 - 11:00)

# Slide 10 - Same SQL, Different Values

## Slide Content

Same SQL:

```sql
SELECT ...
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

Different values:

```text
branch_id = 1 -> many rows
branch_id = 3 -> few rows
```

Problem:

```text
One plan may not be good for every value.
```

---

## Trainer Delivery

"Bind variables are good for scalability.

They reduce hard parsing and help SQL reuse.

But if data is skewed, different bind values may need different plans.

That is where bind peeking and adaptive cursor sharing become important."

---

# Slide 11 - Key Concepts

## Slide Content

| Concept | Meaning |
| ------- | ------- |
| Bind peeking | optimizer looks at bind value during hard parse |
| Skewed data | values are not evenly distributed |
| Bind sensitive | Oracle notices bind values may matter |
| Bind aware | Oracle may use different child cursors/plans |
| Histogram | stats object showing value distribution |

---

# SECTION 7 - LAB 10: BIND VARIABLES AND SKEWED DATA (11:00 - 11:35)

# Slide 12 - Lab Objective

## Slide Content

We will:

1. create skewed branch transaction data
2. gather stats with histogram
3. run the same bind SQL for rare and common values
4. inspect plans
5. inspect child cursors
6. discuss hints and why one forced plan can be unsafe

---

# Step 1 - Drop And Create Branch Transactions

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

```sql
VARIABLE b_branch_id NUMBER
```

Run the same SQL shape with different values. Use aggregate queries to avoid printing rows while still requiring table access.

---

# Step 6 - Rare Value First

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

# SECTION 8 - HINTS, PROFILES, BASELINES, INDEXES (11:35 - 11:50)

# Slide 13 - Why Hints Are Risky With Skew

## Slide Content

Force index:

```sql
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

May be good for:

```text
branch_id = 3
```

May be bad for:

```text
branch_id = 1
```

---

# Hint Demonstration

Compare forced full scan and forced index for both branch values:

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

---

# Slide 14 - Tool Selection Table

## Slide Content

| Problem | Better Tool |
| ------- | ----------- |
| Missing access path | Index |
| Wrong estimate from skew | Histogram or SQL Profile |
| Sudden plan regression | SQL Plan Baseline |
| Need emergency plan control | Baseline or targeted hint |
| Application SQL cannot change | Profile or baseline |
| Bad query logic | Rewrite SQL |
| Different bind values need different plans | ACS, histogram, query design |

---

## Trainer Delivery

"Do not use one tool for every problem.

Hints, profiles, baselines, indexes, and histograms solve different problems.

The senior DBA skill is matching the tool to the root cause."

---

# SECTION 9 - MORNING SUMMARY (11:50 - 12:00)

# Slide 15 - Key Takeaways

## Slide Content

Day 3 morning lessons:

* SQL can regress because the plan changed
* SPM stores accepted plans for stability
* baselines are for critical SQL, not every SQL
* bind variables improve reuse but can expose skew problems
* histograms help Oracle understand skew
* adaptive cursor sharing may create multiple child cursors
* hints can help diagnosis but can be dangerous as a blanket fix

---

## Trainer Delivery

"The main message is stability with evidence.

Do not baseline everything.

Do not hint everything.

Do not assume one plan is good for every bind value.

Read the data distribution, runtime plan, and cursor behavior."

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
