# Day 3 Command Reference

Copy/paste these commands during Day 3 demos and labs.

---

## Day 3 Morning - SQL Plan Management

### Command ID: 0056 - Day 3 session settings

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

### Command ID: 0057 - Recreate `PAYMENTS`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE payments PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
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

### Command ID: 0058 - Insert `PAYMENTS`

```sql
BEGIN
  FOR i IN 1..200000 LOOP
    INSERT INTO payments VALUES (
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

    IF MOD(i,10000) = 0 THEN COMMIT; END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: 0059 - Payment index and stats

```sql
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);

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

### Command ID: 0060 - Run payment SQL and capture plan

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +NOTE'
  )
);
```


### Command ID: 0061 - Find SPM SQL ID and plan hash

```sql
COLUMN spm_sql_id NEW_VALUE spm_sql_id
COLUMN spm_plan_hash NEW_VALUE spm_plan_hash

SELECT sql_id AS spm_sql_id,
       plan_hash_value AS spm_plan_hash,
       child_number,
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

### Command ID: 0062 - Load plan baseline from cursor cache

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

### Command ID: 0063 - View SQL plan baselines

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

### Command ID: 0064 - Optional evolve report

```sql
SET LONG 1000000

SELECT DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
         sql_handle => 'sql_handle_here'
       ) AS evolve_report
FROM dual;
```

---

## Day 3 Morning - Bind Peeking And ACS

### Command ID: 0065 - Recreate `BRANCH_TRANSACTIONS`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE branch_transactions PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
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

### Command ID: 0066 - Insert skewed branch data

```sql
INSERT /*+ APPEND */ INTO branch_transactions
SELECT LEVEL, 1, MOD(LEVEL,50000)+1, MOD(LEVEL,100000)+1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       CASE WHEN MOD(LEVEL,5)=0 THEN 'FAILED' ELSE 'SUCCESS' END,
       'large branch'
FROM dual
CONNECT BY LEVEL <= 300000;

COMMIT;

INSERT /*+ APPEND */ INTO branch_transactions
SELECT 300000 + LEVEL, 2, MOD(LEVEL,50000)+1, MOD(LEVEL,100000)+1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       'SUCCESS',
       'medium branch'
FROM dual
CONNECT BY LEVEL <= 5000;

COMMIT;

INSERT /*+ APPEND */ INTO branch_transactions
SELECT 305000 + LEVEL, 3, MOD(LEVEL,50000)+1, MOD(LEVEL,100000)+1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(100,100000),2),
       'SUCCESS',
       'small branch'
FROM dual
CONNECT BY LEVEL <= 500;

COMMIT;
```

### Command ID: 0067 - Branch index and histogram stats

```sql
CREATE INDEX idx_branch_txn_branch
ON branch_transactions(branch_id);

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

### Command ID: 0068 - Verify skew and histogram

```sql
SELECT branch_id, COUNT(*) AS txn_count
FROM branch_transactions
GROUP BY branch_id
ORDER BY branch_id;

SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

### Command ID: 0069 - Bind variable executions

```sql
VARIABLE b_branch_id NUMBER

EXEC :b_branch_id := 3
SELECT /* day3_bind_branch_demo */ SUM(amount)
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

EXEC :b_branch_id := 1
SELECT /* day3_bind_branch_demo */ SUM(amount)
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

### Command ID: 0070 - Inspect bind-sensitive child cursors

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

### Command ID: 0071 - Hint comparison

```sql
EXEC :b_branch_id := 3
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

EXEC :b_branch_id := 1
SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

## Day 3 Afternoon - Locking And Capstone

### Command ID: 0072 - Ensure account row exists

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
    account_id, account_number, customer_id, branch_id,
    account_type, balance, status, opened_date
  )
  VALUES (
    src.account_id, src.account_number, src.customer_id, src.branch_id,
    src.account_type, src.balance, src.status, src.opened_date
  );

COMMIT;
```

### Command ID: 0073 - Session 1 creates row lock

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

-- Do not commit or rollback yet.
```

### Command ID: 0074 - Session 2 waits on same row

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

-- This session should wait until Session 1 commits or rolls back.
```

### Command ID: 0075 - Session 3 diagnoses blocking

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

### Command ID: 0076 - Resolve lab lock

```sql
-- Run in Session 1:
ROLLBACK;

-- Then run in Session 2 after it completes:
COMMIT;
```

### Command ID: 0077 - Capstone hot branch setup

```sql
UPDATE transactions
SET branch_id = 10
WHERE transaction_id <= 80000;

COMMIT;

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

### Command ID: 0078 - Capstone before query metrics

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* capstone_dashboard_before */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SET AUTOTRACE OFF
```

### Command ID: 0079 - Capstone before plan

```sql
EXPLAIN PLAN FOR
SELECT /* capstone_dashboard_before_plan */
       *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0080 - Capstone create supporting index

```sql
CREATE INDEX idx_txn_branch_date_cap
ON transactions(branch_id, transaction_date DESC);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );
END;
/
```

### Command ID: 0081 - Capstone after query metrics

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

### Command ID: 0082 - Capstone after runtime plan

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

---

## Day 3 Supplemental Commands

### Command ID: 0110 - Day 3 prerequisite table check

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('CUSTOMERS','ACCOUNTS','TRANSACTIONS')
ORDER BY table_name;
```

### Command ID: 0111 - Validate payment setup and histogram

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

### Command ID: 0112 - Confirm SPM SQL ID and plan hash values

```sql
SELECT '&&spm_sql_id' AS sql_id,
       '&&spm_plan_hash' AS plan_hash_value
FROM dual;
```

### Command ID: 0113 - View current user's SQL plan baselines

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

### Command ID: 0114 - Rerun SPM SQL after baseline capture

```sql
SELECT /* day3_spm_payment_pending */
       COUNT(*)
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +NOTE'
  )
);
```

### Command ID: 0115 - Optional SPM baseline rollback

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

### Command ID: 0116 - Repeat bind executions to encourage adaptive cursor sharing

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

### Command ID: 0117 - Inspect a specific bind-aware child cursor plan

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

### Command ID: 0118 - Full hint comparison for rare and common bind values

```sql
EXEC :b_branch_id := 3

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

EXEC :b_branch_id := 1

SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

EXEC :b_branch_id := 3

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

EXEC :b_branch_id := 1

SELECT /*+ FULL(branch_transactions) */
       SUM(amount)
FROM branch_transactions
WHERE branch_id = :b_branch_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: 0119 - General blocked-session and blocker/waiter checks

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

SELECT *
FROM dba_blockers;

SELECT *
FROM dba_waiters;
```

### Command ID: 0120 - General locked-object check

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

### Command ID: 0121 - Blocker transaction details

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

### Command ID: 0122 - SQL text for waiter and blocker

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

### Command ID: 0123 - Validate Day 3 account row

```sql
SELECT account_id, account_number, balance, status
FROM accounts
WHERE account_id = 101;
```

### Command ID: 0124 - Lock lab transaction age check

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

### Command ID: 0125 - Optional emergency session kill template

```sql
ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;
```

### Command ID: 0126 - Active session snapshot during short-lived issue

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

### Command ID: 0127 - Optional ASH recent activity query

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

### Command ID: 0128 - Validate capstone hot branch pattern

```sql
SELECT branch_id, COUNT(*) AS row_count
FROM transactions
WHERE branch_id IN (10, 11, 12)
GROUP BY branch_id
ORDER BY branch_id;
```

### Command ID: 0129 - Make capstone before plan clean

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

### Command ID: 0130 - Optional capstone AWR start snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: 0131 - Capstone better business query preview

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

### Command ID: 0132 - Capstone create or reveal supporting index safely

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

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );
END;
/
```

### Command ID: 0133 - Capstone lock blocker and waiter commands

```sql
-- Session 1:
UPDATE /* capstone_lock_blocker */
       accounts
SET balance = balance - 500
WHERE account_id = 101;

-- Do not commit in Session 1 yet.

-- Session 2:
UPDATE /* capstone_lock_waiter */
       accounts
SET balance = balance + 500
WHERE account_id = 101;

-- Session 2 should wait until Session 1 commits or rolls back.
```

### Command ID: 0134 - Diagnose capstone lock

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

### Command ID: 0135 - Resolve capstone lock

```sql
-- In Session 1:
ROLLBACK;

-- In Session 2 after it completes:
COMMIT;
```

### Command ID: 0136 - Optional capstone AWR end snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

### Command ID: 0143 - Day 3 afternoon session settings

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

### Command ID: 0144 - Lock lab resolution options

```sql
-- In Session 1, choose one:
COMMIT;

-- or:
ROLLBACK;

-- Then in Session 2 after it completes:
COMMIT;
```
