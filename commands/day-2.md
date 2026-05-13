# Day 2 Command Reference

Generated from the current `02-Day/FIRST.md` and `02-Day/SECOND.md` files.

Use the command IDs to identify commands during delivery. Commands are listed in source order: first `FIRST.md`, then `SECOND.md`. Teaching-only fragments are intentionally excluded so each block is copy/paste runnable or clearly uses placeholders.

For low-memory environments, use the mock-report interpretation lab as the primary activity and use these commands for quick demos, advisor practice, and reference.

Key Oracle report scripts referenced during Day 2:

```text
$ORACLE_HOME/rdbms/admin/awrrpt.sql    # AWR report
$ORACLE_HOME/rdbms/admin/ashrpt.sql    # ASH report
$ORACLE_HOME/rdbms/admin/addmrpt.sql   # ADDM report
```

---

## Morning Slot - `02-Day/FIRST.md`

### Command ID: D2-0001 - COMMON SESSION SETTINGS

Source: `02-Day/FIRST.md:92`

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TRIMSPOOL ON
SET TIMING ON
SET AUTOTRACE OFF
```

### Command ID: D2-0002 - WHERE AWR AND ASH REPORT SCRIPTS LIVE, AND WHERE REPORT FILES ARE CREATED

Source: `02-Day/FIRST.md:162`

```bash
pwd
```

### Command ID: D2-0003 - WHERE AWR AND ASH REPORT SCRIPTS LIVE, AND WHERE REPORT FILES ARE CREATED

Source: `02-Day/FIRST.md:168`

```bash
mkdir -p /tmp/day2_awr_reports
cd /tmp/day2_awr_reports
pwd
sqlplus / as sysdba
```

### Command ID: D2-0004 - Step 1 - Confirm Day 1 Tables Exist (9:30 - 9:33)

Source: `02-Day/FIRST.md:401`

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('TRANSACTIONS','CUSTOMERS','ACCOUNTS')
ORDER BY table_name;
```

### Command ID: D2-0005 - Step 2 - Confirm Data Volume (9:33 - 9:36)

Source: `02-Day/FIRST.md:422`

```sql
SELECT 'TRANSACTIONS' table_name, COUNT(*) row_count FROM transactions
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM customers
UNION ALL
SELECT 'ACCOUNTS', COUNT(*) FROM accounts;
```

### Command ID: D2-0006 - Step 3 - Confirm AWR Access (9:36 - 9:39)

Source: `02-Day/FIRST.md:446`

```sql
SELECT COUNT(*) AS awr_snapshot_count
FROM dba_hist_snapshot;
```

### Command ID: D2-0007 - Step 4 - Get DBID And Instance Number (9:39 - 9:42)

Source: `02-Day/FIRST.md:462`

```sql
COLUMN dbid NEW_VALUE dbid
COLUMN inst_num NEW_VALUE inst_num

SELECT dbid
FROM v$database;

SELECT instance_number AS inst_num
FROM v$instance;
```

### Command ID: D2-0008 - Step 5 - Create Workload Helper Table (9:42 - 9:45)

Source: `02-Day/FIRST.md:486`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE awr_commit_test PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE awr_commit_test (
    id          NUMBER,
    payload     VARCHAR2(100),
    created_at  DATE
);
```

### Command ID: D2-0009 - Step 1 - Create Start Snapshot (9:48 - 9:51)

Source: `02-Day/FIRST.md:546`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: D2-0010 - Step 1 - Create Start Snapshot (9:48 - 9:51)

Source: `02-Day/FIRST.md:552`

```sql
COLUMN begin_snap NEW_VALUE begin_snap

SELECT MAX(s.snap_id) AS begin_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;
```

### Command ID: D2-0011 - Step 1 - Create Start Snapshot (9:48 - 9:51)

Source: `02-Day/FIRST.md:563`

```sql
SELECT &begin_snap AS begin_snapshot_id
FROM dual;
```

### Command ID: D2-0012 - Step 2 - Run Tagged Workload (9:51 - 10:00)

Source: `02-Day/FIRST.md:574`

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'ORACLE19C_DAY2_AWR_LAB',
    action_name => 'CONTROLLED_WORKLOAD'
  );
END;
/
```

### Command ID: D2-0013 - Step 2 - Run Tagged Workload (9:51 - 10:00)

Source: `02-Day/FIRST.md:584`

```sql
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

### Command ID: D2-0014 - Optional Step - Generate Commit Wait Activity (9:58 - 10:00, only if machine allows)

Source: `02-Day/FIRST.md:640`

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_ACTION('COMMIT_WORKLOAD');

  FOR i IN 1..500 LOOP
    INSERT /* awr_day2_commit_test */
    INTO awr_commit_test
    VALUES (
      i,
      'commit workload',
      SYSDATE
    );

    COMMIT;
  END LOOP;
END;
/
```

### Command ID: D2-0015 - Step 3 - Verify Tagged SQL In V$SQL (10:00 - 10:03)

Source: `02-Day/FIRST.md:673`

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

### Command ID: D2-0016 - Step 4 - Create End Snapshot (10:03 - 10:06)

Source: `02-Day/FIRST.md:698`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: D2-0017 - Step 4 - Create End Snapshot (10:03 - 10:06)

Source: `02-Day/FIRST.md:704`

```sql
COLUMN end_snap NEW_VALUE end_snap

SELECT MAX(s.snap_id) AS end_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;
```

### Command ID: D2-0018 - Step 4 - Create End Snapshot (10:03 - 10:06)

Source: `02-Day/FIRST.md:715`

```sql
SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

### Command ID: D2-0019 - Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Source: `02-Day/FIRST.md:735`

```bash
mkdir -p /tmp/day2_awr_reports
cd /tmp/day2_awr_reports
pwd
sqlplus / as sysdba
```

### Command ID: D2-0020 - Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Source: `02-Day/FIRST.md:751`

```sql
SELECT name, dbid
FROM v$database;

SELECT instance_name, instance_number
FROM v$instance;

SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

### Command ID: D2-0021 - Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Source: `02-Day/FIRST.md:771`

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

### Command ID: D2-0022 - Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Source: `02-Day/FIRST.md:795`

```bash
ls -lh /tmp/day2_awr_reports/awr_day2_morning.html
```

### Command ID: D2-0023 - Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Source: `02-Day/FIRST.md:807`

```sql
SPOOL /tmp/day2_awr_reports/awr_day2_morning.txt

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

### Command ID: D2-0024 - Step 6 - Generate ASH HTML Report For The Same Window (10:09 - 10:10, demo or trainer reference)

Source: `02-Day/FIRST.md:843`

```sql
@$ORACLE_HOME/rdbms/admin/ashrpt.sql
```

### Command ID: D2-0025 - Step 6 - Generate ASH HTML Report For The Same Window (10:09 - 10:10, demo or trainer reference)

Source: `02-Day/FIRST.md:867`

```sql
SELECT dbid FROM v$database;
SELECT instance_number FROM v$instance;
```

### Command ID: D2-0026 - Step 6 - Generate ASH HTML Report For The Same Window (10:09 - 10:10, demo or trainer reference)

Source: `02-Day/FIRST.md:874`

```sql
SELECT snap_id,
       TO_CHAR(begin_interval_time,'YYYY-MM-DD HH24:MI:SS') AS begin_time,
       TO_CHAR(end_interval_time,'YYYY-MM-DD HH24:MI:SS')   AS end_time
FROM dba_hist_snapshot
WHERE dbid = &dbid
AND instance_number = &inst_num
AND snap_id BETWEEN &begin_snap AND &end_snap
ORDER BY snap_id;
```

### Command ID: D2-0027 - Step 6 - Generate ASH HTML Report For The Same Window (10:09 - 10:10, demo or trainer reference)

Source: `02-Day/FIRST.md:887`

```bash
ls -lh /tmp/day2_awr_reports/ash_day2_morning.html
```

### Command ID: D2-0028 - Slide Content

Source: `02-Day/FIRST.md:1551`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

### Command ID: D2-0029 - Slide Content

Source: `02-Day/FIRST.md:1802`

```sql
SELECT sql_id,
       executions,
       parse_calls,
       version_count,
       substr(sql_text,1,120) sql_text
FROM v$sqlarea
WHERE parse_calls > 1000
ORDER BY parse_calls DESC
FETCH FIRST 20 ROWS ONLY;
```

### Command ID: D2-0030 - Slide Content

Source: `02-Day/FIRST.md:1901`

```sql
SELECT sql_id,
       child_number,
       executions,
       plan_hash_value,
       is_bind_sensitive,
       is_bind_aware,
       is_shareable
FROM v$sql
WHERE sql_id = '&&sql_id_from_awr'
ORDER BY child_number;
```

### Command ID: D2-0031 - Slide Content

Source: `02-Day/FIRST.md:1949`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

### Command ID: D2-0032 - Slide Content

Source: `02-Day/FIRST.md:1961`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    sql_id => '&&sql_id_from_awr',
    cursor_child_no => NULL,
    format => 'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

### Command ID: D2-0033 - Slide Content

Source: `02-Day/FIRST.md:2310`

```sql
SELECT NVL(wait_class,'CPU') AS wait_class,
       COUNT(*) AS ash_samples
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (30/1440)
GROUP BY NVL(wait_class,'CPU')
ORDER BY ash_samples DESC;
```

### Command ID: D2-0034 - Slide Content

Source: `02-Day/FIRST.md:2321`

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

### Command ID: D2-0035 - Slide Content

Source: `02-Day/FIRST.md:2338`

```sql
SELECT h.sql_id,
       NVL(h.wait_class,'CPU') AS wait_class,
       NVL(h.event,'ON CPU') AS event,
       COUNT(*) AS ash_samples
FROM dba_hist_active_sess_history h
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

### Command ID: D2-0036 - Slide Content

Source: `02-Day/FIRST.md:2538`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

### Command ID: D2-0037 - Slide Content

Source: `02-Day/FIRST.md:2550`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&sql_id_from_awr',
    NULL,
    'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

### Command ID: D2-0038 - Step 1 - Confirm Snapshot IDs (11:03 - 11:06)

Source: `02-Day/FIRST.md:2652`

```sql
SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

### Command ID: D2-0039 - Step 1 - Confirm Snapshot IDs (11:03 - 11:06)

Source: `02-Day/FIRST.md:2660`

```sql
SELECT snap_id,
       begin_interval_time,
       end_interval_time
FROM dba_hist_snapshot
WHERE dbid = &dbid
AND instance_number = &inst_num
ORDER BY snap_id DESC
FETCH FIRST 10 ROWS ONLY;
```

### Command ID: D2-0040 - Step 2 - Generate ADDM Report (11:06 - 11:18)

Source: `02-Day/FIRST.md:2677`

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

---

## Afternoon Slot - `02-Day/SECOND.md`

### Command ID: D2-0041 - COMMON SESSION SETTINGS

Source: `02-Day/SECOND.md:92`

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

### Command ID: D2-0042 - BEFORE STARTING

Source: `02-Day/SECOND.md:171`

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('CUSTOMERS','ACCOUNTS','TRANSACTIONS')
ORDER BY table_name;
```

### Command ID: D2-0043 - Step 1 - Run One SQL Once

Source: `02-Day/SECOND.md:293`

```sql
SELECT /* day2_sta_simple_customer */
       *
FROM transactions
WHERE customer_id = 1001;
```

### Command ID: D2-0044 - Step 1 - Run One SQL Once

Source: `02-Day/SECOND.md:302`

```sql
SELECT customer_id
FROM transactions
WHERE customer_id IS NOT NULL
FETCH FIRST 1 ROW ONLY;
```

### Command ID: D2-0045 - Step 2 - Find The SQL_ID

Source: `02-Day/SECOND.md:321`

```sql
COLUMN sql_id FORMAT A15
COLUMN sql_text FORMAT A100

SELECT sql_id,
       child_number,
       executions,
       sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_sta_simple_customer%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY last_active_time DESC;
```

### Command ID: D2-0046 - Step 3 - Drop Any Old Task

Source: `02-Day/SECOND.md:353`

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('TUNE_CUSTOMER_QUERY');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

### Command ID: D2-0047 - Step 4 - Create The Tuning Task

Source: `02-Day/SECOND.md:371`

```sql
DECLARE
  l_task_name VARCHAR2(100);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '9x8abc123xyz',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'TUNE_CUSTOMER_QUERY',
    description => 'Simple Day 2 SQL Tuning Advisor demo'
  );
END;
/
```

### Command ID: D2-0048 - Step 5 - Execute The Task

Source: `02-Day/SECOND.md:397`

```sql
BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK(
    task_name => 'TUNE_CUSTOMER_QUERY'
  );
END;
/
```

### Command ID: D2-0049 - Step 5 - Execute The Task

Source: `02-Day/SECOND.md:408`

```sql
SELECT task_name,
       status
FROM user_advisor_tasks
WHERE task_name = 'TUNE_CUSTOMER_QUERY';
```

### Command ID: D2-0050 - Step 6 - View The Suggestions Report

Source: `02-Day/SECOND.md:425`

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'TUNE_CUSTOMER_QUERY',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

### Command ID: D2-0051 - Step 7 - Optional Cleanup

Source: `02-Day/SECOND.md:462`

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK(
    task_name => 'TUNE_CUSTOMER_QUERY'
  );
END;
/
```

### Command ID: D2-0052 - Step 1 - Confirm Supporting Data

Source: `02-Day/SECOND.md:505`

```sql
SELECT 'CUSTOMERS' table_name, COUNT(*) row_count FROM customers
UNION ALL
SELECT 'TRANSACTIONS', COUNT(*) FROM transactions;
```

### Command ID: D2-0053 - Step 2 - Capture Current Indexes

Source: `02-Day/SECOND.md:524`

```sql
SELECT table_name,
       index_name,
       visibility,
       uniqueness
FROM user_indexes
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name;
```

### Command ID: D2-0054 - Step 3 - Run Tagged SQL With Runtime Metrics

Source: `02-Day/SECOND.md:544`

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

### Command ID: D2-0055 - Step 3 - Run Tagged SQL With Runtime Metrics

Source: `02-Day/SECOND.md:565`

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

### Command ID: D2-0056 - Step 4 - Find SQL ID

Source: `02-Day/SECOND.md:589`

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

### Command ID: D2-0057 - Step 4 - Find SQL ID

Source: `02-Day/SECOND.md:608`

```sql
SELECT '&&tune_sql_id' AS sql_id_for_tuning
FROM dual;
```

### Command ID: D2-0058 - Step 1 - Drop Old Task Safely

Source: `02-Day/SECOND.md:640`

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

### Command ID: D2-0059 - Step 2 - Create Tuning Task From SQL ID

Source: `02-Day/SECOND.md:660`

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

### Command ID: D2-0060 - Fallback - Create Tuning Task From SQL Text

Source: `02-Day/SECOND.md:683`

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

### Command ID: D2-0061 - Step 3 - Execute Tuning Task

Source: `02-Day/SECOND.md:736`

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TUNING_TASK');
```

### Command ID: D2-0062 - Step 3 - Execute Tuning Task

Source: `02-Day/SECOND.md:742`

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_LOAN_SQL_TEXT_TASK');
```

### Command ID: D2-0063 - Step 4 - Check Task Status

Source: `02-Day/SECOND.md:750`

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

### Command ID: D2-0064 - Step 5 - Read Advisor Report

Source: `02-Day/SECOND.md:781`

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

### Command ID: D2-0065 - Step 5 - Read Advisor Report

Source: `02-Day/SECOND.md:793`

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_LOAN_SQL_TEXT_TASK',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;
```

### Command ID: D2-0066 - Step 5 - Read Advisor Report

Source: `02-Day/SECOND.md:805`

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

### Command ID: D2-0067 - Optional Lab - Accept SQL Profile In Training Only

Source: `02-Day/SECOND.md:868`

```sql
EXEC DBMS_SQLTUNE.ACCEPT_SQL_PROFILE(
  task_name => 'DAY2_LOAN_SQL_TUNING_TASK',
  task_owner => USER,
  replace => TRUE
);
```

### Command ID: D2-0068 - Optional Lab - Accept SQL Profile In Training Only

Source: `02-Day/SECOND.md:878`

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

### Command ID: D2-0069 - Optional Lab - Accept SQL Profile In Training Only

Source: `02-Day/SECOND.md:893`

```sql
EXEC DBMS_SQLTUNE.DROP_SQL_PROFILE(name => 'profile_name_here');
```

### Command ID: D2-0070 - Manual Validation If Advisor Suggests Index

Source: `02-Day/SECOND.md:909`

```sql
SELECT table_name,
       index_name,
       column_name,
       column_position
FROM user_ind_columns
WHERE table_name IN ('CUSTOMERS','TRANSACTIONS')
ORDER BY table_name, index_name, column_position;
```

### Command ID: D2-0071 - Step 1 - Create Loan Payments Table Safely

Source: `02-Day/SECOND.md:1101`

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

### Command ID: D2-0072 - Step 2 - Insert Loan Payment Data

Source: `02-Day/SECOND.md:1128`

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

### Command ID: D2-0073 - Step 3 - Gather Stats

Source: `02-Day/SECOND.md:1171`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'LOAN_PAYMENTS', cascade => TRUE);
END;
/
```

### Command ID: D2-0074 - Step 4 - Run Workload Queries With Tags

Source: `02-Day/SECOND.md:1187`

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

### Command ID: D2-0075 - Step 5 - Find Workload SQL In V$SQL

Source: `02-Day/SECOND.md:1244`

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

### Command ID: D2-0076 - Step 6 - Generate Plans For Repeated Patterns

Source: `02-Day/SECOND.md:1263`

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

### Command ID: D2-0077 - Step 6 - Generate Plans For Repeated Patterns

Source: `02-Day/SECOND.md:1278`

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

### Command ID: D2-0078 - Step 6 - Generate Plans For Repeated Patterns

Source: `02-Day/SECOND.md:1293`

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

### Command ID: D2-0079 - Practical Example - Why One Index Is Not Always Enough

Source: `02-Day/SECOND.md:1330`

```sql
-- Query A
SELECT *
FROM transactions
WHERE customer_id = 1001;

-- Query B
SELECT branch_id, SUM(amount)
FROM transactions
WHERE transaction_date >= SYSDATE - 30
GROUP BY branch_id;
```

### Command ID: D2-0080 - Practical Example - Why One Index Is Not Always Enough

Source: `02-Day/SECOND.md:1345`

```sql
CREATE INDEX idx_txn_customer
ON transactions(customer_id);
```

### Command ID: D2-0081 - Practical Example - Why One Index Is Not Always Enough

Source: `02-Day/SECOND.md:1354`

```sql
CREATE INDEX idx_txn_date_branch
ON transactions(transaction_date, branch_id);
```

### Command ID: D2-0082 - Optional Advisor Demo - Drop Old Task

Source: `02-Day/SECOND.md:1403`

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

### Command ID: D2-0083 - Optional Advisor Demo - Run QUICK_TUNE

Source: `02-Day/SECOND.md:1421`

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

### Command ID: D2-0084 - Optional Advisor Demo - Check Task

Source: `02-Day/SECOND.md:1452`

```sql
SELECT task_name,
       advisor_name,
       status,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK';
```

### Command ID: D2-0085 - Optional Advisor Demo - Review Recommendations

Source: `02-Day/SECOND.md:1472`

```sql
SELECT rec_id,
       rank,
       benefit,
       type
FROM user_advisor_recommendations
WHERE task_name = 'DAY2_ACCESS_QUICK_TASK'
ORDER BY rank;
```

### Command ID: D2-0086 - Optional Advisor Demo - Review Recommendations

Source: `02-Day/SECOND.md:1484`

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

### Command ID: D2-0087 - Step 1 - Capture Before Metrics

Source: `02-Day/SECOND.md:1586`

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

### Command ID: D2-0088 - Step 2 - Create Candidate Index As Invisible

Source: `02-Day/SECOND.md:1626`

```sql
CREATE INDEX idx_lp_status_due_branch_inv
ON loan_payments(status, due_date, branch_id)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_INDEX_STATS(USER, 'IDX_LP_STATUS_DUE_BRANCH_INV');
END;
/
```

### Command ID: D2-0089 - Step 2 - Create Candidate Index As Invisible

Source: `02-Day/SECOND.md:1639`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;
```

### Command ID: D2-0090 - Step 3 - Capture After Metrics

Source: `02-Day/SECOND.md:1647`

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

### Command ID: D2-0091 - Step 3 - Capture After Metrics

Source: `02-Day/SECOND.md:1691`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
DROP INDEX idx_lp_status_due_branch_inv;
```

### Command ID: D2-0092 - Materialized View Demonstration - Manual Before/After

Source: `02-Day/SECOND.md:1708`

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

### Command ID: D2-0093 - Materialized View Demonstration - Manual Before/After

Source: `02-Day/SECOND.md:1733`

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

### Command ID: D2-0094 - Materialized View Demonstration - Manual Before/After

Source: `02-Day/SECOND.md:1746`

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

### Command ID: D2-0095 - Materialized View Demonstration - Manual Before/After

Source: `02-Day/SECOND.md:1759`

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

### Command ID: D2-0096 - Step 1 - Top Wait Events

Source: `02-Day/SECOND.md:1852`

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

### Command ID: D2-0097 - Step 2 - Physical Read Statistics

Source: `02-Day/SECOND.md:1877`

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

### Command ID: D2-0098 - Step 3 - SQL Currently Causing Reads

Source: `02-Day/SECOND.md:1899`

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

### Command ID: D2-0099 - Step 4 - PGA Workarea Symptoms

Source: `02-Day/SECOND.md:1923`

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

### Command ID: D2-0100 - Step 5 - Temp Usage Right Now

Source: `02-Day/SECOND.md:1948`

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

### Command ID: D2-0101 - Step 6 - SGA Sizing Context

Source: `02-Day/SECOND.md:1977`

```sql
SELECT name,
       bytes,
       ROUND(bytes/1024/1024,2) AS mb
FROM v$sgainfo
ORDER BY name;
```

---
