# Day 1 Command Reference

Copy/paste these commands during Day 1 demos and labs.

---

## Common Setup

### Command ID: 0001 - SQL*Plus display/session settings

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

### Command ID: 0002 - Recreate `TRANSACTIONS`

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

### Command ID: 0003 - Insert `TRANSACTIONS` demo data

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

COMMIT;
```

### Command ID: 0004 - Gather `TRANSACTIONS` statistics

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

---

## Day 1 Morning - Workload Observation And Plans

### Command ID: 0005 - Enable autotrace statistics

```sql
SET TIMING ON
SET AUTOTRACE TRACEONLY STATISTICS
```

### Command ID: 0006 - Workload pattern comparison

```sql
SELECT COUNT(*)
FROM transactions;

SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101;

SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);
```

### Command ID: 0007 - Turn autotrace off

```sql
SET AUTOTRACE OFF
```

### Command ID: 0008 - Find workload SQL in `V$SQL`

```sql
SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       rows_processed,
       parsing_schema_name,
       last_active_time,
       SUBSTR(sql_text,1,100) sql_text
FROM v$sql
WHERE LOWER(sql_text) LIKE '%transactions%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;
```

### Command ID: 0009 - Ensure status index exists

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

### Command ID: 0010 - Confirm status skew

```sql
SELECT status, COUNT(*) AS row_count
FROM transactions
GROUP BY status
ORDER BY status;
```

### Command ID: 0011 - Gather stats without histogram

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

### Command ID: 0012 - Check histogram status

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

### Command ID: 0013 - Plan for rare value without histogram

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0014 - Gather stats with histogram

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

### Command ID: 0015 - Plan for rare value with histogram

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0016 - Runtime plan with `DBMS_XPLAN.DISPLAY_CURSOR`

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

SELECT /* hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

---

## Day 1 Afternoon - Indexing And Capstone

### Command ID: 0017 - Recreate `CUSTOMERS` and `ACCOUNTS`

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE customers PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE accounts PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

CREATE TABLE customers (
    customer_id     NUMBER PRIMARY KEY,
    full_name       VARCHAR2(100),
    email           VARCHAR2(150),
    mobile_no       VARCHAR2(20),
    branch_id       NUMBER,
    status          VARCHAR2(20),
    created_date    DATE
);

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

### Command ID: 0018 - Insert `CUSTOMERS`

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO customers VALUES (
      i,
      'Customer ' || i,
      CASE WHEN MOD(i,2) = 0 THEN 'USER' || i || '@MAIL.COM'
           ELSE 'user' || i || '@mail.com'
      END,
      '855' || LPAD(i,8,'0'),
      MOD(i,50) + 1,
      CASE WHEN MOD(i,10) = 0 THEN 'INACTIVE' ELSE 'ACTIVE' END,
      SYSDATE - MOD(i,1000)
    );

    IF MOD(i,10000) = 0 THEN COMMIT; END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: 0019 - Insert `ACCOUNTS`

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO accounts VALUES (
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

    IF MOD(i,10000) = 0 THEN COMMIT; END IF;
  END LOOP;
END;
/

COMMIT;
```

### Command ID: 0020 - Gather customer/account stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
END;
/
```

### Command ID: 0021 - Create hot account pattern and composite index

```sql
UPDATE transactions
SET account_id = 777777
WHERE transaction_id <= 60000;

COMMIT;

CREATE INDEX idx_txn_account_date
ON transactions(account_id, transaction_date);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

### Command ID: 0022 - Composite index plan tests

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0023 - Function-based index before plan

```sql
CREATE INDEX idx_customers_email
ON customers(email);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
END;
/

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0024 - Create function-based index and recheck

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
END;
/

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0025 - Invisible index demo

```sql
CREATE INDEX idx_customers_mobile_inv
ON customers(mobile_no)
INVISIBLE;

SELECT index_name, visibility
FROM user_indexes
WHERE index_name = 'IDX_CUSTOMERS_MOBILE_INV';

ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
```

### Command ID: 0026 - DML index maintenance cost demo

```sql
DROP TABLE dml_no_index PURGE;
DROP TABLE dml_with_index PURGE;

CREATE TABLE dml_no_index (
    transaction_id    NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    status            VARCHAR2(20),
    amount            NUMBER(12,2)
);

CREATE TABLE dml_with_index AS
SELECT * FROM dml_no_index WHERE 1=0;

CREATE INDEX idx_dml_account ON dml_with_index(account_id);
CREATE INDEX idx_dml_branch_status ON dml_with_index(branch_id, status);
CREATE INDEX idx_dml_date ON dml_with_index(transaction_date);
CREATE INDEX idx_dml_status ON dml_with_index(status);
```

### Command ID: 0027 - DML insert timing comparison

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

### Command ID: 0028 - Capstone anti-pattern plans

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = 1000005000;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = '1000005000';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

## Day 1 Additional Commands - Missing Runtime And Capstone Blocks

### Command ID: 0083 - Slot 2 account index setup

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

### Command ID: 0084 - Slot 2 estimated vs actual plan

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

SELECT /* slot2_actual_account */ *
FROM transactions
WHERE account_id = 5001;

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: 0085 - Slot 2 no-histogram runtime plan

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

SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

SELECT /* no_hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: 0086 - Slot 2 lab query plans

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* lab_account_id */ *
FROM transactions
WHERE account_id = 5001;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

SELECT /* lab_status_success */ *
FROM transactions
WHERE status='SUCCESS';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

SELECT /* lab_status_failed */ *
FROM transactions
WHERE status='FAILED';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: 0087 - Function-based index runtime before and after

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

SELECT /* before_fbi */ *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

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

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
END;
/

SELECT /* after_fbi */ *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: 0088 - Capstone basic indexes setup

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

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

### Command ID: 0089 - Capstone Query A function index before and after

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

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

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

### Command ID: 0090 - Capstone Query B missing date range before and after

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;

SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* cap_b_before */ *
FROM transactions
WHERE account_id = 777777;

SET AUTOTRACE OFF

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));

SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SET AUTOTRACE TRACEONLY STATISTICS

SELECT /* cap_b_after */ *
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SET AUTOTRACE OFF

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

### Command ID: 0091 - Capstone Query D leading wildcard vs prefix search

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE 'Customer 100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Command ID: 0092 - Capstone Query E large sort before and after

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM transactions
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

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

### Command ID: 0093 - DML index count comparison

```sql
SELECT table_name, COUNT(*) AS index_count
FROM user_indexes
WHERE table_name IN ('DML_NO_INDEX','DML_WITH_INDEX')
GROUP BY table_name
ORDER BY table_name;
```

### Command ID: 0137 - Day 1 Slot 3 readiness and common runtime-plan command

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('TRANSACTIONS');

SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;

SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

### Command ID: 0138 - Validate customer setup and email case

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

SELECT customer_id, email
FROM customers
WHERE customer_id = 500;
```

### Command ID: 0139 - Validate Day 1 capstone data

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

### Command ID: 0140 - Optional Oracle Text index for contains search

```sql
CREATE INDEX idx_customers_name_text
ON customers(full_name)
INDEXTYPE IS CTXSYS.CONTEXT;
```
