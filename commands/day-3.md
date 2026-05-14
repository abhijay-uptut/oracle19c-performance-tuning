# Day 3 Command Reference

Generated from the current `03-Day/FIRST.md` and `03-Day/SECOND.md` files.

Use the command IDs to identify commands during delivery. Commands are listed in source order: first `FIRST.md`, then `SECOND.md`. Teaching-only SQL fragments are intentionally excluded so each block is copy/paste runnable or clearly uses placeholders.

Current high-level sequence: histogram demo, payment workload and SQL Plan Management, bind variables and Adaptive Cursor Sharing, hint comparison, locking diagnosis, short-lived incidents, and final capstone.

---

## Morning Slot - `03-Day/FIRST.md`

### Command ID: D3-0001 - COMMON SESSION SETTINGS

Source: `03-Day/FIRST.md:108`

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

### Command ID: D3-0002 - Part 0 - Setup Bank Table

Source: `03-Day/FIRST.md:356`

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

### Command ID: D3-0003 - Part 1 - Create Index

Source: `03-Day/FIRST.md:389`

```sql
CREATE INDEX idx_bank_txn_status
ON bank_txn_demo(txn_status);
```

### Command ID: D3-0004 - Part 2 - Gather Stats Without Histogram

Source: `03-Day/FIRST.md:405`

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

### Command ID: D3-0005 - Part 3 - Confirm Histogram Is None

Source: `03-Day/FIRST.md:427`

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

### Command ID: D3-0006 - Part 4 - Run Failed Transaction Query Before Histogram

Source: `03-Day/FIRST.md:450`

```sql
SELECT /* hist_demo_failed_before */
       *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

### Command ID: D3-0007 - Part 4 - Run Failed Transaction Query Before Histogram

Source: `03-Day/FIRST.md:459`

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

### Command ID: D3-0008 - Part 4 - Run Failed Transaction Query Before Histogram

Source: `03-Day/FIRST.md:479`

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

### Command ID: D3-0009 - Part 5 - Create Histogram

Source: `03-Day/FIRST.md:507`

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

### Command ID: D3-0010 - Part 6 - Confirm Histogram Created

Source: `03-Day/FIRST.md:528`

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

### Command ID: D3-0011 - Part 7 - Run Same Query After Histogram

Source: `03-Day/FIRST.md:551`

```sql
SELECT /* hist_demo_failed_after */
       *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

### Command ID: D3-0012 - Part 7 - Run Same Query After Histogram

Source: `03-Day/FIRST.md:560`

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

### Command ID: D3-0013 - Part 7 - Run Same Query After Histogram

Source: `03-Day/FIRST.md:580`

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

### Command ID: D3-0014 - Step 1 - Drop And Create Payments Table

Source: `03-Day/FIRST.md:809`

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

### Command ID: D3-0015 - Step 2 - Insert Payment Data

Source: `03-Day/FIRST.md:845`

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

### Command ID: D3-0016 - Step 3 - Create Supporting Index

Source: `03-Day/FIRST.md:902`

```sql
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);
```

### Command ID: D3-0017 - Step 4 - Gather Statistics With Histogram

Source: `03-Day/FIRST.md:918`

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

### Command ID: D3-0018 - Step 5 - Validate Setup

Source: `03-Day/FIRST.md:940`

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

### Command ID: D3-0019 - Step 1 - Run Critical SQL

Source: `03-Day/FIRST.md:1004`

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

### Command ID: D3-0020 - Step 2 - Find SQL ID, Child Number And Plan Hash

Source: `03-Day/FIRST.md:1037`

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

### Command ID: D3-0021 - Step 2 - Find SQL ID, Child Number And Plan Hash

Source: `03-Day/FIRST.md:1059`

```sql
SELECT '&&spm_sql_id' AS sql_id,
       '&&spm_child_no' AS child_number,
       '&&spm_plan_hash' AS plan_hash_value
FROM dual;
```

### Command ID: D3-0022 - Step 3 - Display Captured Runtime Plan

Source: `03-Day/FIRST.md:1079`

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

### Command ID: D3-0023 - Step 4 - Load Plan From Cursor Cache

Source: `03-Day/FIRST.md:1100`

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

### Command ID: D3-0024 - Step 5 - View SQL Plan Baseline

Source: `03-Day/FIRST.md:1139`

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

### Command ID: D3-0025 - Step 5 - View SQL Plan Baseline

Source: `03-Day/FIRST.md:1155`

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

### Command ID: D3-0026 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:1186`

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

### Command ID: D3-0027 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:1196`

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

### Command ID: D3-0028 - Step 6 - Rerun Same SQL And Check Baseline Note

Source: `03-Day/FIRST.md:1218`

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

### Command ID: D3-0029 - Optional - Evolve Report

Source: `03-Day/FIRST.md:1314`

```sql
SET LONG 1000000

SELECT DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
         sql_handle => 'sql_handle_here'
       ) AS evolve_report
FROM dual;
```

### Command ID: D3-0030 - Optional - Baseline Rollback Example

Source: `03-Day/FIRST.md:1399`

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

### Command ID: D3-0031 - Step 1 - Drop And Create Branch Transactions

Source: `03-Day/FIRST.md:1558`

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

### Command ID: D3-0032 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:1596`

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

### Command ID: D3-0033 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:1614`

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

### Command ID: D3-0034 - Step 2 - Insert Skewed Data

Source: `03-Day/FIRST.md:1632`

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

### Command ID: D3-0035 - Step 3 - Create Index And Gather Histogram Stats

Source: `03-Day/FIRST.md:1659`

```sql
CREATE INDEX idx_branch_txn_branch
ON branch_transactions(branch_id);
```

### Command ID: D3-0036 - Step 3 - Create Index And Gather Histogram Stats

Source: `03-Day/FIRST.md:1664`

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

### Command ID: D3-0037 - Step 4 - Verify Distribution And Histogram

Source: `03-Day/FIRST.md:1686`

```sql
SELECT branch_id,
       COUNT(*) AS txn_count
FROM branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

### Command ID: D3-0038 - Step 4 - Verify Distribution And Histogram

Source: `03-Day/FIRST.md:1704`

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

### Command ID: D3-0039 - Step 5 - Prepare Bind Variable

Source: `03-Day/FIRST.md:1731`

```sql
VARIABLE b_branch_id NUMBER
```

### Command ID: D3-0040 - Step 6 - Rare Value First

Source: `03-Day/FIRST.md:1748`

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

### Command ID: D3-0041 - Step 7 - Common Value

Source: `03-Day/FIRST.md:1783`

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

### Command ID: D3-0042 - Step 8 - Repeat Executions To Encourage ACS

Source: `03-Day/FIRST.md:1823`

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

### Command ID: D3-0043 - Step 9 - Inspect Child Cursors

Source: `03-Day/FIRST.md:1851`

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

### Command ID: D3-0044 - Step 9 - Inspect Child Cursors

Source: `03-Day/FIRST.md:1869`

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

### Command ID: D3-0045 - Hint Risk With Uneven Branch Traffic

Source: `03-Day/FIRST.md:1957`

```sql
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

### Command ID: D3-0046 - Hint Demonstration

Source: `03-Day/FIRST.md:1995`

```sql
EXEC :b_branch_id := 3

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0047 - Hint Demonstration

Source: `03-Day/FIRST.md:2007`

```sql
EXEC :b_branch_id := 1

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0048 - Hint Demonstration

Source: `03-Day/FIRST.md:2021`

```sql
EXEC :b_branch_id := 3

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: D3-0049 - Hint Demonstration

Source: `03-Day/FIRST.md:2033`

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

### Command ID: D3-0050 - COMMON SESSION SETTINGS

Source: `03-Day/SECOND.md:98`

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

### Command ID: D3-0051 - BEFORE STARTING

Source: `03-Day/SECOND.md:123`

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('ACCOUNTS','TRANSACTIONS','CUSTOMERS')
ORDER BY table_name;
```

### Command ID: D3-0052 - Query 1 - Blocked Sessions

Source: `03-Day/SECOND.md:443`

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

### Command ID: D3-0053 - Query 2 - Blocker/Waiter Relationship

Source: `03-Day/SECOND.md:474`

```sql
SELECT *
FROM dba_blockers;

SELECT *
FROM dba_waiters;
```

### Command ID: D3-0054 - Query 3 - Locked Objects

Source: `03-Day/SECOND.md:499`

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

### Command ID: D3-0055 - Query 4 - Blocker Details

Source: `03-Day/SECOND.md:531`

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

### Command ID: D3-0056 - Query 5 - SQL Text For Waiter And Blocker

Source: `03-Day/SECOND.md:568`

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

### Command ID: D3-0057 - Step 1 - Setup Account Row

Source: `03-Day/SECOND.md:761`

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

### Command ID: D3-0058 - Step 1 - Setup Account Row

Source: `03-Day/SECOND.md:805`

```sql
SELECT account_id, account_number, balance, status
FROM accounts
WHERE account_id = 101;
```

### Command ID: D3-0059 - Step 2 - Session 1 Creates The Lock

Source: `03-Day/SECOND.md:831`

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

### Command ID: D3-0060 - Step 3 - Session 2 Becomes The Waiter

Source: `03-Day/SECOND.md:874`

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

### Command ID: D3-0061 - Step 4 - Session 3 Diagnoses The Block

Source: `03-Day/SECOND.md:926`

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

### Command ID: D3-0062 - Step 5 - Session 3 Finds Locked Object

Source: `03-Day/SECOND.md:975`

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

### Command ID: D3-0063 - Step 6 - Session 3 Checks Transaction Age

Source: `03-Day/SECOND.md:1014`

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

### Command ID: D3-0064 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:1065`

```sql
COMMIT;
```

### Command ID: D3-0065 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:1071`

```sql
ROLLBACK;
```

### Command ID: D3-0066 - Step 7 - Resolve The Lab Lock

Source: `03-Day/SECOND.md:1083`

```sql
COMMIT;
```

### Command ID: D3-0067 - Optional Emergency Command

Source: `03-Day/SECOND.md:1093`

```sql
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;
```

### Command ID: D3-0068 - Active Session Snapshot Query

Source: `03-Day/SECOND.md:1229`

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

### Command ID: D3-0069 - Active Session Snapshot Query

Source: `03-Day/SECOND.md:1256`

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

### Command ID: D3-0070 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:1448`

```sql
UPDATE transactions
SET branch_id = 10
WHERE transaction_id <= 80000;

COMMIT;
```

### Command ID: D3-0071 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:1458`

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

### Command ID: D3-0072 - Step 1 - Create Hot Branch Pattern

Source: `03-Day/SECOND.md:1472`

```sql
SELECT branch_id, COUNT(*) AS row_count
FROM transactions
WHERE branch_id IN (10, 11, 12)
GROUP BY branch_id
ORDER BY branch_id;
```

### Command ID: D3-0073 - Step 2 - Make Before Plan Clean

Source: `03-Day/SECOND.md:1512`

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

### Command ID: D3-0074 - Optional - AWR Start Snapshot

Source: `03-Day/SECOND.md:1543`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: D3-0075 - Problem Query

Source: `03-Day/SECOND.md:1623`

```sql
SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;
```

### Command ID: D3-0076 - Run Before Query Safely

Source: `03-Day/SECOND.md:1659`

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SET AUTOTRACE OFF
```

### Command ID: D3-0077 - Capture Before Plan

Source: `03-Day/SECOND.md:1682`

```sql
EXPLAIN PLAN FOR
SELECT /* capstone_dashboard_before_plan */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D3-0078 - Better Business Query

Source: `03-Day/SECOND.md:1782`

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

### Command ID: D3-0079 - Create Supporting Index Safely

Source: `03-Day/SECOND.md:1816`

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

### Command ID: D3-0080 - Create Supporting Index Safely

Source: `03-Day/SECOND.md:1838`

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

### Command ID: D3-0081 - Run After Query

Source: `03-Day/SECOND.md:1860`

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

### Command ID: D3-0082 - Capture After Runtime Plan

Source: `03-Day/SECOND.md:1898`

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

### Command ID: D3-0083 - Create A Controlled Lock

Source: `03-Day/SECOND.md:2014`

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

### Command ID: D3-0084 - Create A Controlled Lock

Source: `03-Day/SECOND.md:2064`

```sql
UPDATE /* capstone_lock_blocker */
       accounts
SET balance = balance - 500
WHERE account_id = 101;
```

### Command ID: D3-0085 - Create A Controlled Lock

Source: `03-Day/SECOND.md:2081`

```sql
UPDATE /* capstone_lock_waiter */
       accounts
SET balance = balance + 500
WHERE account_id = 101;
```

### Command ID: D3-0086 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:2107`

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

### Command ID: D3-0087 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:2130`

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

### Command ID: D3-0088 - Diagnose Capstone Lock

Source: `03-Day/SECOND.md:2152`

```sql
-- In Session 1
ROLLBACK;
```

### Command ID: D3-0089 - Optional - AWR End Snapshot

Source: `03-Day/SECOND.md:2237`

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```
