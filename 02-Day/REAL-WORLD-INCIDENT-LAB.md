# Day 2 Real-World Incident Lab

## Huge-Data AWR, ADDM, SQL Tuning Advisor, And Before/After Tuning

This is the full live-workload Day 2 hands-on lab if the environment can support enough data and AWR privileges.

If the VM cannot support the data volume, use the mock-report path instead:

```text
02-Day/MOCK-REPORT-INTERPRETATION-LAB.md
```

Use it instead of the smaller demo workload when you want trainees to feel:

```text
I can create a useful AWR window.
I can identify real pain points from AWR/ASH/ADDM.
I can take a SQL_ID into SQL Tuning Advisor.
I can validate the recommendation before applying it.
```

---

# Scenario

At 11:00 AM, the bank reports:

```text
Customer statement screen is slow.
Branch transaction dashboard is slow.
Fund transfer confirmation is sometimes delayed.
```

The application team cannot provide SQL text.

The DBA must answer:

* Which SQL consumed the most DB time?
* Was the pain CPU, I/O, commit latency, or bad access path?
* What does ADDM recommend?
* Does SQL Tuning Advisor suggest an index, profile, stats, or rewrite?
* Can we prove the fix with before/after metrics?

---

# Lab Shape

This lab creates:

* one large transaction table
* one transfer log table
* an intentionally imperfect index design
* three production-like pain points:
  * customer statement lookup without the right composite index
  * branch dashboard scan and aggregation
  * frequent commit workload

Recommended data scale:

| Machine | `incident_rows` |
| ------- | ---------------: |
| Low-memory VM | use mock report lab |
| Small laptop VM | 500000 |
| Normal training VM | 2000000 |
| Strong training server | 5000000 |

Trainer default:

```sql
DEFINE incident_rows = 2000000
```

Best delivery:

```text
Build DAY2_TXN_BIG before class starts.
During class, trainees validate row count, create snapshots, run workload, read reports, and tune.
```

If table creation takes too long, reduce to:

```sql
DEFINE incident_rows = 500000
```

---

# PART 1 - Build Large Incident Data

## Step 1 - Session Settings

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TRIMSPOOL ON
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

DEFINE incident_rows = 2000000
```

---

## Step 2 - Drop Old Incident Objects

```sql
BEGIN
  FOR r IN (
    SELECT object_name, object_type
    FROM user_objects
    WHERE object_name IN (
      'DAY2_TXN_BIG',
      'DAY2_TRANSFER_LOG',
      'IDX_DAY2_TXN_BRANCH_DATE',
      'IDX_DAY2_TXN_STMT_FIX_INV'
    )
  ) LOOP
    BEGIN
      IF r.object_type = 'TABLE' THEN
        EXECUTE IMMEDIATE 'DROP TABLE ' || r.object_name || ' PURGE';
      ELSIF r.object_type = 'INDEX' THEN
        EXECUTE IMMEDIATE 'DROP INDEX ' || r.object_name;
      END IF;
    EXCEPTION
      WHEN OTHERS THEN NULL;
    END;
  END LOOP;
END;
/
```

---

## Step 3 - Create Large Banking Transaction Table

```sql
CREATE TABLE day2_txn_big
NOLOGGING
AS
SELECT level AS transaction_id,
       MOD(level,100000) + 1 AS customer_id,
       MOD(level,120000) + 1 AS account_id,
       MOD(level,80) + 1 AS branch_id,
       TRUNC(SYSDATE) - MOD(level,730) + DBMS_RANDOM.VALUE(0,1) AS txn_ts,
       ROUND(DBMS_RANDOM.VALUE(1,5000),2) AS amount,
       CASE MOD(level,10)
         WHEN 0 THEN 'FAILED'
         WHEN 1 THEN 'PENDING'
         ELSE 'SUCCESS'
       END AS status,
       CASE MOD(level,5)
         WHEN 0 THEN 'MOBILE'
         WHEN 1 THEN 'ATM'
         WHEN 2 THEN 'BRANCH'
         WHEN 3 THEN 'INTERNET'
         ELSE 'API'
       END AS channel,
       LPAD(MOD(level,1000000000),12,'0') AS reference_no,
       RPAD('statement payload',120,'x') AS payload
FROM dual
CONNECT BY level <= &incident_rows;
```

Create only a partial index. This is intentional.

```sql
CREATE INDEX idx_day2_txn_branch_date
ON day2_txn_big(branch_id, txn_ts);
```

The missing index is:

```text
customer_id + txn_ts
```

This missing access path should make the customer-statement SQL expensive enough to appear in AWR.

---

## Step 4 - Create Commit Workload Table

```sql
CREATE TABLE day2_transfer_log (
    log_id      NUMBER,
    customer_id NUMBER,
    amount      NUMBER(12,2),
    status      VARCHAR2(20),
    created_at  DATE
);
```

---

## Step 5 - Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname          => USER,
    tabname          => 'DAY2_TXN_BIG',
    estimate_percent => DBMS_STATS.AUTO_SAMPLE_SIZE,
    method_opt       => 'FOR ALL COLUMNS SIZE AUTO',
    cascade          => TRUE
  );

  DBMS_STATS.GATHER_TABLE_STATS(
    ownname          => USER,
    tabname          => 'DAY2_TRANSFER_LOG',
    cascade          => TRUE
  );
END;
/
```

Check row count:

```sql
SELECT COUNT(*) AS day2_txn_big_rows
FROM day2_txn_big;
```

---

# PART 2 - Quality Snapshot Rules

Do not generate AWR from a weak 30-second workload.

For a useful classroom AWR:

* use at least 500k rows, preferably 2M+
* warm up the SQL once before the start snapshot
* run the workload for 6-10 minutes
* include repeated executions
* include more than one symptom, but keep one clear top SQL
* create manual begin and end snapshots
* verify tagged SQL is visible in `V$SQL`
* generate AWR and ADDM from the exact same snapshot pair

Quality target:

```text
The AWR report should show DAY2_INCIDENT tags in Top SQL sections.
ADDM should either identify high-load SQL/I/O/commit impact or explain that the window was not intense enough.
```

---

# PART 3 - Warm Up The Incident SQL

Run each SQL once before the start snapshot.

## Customer Statement Pain Point

```sql
SELECT /* day2_incident_customer_statement */
       COUNT(*)
FROM (
  SELECT transaction_id,
         txn_ts,
         amount,
         status,
         channel
  FROM day2_txn_big
  WHERE customer_id = 42424
  AND txn_ts >= ADD_MONTHS(SYSDATE,-18)
  ORDER BY txn_ts DESC
  FETCH FIRST 200 ROWS ONLY
);
```

## Branch Dashboard Pain Point

```sql
SELECT /* day2_incident_branch_dashboard */
       COUNT(*)
FROM (
  SELECT branch_id,
         status,
         COUNT(*) AS txn_count,
         SUM(amount) AS total_amount
  FROM day2_txn_big
  WHERE txn_ts >= ADD_MONTHS(SYSDATE,-6)
  GROUP BY branch_id, status
  ORDER BY total_amount DESC
);
```

## Reference Search Pain Point

```sql
SELECT /* day2_incident_reference_search */
       COUNT(*)
FROM day2_txn_big
WHERE SUBSTR(reference_no,8,5) = '12345';
```

---

# PART 4 - Create AWR Begin Snapshot

```sql
COLUMN dbid NEW_VALUE dbid
COLUMN inst_num NEW_VALUE inst_num

SELECT dbid
FROM v$database;

SELECT instance_number AS inst_num
FROM v$instance;

EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;

COLUMN begin_snap NEW_VALUE begin_snap

SELECT MAX(s.snap_id) AS begin_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;

SELECT &begin_snap AS begin_snapshot_id
FROM dual;
```

---

# PART 5 - Run Production-Like Workload

## Preferred Path - Concurrent Workload With Scheduler Jobs

Use this if the training user has `CREATE JOB`.

This creates three sessions:

* customer statement lookup loop
* dashboard/reporting loop
* commit-heavy transfer loop

Run for about 8 minutes.

```sql
BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_STMT_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_DASH_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_COMMIT_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
```

```sql
BEGIN
  DBMS_SCHEDULER.CREATE_JOB(
    job_name   => 'DAY2_INCIDENT_STMT_JOB',
    job_type   => 'PLSQL_BLOCK',
    job_action => q'[
      DECLARE
        l_count NUMBER;
        l_end   DATE := SYSDATE + (8/1440);
        l_customer_id NUMBER;
      BEGIN
        DBMS_APPLICATION_INFO.SET_MODULE('DAY2_INCIDENT_BANKING_APP','CUSTOMER_STATEMENT');

        WHILE SYSDATE < l_end LOOP
          l_customer_id := MOD(ABS(DBMS_RANDOM.RANDOM),100000) + 1;

          SELECT /* day2_incident_customer_statement */
                 COUNT(*)
          INTO l_count
          FROM (
            SELECT transaction_id,
                   txn_ts,
                   amount,
                   status,
                   channel
            FROM day2_txn_big
            WHERE customer_id = l_customer_id
            AND txn_ts >= ADD_MONTHS(SYSDATE,-18)
            ORDER BY txn_ts DESC
            FETCH FIRST 200 ROWS ONLY
          );
        END LOOP;
      END;
    ]',
    enabled    => TRUE,
    auto_drop  => FALSE
  );

  DBMS_SCHEDULER.CREATE_JOB(
    job_name   => 'DAY2_INCIDENT_DASH_JOB',
    job_type   => 'PLSQL_BLOCK',
    job_action => q'[
      DECLARE
        l_count NUMBER;
        l_end   DATE := SYSDATE + (8/1440);
      BEGIN
        DBMS_APPLICATION_INFO.SET_MODULE('DAY2_INCIDENT_BANKING_APP','BRANCH_DASHBOARD');

        WHILE SYSDATE < l_end LOOP
          SELECT /* day2_incident_branch_dashboard */
                 COUNT(*)
          INTO l_count
          FROM (
            SELECT branch_id,
                   status,
                   COUNT(*) AS txn_count,
                   SUM(amount) AS total_amount
            FROM day2_txn_big
            WHERE txn_ts >= ADD_MONTHS(SYSDATE,-6)
            GROUP BY branch_id, status
            ORDER BY total_amount DESC
          );
        END LOOP;
      END;
    ]',
    enabled    => TRUE,
    auto_drop  => FALSE
  );

  DBMS_SCHEDULER.CREATE_JOB(
    job_name   => 'DAY2_INCIDENT_COMMIT_JOB',
    job_type   => 'PLSQL_BLOCK',
    job_action => q'[
      DECLARE
        l_end DATE := SYSDATE + (8/1440);
        l_id  NUMBER := 0;
      BEGIN
        DBMS_APPLICATION_INFO.SET_MODULE('DAY2_INCIDENT_BANKING_APP','TRANSFER_COMMIT');

        WHILE SYSDATE < l_end LOOP
          l_id := l_id + 1;

          INSERT /* day2_incident_transfer_commit */
          INTO day2_transfer_log
          VALUES (
            l_id,
            MOD(l_id,100000) + 1,
            ROUND(DBMS_RANDOM.VALUE(10,5000),2),
            'POSTED',
            SYSDATE
          );

          COMMIT;
        END LOOP;
      END;
    ]',
    enabled    => TRUE,
    auto_drop  => FALSE
  );
END;
/
```

Watch progress:

```sql
SELECT job_name,
       state,
       run_count,
       failure_count,
       last_start_date
FROM user_scheduler_jobs
WHERE job_name LIKE 'DAY2_INCIDENT_%'
ORDER BY job_name;
```

---

## Fallback Path - Single-Session Workload

Use this if scheduler privileges are unavailable.

```sql
DECLARE
  l_count NUMBER;
  l_end   DATE := SYSDATE + (8/1440);
  l_id    NUMBER := 0;
  l_customer_id NUMBER;
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE('DAY2_INCIDENT_BANKING_APP','SINGLE_SESSION_FALLBACK');

  WHILE SYSDATE < l_end LOOP
    l_customer_id := MOD(ABS(DBMS_RANDOM.RANDOM),100000) + 1;

    SELECT /* day2_incident_customer_statement */
           COUNT(*)
    INTO l_count
    FROM (
      SELECT transaction_id,
             txn_ts,
             amount,
             status,
             channel
      FROM day2_txn_big
      WHERE customer_id = l_customer_id
      AND txn_ts >= ADD_MONTHS(SYSDATE,-18)
      ORDER BY txn_ts DESC
      FETCH FIRST 200 ROWS ONLY
    );

    SELECT /* day2_incident_branch_dashboard */
           COUNT(*)
    INTO l_count
    FROM (
      SELECT branch_id,
             status,
             COUNT(*) AS txn_count,
             SUM(amount) AS total_amount
      FROM day2_txn_big
      WHERE txn_ts >= ADD_MONTHS(SYSDATE,-6)
      GROUP BY branch_id, status
      ORDER BY total_amount DESC
    );

    SELECT /* day2_incident_reference_search */
           COUNT(*)
    INTO l_count
    FROM day2_txn_big
    WHERE SUBSTR(reference_no,8,5) = '12345';

    l_id := l_id + 1;

    INSERT /* day2_incident_transfer_commit */
    INTO day2_transfer_log
    VALUES (
      l_id,
      MOD(l_id,100000) + 1,
      ROUND(DBMS_RANDOM.VALUE(10,5000),2),
      'POSTED',
      SYSDATE
    );

    COMMIT;
  END LOOP;
END;
/
```

---

# PART 6 - Confirm Workload Visibility Before Ending Snapshot

```sql
SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       rows_processed,
       SUBSTR(sql_text,1,90) sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_incident_%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY elapsed_time DESC
FETCH FIRST 15 ROWS ONLY;
```

Quality check:

```text
If executions are low or elapsed time is too small, run the workload again before creating the end snapshot.
```

---

# PART 7 - Create AWR End Snapshot

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

---

# PART 8 - Generate AWR And ADDM

## AWR Text Report

```sql
SPOOL awr_day2_real_incident.txt

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

## ADDM Report

Preferred reliable path:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

Use:

```text
Begin snapshot: &begin_snap
End snapshot:   &end_snap
Report name:    addm_day2_real_incident.txt
```

---

# PART 9 - Find Pain Points From AWR / ASH

## Top Incident SQL From Cursor Cache

```sql
SELECT sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       ROUND(buffer_gets / NULLIF(executions,0)) buffers_per_exec,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_incident_%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;
```

## ASH Wait Class By SQL

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

## Choose SQL ID For Tuning

Use the customer statement SQL if it appears near the top.

```sql
COLUMN incident_sql_id NEW_VALUE incident_sql_id

SELECT sql_id AS incident_sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE sql_text LIKE '%day2_incident_customer_statement%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY elapsed_time DESC
FETCH FIRST 1 ROW ONLY;

SELECT '&&incident_sql_id' AS sql_id_for_tuning
FROM dual;
```

---

# PART 10 - Inspect The Runtime Plan

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&incident_sql_id',
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Pain-point clues:

* high buffers
* full table scan
* sort operation
* predicates on `CUSTOMER_ID` and `TXN_TS`
* many executions
* same SQL appearing in AWR SQL by elapsed time, gets, or reads

---

# PART 11 - Run SQL Tuning Advisor On The Real Incident SQL

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('DAY2_REAL_INCIDENT_TUNE');
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE NOT IN (-13605, -13780) THEN
      RAISE;
    END IF;
END;
/
```

```sql
DECLARE
  l_task_name VARCHAR2(128);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '&&incident_sql_id',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 90,
    task_name   => 'DAY2_REAL_INCIDENT_TUNE',
    description => 'Real Day 2 incident customer statement SQL'
  );
END;
/
```

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('DAY2_REAL_INCIDENT_TUNE');

SELECT task_name,
       status,
       advisor_name,
       created,
       last_modified
FROM user_advisor_tasks
WHERE task_name = 'DAY2_REAL_INCIDENT_TUNE';
```

```sql
SPOOL sql_tuning_advisor_day2_real_incident.txt

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK(
         task_name => 'DAY2_REAL_INCIDENT_TUNE',
         type      => 'TEXT',
         level     => 'ALL',
         section   => 'ALL'
       ) AS report
FROM dual;

SPOOL OFF
```

Read the report in this order:

```text
1. Findings
2. Recommendation type
3. Estimated benefit
4. Suggested command
5. Risk
6. Manual validation test
```

---

# PART 12 - Validate The Likely Index Fix Safely

Do not create a production-visible index directly.

Use an invisible index for the test session.

## Step 1 - Baseline Before Fix

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
ALTER SESSION SET statistics_level = ALL;

SELECT /* day2_incident_customer_statement_before */
       COUNT(*)
FROM (
  SELECT transaction_id,
         txn_ts,
         amount,
         status,
         channel
  FROM day2_txn_big
  WHERE customer_id = 42424
  AND txn_ts >= ADD_MONTHS(SYSDATE,-18)
  ORDER BY txn_ts DESC
  FETCH FIRST 200 ROWS ONLY
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
* sort operation

---

## Step 2 - Create Candidate Invisible Index

```sql
CREATE INDEX idx_day2_txn_stmt_fix_inv
ON day2_txn_big(customer_id, txn_ts DESC)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_INDEX_STATS(USER, 'IDX_DAY2_TXN_STMT_FIX_INV');
END;
/
```

---

## Step 3 - Test After Fix In This Session Only

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;

SELECT /* day2_incident_customer_statement_after */
       COUNT(*)
FROM (
  SELECT transaction_id,
         txn_ts,
         amount,
         status,
         channel
  FROM day2_txn_big
  WHERE customer_id = 42424
  AND txn_ts >= ADD_MONTHS(SYSDATE,-18)
  ORDER BY txn_ts DESC
  FETCH FIRST 200 ROWS ONLY
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

| Metric | Before | After | Evidence |
| ------ | ------ | ----- | -------- |
| Elapsed time | | | |
| Buffers | | | |
| Disk reads | | | |
| Access path | | | |
| Sort operation | | | |
| DML risk | | | |

Expected improvement:

```text
The after plan should use IDX_DAY2_TXN_STMT_FIX_INV or show lower buffers/elapsed time.
```

If Oracle does not choose the index:

* check stats
* check selectivity
* test a more selective customer
* compare with `INDEX` hint only as a diagnostic test, not as the final fix

Diagnostic hint test:

```sql
SELECT /*+ INDEX(t idx_day2_txn_stmt_fix_inv) */ /* day2_incident_customer_statement_after_hint */
       COUNT(*)
FROM (
  SELECT t.transaction_id,
         t.txn_ts,
         t.amount,
         t.status,
         t.channel
  FROM day2_txn_big t
  WHERE t.customer_id = 42424
  AND t.txn_ts >= ADD_MONTHS(SYSDATE,-18)
  ORDER BY t.txn_ts DESC
  FETCH FIRST 200 ROWS ONLY
);
```

---

# PART 13 - Final DBA Recommendation

Participants must write this:

```text
Incident summary:

The AWR window from [begin_snap] to [end_snap] shows the main database time was caused by [SQL_ID / wait class / event].

ADDM finding:
[finding and impact]

Top SQL evidence:
[SQL_ID, elapsed time, executions, buffers, disk reads]

Plan evidence:
[full scan/index scan/sort/predicate issue]

SQL Tuning Advisor recommendation:
[index/profile/stats/rewrite/no recommendation]

Validated fix:
[candidate invisible index or other fix]

Before/after proof:
[elapsed, buffers, reads, plan change]

Production caution:
[DML impact, storage, change approval, rollback, license]
```

Trainer target:

```text
Every trainee should leave with this exact mental workflow:

Complaint
  -> quality AWR snapshot window
  -> AWR/ASH pain point
  -> ADDM recommendation
  -> SQL_ID plan
  -> SQL Tuning Advisor
  -> controlled fix test
  -> before/after proof
  -> production-safe recommendation
```

---

# PART 14 - Cleanup

Only run cleanup after the training is finished.

```sql
BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_STMT_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_DASH_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SCHEDULER.DROP_JOB('DAY2_INCIDENT_COMMIT_JOB', force => TRUE);
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

DROP INDEX idx_day2_txn_stmt_fix_inv;
DROP TABLE day2_transfer_log PURGE;
DROP TABLE day2_txn_big PURGE;
```

If an object does not exist, ignore the drop error.
