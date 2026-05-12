# Day 2 - SECOND HALF (FINAL ENTERPRISE VERSION)

## 1:00 PM - 5:00 PM

# SQL Tuning Advisor, SQL Access Advisor & Memory/I/O Diagnosis

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* take a SQL ID from AWR/ADDM and run SQL Tuning Advisor
* capture before metrics before trusting advisor output
* read SQL Tuning Advisor recommendations safely
* understand SQL Profiles, index recommendations, statistics recommendations, and rewrite recommendations
* test advisor recommendations without blindly applying them
* understand how SQL Access Advisor differs from SQL Tuning Advisor
* analyze a workload, not only one SQL
* evaluate index/materialized-view recommendations against DML risk
* inspect memory and I/O symptoms using dynamic performance views

---

# HALF-DAY DESIGN PHILOSOPHY

This half day is intentionally:

* tool-driven
* practical
* evidence-first
* safe for production-thinking DBAs
* connected to AWR/ADDM from the morning

NOT:

* advisor-button-click training
* blind SQL Profile acceptance
* "create every suggested index"
* memory-parameter guessing

---

# FINAL TIME STRUCTURE

| Time          | Section                                      |
| ------------- | -------------------------------------------- |
| 1:00 - 1:10   | Advisor workflow from AWR/ADDM               |
| 1:10 - 1:30   | Create and capture a tunable SQL             |
| 1:30 - 2:05   | Lab 7: SQL Tuning Advisor                    |
| 2:05 - 2:25   | Validate recommendations and rollback        |
| 2:25 - 2:30   | Slot 3 summary                               |
| 2:45 - 3:05   | SQL Access Advisor and workload thinking     |
| 3:05 - 3:45   | Lab 8: workload access design                |
| 3:45 - 4:20   | SQL Access Advisor practical path            |
| 4:20 - 4:40   | Memory and I/O diagnosis mini-lab            |
| 4:40 - 4:55   | End-to-end Day 2 capstone                    |
| 4:55 - 5:00   | Day 2 close and Day 3 transition             |

---

# LICENSING AND PRIVILEGE NOTE

SQL Tuning Advisor and SQL Access Advisor are Oracle Tuning Pack features.

Before using them in a real bank environment, confirm:

* Tuning Pack license is approved
* Diagnostic Pack/Tuning Pack use is permitted on the training database
* the training user has advisor privileges
* recommendations will not be applied directly in production

Typical access needed:

```text
ADVISOR privilege
ADMINISTER SQL TUNING SET privilege for some workflows
SELECT_CATALOG_ROLE or access to V$SQL / DBA_ADVISOR_* views
EXECUTE on DBMS_SQLTUNE
EXECUTE on DBMS_ADVISOR
```

Trainer note:

If privileges are restricted, still run the manual validation parts. The learning goal is not only running the package. The learning goal is evaluating recommendations safely.

---

# COMMON SESSION SETTINGS

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TRIMSPOOL ON
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

---

# BEFORE STARTING

This file assumes Day 1 and Day 2 morning setup already created:

```text
CUSTOMERS
ACCOUNTS
TRANSACTIONS
```

Validate:

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('CUSTOMERS','ACCOUNTS','TRANSACTIONS')
ORDER BY table_name;
```

If a table is missing, run `01-Day/SECOND.md` setup first.

---

# SLOT 3 - SQL TUNING ADVISOR

## 1:00 PM - 2:30 PM

# SECTION 1 - WHERE SQL TUNING ADVISOR FITS (1:00 - 1:10)

# Slide 1 - Advisor Flow

## Slide Content

Use SQL Tuning Advisor after AWR/ASH/ADDM evidence points to one SQL.

For the low-memory Day 2 flow, use the SQL_ID and recommendation from:

```text
02-Day/MOCK-REPORT-INTERPRETATION-LAB.md
02-Day/mock-reports/sql_tuning_advisor_day2_mock.txt
```

Mock target SQL_ID:

```text
g8m1s9k2p6z0a
```

For a live workload flow, use the SQL_ID selected in:

```text
02-Day/REAL-WORLD-INCIDENT-LAB.md
```

The target variable from that lab is:

```text
&&incident_sql_id
```

Advisor flow:

```text
AWR identifies top SQL
  -> ASH confirms wait class / event / SQL_ID pressure
  -> ADDM recommends SQL tuning
  -> DBA captures current plan and metrics
  -> SQL Tuning Advisor analyzes SQL
  -> DBA validates recommendation
  -> change is tested and approved
```

---

## Trainer Delivery

"SQL Tuning Advisor is not the first tool for every slow system.

It is useful when AWR or ADDM has already pointed us to a specific SQL.

The advisor may suggest a SQL Profile, index, statistics gathering, or SQL rewrite.

But the DBA must prove the recommendation is safe."

Trainer note:

If the mock report lab is being used, teach this section by reading the mock SQL Tuning Advisor report and asking trainees to justify or reject the recommendation. If the real incident lab ran successfully, use `&&incident_sql_id` and the SQL Tuning Advisor section in `02-Day/REAL-WORLD-INCIDENT-LAB.md`. Use the standalone SQL below only as a fallback.

---

# Slide 2 - Recommendation Types

## Slide Content

SQL Tuning Advisor may recommend:

* SQL Profile
* index creation
* statistics gathering
* SQL restructuring
* alternative execution approach

Production question:

```text
Which recommendation is safe for this workload?
```

---

# SECTION 2 - CREATE A TUNABLE SQL (1:10 - 1:30)

# Slide 3 - Lab SQL Objective

## Slide Content

We will create one expensive reporting SQL:

* joins customers and transactions
* filters active customers
* aggregates transaction amount
* sorts by total amount
* is tagged for easy SQL ID discovery

---

# Step 1 - Confirm Supporting Data

```sql
SELECT 'CUSTOMERS' table_name, COUNT(*) row_count FROM customers
UNION ALL
SELECT 'TRANSACTIONS', COUNT(*) FROM transactions;
```

Recommended:

```text
CUSTOMERS    >= 100000
TRANSACTIONS >= 300000
```

---

# Step 2 - Capture Current Indexes

Before advisor recommendations, know the current structure.

```sql
SELECT table_name,
       index_name,
       visibility,
       uniqueness
FROM user_indexes
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name;
```

Trainer note:

This is important because advisor may recommend an index similar to an existing one. DBAs must check duplicates.

---

# Step 3 - Run Tagged SQL With Runtime Metrics

Use a wrapper query to avoid printing thousands of rows.

```sql
SELECT /* day2_sqltune_loan_eligibility */
       COUNT(*)
FROM (
  SELECT c.customer_id,
         c.full_name,
         c.status,
         COUNT(t.transaction_id) AS txn_count,
         SUM(t.amount) AS total_amount
  FROM customers c
  JOIN transactions t
    ON c.customer_id = t.customer_id
  WHERE c.status = 'ACTIVE'
  AND t.transaction_date >= ADD_MONTHS(SYSDATE,-12)
  GROUP BY c.customer_id, c.full_name, c.status
  ORDER BY total_amount DESC
);
```

Then capture the runtime plan:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Record:

* SQL shape
* join method
* E-Rows vs A-Rows
* buffers
* sort operation
* predicates

---

# Step 4 - Find SQL ID

```sql
COLUMN tune_sql_id NEW_VALUE tune_sql_id

SELECT sql_id AS tune_sql_id,
       child_number,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_sqltune_loan_eligibility%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC
FETCH FIRST 1 ROW ONLY;
```

Confirm:

```sql
SELECT '&&tune_sql_id' AS sql_id_for_tuning
FROM dual;
```

If no SQL ID appears:

* run the tagged SQL again
* confirm you are in the same database instance
* search using only `%loan_eligibility%`

---

# SECTION 3 - LAB 7: RUN SQL TUNING ADVISOR (1:30 - 2:05)

# Slide 4 - Lab Objective

## Slide Content

We will:

1. drop old advisor task if it exists
2. create a tuning task for the SQL ID
3. execute the task
4. read the report
5. classify recommendations
6. decide validation steps

---

# Step 1 - Drop Old Task Safely

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_LOAN_SQL_TUNING_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

Trainer note:

This makes the lab rerunnable.

---

# Step 2 - Create Tuning Task From SQL ID

```sql
DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '&&tune_sql_id',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'DAY2_LOAN_SQL_TUNING_TASK',
    description => 'Day 2 lab SQL Tuning Advisor task'
  );
END;
/
```

If this fails because the cursor is unavailable, use the SQL text fallback below.

---

# Fallback - Create Tuning Task From SQL Text

Use this only if SQL ID method fails.

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_LOAN_SQL_TEXT_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/

DECLARE
  l_sql CLOB;
  l_task_name VARCHAR2(128);
BEGIN
  l_sql := q'[
    SELECT COUNT(*)
    FROM (
      SELECT c.customer_id,
             c.full_name,
             c.status,
             COUNT(t.transaction_id) AS txn_count,
             SUM(t.amount) AS total_amount
      FROM customers c
      JOIN transactions t
        ON c.customer_id = t.customer_id
      WHERE c.status = 'ACTIVE'
      AND t.transaction_date >= ADD_MONTHS(SYSDATE,-12)
      GROUP BY c.customer_id, c.full_name, c.status
      ORDER BY total_amount DESC
    )
  ]';

  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_text    => l_sql,
    user_name   => USER,
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'DAY2_LOAN_SQL_TEXT_TASK',
    description => 'Fallback SQL text tuning task'
  );
END;
/
```

Trainer note:

The SQL ID method is closer to production AWR/ADDM workflow. The SQL text method is a reliable classroom fallback.

---

# Step 3 - Execute Tuning Task

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TUNING_TASK');
```

Fallback task:

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TEXT_TASK');
```

---

# Step 4 - Check Task Status

```sql
SELECT task_name,
       status,
       advisor_name,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name IN (
  'DAY2_LOAN_SQL_TUNING_TASK',
  'DAY2_LOAN_SQL_TEXT_TASK'
)
ORDER BY created DESC;
```

Expected:

```text
STATUS = COMPLETED
```

If the task fails:

* check Tuning Pack privilege
* check SQL ID availability
* use SQL text fallback
* reduce advisor time limit if the lab machine is slow

---

# Step 5 - Read Advisor Report

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

Fallback task:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TEXT_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

Spool option:

```sql
SPOOL sql_tuning_advisor_day2.txt

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

SPOOL OFF
```

---

# SECTION 4 - VALIDATE RECOMMENDATIONS (2:05 - 2:25)

# Slide 5 - Advisor Report Reading Order

## Slide Content

Read the report in this order:

```text
1. Findings
2. Estimated benefit
3. Recommendation type
4. Suggested command
5. Rationale
6. Risk
7. Validation test
```

---

# Slide 6 - Recommendation Decision Table

## Slide Content

| Recommendation | What It Means | Production Validation |
| -------------- | ------------- | --------------------- |
| SQL Profile | optimizer guidance | test bind values, plan stability |
| Index | new access structure | DML impact, duplicate index check |
| Statistics | better optimizer knowledge | plan changes for other SQL |
| Restructure SQL | application/query change | result correctness |

---

## Trainer Delivery

"Never scroll directly to the command and execute it.

First understand what problem Oracle found.

Then decide whether the recommendation is safe."

---

# Optional Lab - Accept SQL Profile In Training Only

Only do this in a disposable training schema.

```sql
EXEC DBMS_SQLTUNE.ACCEPT_SQL_PROFILE(
  task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
  task_owner => USER,
  replace => TRUE
);
```

Check profiles:

```sql
SELECT name,
       category,
       status,
       created,
       sql_text
FROM dba_sql_profiles
ORDER BY created DESC
FETCH FIRST 10 ROWS ONLY;
```

If `DBA_SQL_PROFILES` is not accessible, ask the training DBA to show the profile name before testing rollback.

Rollback:

```sql
EXEC DBMS_SQLTUNE.DROP_SQL_PROFILE(name => 'profile_name_here');
```

Trainer note:

Do not accept profiles in a shared production-like database during class unless the environment is explicitly disposable.

---

# Manual Validation If Advisor Suggests Index

If the advisor suggests an index, do not create it blindly.

First inspect existing indexes:

```sql
SELECT table_name,
       index_name,
       column_name,
       column_position
FROM user_ind_columns
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name, column_position;
```

Then ask:

* is the table DML-heavy?
* does the index duplicate an existing index?
* does it support other important SQL?
* does it help only one report?
* what is the rollback plan?

---

# Lab Worksheet - SQL Tuning Advisor

| Item | Answer |
| ---- | ------ |
| SQL ID analyzed | |
| Current main plan issue | |
| Advisor recommendation type | |
| Estimated benefit | |
| Suggested command | |
| Is it safe directly? | |
| Before/after metric to compare | |
| Rollback plan | |

---

# Guided Answer Key - SQL Tuning Advisor

Use this after participants read the advisor report.

The exact recommendation may vary by data, stats, and indexes. Grade the reasoning, not the exact output.

| Advisor Output | Good DBA Interpretation | Required Validation |
| -------------- | ----------------------- | ------------------- |
| SQL Profile | optimizer may need better cardinality/selectivity guidance | test multiple bind values and confirm plan stability |
| Index recommendation | new access path may reduce reads for this SQL | check duplicate indexes, DML cost, and other workload impact |
| Statistics recommendation | optimizer may be using stale/missing object stats | gather in test first and check plans for important SQL |
| SQL rewrite | query shape may be inefficient | verify result correctness and application feasibility |
| No recommendation | advisor did not find a safe/high-benefit change | manually inspect plan, predicates, rows, and buffers |

Strong trainee answer:

```text
The advisor recommendation is a candidate fix.
I will compare before/after elapsed time, buffers, disk reads, and plan shape before accepting it.
```

Weak trainee answer to correct:

```text
SQL Tuning Advisor recommended an index, so we should create it.
```

Trainer correction:

```text
An index can speed one report and slow many inserts/updates/deletes.
Check DML risk, duplicate indexes, and rollback plan first.
```

---

# SLOT 3 SUMMARY

```text
SQL Tuning Advisor can suggest a fix.
The DBA must prove the fix is safe.
```

---

# SLOT 4 - SQL ACCESS ADVISOR + MEMORY/I/O DIAGNOSIS

## 2:45 PM - 5:00 PM

# SECTION 5 - WORKLOAD-LEVEL ACCESS THINKING (2:45 - 3:05)

# Slide 7 - SQL Tuning Advisor vs SQL Access Advisor

## Slide Content

| Tool | Scope | Common Output |
| ---- | ----- | ------------- |
| SQL Tuning Advisor | one SQL | profile, stats, index, rewrite |
| SQL Access Advisor | workload | indexes, materialized views, partitioning ideas |

---

## Trainer Delivery

"SQL Access Advisor is about access structures for a workload.

In banking, a dashboard or report module may run many SQLs.

The correct question is not:

> What index helps this one SQL?

The better question is:

> What access design helps this workload without hurting core transactions?"

---

# SECTION 6 - LAB 8: WORKLOAD ACCESS DESIGN (3:05 - 3:45)

# Slide 8 - Workload Objective

## Slide Content

We will analyze four reporting queries:

* daily transaction report
* branch transaction dashboard
* customer account summary
* loan EMI due report

We will find repeated access patterns.

---

# Step 1 - Create Loan Payments Table Safely

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE loan_payments PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE loan_payments (
    payment_id   NUMBER PRIMARY KEY,
    customer_id  NUMBER,
    loan_id      NUMBER,
    branch_id    NUMBER,
    due_date     DATE,
    paid_date    DATE,
    emi_amount   NUMBER(12,2),
    status       VARCHAR2(20)
);
```

---

# Step 2 - Insert Loan Payment Data

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO loan_payments (
      payment_id,
      customer_id,
      loan_id,
      branch_id,
      due_date,
      paid_date,
      emi_amount,
      status
    )
    VALUES (
      i,
      MOD(i,5000) + 1,
      MOD(i,20000) + 1,
      MOD(i,50) + 1,
      SYSDATE - MOD(i,365),
      CASE WHEN MOD(i,4) = 0 THEN NULL ELSE SYSDATE - MOD(i,300) END,
      ROUND(DBMS_RANDOM.VALUE(100,5000),2),
      CASE MOD(i,4)
        WHEN 0 THEN 'DUE'
        WHEN 1 THEN 'PAID'
        WHEN 2 THEN 'OVERDUE'
        ELSE 'PENDING'
      END
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;
```

---

# Step 3 - Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'LOAN_PAYMENTS', cascade => TRUE);
END;
/
```

---

# Step 4 - Run Workload Queries With Tags

Use `COUNT(*)` wrappers to avoid printing large reports.

```sql
SELECT /* access_wkld_daily_txn */
       COUNT(*)
FROM (
  SELECT TRUNC(transaction_date) AS txn_day,
         COUNT(*) AS txn_count,
         SUM(amount) AS total_amount
  FROM transactions
  WHERE transaction_date >= ADD_MONTHS(SYSDATE,-1)
  GROUP BY TRUNC(transaction_date)
  ORDER BY txn_day
);

SELECT /* access_wkld_branch_txn */
       COUNT(*)
FROM (
  SELECT branch_id,
         COUNT(*) AS txn_count,
         SUM(amount) AS total_amount
  FROM transactions
  WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3)
  GROUP BY branch_id
  ORDER BY total_amount DESC
);

SELECT /* access_wkld_customer_accounts */
       COUNT(*)
FROM (
  SELECT c.customer_id,
         c.full_name,
         COUNT(a.account_id) AS total_accounts,
         SUM(a.balance) AS total_balance
  FROM customers c
  JOIN accounts a
    ON c.customer_id = a.customer_id
  WHERE c.status = 'ACTIVE'
  GROUP BY c.customer_id, c.full_name
);

SELECT /* access_wkld_loan_due */
       COUNT(*)
FROM (
  SELECT branch_id,
         COUNT(*) AS due_count,
         SUM(emi_amount) AS total_due
  FROM loan_payments
  WHERE status IN ('DUE','OVERDUE')
  AND due_date <= SYSDATE
  GROUP BY branch_id
  ORDER BY total_due DESC
);
```

---

# Step 5 - Find Workload SQL In V$SQL

```sql
SELECT sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,90) sql_text
FROM v$sql
WHERE sql_text LIKE '%access_wkld_%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY elapsed_time DESC;
```

---

# Step 6 - Generate Plans For Repeated Patterns

Daily transaction report:

```sql
EXPLAIN PLAN FOR
SELECT TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-1)
GROUP BY TRUNC(transaction_date)
ORDER BY txn_day;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Branch transaction report:

```sql
EXPLAIN PLAN FOR
SELECT branch_id,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3)
GROUP BY branch_id
ORDER BY total_amount DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Loan due report:

```sql
EXPLAIN PLAN FOR
SELECT branch_id,
       COUNT(*) AS due_count,
       SUM(emi_amount) AS total_due
FROM loan_payments
WHERE status IN ('DUE','OVERDUE')
AND due_date <= SYSDATE
GROUP BY branch_id
ORDER BY total_due DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

# Step 7 - Manual Workload Pattern Table

Participants fill this before seeing advisor output:

| Query | Main Table | Filters | Join Columns | Group/Sort | Possible Access Structure | Risk |
| ----- | ---------- | ------- | ------------ | ---------- | ------------------------- | ---- |
| Daily transaction | TRANSACTIONS | transaction_date | | TRUNC(date) | date index or summary MV | DML/refresh |
| Branch transaction | TRANSACTIONS | transaction_date | | branch_id | date/branch index or MV | DML/refresh |
| Customer accounts | CUSTOMERS, ACCOUNTS | customer status | customer_id | customer | account customer index | DML |
| Loan due | LOAN_PAYMENTS | status, due_date | | branch_id | status/due/branch index | DML |

Trainer note:

This manual step matters. DBAs should have a hypothesis before reading advisor output.

---

# SECTION 7 - SQL ACCESS ADVISOR PRACTICAL PATH (3:45 - 4:20)

# Slide 9 - Practical Advisor Path

## Slide Content

SQL Access Advisor setup can vary by privileges and environment.

We use two paths:

1. Reliable manual workload design lab
2. Optional SQL Access Advisor `QUICK_TUNE` demo

---

## Trainer Delivery

"The advisor package can be restricted in many training databases.

Do not let tool setup block the learning.

The important production skill is evaluating workload access structures.

If the package is available, we run the quick advisor demo."

---

# Optional Advisor Demo - Drop Old Task

```sql
BEGIN
  DBMS_ADVISOR.DELETE_TASK('DAY2_ACCESS_QUICK_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

---

# Optional Advisor Demo - Run QUICK_TUNE

This analyzes one representative SQL using SQL Access Advisor.

```sql
DECLARE
  l_sql VARCHAR2(32767);
BEGIN
  l_sql := q'[
    SELECT branch_id,
           COUNT(*) AS txn_count,
           SUM(amount) AS total_amount
    FROM transactions
    WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3)
    GROUP BY branch_id
    ORDER BY total_amount DESC
  ]';

  DBMS_ADVISOR.QUICK_TUNE(
    advisor_name => 'SQL Access Advisor',
    task_name    => 'DAY2_ACCESS_QUICK_TASK',
    attr1        => l_sql
  );
END;
/
```

Trainer note:

`QUICK_TUNE` is used because it is simpler and more reliable for classroom execution than a full SQL workload object setup. The manual workload lab above still teaches workload-level thinking.

---

# Optional Advisor Demo - Check Task

```sql
SELECT task_name,
       advisor_name,
       status,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK';
```

Expected:

```text
STATUS = COMPLETED
```

---

# Optional Advisor Demo - Review Recommendations

```sql
SELECT rec_id,
       rank,
       benefit,
       type
FROM user_advisor_recommendations
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK'
ORDER BY rank;
```

Actions:

```sql
SELECT rec_id,
       action_id,
       command,
       attr1,
       attr2,
       attr3
FROM user_advisor_actions
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK'
ORDER BY rec_id, action_id;
```

If no recommendation appears:

* existing indexes may already satisfy the query
* data volume may be too small
* advisor may not find enough benefit
* use the manual workload design table as the lab output

---

# Recommendation Evaluation Worksheet

| Recommendation | Type | Benefit | SQL Helped | DML Risk | Test Before Production |
| -------------- | ---- | ------: | ---------- | -------- | ---------------------- |
| | Index | | | | |
| | Materialized View | | | | |
| | Partitioning idea | | | | |

Production questions:

* Does this help multiple SQLs or only one?
* Is the table write-heavy?
* Is the recommendation duplicating an index?
* Is a materialized view refresh strategy needed?
* Can we rollback quickly?

---

# Manual Index Recommendation Validation - Before/After

This lab works even when SQL Access Advisor privileges are restricted.

Goal:

```text
Prove or reject an index recommendation using before/after evidence.
```

## Step 1 - Capture Before Metrics

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* access_before_loan_due */
       COUNT(*)
FROM (
  SELECT branch_id,
         COUNT(*) AS due_count,
         SUM(emi_amount) AS total_due
  FROM loan_payments
  WHERE status IN ('DUE','OVERDUE')
  AND due_date <= SYSDATE
  GROUP BY branch_id
  ORDER BY total_due DESC
);

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Record:

* elapsed time
* buffers
* disk reads
* access path
* predicates

---

## Step 2 - Create Candidate Index As Invisible

Use an invisible index so the test does not affect other sessions by default.

```sql
CREATE INDEX idx_lp_status_due_branch_inv
ON loan_payments(status, due_date, branch_id)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_INDEX_STATS(USER, 'IDX_LP_STATUS_DUE_BRANCH_INV');
END;
/
```

Enable invisible indexes only in this session:

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;
```

---

## Step 3 - Capture After Metrics

```sql
SELECT /* access_after_loan_due */
       COUNT(*)
FROM (
  SELECT branch_id,
         COUNT(*) AS due_count,
         SUM(emi_amount) AS total_due
  FROM loan_payments
  WHERE status IN ('DUE','OVERDUE')
  AND due_date <= SYSDATE
  GROUP BY branch_id
  ORDER BY total_due DESC
);

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Compare:

| Metric | Before | After | Decision |
| ------ | ------ | ----- | -------- |
| Elapsed time | | | |
| Buffers | | | |
| Disk reads | | | |
| Access path | | | |
| Sort/hash work | | | |
| DML risk | | | |

Decision rules:

* keep testing if the index helps the report but may hurt DML
* reject if buffers/elapsed time do not improve meaningfully
* consider a different column order if predicates do not match the index well
* never make it visible in production without workload testing and change approval

Rollback:

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
DROP INDEX idx_lp_status_due_branch_inv;
```

Trainer note:

This is one of the most important confidence labs of Day 2. It shows that advisor/index recommendations must be proven, not trusted blindly.

---

# Materialized View Demonstration - Manual Before/After

This demo works without SQL Access Advisor.

Create summary MV:

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP MATERIALIZED VIEW mv_branch_daily_txn';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-12003, -942) THEN
      RAISE;
    END IF;
END;
/

CREATE MATERIALIZED VIEW mv_branch_daily_txn
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT branch_id,
       TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
GROUP BY branch_id, TRUNC(transaction_date);
```

Compare report against base table:

```sql
SELECT /* mv_demo_base */
       branch_id,
       TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-1)
GROUP BY branch_id, TRUNC(transaction_date);
```

Against summary:

```sql
SELECT /* mv_demo_summary */
       branch_id,
       txn_day,
       SUM(txn_count) AS txn_count,
       SUM(total_amount) AS total_amount
FROM mv_branch_daily_txn
WHERE txn_day >= ADD_MONTHS(TRUNC(SYSDATE),-1)
GROUP BY branch_id, txn_day;
```

Find and compare the tagged SQL metrics:

```sql
SELECT sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,80) sql_text
FROM v$sql
WHERE sql_text LIKE '%mv_demo_%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC;
```

Trainer note:

This is not automatic query rewrite training. It is a practical demonstration that reporting workloads may be better served by summary structures than repeatedly scanning transaction detail.

---

# SECTION 8 - MEMORY AND I/O DIAGNOSIS MINI-LAB (4:20 - 4:40)

# Slide 10 - Objective

## Slide Content

We will inspect:

* wait events
* physical reads
* PGA symptoms
* SGA sizing context
* temp usage
* SQL causing reads

---

# Step 1 - Top Wait Events

```sql
SELECT event,
       total_waits,
       ROUND(time_waited/100,2) AS time_waited_sec,
       ROUND(average_wait/100,4) AS avg_wait_sec
FROM v$system_event
WHERE wait_class <> 'Idle'
ORDER BY time_waited DESC
FETCH FIRST 15 ROWS ONLY;
```

Interpretation:

| Wait | First Question |
| ---- | -------------- |
| db file sequential read | Which SQL/index lookups caused single-block reads? |
| db file scattered read | Which SQL caused full scans? |
| direct path read | Which report or scan used direct reads? |
| log file sync | Who commits frequently? |
| enq: TX - row lock contention | Who is blocking whom? |

---

# Step 2 - Physical Read Statistics

```sql
SELECT name,
       value
FROM v$sysstat
WHERE name IN (
  'physical reads',
  'physical reads cache',
  'physical reads direct',
  'physical write total IO requests',
  'session logical reads'
)
ORDER BY name;
```

Trainer note:

These are cumulative since instance startup. Use AWR deltas for historical windows.

---

# Step 3 - SQL Currently Causing Reads

```sql
SELECT sql_id,
       executions,
       buffer_gets,
       disk_reads,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE disk_reads > 0
ORDER BY disk_reads DESC
FETCH FIRST 10 ROWS ONLY;
```

Ask:

* Is this reporting SQL?
* Is it scanning too much?
* Does it match AWR SQL by Reads?
* Should we inspect the execution plan?

---

# Step 4 - PGA Workarea Symptoms

```sql
SELECT name,
       value,
       unit
FROM v$pgastat
WHERE name IN (
  'aggregate PGA target parameter',
  'total PGA allocated',
  'maximum PGA allocated',
  'over allocation count',
  'cache hit percentage'
)
ORDER BY name;
```

Interpretation:

* low cache hit percentage may indicate workarea pressure
* over allocation count above zero deserves investigation
* large sorts/hash joins may spill to TEMP

---

# Step 5 - Temp Usage Right Now

```sql
SELECT s.sid,
       s.serial#,
       s.username,
       u.tablespace,
       ROUND(u.blocks * ts.block_size / 1024 / 1024,2) AS temp_mb,
       q.sql_id,
       SUBSTR(q.sql_text,1,80) sql_text
FROM v$tempseg_usage u
JOIN v$session s
  ON u.session_addr = s.saddr
LEFT JOIN v$sql q
  ON s.sql_id = q.sql_id
JOIN dba_tablespaces ts
  ON u.tablespace = ts.tablespace_name
ORDER BY temp_mb DESC;
```

If no rows appear:

```text
No active temp-consuming operation at this moment.
That is normal if no large sort/hash is running.
```

---

# Step 6 - SGA Sizing Context

```sql
SELECT name,
       bytes,
       ROUND(bytes/1024/1024,2) AS mb
FROM v$sgainfo
ORDER BY name;
```

Trainer note:

Do not tune memory only from this output. Use it as context with AWR, ADDM, waits, and SQL evidence.

---

# Mini-Lab Worksheet

| Check | Observation | Possible Meaning | Next Evidence |
| ----- | ----------- | ---------------- | ------------- |
| Top wait event | | CPU/I/O/commit/lock direction | AWR Top Events |
| SQL by disk reads | | I/O driver | execution plan |
| PGA stats | | sort/hash pressure | temp usage |
| Temp usage | | active spill | SQL_ID |
| SGA info | | memory context | ADDM/memory advisors |

---

# ORAchk / Health Check Positioning

Use this short note because trainees may ask about ORAchk or database health checks.

## Slide Content

```text
ORAchk answers:
Is the database environment configured according to known best practices?

AWR/ASH/ADDM answer:
What happened during a performance window?

SQL tuning answers:
Which SQL, plan, predicates, reads, waits, and fix options explain the slowness?
```

## Trainer Delivery

"ORAchk is useful for health and configuration review.

It is not a replacement for AWR, ASH, ADDM, SQL_ID analysis, or execution plans.

If a user says a screen was slow at 11 AM, ORAchk may show general risks, but AWR/ASH/ADDM and SQL plans show what happened in that time window."

---

# SECTION 9 - END-TO-END DAY 2 CAPSTONE (4:40 - 4:55)

# Slide 11 - Integrated Tuning Workflow

## Slide Content

```text
Complaint
  -> AWR window
  -> AWR top waits and top SQL
  -> ASH wait class / event / SQL_ID
  -> ADDM finding
  -> DBMS_XPLAN for the SQL_ID
  -> SQL Tuning Advisor if one SQL is the driver
  -> SQL Access Advisor or manual index/MV test if workload design is the driver
  -> before/after proof
  -> rollback and production recommendation
```

---

## Capstone Scenario

```text
At 11:00 AM, customer statement and fund transfer screens were slow.
The application team cannot provide SQL text.
Management asks whether this is CPU, I/O, locking, commit latency, or bad SQL.
```

Participants must produce a DBA recommendation using evidence.

---

## Capstone Worksheet

| Step | Evidence To Capture | Trainee Answer |
| ---- | ------------------- | -------------- |
| 1. Report window | begin/end snapshots, elapsed time, DB time | |
| 2. Top wait direction | AWR Top Timed Events or ASH wait class | |
| 3. Top SQL | SQL_ID from AWR/ASH | |
| 4. Plan evidence | DBMS_XPLAN operation, predicates, buffers | |
| 5. ADDM view | finding, impact, recommendation | |
| 6. Advisor view | profile/index/stats/rewrite/no recommendation | |
| 7. Before/after proof | elapsed, buffers, reads, plan shape | |
| 8. Production caution | DML risk, license, rollback, change window | |
| 9. Final recommendation | fix, test, or next investigation | |

---

## Expected Capstone Answer Pattern

```text
The evidence points to [SQL_ID / wait class / object].
The likely cause is [bad access path / excessive reads / frequent commits / lock wait / memory spill].
The supporting evidence is [AWR section + ASH samples + DBMS_XPLAN + ADDM finding].
The proposed action is [test index/profile/stats/rewrite/MV/application commit change].
Before production, we must compare before/after metrics and prepare rollback.
```

Trainer scoring:

| Rating | Evidence Quality |
| ------ | ---------------- |
| 6/6 | connects AWR, ASH/ADDM, SQL_ID, plan, advisor output, before/after proof, and production risk |
| 4/6 | finds top SQL or wait but cannot validate the recommendation |
| 2/6 | jumps to a fix without evidence |

---

# SECTION 10 - DAY 2 CLOSING (4:55 - 5:00)

# Slide 12 - Day 2 Full Workflow

## Slide Content

```text
User complaint
  -> AWR window
  -> Top waits and top SQL
  -> ASH wait class and event evidence
  -> ADDM findings
  -> SQL Tuning Advisor for one SQL
  -> SQL Access Advisor for workload design
  -> Memory/I/O views for system symptoms
  -> Validate before applying fix
```

---

## Trainer Delivery

"Day 1 taught us how to read one SQL.

Day 2 taught us how to diagnose the workload and use Oracle advisors safely.

Tomorrow we handle production stability issues:

* plan baselines,
* bind peeking,
* adaptive cursor sharing,
* hints,
* SQL Profiles,
* locking,
* concurrency."

---

# FINAL DAY 2 MESSAGE

Repeat clearly:

```text
Advisors are not decision-makers.
They are accelerators for investigation.

A senior DBA validates every recommendation with evidence,
business context,
and rollback planning.
```
