# Day 2 Command Reference

Copy/paste these commands during Day 2 demos and labs.

For low-memory environments, use this mock-report lab as the primary Day 2 activity:

```text
02-Day/MOCK-REPORT-INTERPRETATION-LAB.md
```

Mock report files:

```text
02-Day/mock-reports/awr_day2_mock_incident.txt
02-Day/mock-reports/addm_day2_mock_incident.txt
02-Day/mock-reports/sql_tuning_advisor_day2_mock.txt
```

For a stronger live workload environment, use this runbook as the primary command source:

```text
02-Day/REAL-WORLD-INCIDENT-LAB.md
```

It covers:

```text
large incident data
quality AWR snapshots
production-like workload
AWR/ASH pain-point discovery
ADDM report generation
SQL Tuning Advisor on the real SQL_ID
invisible-index before/after validation
```

Use the smaller commands below as fallback or quick demos.

---

## Day 2 Morning - AWR And ADDM

### Command ID: 0029 - SQL*Plus settings for reports

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TRIMSPOOL ON
SET TIMING ON
SET AUTOTRACE OFF
```

### Command ID: 0030 - Confirm AWR access and get DBID/instance

```sql
SELECT COUNT(*) AS awr_snapshot_count
FROM dba_hist_snapshot;

COLUMN dbid NEW_VALUE dbid
COLUMN inst_num NEW_VALUE inst_num

SELECT dbid
FROM v$database;

SELECT instance_number AS inst_num
FROM v$instance;
```

### Command ID: 0031 - Create AWR helper table

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE awr_commit_test PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

CREATE TABLE awr_commit_test (
    id          NUMBER,
    payload     VARCHAR2(100),
    created_at  DATE
);
```

### Command ID: 0032 - Create AWR start snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;

COLUMN begin_snap NEW_VALUE begin_snap

SELECT MAX(s.snap_id) AS begin_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;

SELECT &begin_snap AS begin_snapshot_id
FROM dual;
```

### Command ID: 0033 - Run tagged AWR workload

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'ORACLE19C_DAY2_AWR_LAB',
    action_name => 'CONTROLLED_WORKLOAD'
  );
END;
/

DECLARE
  v_number NUMBER;
BEGIN
  FOR i IN 1..12 LOOP
    SELECT /*+ FULL(t) */ /* awr_day2_full_scan_txn */
           SUM(amount)
    INTO v_number
    FROM transactions t
    WHERE status = 'SUCCESS';

    SELECT /* awr_day2_date_sort_txn */
           COUNT(*)
    INTO v_number
    FROM (
      SELECT /*+ FULL(t) */ transaction_id, amount, transaction_date
      FROM transactions t
      WHERE transaction_date >= ADD_MONTHS(SYSDATE,-24)
      ORDER BY amount DESC, transaction_date DESC
      FETCH FIRST 5000 ROWS ONLY
    );

    SELECT /*+ FULL(c) */ /* awr_day2_function_customer */
           COUNT(*)
    INTO v_number
    FROM customers c
    WHERE LOWER(email) LIKE '%user%';

    SELECT /*+ FULL(a) */ /* awr_day2_account_lookup */
           COUNT(*)
    INTO v_number
    FROM accounts a
    WHERE TO_NUMBER(account_number) BETWEEN 1000000001 AND 1000010000;
  END LOOP;
END;
/
```

### Command ID: 0034 - Optional commit workload

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_ACTION('COMMIT_WORKLOAD');

  FOR i IN 1..500 LOOP
    INSERT /* awr_day2_commit_test */
    INTO awr_commit_test
    VALUES (i, 'commit workload', SYSDATE);

    COMMIT;
  END LOOP;
END;
/
```

### Command ID: 0035 - Verify tagged SQL in `V$SQL`

```sql
SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       rows_processed,
       SUBSTR(sql_text,1,80) sql_text
FROM v$sql
WHERE sql_text LIKE '%awr_day2_%'
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;
```

### Command ID: 0036 - Create AWR end snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;

COLUMN end_snap NEW_VALUE end_snap

SELECT MAX(s.snap_id) AS end_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;

SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

### Command ID: 0037 - Generate AWR text report

```sql
SPOOL awr_day2_morning.txt

SELECT output
FROM TABLE(
  DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_TEXT(
    &dbid,
    &inst_num,
    &begin_snap,
    &end_snap
  )
);

SPOOL OFF
```

### Command ID: 0038 - Interactive AWR report fallback

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

### Command ID: 0039 - Generate ADDM report

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

### Command ID: 0040 - Follow up from AWR SQL ID

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    'sql_id_from_awr_here',
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: 0040A - ASH wait-class summary for the live window

```sql
SELECT NVL(wait_class,'CPU') AS wait_class,
       COUNT(*) AS ash_samples
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (30/1440)
GROUP BY NVL(wait_class,'CPU')
ORDER BY ash_samples DESC;
```

### Command ID: 0040B - ASH by SQL ID and event

```sql
SELECT sql_id,
       NVL(wait_class,'CPU') AS wait_class,
       NVL(event,'ON CPU') AS event,
       COUNT(*) AS ash_samples
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (30/1440)
AND sql_id IS NOT NULL
GROUP BY sql_id,
         NVL(wait_class,'CPU'),
         NVL(event,'ON CPU')
ORDER BY ash_samples DESC
FETCH FIRST 10 ROWS ONLY;
```

### Command ID: 0040C - Historical ASH for the AWR snapshot window

```sql
SELECT h.sql_id,
       NVL(h.wait_class,'CPU') AS wait_class,
       NVL(h.event,'ON CPU') AS event,
       COUNT(*) AS ash_samples
FROM dba_hist_active_sess_history h
JOIN dba_hist_snapshot s
  ON h.dbid = s.dbid
 AND h.instance_number = s.instance_number
 AND h.snap_id = s.snap_id
WHERE h.dbid = &dbid
AND h.instance_number = &inst_num
AND h.snap_id BETWEEN &begin_snap AND &end_snap
AND h.sql_id IS NOT NULL
GROUP BY h.sql_id,
         NVL(h.wait_class,'CPU'),
         NVL(h.event,'ON CPU')
ORDER BY ash_samples DESC
FETCH FIRST 10 ROWS ONLY;
```

---

## Day 2 Afternoon - SQL Tuning Advisor

### Command ID: 0041 - Run tagged SQL for SQL Tuning Advisor

```sql
ALTER SESSION SET statistics_level = ALL;

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

### Command ID: 0042 - Find SQL ID for tuning

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

### Command ID: 0043 - Drop old SQL tuning task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_LOAN_SQL_TUNING_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN RAISE; END IF;
END;
/
```

### Command ID: 0044 - Create SQL tuning task from SQL ID

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

### Command ID: 0045 - Execute and report SQL tuning task

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TUNING_TASK');

SELECT task_name, status, advisor_name, created, last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_LOAN_SQL_TUNING_TASK';

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

### Command ID: 0046 - Optional accept SQL Profile in disposable lab only

```sql
EXEC DBMS_SQLTUNE.ACCEPT_SQL_PROFILE(
  task_name  => 'DAY2_LOAN_SQL_TUNING_TASK',
  task_owner => USER,
  replace    => TRUE
);

SELECT name, category, status, created, sql_text
FROM dba_sql_profiles
ORDER BY created DESC
FETCH FIRST 10 ROWS ONLY;
```

### Command ID: 0047 - SQL Profile rollback

```sql
EXEC DBMS_SQLTUNE.DROP_SQL_PROFILE(name => 'profile_name_here');
```

---

## Day 2 Afternoon - SQL Access Advisor And Memory/I/O

### Command ID: 0048 - Recreate `LOAN_PAYMENTS`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE loan_payments PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
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

### Command ID: 0049 - Insert `LOAN_PAYMENTS`

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO loan_payments VALUES (
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

    IF MOD(i,10000) = 0 THEN COMMIT; END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: 0050 - Gather Day 2 advisor stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'LOAN_PAYMENTS', cascade => TRUE);
END;
/
```

### Command ID: 0051 - Run SQL Access workload queries

```sql
SELECT /* access_wkld_daily_txn */ COUNT(*)
FROM (
  SELECT TRUNC(transaction_date), COUNT(*), SUM(amount)
  FROM transactions
  WHERE transaction_date >= ADD_MONTHS(SYSDATE,-1)
  GROUP BY TRUNC(transaction_date)
);

SELECT /* access_wkld_branch_txn */ COUNT(*)
FROM (
  SELECT branch_id, COUNT(*), SUM(amount)
  FROM transactions
  WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3)
  GROUP BY branch_id
);

SELECT /* access_wkld_customer_accounts */ COUNT(*)
FROM (
  SELECT c.customer_id, c.full_name, COUNT(a.account_id), SUM(a.balance)
  FROM customers c
  JOIN accounts a ON c.customer_id = a.customer_id
  WHERE c.status = 'ACTIVE'
  GROUP BY c.customer_id, c.full_name
);

SELECT /* access_wkld_loan_due */ COUNT(*)
FROM (
  SELECT branch_id, COUNT(*), SUM(emi_amount)
  FROM loan_payments
  WHERE status IN ('DUE','OVERDUE')
  AND due_date <= SYSDATE
  GROUP BY branch_id
);
```

### Command ID: 0052 - Optional SQL Access Advisor quick tune

```sql
BEGIN
  DBMS_ADVISOR.DELETE_TASK('DAY2_ACCESS_QUICK_TASK');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN RAISE; END IF;
END;
/

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

### Command ID: 0053 - View SQL Access Advisor recommendations

```sql
SELECT rec_id, rank, benefit, type
FROM user_advisor_recommendations
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK'
ORDER BY rank;

SELECT rec_id, action_id, command, attr1, attr2, attr3
FROM user_advisor_actions
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK'
ORDER BY rec_id, action_id;
```

### Command ID: 0054 - Materialized view summary demo

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP MATERIALIZED VIEW mv_branch_daily_txn';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-12003, -942) THEN RAISE; END IF;
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

### Command ID: 0054A - Manual invisible-index before/after test

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

CREATE INDEX idx_lp_status_due_branch_inv
ON loan_payments(status, due_date, branch_id)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_INDEX_STATS(USER, 'IDX_LP_STATUS_DUE_BRANCH_INV');
END;
/

ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;

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

ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
DROP INDEX idx_lp_status_due_branch_inv;
```

### Command ID: 0054B - Compare materialized-view demo metrics in `V$SQL`

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

### Command ID: 0055 - Memory and I/O symptom queries

```sql
SELECT event,
       total_waits,
       ROUND(time_waited/100,2) AS time_waited_sec,
       ROUND(average_wait/100,4) AS avg_wait_sec
FROM v$system_event
WHERE wait_class <> 'Idle'
ORDER BY time_waited DESC
FETCH FIRST 15 ROWS ONLY;

SELECT name, value
FROM v$sysstat
WHERE name IN (
  'physical reads',
  'physical reads cache',
  'physical reads direct',
  'physical write total IO requests',
  'session logical reads'
)
ORDER BY name;

SELECT name, value, unit
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

### Command ID: 0094 - Day 2 table and row-count readiness checks

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('CUSTOMERS','ACCOUNTS','TRANSACTIONS')
ORDER BY table_name;

SELECT 'CUSTOMERS' table_name, COUNT(*) row_count FROM customers
UNION ALL
SELECT 'TRANSACTIONS', COUNT(*) FROM transactions
UNION ALL
SELECT 'ACCOUNTS', COUNT(*) FROM accounts;
```

### Command ID: 0095 - Capture current indexes before advisor demos

```sql
SELECT table_name,
       index_name,
       visibility,
       uniqueness
FROM user_indexes
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name;
```

### Command ID: 0096 - Capture runtime plan for SQL Tuning Advisor target SQL

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);

SELECT '&&tune_sql_id' AS sql_id_for_tuning
FROM dual;
```

### Command ID: 0097 - SQL Tuning Advisor SQL-text fallback task

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

### Command ID: 0098 - Execute fallback task and check advisor task status

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TEXT_TASK');

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

### Command ID: 0099 - SQL Tuning Advisor fallback report and spool option

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TEXT_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

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

### Command ID: 0100 - Inspect existing index columns before applying advisor index advice

```sql
SELECT table_name,
       index_name,
       column_name,
       column_position
FROM user_ind_columns
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name, column_position;
```

### Command ID: 0101 - Find SQL Access workload SQL in `V$SQL`

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

### Command ID: 0102 - Explain plan for daily transaction workload pattern

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

### Command ID: 0103 - Explain plan for branch transaction workload pattern

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

### Command ID: 0104 - Explain plan for loan due workload pattern

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

### Command ID: 0105 - Check SQL Access Advisor quick-tune task status

```sql
SELECT task_name,
       advisor_name,
       status,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK';
```

### Command ID: 0106 - Compare base-table report against materialized-view summary

```sql
SELECT /* mv_demo_base */
       branch_id,
       TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-1)
GROUP BY branch_id, TRUNC(transaction_date);

SELECT /* mv_demo_summary */
       branch_id,
       txn_day,
       SUM(txn_count) AS txn_count,
       SUM(total_amount) AS total_amount
FROM mv_branch_daily_txn
WHERE txn_day >= ADD_MONTHS(TRUNC(SYSDATE),-1)
GROUP BY branch_id, txn_day;
```

### Command ID: 0107 - SQL currently causing physical reads

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

### Command ID: 0108 - Current TEMP usage by session and SQL

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

### Command ID: 0109 - SGA sizing context

```sql
SELECT name,
       bytes,
       ROUND(bytes/1024/1024,2) AS mb
FROM v$sgainfo
ORDER BY name;
```

### Command ID: 0141 - Day 2 afternoon session settings

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

### Command ID: 0142 - ADDM snapshot confirmation and recent snapshot list

```sql
SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;

SELECT snap_id,
       begin_interval_time,
       end_interval_time
FROM dba_hist_snapshot
WHERE dbid = &dbid
AND instance_number = &inst_num
ORDER BY snap_id DESC
FETCH FIRST 10 ROWS ONLY;
```
