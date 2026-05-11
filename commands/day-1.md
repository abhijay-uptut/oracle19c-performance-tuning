# Day 1 Command Reference

Generated from the current `01-Day/FIRST.md` and `01-Day/SECOND.md` files.

Use the command IDs to identify commands during delivery. Commands are listed in source order: first `FIRST.md`, then `SECOND.md`. Teaching-only SQL fragments are intentionally excluded so each block is copy/paste runnable.

---

## Morning and Midday Slots - `01-Day/FIRST.md`

### Command ID: D1-0001 - Step 1 — Create Table

Source: `01-Day/FIRST.md:192`

```sql
DROP TABLE transactions PURGE;

CREATE TABLE transactions (
    transaction_id    NUMBER PRIMARY KEY,
    customer_id       NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    transaction_type  VARCHAR2(20),
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(200)
);
```

### Command ID: D1-0002 - Step 2 — Insert Data

Source: `01-Day/FIRST.md:212`

```sql
BEGIN
  FOR i IN 1..300000 LOOP
    INSERT INTO transactions VALUES (
      i,
      MOD(i,5000)+1,
      MOD(i,20000)+1,
      MOD(i,50)+1,
      SYSDATE - MOD(i,730),
      CASE MOD(i,4)
        WHEN 0 THEN 'DEBIT'
        WHEN 1 THEN 'CREDIT'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'ATM'
      END,
      ROUND(DBMS_RANDOM.VALUE(100,100000),2),
      CASE
        WHEN MOD(i,20) = 0 THEN 'FAILED'
        ELSE 'SUCCESS'
      END,
      'Training transaction'
    );

    IF MOD(i,10000)=0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/
```

### Command ID: D1-0003 - Step 3 — Gather Statistics

Source: `01-Day/FIRST.md:247`

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

### Command ID: D1-0004 - Step 4 — Enable Runtime Metrics

Source: `01-Day/FIRST.md:262`

```sql
SET TIMING ON
SET AUTOTRACE TRACEONLY STATISTICS
```

### Command ID: D1-0005 - Query 1 — Broad Workload

Source: `01-Day/FIRST.md:275`

```sql
SELECT *
FROM transactions;
```

### Command ID: D1-0006 - Query 1 — Broad Workload / Run Query

Source: `01-Day/FIRST.md:294`

```sql
SELECT *
FROM transactions;
```

### Command ID: D1-0007 - Query 1 — Broad Workload / Run Query

Source: `01-Day/FIRST.md:301`

```sql
SELECT COUNT(*)
FROM transactions;
```

### Command ID: D1-0008 - Query 2 — Customer-Specific

Source: `01-Day/FIRST.md:325`

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

### Command ID: D1-0009 - Query 2 — Customer-Specific / Run Query

Source: `01-Day/FIRST.md:345`

```sql
SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101;
```

### Command ID: D1-0010 - Query 3 — Business-Focused

Source: `01-Day/FIRST.md:367`

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE,-3)
ORDER BY transaction_date DESC;
```

### Command ID: D1-0011 - Query 3 — Business-Focused / Run Query

Source: `01-Day/FIRST.md:391`

```sql
SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);
```

### Command ID: D1-0012 - Dynamic Performance Views

Source: `01-Day/FIRST.md:449`

```sql
SELECT sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) AS elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,80) AS sql_text
FROM v$sql
WHERE LOWER(sql_text) LIKE '%transactions%'
ORDER BY buffer_gets DESC;
```

### Command ID: D1-0013 - Live Demo

Source: `01-Day/FIRST.md:489`

```sql
SELECT sql_id,
       executions,
       elapsed_time,
       buffer_gets
FROM v$sql
WHERE sql_text LIKE '%transactions%';
```

### Command ID: D1-0014 - Cardinality

Source: `01-Day/FIRST.md:625`

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

### Command ID: D1-0015 - Step 1 — Create Supporting Index

Source: `01-Day/FIRST.md:959`

Source code id: `84jprf`

```sql
CREATE INDEX idx_txn_account
ON transactions(account_id);
```

### Command ID: D1-0016 - Step 2 — Gather Stats

Source: `01-Day/FIRST.md:968`

Source code id: `jlwm85`

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

### Command ID: D1-0017 - Step 3 — Enable Runtime Statistics

Source: `01-Day/FIRST.md:983`

Source code id: `5a48k8`

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

### Command ID: D1-0018 - Slide 21 — Query Under Investigation

Source: `01-Day/FIRST.md:994`

Source code id: `jlwm7v`

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

### Command ID: D1-0019 - Step 4 — Generate Estimated Plan

Source: `01-Day/FIRST.md:1017`

Source code id: `jznkxt`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0020 - Slide 22 — Actual Runtime Plan

Source: `01-Day/FIRST.md:1041`

Source code id: `6s9zfd`

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

### Command ID: D1-0021 - Slide 22 — Actual Runtime Plan

Source: `01-Day/FIRST.md:1049`

Source code id: `h0z5xa`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST'
  )
);
```

### Command ID: D1-0022 - Slide 25 — Common Code To Generate Runtime Plans

Source: `01-Day/FIRST.md:1171`

```sql
ALTER SESSION SET statistics_level = ALL;
SET LINESIZE 200
SET PAGESIZE 100
```

### Command ID: D1-0023 - Slide 25 — Common Code To Generate Runtime Plans

Source: `01-Day/FIRST.md:1179`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */
       ...
FROM ...
WHERE ...;
```

### Command ID: D1-0024 - Slide 25 — Common Code To Generate Runtime Plans

Source: `01-Day/FIRST.md:1188`

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE +ALIAS'
  )
);
```

### Command ID: D1-0025 - Slide 26 — Setup For Operation Demos

Source: `01-Day/FIRST.md:1237`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_ACCOUNT';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_account ON transactions(account_id)';
  END IF;

  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_CUSTOMER';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_customer ON transactions(customer_id)';
  END IF;
END;
/
```

### Command ID: D1-0026 - Slide 26 — Setup For Operation Demos

Source: `01-Day/FIRST.md:1266`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE customers_demo PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE customers_demo AS
SELECT LEVEL AS customer_id,
       'CUSTOMER_' || LEVEL AS customer_name,
       CASE
         WHEN MOD(LEVEL,10) = 0 THEN 'VIP'
         ELSE 'REGULAR'
       END AS customer_type
FROM dual
CONNECT BY LEVEL <= 5000;

ALTER TABLE customers_demo
ADD CONSTRAINT pk_customers_demo
PRIMARY KEY(customer_id);
```

### Command ID: D1-0027 - Slide 26 — Setup For Operation Demos

Source: `01-Day/FIRST.md:1294`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );

  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS_DEMO',
    cascade => TRUE
  );
END;
/
```

### Command ID: D1-0028 - Slide 27 — TABLE ACCESS FULL

Source: `01-Day/FIRST.md:1343`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS FULL(t) */
       COUNT(*)
FROM transactions t
WHERE status = 'SUCCESS';
```

### Command ID: D1-0029 - Slide 27 — TABLE ACCESS FULL

Source: `01-Day/FIRST.md:1352`

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

### Command ID: D1-0030 - Slide 28 — INDEX RANGE SCAN

Source: `01-Day/FIRST.md:1422`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS INDEX(t idx_txn_account) */
       COUNT(*)
FROM transactions t
WHERE account_id = 5001;
```

### Command ID: D1-0031 - Slide 28 — INDEX RANGE SCAN

Source: `01-Day/FIRST.md:1431`

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

### Command ID: D1-0032 - Slide 28 — INDEX RANGE SCAN

Source: `01-Day/FIRST.md:1465`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS INDEX(t idx_txn_account) */
       COUNT(*)
FROM transactions t
WHERE account_id BETWEEN 5001 AND 5010;
```

### Command ID: D1-0033 - Slide 29 — INDEX UNIQUE SCAN

Source: `01-Day/FIRST.md:1512`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */
       transaction_id
FROM transactions
WHERE transaction_id = 1001;
```

### Command ID: D1-0034 - Slide 29 — INDEX UNIQUE SCAN

Source: `01-Day/FIRST.md:1521`

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

### Command ID: D1-0035 - Slide 30 — TABLE ACCESS BY ROWID

Source: `01-Day/FIRST.md:1594`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS INDEX(t idx_txn_account) */
       *
FROM transactions t
WHERE account_id = 5001;
```

### Command ID: D1-0036 - Slide 30 — TABLE ACCESS BY ROWID

Source: `01-Day/FIRST.md:1603`

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

### Command ID: D1-0037 - Slide 30 — TABLE ACCESS BY ROWID

Source: `01-Day/FIRST.md:1637`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS INDEX(t idx_txn_account) */
       account_id
FROM transactions t
WHERE account_id = 5001;
```

### Command ID: D1-0038 - Slide 31 — NESTED LOOPS

Source: `01-Day/FIRST.md:1687`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS
           LEADING(c)
           USE_NL(t)
           INDEX(t idx_txn_customer) */
       c.customer_id,
       c.customer_name,
       t.transaction_id,
       t.amount
FROM customers_demo c
JOIN transactions t
  ON t.customer_id = c.customer_id
WHERE c.customer_id = 100;
```

### Command ID: D1-0039 - Slide 31 — NESTED LOOPS

Source: `01-Day/FIRST.md:1704`

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

### Command ID: D1-0040 - Slide 32 — HASH JOIN

Source: `01-Day/FIRST.md:1784`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS
           USE_HASH(t)
           FULL(t)
           FULL(c) */
       COUNT(*)
FROM customers_demo c
JOIN transactions t
  ON t.customer_id = c.customer_id;
```

### Command ID: D1-0041 - Slide 32 — HASH JOIN

Source: `01-Day/FIRST.md:1797`

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

### Command ID: D1-0042 - Slide 33 — SORT ORDER BY

Source: `01-Day/FIRST.md:1870`

```sql
EXPLAIN PLAN FOR
SELECT transaction_id,
       transaction_date,
       amount
FROM transactions
ORDER BY amount DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0043 - Slide 33 — SORT ORDER BY

Source: `01-Day/FIRST.md:1893`

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */
       transaction_id,
       transaction_date,
       amount
FROM transactions
ORDER BY amount DESC
FETCH FIRST 20 ROWS ONLY;
```

### Command ID: D1-0044 - Slide 33 — SORT ORDER BY

Source: `01-Day/FIRST.md:1905`

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

### Command ID: D1-0045 - Step 1 — Create Controlled Skew

Source: `01-Day/FIRST.md:2133`

Source code id: `nfdqkq`

```sql
UPDATE transactions
SET status =
  CASE
    WHEN MOD(transaction_id,20) = 0 THEN 'FAILED'
    ELSE 'SUCCESS'
  END;

COMMIT;
```

### Command ID: D1-0046 - Step 2 — Verify The Skew

Source: `01-Day/FIRST.md:2181`

```sql
SELECT status,
       COUNT(*) AS row_count,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct_of_table
FROM transactions
GROUP BY status
ORDER BY status;
```

### Command ID: D1-0047 - Step 3 — Ensure Status Index Exists

Source: `01-Day/FIRST.md:2217`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_STATUS';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_status ON transactions(status)';
  END IF;
END;
/
```

### Command ID: D1-0048 - Step 4 — Gather Stats WITHOUT Histogram

Source: `01-Day/FIRST.md:2272`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 1 status',
    cascade    => TRUE
  );
END;
/
```

### Command ID: D1-0049 - Step 5 — Confirm No Histogram

Source: `01-Day/FIRST.md:2326`

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

### Command ID: D1-0050 - Step 6 — Run Rare-Value Query With Runtime Stats

Source: `01-Day/FIRST.md:2364`

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

### Command ID: D1-0051 - Step 6 — Run Rare-Value Query With Runtime Stats

Source: `01-Day/FIRST.md:2369`

```sql
SELECT /* no_hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';
```

### Command ID: D1-0052 - Step 6 — Run Rare-Value Query With Runtime Stats

Source: `01-Day/FIRST.md:2377`

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

### Command ID: D1-0053 - Step 7 — Gather Stats WITH Histogram

Source: `01-Day/FIRST.md:2448`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 254 status',
    cascade    => TRUE
  );
END;
/
```

### Command ID: D1-0054 - Step 8 — Confirm Histogram Exists

Source: `01-Day/FIRST.md:2492`

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

### Command ID: D1-0055 - Step 9 — Rerun Rare-Value Query

Source: `01-Day/FIRST.md:2532`

```sql
SELECT /* hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';
```

### Command ID: D1-0056 - Step 9 — Rerun Rare-Value Query

Source: `01-Day/FIRST.md:2540`

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

### Command ID: D1-0057 - Lab Query A

Source: `01-Day/FIRST.md:2765`

Source code id: `jlwm7v`

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

### Command ID: D1-0058 - Lab Query B

Source: `01-Day/FIRST.md:2775`

Source code id: `3r0qzn`

```sql
SELECT *
FROM transactions
WHERE status='SUCCESS';
```

### Command ID: D1-0059 - Lab Query C

Source: `01-Day/FIRST.md:2785`

Source code id: `v9h6y3`

```sql
SELECT *
FROM transactions
WHERE status='FAILED';
```

## Afternoon Slots - `01-Day/SECOND.md`

### Command ID: D1-0060 - BEFORE STARTING

Source: `01-Day/SECOND.md:70`

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('TRANSACTIONS');
```

### Command ID: D1-0061 - COMMON SESSION SETTINGS

Source: `01-Day/SECOND.md:90`

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

### Command ID: D1-0062 - COMMON SESSION SETTINGS

Source: `01-Day/SECOND.md:100`

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

### Command ID: D1-0063 - Step 1 - Drop Old Demo Tables Safely

Source: `01-Day/SECOND.md:213`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE customers PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE accounts PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/
```

### Command ID: D1-0064 - Step 2 - Create Customers Table

Source: `01-Day/SECOND.md:239`

```sql
CREATE TABLE customers (
    customer_id     NUMBER PRIMARY KEY,
    full_name       VARCHAR2(100),
    email           VARCHAR2(150),
    mobile_no       VARCHAR2(20),
    branch_id       NUMBER,
    status          VARCHAR2(20),
    created_date    DATE
);
```

### Command ID: D1-0065 - Step 3 - Insert Customers

Source: `01-Day/SECOND.md:255`

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO customers (
      customer_id,
      full_name,
      email,
      mobile_no,
      branch_id,
      status,
      created_date
    )
    VALUES (
      i,
      'Customer ' || i,
      CASE
        WHEN MOD(i,2) = 0 THEN 'USER' || i || '@MAIL.COM'
        ELSE 'user' || i || '@mail.com'
      END,
      '855' || LPAD(i,8,'0'),
      MOD(i,50) + 1,
      CASE
        WHEN MOD(i,10) = 0 THEN 'INACTIVE'
        ELSE 'ACTIVE'
      END,
      SYSDATE - MOD(i,1000)
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: D1-0066 - Step 4 - Gather Statistics

Source: `01-Day/SECOND.md:304`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'CUSTOMERS',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/
```

### Command ID: D1-0067 - Step 5 - Validate Setup

Source: `01-Day/SECOND.md:320`

```sql
SELECT COUNT(*) AS total_customers
FROM customers;

SELECT status, COUNT(*) AS row_count
FROM customers
GROUP BY status
ORDER BY status;

SELECT *
FROM customers
WHERE customer_id = 500;
```

### Command ID: D1-0068 - Step 1 - Create Hot Account Pattern

Source: `01-Day/SECOND.md:384`

```sql
UPDATE transactions
SET account_id = 777777
WHERE transaction_id <= 60000;

COMMIT;
```

### Command ID: D1-0069 - Step 2 - Create Composite Index Safely

Source: `01-Day/SECOND.md:402`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_ACCOUNT_DATE';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_account_date ON transactions(account_id, transaction_date)';
  END IF;
END;
/
```

### Command ID: D1-0070 - Step 3 - Gather Transaction Stats

Source: `01-Day/SECOND.md:423`

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

### Command ID: D1-0071 - Step 4 - Query A: Account Only

Source: `01-Day/SECOND.md:439`

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0072 - Step 5 - Query B: Account Plus Date

Source: `01-Day/SECOND.md:464`

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0073 - Step 6 - Query C: Date Only

Source: `01-Day/SECOND.md:490`

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0074 - Step 1 - Create Normal Email Index

Source: `01-Day/SECOND.md:596`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_CUSTOMERS_EMAIL';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_customers_email ON customers(email)';
  END IF;
END;
/
```

### Command ID: D1-0075 - Step 2 - Gather Customer Stats

Source: `01-Day/SECOND.md:617`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS',
    cascade => TRUE
  );
END;
/
```

### Command ID: D1-0076 - Step 3 - Confirm Stored Email Case

Source: `01-Day/SECOND.md:632`

```sql
SELECT customer_id, email
FROM customers
WHERE customer_id = 500;
```

### Command ID: D1-0077 - Step 4 - Before Plan: Normal Index Does Not Match Expression

Source: `01-Day/SECOND.md:648`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0078 - Step 5 - Runtime Evidence Before Function-Based Index

Source: `01-Day/SECOND.md:672`

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

SELECT /* before_fbi */ *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: D1-0079 - Step 6 - Create Function-Based Index

Source: `01-Day/SECOND.md:702`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_CUSTOMERS_LOWER_EMAIL';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_customers_lower_email ON customers(LOWER(email))';
  END IF;
END;
/
```

### Command ID: D1-0080 - Step 7 - Gather Stats Again

Source: `01-Day/SECOND.md:723`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS',
    cascade => TRUE
  );
END;
/
```

### Command ID: D1-0081 - Step 8 - After Plan: Expression Now Has Matching Index

Source: `01-Day/SECOND.md:738`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0082 - Step 9 - Runtime Evidence After Function-Based Index

Source: `01-Day/SECOND.md:761`

```sql
SELECT /* after_fbi */ *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: D1-0083 - Step 1 - Create Invisible Mobile Index

Source: `01-Day/SECOND.md:864`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_CUSTOMERS_MOBILE_INV';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_customers_mobile_inv ON customers(mobile_no) INVISIBLE';
  ELSE
    EXECUTE IMMEDIATE
      'ALTER INDEX idx_customers_mobile_inv INVISIBLE';
  END IF;
END;
/
```

### Command ID: D1-0084 - Step 2 - Confirm Index Visibility

Source: `01-Day/SECOND.md:888`

```sql
SELECT index_name, visibility
FROM user_indexes
WHERE index_name = 'IDX_CUSTOMERS_MOBILE_INV';
```

### Command ID: D1-0085 - Step 3 - Optimizer Ignores Invisible Index By Default

Source: `01-Day/SECOND.md:904`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0086 - Step 4 - Test Invisible Index In Current Session

Source: `01-Day/SECOND.md:925`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0087 - Step 5 - Reset Session Setting

Source: `01-Day/SECOND.md:946`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
```

### Command ID: D1-0088 - Step 1 - Drop Test Tables Safely

Source: `01-Day/SECOND.md:989`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE dml_no_index PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE dml_with_index PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/
```

### Command ID: D1-0089 - Step 2 - Create Identical Tables

Source: `01-Day/SECOND.md:1015`

```sql
CREATE TABLE dml_no_index (
    transaction_id    NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    status            VARCHAR2(20),
    amount            NUMBER(12,2)
);

CREATE TABLE dml_with_index (
    transaction_id    NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    status            VARCHAR2(20),
    amount            NUMBER(12,2)
);
```

### Command ID: D1-0090 - Step 3 - Add Indexes To One Table Only

Source: `01-Day/SECOND.md:1039`

```sql
CREATE INDEX idx_dml_account
ON dml_with_index(account_id);

CREATE INDEX idx_dml_branch_status
ON dml_with_index(branch_id, status);

CREATE INDEX idx_dml_date
ON dml_with_index(transaction_date);

CREATE INDEX idx_dml_status
ON dml_with_index(status);
```

### Command ID: D1-0091 - Step 4 - Insert Into Table Without Secondary Indexes

Source: `01-Day/SECOND.md:1057`

```sql
SET TIMING ON

INSERT INTO dml_no_index
SELECT LEVEL,
       MOD(LEVEL,20000) + 1,
       MOD(LEVEL,50) + 1,
       SYSDATE - MOD(LEVEL,730),
       CASE WHEN MOD(LEVEL,20) = 0 THEN 'FAILED' ELSE 'SUCCESS' END,
       ROUND(DBMS_RANDOM.VALUE(100,100000),2)
FROM dual
CONNECT BY LEVEL <= 50000;

COMMIT;
```

### Command ID: D1-0092 - Step 5 - Insert Same Rows Into Indexed Table

Source: `01-Day/SECOND.md:1079`

```sql
INSERT INTO dml_with_index
SELECT LEVEL,
       MOD(LEVEL,20000) + 1,
       MOD(LEVEL,50) + 1,
       SYSDATE - MOD(LEVEL,730),
       CASE WHEN MOD(LEVEL,20) = 0 THEN 'FAILED' ELSE 'SUCCESS' END,
       ROUND(DBMS_RANDOM.VALUE(100,100000),2)
FROM dual
CONNECT BY LEVEL <= 50000;

COMMIT;
```

### Command ID: D1-0093 - Step 6 - Compare Index Count

Source: `01-Day/SECOND.md:1099`

```sql
SELECT table_name, COUNT(*) AS index_count
FROM user_indexes
WHERE table_name IN ('DML_NO_INDEX','DML_WITH_INDEX')
GROUP BY table_name
ORDER BY table_name;
```

### Command ID: D1-0094 - Step 1 - Recreate Accounts Table

Source: `01-Day/SECOND.md:1182`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE accounts PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE accounts (
    account_id      NUMBER PRIMARY KEY,
    account_number  VARCHAR2(30),
    customer_id     NUMBER,
    branch_id       NUMBER,
    account_type    VARCHAR2(20),
    balance         NUMBER(14,2),
    status          VARCHAR2(20),
    opened_date     DATE
);
```

### Command ID: D1-0095 - Step 2 - Insert Accounts

Source: `01-Day/SECOND.md:1213`

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO accounts (
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
      i,
      TO_CHAR(1000000000 + i),
      MOD(i,5000) + 1,
      MOD(i,50) + 1,
      CASE MOD(i,3)
        WHEN 0 THEN 'SAVINGS'
        WHEN 1 THEN 'CURRENT'
        ELSE 'LOAN'
      END,
      ROUND(DBMS_RANDOM.VALUE(100,500000),2),
      CASE WHEN MOD(i,5) = 0 THEN 'INACTIVE' ELSE 'ACTIVE' END,
      SYSDATE - MOD(i,2000)
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: D1-0096 - Step 3 - Create Capstone Indexes Safely

Source: `01-Day/SECOND.md:1255`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count FROM user_indexes WHERE index_name = 'IDX_ACCOUNTS_ACCOUNT_NUMBER';
  IF v_count = 0 THEN
    EXECUTE IMMEDIATE 'CREATE INDEX idx_accounts_account_number ON accounts(account_number)';
  END IF;

  SELECT COUNT(*) INTO v_count FROM user_indexes WHERE index_name = 'IDX_CUSTOMERS_NAME';
  IF v_count = 0 THEN
    EXECUTE IMMEDIATE 'CREATE INDEX idx_customers_name ON customers(full_name)';
  END IF;

  SELECT COUNT(*) INTO v_count FROM user_indexes WHERE index_name = 'IDX_TXN_DATE_DESC';
  IF v_count > 0 THEN
    EXECUTE IMMEDIATE 'ALTER INDEX idx_txn_date_desc INVISIBLE';
  END IF;
END;
/
```

### Command ID: D1-0097 - Step 4 - Gather Stats

Source: `01-Day/SECOND.md:1285`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

### Command ID: D1-0098 - Step 5 - Validate Capstone Data

Source: `01-Day/SECOND.md:1298`

```sql
SELECT COUNT(*) AS accounts_count
FROM accounts;

SELECT COUNT(*) AS hot_account_rows
FROM transactions
WHERE account_id = 777777;

SELECT account_id, account_number
FROM accounts
WHERE account_id = 5000;
```

### Command ID: D1-0099 - SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35) / Problem Query

Source: `01-Day/SECOND.md:1325`

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

### Command ID: D1-0100 - SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35) / Before Plan

Source: `01-Day/SECOND.md:1337`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_CUSTOMERS_LOWER_EMAIL';

  IF v_count > 0 THEN
    EXECUTE IMMEDIATE 'ALTER INDEX idx_customers_lower_email INVISIBLE';
  END IF;
END;
/
```

### Command ID: D1-0101 - SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35) / Before Plan

Source: `01-Day/SECOND.md:1355`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0102 - SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35) / Fix

Source: `01-Day/SECOND.md:1374`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_CUSTOMERS_LOWER_EMAIL';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_customers_lower_email ON customers(LOWER(email))';
  ELSE
    EXECUTE IMMEDIATE
      'ALTER INDEX idx_customers_lower_email VISIBLE';
  END IF;
END;
/
```

### Command ID: D1-0103 - SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35) / Fix

Source: `01-Day/SECOND.md:1396`

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
END;
/

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0104 - SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50) / Problem Query

Source: `01-Day/SECOND.md:1428`

```sql
SELECT *
FROM transactions
WHERE account_id = 777777;
```

### Command ID: D1-0105 - SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50) / Observe Row Count

Source: `01-Day/SECOND.md:1438`

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;
```

### Command ID: D1-0106 - SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50) / Before Runtime Plan

Source: `01-Day/SECOND.md:1454`

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* cap_b_before */ *
FROM transactions
WHERE account_id = 777777;

SET AUTOTRACE OFF

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: D1-0107 - SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50) / Better Query

Source: `01-Day/SECOND.md:1487`

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);
```

### Command ID: D1-0108 - SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50) / Better Query

Source: `01-Day/SECOND.md:1496`

```sql
SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* cap_b_after */ *
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SET AUTOTRACE OFF

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: D1-0109 - SECTION 10 - CAPSTONE QUERY C: IMPLICIT CONVERSION (3:50 - 4:05) / Problem Query

Source: `01-Day/SECOND.md:1535`

```sql
SELECT *
FROM accounts
WHERE account_number = 1000005000;
```

### Command ID: D1-0110 - SECTION 10 - CAPSTONE QUERY C: IMPLICIT CONVERSION (3:50 - 4:05) / Before Plan

Source: `01-Day/SECOND.md:1551`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = 1000005000;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0111 - SECTION 10 - CAPSTONE QUERY C: IMPLICIT CONVERSION (3:50 - 4:05) / Fix

Source: `01-Day/SECOND.md:1578`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = '1000005000';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0112 - SECTION 11 - CAPSTONE QUERY D: LEADING WILDCARD SEARCH (4:05 - 4:15) / Problem Query

Source: `01-Day/SECOND.md:1606`

```sql
SELECT *
FROM customers
WHERE full_name LIKE '%100%';
```

### Command ID: D1-0113 - SECTION 11 - CAPSTONE QUERY D: LEADING WILDCARD SEARCH (4:05 - 4:15) / Before Plan

Source: `01-Day/SECOND.md:1616`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0114 - SECTION 11 - CAPSTONE QUERY D: LEADING WILDCARD SEARCH (4:05 - 4:15) / Better Prefix Search

Source: `01-Day/SECOND.md:1637`

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE 'Customer 100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0115 - SECTION 11 - CAPSTONE QUERY D: LEADING WILDCARD SEARCH (4:05 - 4:15) / Better Prefix Search

Source: `01-Day/SECOND.md:1658`

```sql
CREATE INDEX idx_customers_name_text
ON customers(full_name)
INDEXTYPE IS CTXSYS.CONTEXT;
```

### Command ID: D1-0116 - SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25) / Problem Query

Source: `01-Day/SECOND.md:1670`

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

### Command ID: D1-0117 - SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25) / Before Plan

Source: `01-Day/SECOND.md:1680`

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM transactions
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0118 - SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25) / Better Screen-Level Query

Source: `01-Day/SECOND.md:1703`

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_DATE_DESC';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_date_desc ON transactions(transaction_date DESC)';
  ELSE
    EXECUTE IMMEDIATE
      'ALTER INDEX idx_txn_date_desc VISIBLE';
  END IF;
END;
/

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

### Command ID: D1-0119 - SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25) / Better Screen-Level Query

Source: `01-Day/SECOND.md:1730`

```sql
EXPLAIN PLAN FOR
SELECT transaction_id,
       account_id,
       transaction_date,
       amount,
       status
FROM transactions
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: D1-0120 - SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25) / Better Screen-Level Query

Source: `01-Day/SECOND.md:1746`

```sql
EXPLAIN PLAN FOR
SELECT transaction_id,
       account_id,
       transaction_date,
       amount,
       status
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```
