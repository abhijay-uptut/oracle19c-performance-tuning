# SQL Tuning Advisor Assignment Solution - Multiple Bad SQLs

# Objective

This solution shows one practical way to complete the SQL Tuning Advisor assignment.

It uses each trainee's own Oracle training user and creates a dummy transaction table called `STA_ASSIGN_TXN`.

The evidence chain is:

```text
create dummy data
  -> run bad SQL without indexes
  -> capture SQL_ID
  -> run SQL Tuning Advisor
  -> review index recommendations
  -> apply recommendations in training
  -> compare before and after plans and metrics
```

---

# Part 1 - Create Dummy Table

Connect as your training user in SQL Developer or SQL*Plus.

Run:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE sta_assign_txn PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE sta_assign_txn (
  transaction_id    NUMBER,
  customer_id       NUMBER,
  branch_id         NUMBER,
  txn_date          DATE,
  amount            NUMBER(12,2),
  status            VARCHAR2(20),
  channel           VARCHAR2(20),
  merchant_category VARCHAR2(30)
);

INSERT /*+ APPEND */ INTO sta_assign_txn
SELECT
  level AS transaction_id,
  CASE
    WHEN level <= 25000 THEN 1001
    WHEN MOD(level, 200) = 0 THEN 2002
    ELSE MOD(level, 50000) + 1
  END AS customer_id,
  MOD(level, 80) + 1 AS branch_id,
  TRUNC(SYSDATE) - MOD(level, 730) AS txn_date,
  ROUND(DBMS_RANDOM.VALUE(5, 50000), 2) AS amount,
  CASE
    WHEN MOD(level, 100) < 3 THEN 'FAILED'
    WHEN MOD(level, 100) < 8 THEN 'PENDING'
    WHEN MOD(level, 100) < 12 THEN 'REVERSED'
    ELSE 'POSTED'
  END AS status,
  CASE MOD(level, 4)
    WHEN 0 THEN 'MOBILE'
    WHEN 1 THEN 'ATM'
    WHEN 2 THEN 'BRANCH'
    ELSE 'ONLINE'
  END AS channel,
  CASE MOD(level, 6)
    WHEN 0 THEN 'GROCERY'
    WHEN 1 THEN 'FUEL'
    WHEN 2 THEN 'TRAVEL'
    WHEN 3 THEN 'DINING'
    WHEN 4 THEN 'UTILITIES'
    ELSE 'RETAIL'
  END AS merchant_category
FROM dual
CONNECT BY level <= 300000;

COMMIT;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'STA_ASSIGN_TXN',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/

SELECT COUNT(*) AS row_count
FROM sta_assign_txn;
```

Expected:

```text
ROW_COUNT = 300000
```

Important:

```text
Do not create any tuning indexes yet.
```

---

# Part 2 - Run Four Bad SQL Statements

Enable runtime statistics:

```sql
ALTER SESSION SET statistics_level = ALL;
```

Run SQL 1:

```sql
SELECT /* sta_assign_q1_customer */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM sta_assign_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
```

Run SQL 2:

```sql
SELECT /* sta_assign_q2_status_function */
       COUNT(*) AS failed_count
FROM sta_assign_txn
WHERE LOWER(status) = 'failed';
```

Run SQL 3:

```sql
SELECT /* sta_assign_q3_branch_channel */
       branch_id,
       channel,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM sta_assign_txn
WHERE branch_id = 25
AND channel = 'MOBILE'
AND txn_date >= TRUNC(SYSDATE) - 90
GROUP BY branch_id, channel;
```

Run SQL 4:

```sql
SELECT /* sta_assign_q4_amount_range */
       transaction_id,
       customer_id,
       amount,
       txn_date
FROM sta_assign_txn
WHERE amount BETWEEN 49000 AND 50000
ORDER BY amount DESC;
```

Expected before direction:

```text
The optimizer may use TABLE ACCESS FULL because there are no supporting indexes.
```

---

# Part 3 - Find The Four SQL IDs

Use the comment tags to find the SQL IDs.

```sql
COLUMN sql_id FORMAT A15
COLUMN tag FORMAT A35
COLUMN sql_text FORMAT A100

SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
       buffer_gets,
       disk_reads,
       CASE
         WHEN sql_text LIKE '%sta_assign_q1_customer%' THEN 'sta_assign_q1_customer'
         WHEN sql_text LIKE '%sta_assign_q2_status_function%' THEN 'sta_assign_q2_status_function'
         WHEN sql_text LIKE '%sta_assign_q3_branch_channel%' THEN 'sta_assign_q3_branch_channel'
         WHEN sql_text LIKE '%sta_assign_q4_amount_range%' THEN 'sta_assign_q4_amount_range'
       END AS tag,
       sql_text
FROM v$sql
WHERE (
      sql_text LIKE '%sta_assign_q1_customer%'
   OR sql_text LIKE '%sta_assign_q2_status_function%'
   OR sql_text LIKE '%sta_assign_q3_branch_channel%'
   OR sql_text LIKE '%sta_assign_q4_amount_range%'
)
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC;
```

Record the four SQL IDs.

Example worksheet:

| SQL | Tag | SQL ID |
| --- | --- | ------ |
| SQL 1 | `sta_assign_q1_customer` | `<q1_sql_id>` |
| SQL 2 | `sta_assign_q2_status_function` | `<q2_sql_id>` |
| SQL 3 | `sta_assign_q3_branch_channel` | `<q3_sql_id>` |
| SQL 4 | `sta_assign_q4_amount_range` | `<q4_sql_id>` |

---

# Part 4 - Capture Before Plans

For each SQL, run the SQL once and immediately display the last cursor plan:

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

For a specific SQL ID, use:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '<sql_id>',
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Expected before plan examples:

```text
TABLE ACCESS FULL STA_ASSIGN_TXN
FILTER
SORT ORDER BY
HASH GROUP BY
```

Record:

| SQL | Before Main Operation | Before Evidence |
| --- | --------------------- | --------------- |
| SQL 1 | `TABLE ACCESS FULL` | no customer/date index |
| SQL 2 | `TABLE ACCESS FULL` | function on status |
| SQL 3 | `TABLE ACCESS FULL` | no branch/channel/date index |
| SQL 4 | `TABLE ACCESS FULL` | no amount index |

---

# Part 5 - Run SQL Tuning Advisor For Each SQL ID

Replace the placeholder SQL IDs before running this section.

## SQL 1 Advisor Task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q1_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '<q1_sql_id>',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'STA_ASSIGN_Q1_TASK',
    description => 'STA assignment SQL 1 tuning task'
  );
END;
/

BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('STA_ASSIGN_Q1_TASK');
END;
/
```

## SQL 2 Advisor Task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q2_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '<q2_sql_id>',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'STA_ASSIGN_Q2_TASK',
    description => 'STA assignment SQL 2 tuning task'
  );
END;
/

BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('STA_ASSIGN_Q2_TASK');
END;
/
```

## SQL 3 Advisor Task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q3_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '<q3_sql_id>',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'STA_ASSIGN_Q3_TASK',
    description => 'STA assignment SQL 3 tuning task'
  );
END;
/

BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('STA_ASSIGN_Q3_TASK');
END;
/
```

## SQL 4 Advisor Task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q4_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '<q4_sql_id>',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'STA_ASSIGN_Q4_TASK',
    description => 'STA assignment SQL 4 tuning task'
  );
END;
/

BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('STA_ASSIGN_Q4_TASK');
END;
/
```

Check task status:

```sql
COLUMN task_name FORMAT A25
COLUMN status FORMAT A15

SELECT task_name,
       status,
       advisor_name,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name IN (
  'STA_ASSIGN_Q1_TASK',
  'STA_ASSIGN_Q2_TASK',
  'STA_ASSIGN_Q3_TASK',
  'STA_ASSIGN_Q4_TASK'
)
ORDER BY task_name;
```

Expected:

```text
STATUS = COMPLETED
```

---

# Part 6 - Read Advisor Reports

Set display options:

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 220
SET PAGESIZE 1000
```

Read each report:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'STA_ASSIGN_Q1_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'STA_ASSIGN_Q2_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'STA_ASSIGN_Q3_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'STA_ASSIGN_Q4_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

Expected recommendation direction:

| SQL | Likely Recommendation |
| --- | --------------------- |
| SQL 1 | index on `CUSTOMER_ID, TXN_DATE` |
| SQL 2 | function-based index on `LOWER(STATUS)` |
| SQL 3 | index on `BRANCH_ID, CHANNEL, TXN_DATE` |
| SQL 4 | index on `AMOUNT` |

Actual advisor output may vary by Oracle version, statistics, data distribution, and optimizer choices.

---

# Part 7 - Apply Safe Training Recommendations

In this training schema, create candidate indexes.

```sql
CREATE INDEX idx_sta_assign_q1
ON sta_assign_txn(customer_id, txn_date DESC);

CREATE INDEX idx_sta_assign_q2
ON sta_assign_txn(LOWER(status));

CREATE INDEX idx_sta_assign_q3
ON sta_assign_txn(branch_id, channel, txn_date);

CREATE INDEX idx_sta_assign_q4
ON sta_assign_txn(amount);
```

Gather statistics again:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'STA_ASSIGN_TXN',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/
```

Training note:

```text
These indexes are acceptable for a lab.
In production, review duplicate indexes, DML impact, storage, and workload-wide benefit first.
```

---

# Part 8 - Rerun The Same SQL Statements

Run the exact same SQL text again.

```sql
ALTER SESSION SET statistics_level = ALL;
```

SQL 1:

```sql
SELECT /* sta_assign_q1_customer */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM sta_assign_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
```

SQL 2:

```sql
SELECT /* sta_assign_q2_status_function */
       COUNT(*) AS failed_count
FROM sta_assign_txn
WHERE LOWER(status) = 'failed';
```

SQL 3:

```sql
SELECT /* sta_assign_q3_branch_channel */
       branch_id,
       channel,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM sta_assign_txn
WHERE branch_id = 25
AND channel = 'MOBILE'
AND txn_date >= TRUNC(SYSDATE) - 90
GROUP BY branch_id, channel;
```

SQL 4:

```sql
SELECT /* sta_assign_q4_amount_range */
       transaction_id,
       customer_id,
       amount,
       txn_date
FROM sta_assign_txn
WHERE amount BETWEEN 49000 AND 50000
ORDER BY amount DESC;
```

Display the runtime plan after each SQL:

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

Expected after direction:

| SQL | Expected After Plan Direction |
| --- | ----------------------------- |
| SQL 1 | `INDEX RANGE SCAN` on `IDX_STA_ASSIGN_Q1` |
| SQL 2 | index access on `IDX_STA_ASSIGN_Q2`, or lower-cost index scan |
| SQL 3 | `INDEX RANGE SCAN` on `IDX_STA_ASSIGN_Q3` |
| SQL 4 | `INDEX RANGE SCAN` on `IDX_STA_ASSIGN_Q4` |

---

# Part 9 - Compare Before And After Metrics

Use this query to review current cursor-level metrics:

```sql
COLUMN sql_id FORMAT A15
COLUMN tag FORMAT A35
COLUMN sql_text FORMAT A90

SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
       buffer_gets,
       disk_reads,
       ROUND(buffer_gets / NULLIF(executions, 0), 2) AS buffers_per_exec,
       CASE
         WHEN sql_text LIKE '%sta_assign_q1_customer%' THEN 'sta_assign_q1_customer'
         WHEN sql_text LIKE '%sta_assign_q2_status_function%' THEN 'sta_assign_q2_status_function'
         WHEN sql_text LIKE '%sta_assign_q3_branch_channel%' THEN 'sta_assign_q3_branch_channel'
         WHEN sql_text LIKE '%sta_assign_q4_amount_range%' THEN 'sta_assign_q4_amount_range'
       END AS tag,
       sql_text
FROM v$sql
WHERE (
      sql_text LIKE '%sta_assign_q1_customer%'
   OR sql_text LIKE '%sta_assign_q2_status_function%'
   OR sql_text LIKE '%sta_assign_q3_branch_channel%'
   OR sql_text LIKE '%sta_assign_q4_amount_range%'
)
AND sql_text NOT LIKE '%v$sql%'
ORDER BY tag, child_number;
```

Use your captured plan output and cursor metrics to fill:

| SQL | Before Plan | After Plan | Expected Result |
| --- | ----------- | ---------- | --------------- |
| SQL 1 | Full scan | Customer/date index access | fewer buffers and less sort work |
| SQL 2 | Full scan with function filter | function-based index access | fewer rows scanned |
| SQL 3 | Full scan with filter/group | branch/channel/date index access | fewer rows scanned before grouping |
| SQL 4 | Full scan and sort | amount index access | fewer rows scanned for high amount range |

---

# Part 10 - Example Completed Recommendation

Example final answer:

```text
The bad SQL IDs tested were:
1. <q1_sql_id>
2. <q2_sql_id>
3. <q3_sql_id>
4. <q4_sql_id>

The main problem before tuning was missing access paths. The SQL statements filtered by customer/date, LOWER(status), branch/channel/date, and amount, but the table had no supporting indexes.

SQL Tuning Advisor recommended index-based access improvements.

After applying recommendations in training, the plans changed from full table scans to index access paths for the tested SQLs. Buffer gets and elapsed time should reduce, especially for selective predicates.

The recommendation I would take to production is to test the candidate indexes against the full workload, check duplicate indexes, estimate DML overhead, and apply only the indexes with proven workload benefit.

Production cautions:
1. Extra indexes slow INSERT, UPDATE, and DELETE operations.
2. Extra indexes consume storage and require maintenance.
3. A recommendation for one SQL can hurt another SQL, so workload testing is required.
```

---

# Cleanup

Use this only after the assignment is complete.

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q1_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q2_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q3_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('STA_ASSIGN_Q4_TASK');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DROP TABLE sta_assign_txn PURGE;
```

