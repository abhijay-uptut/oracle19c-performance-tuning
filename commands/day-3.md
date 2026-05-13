# Day 3 Command Reference

Generated from the current `03-Day/FIRST.md` and `03-Day/SECOND.md` files.

Use the command IDs to identify commands during delivery. Commands are listed in source order: first `FIRST.md`, then `SECOND.md`. Teaching-only SQL fragments are intentionally excluded so each block is copy/paste runnable or clearly uses placeholders.

---

## Morning Slot - `03-Day/FIRST.md`

### Command ID: D3-0001 - COMMON SESSION SETTINGS

Source: `03-Day/FIRST.md:79`

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

### Command ID: D3-0002 - Step 1 - Drop And Create Payments Table

Source: `03-Day/FIRST.md:273`

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

### Command ID: D3-0003 - Step 2 - Insert Payment Data

Source: `03-Day/FIRST.md:302`

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

### Command ID: D3-0004 - Step 3 - Create Supporting Index

Source: `03-Day/FIRST.md:352`

```sql
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);
```

### Command ID: D3-0005 - Step 4 - Gather Statistics With Histogram

Source: `03-Day/FIRST.md:361`

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

### Command ID: D3-0006 - Step 5 - Validate Setup

Source: `03-Day/FIRST.md:377`

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

### Command ID: D3-0007 - Step 1 - Run Critical SQL

Source: `03-Day/FIRST.md:415`

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

### Command ID: D3-0008 - Step 2 - Find SQL ID, Child Number And Plan Hash

Source: `03-Day/FIRST.md:439`

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

### Command ID: D3-0009 - Step 2 - Find SQL ID, Child Number And Plan Hash

Source: `03-Day/FIRST.md:461`

```sql
SELECT '&&spm_sql_id' AS sql_id,
       '&&spm_child_no' AS child_number,
       '&&spm_plan_hash' AS plan_hash_value
FROM dual;
```

### Command ID: D3-0010 - Step 3 - Display Captured Runtime Plan

Source: `03-Day/FIRST.md:474`

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

### Command ID: D3-0011 - Step 4 - Load Plan From Cursor Cache

Source: `03-Day/FIRST.md:489`

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

### Command ID: D3-0012 - Step 5 - View SQL Plan Baseline

Source: `03-Day/FIRST.md:521`

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

### Command ID: D3-0013 - Step 5 - View SQL Plan Baseline

Source: `03-Day/FIRST.md:537`

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

### Command ID: D3-0014 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:562`

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

### Command ID: D3-0015 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:572`

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

### Command ID: D3-0016 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:594`

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

### Command ID: D3-0017 - Optional - Evolve Report

Source: `03-Day/FIRST.md:659`

```sql
SET LONG 1000000

SELECT DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
         sql_handle => 'sql_handle_here'
       ) AS evolve_report
FROM dual;
```

### Command ID: D3-0018 - Optional - Baseline Rollback Example

Source: `03-Day/FIRST.md:717`

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

### Command ID: D3-0019 - Step 1 - Drop And Create Branch Transactions

Source: `03-Day/FIRST.md:815`

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

### Command ID: D3-0020 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:846`

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

### Command ID: D3-0021 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:864`

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

### Command ID: D3-0022 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:882`

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

### Command ID: D3-0023 - Step 3 - Create Index And Gather Histogram Stats

Source: `03-Day/FIRST.md:902`

```sql
CREATE INDEX idx_branch_txn_branch
ON branch_transactions(branch_id);
```

### Command ID: D3-0024 - Step 3 - Create Index And Gather Histogram Stats

Source: `03-Day/FIRST.md:907`

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

### Command ID: D3-0025 - Step 4 - Verify Distribution And Histogram

Source: `03-Day/FIRST.md:923`

```sql
SELECT branch_id,
       COUNT(*) AS txn_count
FROM branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

### Command ID: D3-0026 - Step 4 - Verify Distribution And Histogram

Source: `03-Day/FIRST.md:941`

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

### Command ID: D3-0027 - Step 5 - Prepare Bind Variable

Source: `03-Day/FIRST.md:961`

```sql
VARIABLE b_branch_id NUMBER
```

### Command ID: D3-0028 - Step 6 - Rare Value First

Source: `03-Day/FIRST.md:971`

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

### Command ID: D3-0029 - Step 7 - Common Value

Source: `03-Day/FIRST.md:999`

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

### Command ID: D3-0030 - Step 8 - Repeat Executions To Encourage ACS

Source: `03-Day/FIRST.md:1033`

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

### Command ID: D3-0031 - Step 9 - Inspect Child Cursors

Source: `03-Day/FIRST.md:1054`

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

### Command ID: D3-0032 - Step 9 - Inspect Child Cursors

Source: `03-Day/FIRST.md:1072`

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

### Command ID: D3-0033 - Slide Content

Source: `03-Day/FIRST.md:1136`

```sql
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

### Command ID: D3-0034 - Hint Demonstration

Source: `03-Day/FIRST.md:1161`

```sql
EXEC :b_branch_id := 3

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0035 - Hint Demonstration

Source: `03-Day/FIRST.md:1173`

```sql
EXEC :b_branch_id := 1

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0036 - Hint Demonstration

Source: `03-Day/FIRST.md:1187`

```sql
EXEC :b_branch_id := 3

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0037 - Hint Demonstration

Source: `03-Day/FIRST.md:1199`

```sql
EXEC :b_branch_id := 1

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```


## Afternoon Slot - `03-Day/SECOND.md`

### Command ID: D3-0038 - COMMON SESSION SETTINGS

Source: `03-Day/SECOND.md:63`

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

### Command ID: D3-0039 - BEFORE STARTING

Source: `03-Day/SECOND.md:88`

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('ACCOUNTS','TRANSACTIONS','CUSTOMERS')
ORDER BY table_name;
```

### Command ID: D3-0040 - Query 1 - Blocked Sessions

Source: `03-Day/SECOND.md:201`

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

### Command ID: D3-0041 - Query 2 - Blocker/Waiter Relationship

Source: `03-Day/SECOND.md:225`

```sql
SELECT *
FROM dba_blockers;

SELECT *
FROM dba_waiters;
```

### Command ID: D3-0042 - Query 3 - Locked Objects

Source: `03-Day/SECOND.md:243`

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

### Command ID: D3-0043 - Query 4 - Blocker Details

Source: `03-Day/SECOND.md:268`

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

### Command ID: D3-0044 - Query 5 - SQL Text For Waiter And Blocker

Source: `03-Day/SECOND.md:298`

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

### Command ID: D3-0045 - Step 1 - Setup Account Row

Source: `03-Day/SECOND.md:344`

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

### Command ID: D3-0046 - Step 1 - Setup Account Row

Source: `03-Day/SECOND.md:388`

```sql
SELECT account_id, account_number, balance, status
FROM accounts
WHERE account_id = 101;
```

### Command ID: D3-0047 - Step 2 - Session 1 Creates The Lock

Source: `03-Day/SECOND.md:400`

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

### Command ID: D3-0048 - Step 3 - Session 2 Becomes The Waiter

Source: `03-Day/SECOND.md:429`

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

### Command ID: D3-0049 - Step 4 - Session 3 Diagnoses The Block

Source: `03-Day/SECOND.md:458`

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

### Command ID: D3-0050 - Step 5 - Session 3 Finds Locked Object

Source: `03-Day/SECOND.md:486`

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

### Command ID: D3-0051 - Step 6 - Session 3 Checks Transaction Age

Source: `03-Day/SECOND.md:511`

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

### Command ID: D3-0052 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:539`

```sql
COMMIT;
```

### Command ID: D3-0053 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:545`

```sql
ROLLBACK;
```

### Command ID: D3-0054 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:557`

```sql
COMMIT;
```

### Command ID: D3-0055 - Optional Emergency Command

Source: `03-Day/SECOND.md:567`

```sql
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;
```

### Command ID: D3-0056 - Active Session Snapshot Query

Source: `03-Day/SECOND.md:615`

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

### Command ID: D3-0057 - Active Session Snapshot Query

Source: `03-Day/SECOND.md:635`

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

### Command ID: D3-0058 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:717`

```sql
UPDATE transactions
SET branch_id = 10
WHERE transaction_id <= 80000;

COMMIT;
```

### Command ID: D3-0059 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:727`

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

### Command ID: D3-0060 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:741`

```sql
SELECT branch_id, COUNT(*) AS row_count
FROM transactions
WHERE branch_id IN (10, 11, 12)
GROUP BY branch_id
ORDER BY branch_id;
```

### Command ID: D3-0061 - Step 2 - Make Before Plan Clean

Source: `03-Day/SECOND.md:761`

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

### Command ID: D3-0062 - Optional - AWR Start Snapshot

Source: `03-Day/SECOND.md:785`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: D3-0063 - Problem Query

Source: `03-Day/SECOND.md:801`

```sql
SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;
```

### Command ID: D3-0064 - Run Before Query Safely

Source: `03-Day/SECOND.md:823`

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SET AUTOTRACE OFF
```

### Command ID: D3-0065 - Capture Before Plan

Source: `03-Day/SECOND.md:846`

```sql
EXPLAIN PLAN FOR
SELECT /* capstone_dashboard_before_plan */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D3-0066 - Better Business Query

Source: `03-Day/SECOND.md:875`

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

### Command ID: D3-0067 - Create Supporting Index Safely

Source: `03-Day/SECOND.md:895`

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

### Command ID: D3-0068 - Create Supporting Index Safely

Source: `03-Day/SECOND.md:917`

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

### Command ID: D3-0069 - Run After Query

Source: `03-Day/SECOND.md:932`

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

### Command ID: D3-0070 - Capture After Runtime Plan

Source: `03-Day/SECOND.md:963`

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

### Command ID: D3-0071 - Create A Controlled Lock

Source: `03-Day/SECOND.md:1010`

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

### Command ID: D3-0072 - Create A Controlled Lock

Source: `03-Day/SECOND.md:1054`

```sql
UPDATE /* capstone_lock_blocker */
       accounts
SET balance = balance - 500
WHERE account_id = 101;
```

### Command ID: D3-0073 - Create A Controlled Lock

Source: `03-Day/SECOND.md:1065`

```sql
UPDATE /* capstone_lock_waiter */
       accounts
SET balance = balance + 500
WHERE account_id = 101;
```

### Command ID: D3-0074 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:1084`

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

### Command ID: D3-0075 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:1100`

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

### Command ID: D3-0076 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:1115`

```sql
-- In Session 1
ROLLBACK;
```

### Command ID: D3-0077 - Optional - AWR End Snapshot

Source: `03-Day/SECOND.md:1132`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```
