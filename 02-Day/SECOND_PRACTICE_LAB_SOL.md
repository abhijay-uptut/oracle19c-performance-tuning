# Day 2 Second Practice Lab Solution - SQL Tuning Advisor And Access Design

# Objective

This solution shows one practical way to complete the second-half Day 2 practice lab.

It uses each trainee's own Oracle training user. It does not require the `SOE` sample schema.

The lab has four parts:

```text
1. Create a practice transaction table
2. Use SQL Tuning Advisor for one SQL
3. Validate an index recommendation with before/after evidence
4. Think about workload access design and memory/I/O clues
```

---

# Part 1 - Create Practice Data In SQL Developer

Connect as your training user in SQL Developer.

Run:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE day2_practice_txn PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE day2_practice_txn (
    transaction_id NUMBER PRIMARY KEY,
    customer_id    NUMBER,
    branch_id      NUMBER,
    txn_date       DATE,
    amount         NUMBER(12,2),
    status         VARCHAR2(20),
    channel        VARCHAR2(20)
);

BEGIN
  FOR i IN 1..300000 LOOP
    INSERT INTO day2_practice_txn (
      transaction_id,
      customer_id,
      branch_id,
      txn_date,
      amount,
      status,
      channel
    )
    VALUES (
      i,
      CASE
        WHEN i <= 25000 THEN 1001
        ELSE MOD(i,20000) + 1
      END,
      MOD(i,60) + 1,
      TRUNC(SYSDATE) - MOD(i,730),
      ROUND(DBMS_RANDOM.VALUE(10,10000),2),
      CASE
        WHEN MOD(i,100) < 3 THEN 'FAILED'
        WHEN MOD(i,100) < 8 THEN 'PENDING'
        WHEN MOD(i,100) < 12 THEN 'REVERSED'
        ELSE 'POSTED'
      END,
      CASE MOD(i,4)
        WHEN 0 THEN 'MOBILE'
        WHEN 1 THEN 'ATM'
        WHEN 2 THEN 'BRANCH'
        ELSE 'ONLINE'
      END
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'DAY2_PRACTICE_TXN',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/

SELECT COUNT(*) AS row_count
FROM day2_practice_txn;

SELECT customer_id, COUNT(*) AS row_count
FROM day2_practice_txn
WHERE customer_id = 1001
GROUP BY customer_id;
```

Expected:

```text
DAY2_PRACTICE_TXN has 300000 rows.
CUSTOMER_ID 1001 has many rows.
```

Do not create the tuning index yet.

---

# Part 2 - Run One SQL And Find SQL ID

Run the target SQL once:

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* day2_second_sta_customer */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM day2_practice_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
```

Capture the runtime plan:

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

Find the SQL ID:

```sql
COLUMN sql_id FORMAT A15
COLUMN sql_text FORMAT A100

SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time / 1000000, 2) AS elapsed_sec,
       buffer_gets,
       disk_reads,
       sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_second_sta_customer%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC;
```

Expected before direction:

```text
The plan may show TABLE ACCESS FULL DAY2_PRACTICE_TXN.
Buffers may be higher than needed.
```

Record the SQL ID.

---

# Part 3 - Run SQL Tuning Advisor

Replace `<your_sql_id>` with the SQL ID from Part 2.

Drop the old task if it exists:

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_SECOND_STA_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

Create the tuning task:

```sql
DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '<your_sql_id>',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'DAY2_SECOND_STA_TASK',
    description => 'Day 2 second practice SQL Tuning Advisor task'
  );
END;
/
```

Execute the task:

```sql
BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK(
    task_name => 'DAY2_SECOND_STA_TASK'
  );
END;
/
```

Check status:

```sql
SELECT task_name,
       status,
       advisor_name,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_SECOND_STA_TASK';
```

Expected:

```text
STATUS = COMPLETED
```

View the report:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_SECOND_STA_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

Common recommendation:

```text
Create an index on DAY2_PRACTICE_TXN(CUSTOMER_ID, TXN_DATE)
or gather statistics
or no recommendation if the optimizer already finds a good plan.
```

Correct DBA interpretation:

```text
The advisor recommendation is a candidate fix, not an automatic production change.
```

---

# Part 4 - Validate Candidate Index Safely

Inspect existing indexes first:

```sql
SELECT index_name,
       column_name,
       column_position
FROM user_ind_columns
WHERE table_name = 'DAY2_PRACTICE_TXN'
ORDER BY index_name, column_position;
```

Create a candidate invisible index:

```sql
CREATE INDEX idx_d2p_txn_cust_date_inv
ON day2_practice_txn(customer_id, txn_date DESC)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_INDEX_STATS(
    ownname => USER,
    indname => 'IDX_D2P_TXN_CUST_DATE_INV'
  );
END;
/
```

Enable invisible indexes only in your session:

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;
ALTER SESSION SET statistics_level = ALL;
```

Rerun the same SQL:

```sql
SELECT /* day2_second_sta_customer_after */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM day2_practice_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
```

Capture after plan:

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

```text
INDEX RANGE SCAN on IDX_D2P_TXN_CUST_DATE_INV
TABLE ACCESS BY INDEX ROWID DAY2_PRACTICE_TXN
```

Compare:

| Metric | Before | After | Expected |
| ------ | ------ | ----- | -------- |
| Plan operation | full scan | index range scan | improved access path |
| Buffer gets | higher | lower | after should improve |
| Disk reads | higher or variable | lower or variable | after often improves |
| Elapsed time | higher | lower | after should improve |

Decision:

```text
If the index reduces buffers and elapsed time meaningfully, it is a candidate.
It still needs DML impact testing, duplicate index checks, storage review, and change approval.
```

Rollback for the lab:

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
DROP INDEX idx_d2p_txn_cust_date_inv;
```

---

# Part 5 - Workload Access Design

Run three workload queries:

```sql
SELECT /* day2_second_wkld_customer */
       COUNT(*)
FROM (
  SELECT transaction_id,
         customer_id,
         txn_date,
         amount,
         status
  FROM day2_practice_txn
  WHERE customer_id = 1001
  AND txn_date >= ADD_MONTHS(SYSDATE, -12)
  ORDER BY txn_date DESC
);

SELECT /* day2_second_wkld_branch */
       COUNT(*)
FROM (
  SELECT branch_id,
         COUNT(*) AS txn_count,
         SUM(amount) AS total_amount
  FROM day2_practice_txn
  WHERE txn_date >= ADD_MONTHS(SYSDATE, -3)
  GROUP BY branch_id
  ORDER BY total_amount DESC
);

SELECT /* day2_second_wkld_exception */
       COUNT(*)
FROM (
  SELECT status,
         txn_date,
         COUNT(*) AS txn_count,
         SUM(amount) AS total_amount
  FROM day2_practice_txn
  WHERE status IN ('FAILED','PENDING')
  AND txn_date >= ADD_MONTHS(SYSDATE, -1)
  GROUP BY status, txn_date
  ORDER BY txn_date DESC
);
```

Manual access-design answer:

| Query | Main Filter | Sort/Group By | Candidate Access Structure | Risk |
| ----- | ----------- | ------------- | -------------------------- | ---- |
| Customer lookup | `customer_id`, `txn_date` | `txn_date DESC` | `(customer_id, txn_date DESC)` index | DML/storage |
| Branch dashboard | `txn_date` | `branch_id`, total amount | `(txn_date, branch_id)` index or summary MV | report may scan many rows |
| Exception report | `status`, `txn_date` | `status`, `txn_date` | `(status, txn_date)` index | low-cardinality status may need testing |

Correct conclusion:

```text
One index does not solve the whole workload.
Different queries have different filters and grouping needs.
The branch dashboard may be better served by a summary/materialized view if it runs often.
```

---

# Part 6 - Optional SQL Access Advisor Quick Tune

Use this only if privileges allow.

Drop old task:

```sql
BEGIN
  DBMS_ADVISOR.DELETE_TASK('DAY2_SECOND_ACCESS_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

Run quick tune for the branch dashboard:

```sql
DECLARE
  l_sql VARCHAR2(32767);
BEGIN
  l_sql := q'[
    SELECT branch_id,
           COUNT(*) AS txn_count,
           SUM(amount) AS total_amount
    FROM day2_practice_txn
    WHERE txn_date >= ADD_MONTHS(SYSDATE, -3)
    GROUP BY branch_id
    ORDER BY total_amount DESC
  ]';

  DBMS_ADVISOR.QUICK_TUNE(
    advisor_name => 'SQL Access Advisor',
    task_name    => 'DAY2_SECOND_ACCESS_TASK',
    attr1        => l_sql
  );
END;
/
```

Check task:

```sql
SELECT task_name,
       advisor_name,
       status,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_SECOND_ACCESS_TASK';
```

Review recommendations:

```sql
SELECT rec_id,
       rank,
       benefit,
       type
FROM user_advisor_recommendations
WHERE task_name = 'DAY2_SECOND_ACCESS_TASK'
ORDER BY rank;
```

Review actions:

```sql
SELECT rec_id,
       action_id,
       command,
       attr1,
       attr2,
       attr3
FROM user_advisor_actions
WHERE task_name = 'DAY2_SECOND_ACCESS_TASK'
ORDER BY rec_id, action_id;
```

If this fails:

```text
Use the manual access-design table. Privilege issues should not block the learning objective.
```

---

# Part 7 - Memory And I/O Evidence Check

These queries may require catalog access. If your normal user cannot run them, run through the instructor or SYSDBA training session.

Top non-idle waits:

```sql
SELECT event,
       total_waits,
       ROUND(time_waited/100,2) AS time_waited_sec,
       ROUND(average_wait/100,4) AS avg_wait_sec
FROM v$system_event
WHERE wait_class <> 'Idle'
ORDER BY time_waited DESC
FETCH FIRST 10 ROWS ONLY;
```

SQL by disk reads:

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

Temp usage right now:

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

Good interpretation:

```text
Do not jump directly to changing memory parameters.
First identify the SQL, wait event, access path, and whether TEMP or reads are caused by a specific query.
```

---

# Final Answer Pattern

A good final trainee answer:

```text
The slow SQL ID was <sql_id>.

Before tuning, the plan used a full scan of DAY2_PRACTICE_TXN and had higher buffers.

SQL Tuning Advisor recommended <index/statistics/profile/rewrite/no recommendation>.

We tested an invisible index on CUSTOMER_ID, TXN_DATE DESC.

After testing, the plan used an index range scan and buffer gets were lower.

For the wider workload, one index is not enough. The customer lookup, branch dashboard, and exception report have different access patterns.

Before production, we must check duplicate indexes, DML overhead, storage, before/after AWR or SQL metrics, and rollback.
```

---

# Cleanup

Drop advisor tasks:

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_SECOND_STA_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/

BEGIN
  DBMS_ADVISOR.DELETE_TASK('DAY2_SECOND_ACCESS_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

Drop lab objects:

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP INDEX idx_d2p_txn_cust_date_inv';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -1418 THEN
      RAISE;
    END IF;
END;
/

DROP TABLE day2_practice_txn PURGE;
```
