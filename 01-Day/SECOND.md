# Day 1 - SECOND HALF (FINAL ENTERPRISE VERSION)

## 1:00 PM - 5:00 PM

# Indexing Strategy, Plan Pitfalls & Day 1 Capstone Lab

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* decide when an index is useful and when it is harmful
* validate index impact using execution plans and runtime metrics
* understand composite index column order
* prove why functions on indexed columns can cause full scans
* test function-based indexes safely
* understand invisible indexes as a controlled testing mechanism
* recognize common production SQL anti-patterns
* compare before and after tuning using evidence
* explain findings like a production DBA, not like a syntax user

---

# HALF-DAY DESIGN PHILOSOPHY

This half day is intentionally:

* practical
* lab-heavy
* plan-focused
* evidence-driven
* banking-workload oriented

NOT:

* index theory lecture
* memorization of index types
* "create index for every slow query"
* certification-style slide delivery

---

# FINAL TIME STRUCTURE

| Time          | Section                                      |
| ------------- | -------------------------------------------- |
| 1:00 - 1:10   | Recap from FIRST.md                          |
| 1:10 - 1:30   | Index decision framework                     |
| 1:30 - 1:55   | Demo 1: composite index and column order     |
| 1:55 - 2:20   | Demo 2: function-based index                 |
| 2:20 - 2:30   | Demo 3: invisible index testing              |
| 2:45 - 3:10   | Demo 4: index maintenance cost               |
| 3:10 - 4:25   | Capstone lab: 5 common SQL plan pitfalls     |
| 4:25 - 4:50   | Group review and before/after comparison     |
| 4:50 - 5:00   | Day 1 closing and Day 2 transition           |

---

# BEFORE STARTING

This file assumes `01-Day/FIRST.md` has already created:

```text
TRANSACTIONS
```

Quick validation:

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('TRANSACTIONS');
```

Expected:

```text
TRANSACTIONS
```

If `TRANSACTIONS` does not exist, run the table setup from `01-Day/FIRST.md` first.

---

# COMMON SESSION SETTINGS

Use these settings before demos:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

Use this after running a query when you want runtime evidence:

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

Trainer note:

Use `EXPLAIN PLAN` when you want to show optimizer prediction. Use `DISPLAY_CURSOR` when you want to show what actually ran.

---

# SLOT 3 - INDEXING STRATEGIES FOR BANKING WORKLOADS

## 1:00 PM - 2:30 PM

# SECTION 1 - RECAP AND INDEX MINDSET (1:00 - 1:10)

# Slide 1 - Opening

## Slide Content

# Indexes Are Not Magic

Indexes can:

* reduce reads
* improve selective lookups
* support joins
* avoid some sorts

Indexes can also:

* slow down inserts
* slow down updates
* increase storage
* create plan risk
* become unused overhead

---

## Trainer Delivery

"In the morning, we learned how to observe SQL behavior and read execution plans.

Now we discuss the most common tuning reaction:

> create an index.

That reaction is sometimes correct.

But in banking systems, every index has operational cost.

Our job is not to create more indexes.

Our job is to create the right index for the right workload and prove the improvement."

---

# Slide 2 - Production Index Question

## Slide Content

Before creating an index, ask:

* Which SQL needs it?
* How often does that SQL run?
* How many rows does it return?
* Is the predicate selective?
* Does the index match the SQL?
* What DML cost will this add?
* Is there already a similar index?
* Can we test safely?

---

## Trainer Delivery

"A production index decision is a workload decision.

If a query runs once per month, a new index may not be worth the DML overhead.

If a query runs 50,000 times per hour and returns one customer, an index may be critical.

Frequency matters.
Selectivity matters.
Business importance matters."

---

# SECTION 2 - CUSTOMER TABLE SETUP (1:10 - 1:20)

# Slide 3 - Setup Objective

## Slide Content

We will create a banking-style customer table to test:

* selective lookups
* function-based indexes
* invisible indexes
* wildcard search behavior
* index maintenance cost

---

# Step 1 - Drop Old Demo Tables Safely

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

---

# Step 2 - Create Customers Table

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

---

# Step 3 - Insert Customers

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

Expected distribution:

```text
ACTIVE   = around 90%
INACTIVE = around 10%
```

---

# Step 4 - Gather Statistics

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

---

# Step 5 - Validate Setup

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

Trainer note:

Customer 500 has uppercase stored email:

```text
USER500@MAIL.COM
```

This is useful for the case-insensitive email search demo.

---

# SECTION 3 - DEMO 1: COMPOSITE INDEX AND COLUMN ORDER (1:30 - 1:55)

# Slide 4 - Demo Objective

## Slide Content

# Composite Index Demo

We will test:

```sql
(account_id, transaction_date)
```

against:

* account-only lookup
* account plus date lookup
* date-only lookup

---

## Trainer Delivery

"Composite indexes are very important in banking systems.

A customer statement screen rarely filters by only one thing.

It often filters by account and time range.

The index must match that access pattern."

---

# Step 1 - Create Hot Account Pattern

This makes the demo visible even on a 300,000-row table.

```sql
UPDATE transactions
SET account_id = 777777
WHERE transaction_id <= 60000;

COMMIT;
```

Expected:

```text
account_id = 777777 has around 60,000 rows
```

---

# Step 2 - Create Composite Index Safely

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

---

# Step 3 - Gather Transaction Stats

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

---

# Step 4 - Query A: Account Only

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
The composite index can support a predicate on the leading column.
```

Ask:

* "How many rows are expected?"
* "Is this account selective?"
* "Would this be safe under high concurrency?"

---

# Step 5 - Query B: Account Plus Date

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
The composite index supports both account_id and transaction_date.
```

Ask:

* "Did the date predicate reduce the workload?"
* "Does this match a real account statement screen better?"
* "Is this more business-friendly than full account history?"

---

# Step 6 - Query C: Date Only

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE,-3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
The index starts with account_id, so it is not designed primarily for date-only search.
```

Trainer note:

Oracle may choose a full scan, an index skip scan, or another access path depending on table size and stats. Do not promise one exact plan. The point is index design must follow query patterns.

---

# Slide 5 - Composite Index Lesson

## Slide Content

Index:

```sql
(account_id, transaction_date)
```

Usually supports:

```sql
WHERE account_id = :b1
```

and:

```sql
WHERE account_id = :b1
AND transaction_date >= :b2
```

Not designed primarily for:

```sql
WHERE transaction_date >= :b1
```

---

## Trainer Delivery

"Column order is not cosmetic.

It determines which query patterns the index supports well.

This is why we do not design indexes from table columns.

We design indexes from workload."

---

# SECTION 4 - DEMO 2: FUNCTION-BASED INDEX (1:55 - 2:20)

# Slide 6 - Demo Objective

## Slide Content

# Function on Indexed Column

Problem SQL:

```sql
WHERE LOWER(email) = 'user500@mail.com'
```

Normal index:

```sql
ON customers(email)
```

does not match:

```sql
LOWER(email)
```

---

## Trainer Delivery

"This is a very common application pattern.

Developers use `LOWER` or `UPPER` for case-insensitive search.

That is understandable.

But from the optimizer perspective, `email` and `LOWER(email)` are different expressions."

---

# Step 1 - Create Normal Email Index

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

---

# Step 2 - Gather Customer Stats

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

---

# Step 3 - Confirm Stored Email Case

```sql
SELECT customer_id, email
FROM customers
WHERE customer_id = 500;
```

Expected:

```text
USER500@MAIL.COM
```

---

# Step 4 - Before Plan: Normal Index Does Not Match Expression

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected before:

```text
TABLE ACCESS FULL CUSTOMERS
filter(LOWER("EMAIL")='user500@mail.com')
```

Trainer note:

If Oracle still chooses a different plan because of environment differences, focus on the predicate section. The normal index on `email` does not directly match `LOWER(email)`.

---

# Step 5 - Runtime Evidence Before Function-Based Index

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

Record:

* access path
* E-Rows
* A-Rows
* buffers
* predicate type

---

# Step 6 - Create Function-Based Index

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

---

# Step 7 - Gather Stats Again

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

---

# Step 8 - After Plan: Expression Now Has Matching Index

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected after:

```text
INDEX RANGE SCAN IDX_CUSTOMERS_LOWER_EMAIL
TABLE ACCESS BY INDEX ROWID CUSTOMERS
access(LOWER("EMAIL")='user500@mail.com')
```

---

# Step 9 - Runtime Evidence After Function-Based Index

Use a different SQL comment to get a fresh cursor.

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

Now compare:

| Metric | Before FBI | After FBI |
| ------ | ---------- | --------- |
| Access path | | |
| Predicate type | | |
| E-Rows | | |
| A-Rows | | |
| Buffers | | |
| Runtime | | |

---

# Slide 7 - Function-Based Index Lesson

## Slide Content

The index must match the SQL expression.

Normal index:

```sql
email
```

supports:

```sql
WHERE email = :b1
```

Function-based index:

```sql
LOWER(email)
```

supports:

```sql
WHERE LOWER(email) = :b1
```

---

## Trainer Delivery

"This is the exact kind of issue experienced DBAs see in real systems.

The query looks simple.

The column has an index.

But the predicate does not match the index.

That is why we always read the predicate section, not just the operation name."

---

# SECTION 5 - DEMO 3: INVISIBLE INDEX TESTING (2:20 - 2:30)

# Slide 8 - Demo Objective

## Slide Content

# Invisible Index

Useful for controlled testing:

* index exists
* optimizer ignores it by default
* session can test it explicitly
* production risk is lower than making it visible immediately

---

## Trainer Delivery

"Invisible indexes are useful when you want to test a possible index without immediately changing plans for every session.

This is not a replacement for proper testing.

But it gives DBAs a safer validation mechanism."

---

# Step 1 - Create Invisible Mobile Index

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

---

# Step 2 - Confirm Index Visibility

```sql
SELECT index_name, visibility
FROM user_indexes
WHERE index_name = 'IDX_CUSTOMERS_MOBILE_INV';
```

Expected:

```text
VISIBILITY = INVISIBLE
```

---

# Step 3 - Optimizer Ignores Invisible Index By Default

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
Invisible index is ignored by default.
```

---

# Step 4 - Test Invisible Index In Current Session

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;

EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE mobile_no = '85500000500';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected:

```text
INDEX RANGE SCAN IDX_CUSTOMERS_MOBILE_INV
```

---

# Step 5 - Reset Session Setting

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;
```

Trainer note:

Do not leave this setting enabled accidentally. It changes how the optimizer treats invisible indexes in the session.

---

# SLOT 4 - COMMON PLAN PITFALLS + CAPSTONE LAB

## 2:45 PM - 5:00 PM

# SECTION 6 - DEMO 4: INDEX MAINTENANCE COST (2:45 - 3:10)

# Slide 9 - Demo Objective

## Slide Content

# Indexes Improve Reads, But Add Write Cost

We will compare insert time into:

* table with no secondary indexes
* table with multiple secondary indexes

---

## Trainer Delivery

"Every index must be maintained.

This is why a read-improving index can hurt an OLTP transaction table.

The goal is not to avoid indexes.

The goal is to create indexes that justify their write cost."

---

# Step 1 - Drop Test Tables Safely

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

---

# Step 2 - Create Identical Tables

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

---

# Step 3 - Add Indexes To One Table Only

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

---

# Step 4 - Insert Into Table Without Secondary Indexes

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

Record elapsed time.

---

# Step 5 - Insert Same Rows Into Indexed Table

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

Record elapsed time.

---

# Step 6 - Compare Index Count

```sql
SELECT table_name, COUNT(*) AS index_count
FROM user_indexes
WHERE table_name IN ('DML_NO_INDEX','DML_WITH_INDEX')
GROUP BY table_name
ORDER BY table_name;
```

Expected:

```text
DML_NO_INDEX    = 0 secondary indexes
DML_WITH_INDEX  = 4 secondary indexes
```

Trainer note:

Timing varies by machine. The indexed table should generally take longer because Oracle maintains four indexes during the insert. If the difference is small, explain that production impact becomes clearer at higher volume and concurrency.

---

# Slide 10 - Index Cost Lesson

## Slide Content

Index cost appears during:

* INSERT
* UPDATE indexed columns
* DELETE
* bulk loads
* ETL jobs
* batch processing

Decision rule:

```text
Create indexes that serve important workload.
Remove or avoid indexes that only add cost.
```

---

# SECTION 7 - CAPSTONE SETUP (3:10 - 3:25)

# Slide 11 - Capstone Objective

## Slide Content

# Banking SQL Tuning Challenge

We will diagnose five common issues:

* A - function on indexed column
* B - missing date range
* C - implicit conversion
* D - leading wildcard search
* E - large sort

For each:

* observe
* read plan
* identify issue
* apply fix
* compare evidence

---

## Trainer Delivery

"This capstone combines the whole day.

Do not jump to the answer.

For each query, follow the same production workflow:

problem, observe, plan, diagnose, fix, validate."

---

# Step 1 - Recreate Accounts Table

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

Trainer note:

`account_number` is intentionally `VARCHAR2`. This is required for the implicit conversion demo.

---

# Step 2 - Insert Accounts

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

---

# Step 3 - Create Capstone Indexes Safely

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

Trainer note:

If `IDX_TXN_DATE_DESC` exists from an earlier run, we make it invisible here so Query E can still show the large-sort problem before the fix.

---

# Step 4 - Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

---

# Step 5 - Validate Capstone Data

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

Expected:

```text
ACCOUNTS_COUNT   = 100000
HOT_ACCOUNT_ROWS = around 60000
ACCOUNT_NUMBER   = 1000005000
```

---

# SECTION 8 - CAPSTONE QUERY A: FUNCTION ON INDEXED COLUMN (3:25 - 3:35)

# Problem Query

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

---

# Before Plan

If the function-based index exists from Slot 3, make it invisible temporarily for this problem:

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

Then:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected issue:

```text
Normal email index does not directly support LOWER(email).
```

---

# Fix

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

Then:

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

Expected after:

```text
INDEX RANGE SCAN IDX_CUSTOMERS_LOWER_EMAIL
```

Ask:

* "Did the predicate become an access predicate?"
* "Would this index be justified if login/email search is frequent?"
* "What DML cost does it add?"

---

# SECTION 9 - CAPSTONE QUERY B: MISSING DATE RANGE (3:35 - 3:50)

# Problem Query

```sql
SELECT *
FROM transactions
WHERE account_id = 777777;
```

---

# Observe Row Count

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777;
```

Expected:

```text
around 60000 rows
```

---

# Before Runtime Plan

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

Issue:

```text
The SQL may use an index, but it still returns too much history.
```

Trainer note:

This is important: the problem is not always "index not used." Sometimes the SQL is business-broad and fetches too much data.

---

# Better Query

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 777777
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);
```

Then:

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

Compare:

* rows returned
* buffers
* predicate section
* business correctness

Expected lesson:

```text
The best fix may be reducing unnecessary business scope before adding more indexes.
```

---

# SECTION 10 - CAPSTONE QUERY C: IMPLICIT CONVERSION (3:50 - 4:05)

# Problem Query

```sql
SELECT *
FROM accounts
WHERE account_number = 1000005000;
```

Column type:

```sql
ACCOUNT_NUMBER VARCHAR2(30)
```

---

# Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = 1000005000;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Look for predicate like:

```text
TO_NUMBER("ACCOUNT_NUMBER")=1000005000
```

Expected issue:

```text
Function is applied internally to the column, so index access may be lost.
```

---

# Fix

Match the literal type to the column type:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = '1000005000';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected after:

```text
INDEX RANGE SCAN IDX_ACCOUNTS_ACCOUNT_NUMBER
access("ACCOUNT_NUMBER"='1000005000')
```

Ask:

* "What changed in the predicate section?"
* "Did SQL text look almost the same?"
* "Why is this dangerous in application code?"

---

# SECTION 11 - CAPSTONE QUERY D: LEADING WILDCARD SEARCH (4:05 - 4:15)

# Problem Query

```sql
SELECT *
FROM customers
WHERE full_name LIKE '%100%';
```

---

# Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected issue:

```text
Leading wildcard usually prevents efficient B-tree index access.
```

---

# Better Prefix Search

If business requirement allows "starts with":

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE 'Customer 100%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
Prefix search can use normal B-tree index more effectively than contains search.
```

Production note:

If the business truly needs contains search, consider Oracle Text instead of forcing a normal B-tree index.

Do not run Oracle Text setup unless the environment has the required privileges:

```sql
CREATE INDEX idx_customers_name_text
ON customers(full_name)
INDEXTYPE IS CTXSYS.CONTEXT;
```

---

# SECTION 12 - CAPSTONE QUERY E: LARGE SORT (4:15 - 4:25)

# Problem Query

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

---

# Before Plan

```sql
ALTER SESSION SET optimizer_use_invisible_indexes = FALSE;

EXPLAIN PLAN FOR
SELECT *
FROM transactions
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected issue:

```text
SORT ORDER BY on a large row set
```

---

# Better Screen-Level Query

First create or enable the supporting index:

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

If the application needs latest rows:

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

Even better if the screen has a business time window:

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

Compare:

* rows processed
* sort operation
* STOPKEY / FETCH FIRST behavior
* whether the date index helps

Trainer note:

Do not sell `FETCH FIRST 100 ROWS ONLY` as a tuning trick by itself. It is correct only when the business requirement is to show the latest 100 rows.

---

# SECTION 13 - GROUP REVIEW (4:25 - 4:50)

# Slide 12 - Capstone Observation Table

## Slide Content

| Query | Main Issue | Before Evidence | Fix | After Evidence | Production Caution |
| ----- | ---------- | --------------- | --- | -------------- | ------------------ |
| A | Function on column | | | | |
| B | Missing date range | | | | |
| C | Implicit conversion | | | | |
| D | Leading wildcard | | | | |
| E | Large sort | | | | |

---

# Slide 13 - What Counts As Improvement?

## Slide Content

Improvement can mean:

* fewer rows processed
* fewer buffers
* better predicate usage
* better access path
* less sorting
* lower execution time
* more correct business scope
* lower production risk

Not enough by itself:

```text
Cost went down.
```

---

## Trainer Delivery

"Cost is an optimizer estimate.

It is useful, but it is not the final truth.

For production tuning, compare multiple signals:

* row counts
* buffers
* elapsed time
* predicates
* business requirement
* concurrency impact."

---

# Slide 14 - Common Mistakes To Avoid

## Slide Content

Avoid:

* creating indexes without workload evidence
* assuming full table scan is always bad
* assuming index scan is always good
* ignoring row count
* ignoring bind values
* ignoring predicate information
* comparing only cost
* forgetting DML overhead
* forgetting rollback plan

---

# SECTION 14 - DAY 1 CLOSING (4:50 - 5:00)

# Slide 15 - Day 1 DBA Workflow

## Slide Content

```text
Problem
  -> Observe SQL
  -> Measure rows and reads
  -> Capture runtime plan
  -> Check predicates
  -> Compare E-Rows vs A-Rows
  -> Identify wrong assumption
  -> Apply smallest safe fix
  -> Validate before and after
```

---

## Trainer Delivery

"Today was about manual SQL diagnosis.

Before using AWR, ADDM, SQL Tuning Advisor, or SQL Profiles, a DBA must understand what the SQL and execution plan are saying.

Tomorrow we move from single-SQL analysis to workload-level diagnosis."

---

# Slide 16 - Transition To Day 2

## Slide Content

Day 2 focus:

* AWR interpretation workflow
* ADDM recommendations
* Top SQL analysis
* wait event diagnosis
* SQL Tuning Advisor
* SQL Access Advisor
* memory and I/O symptoms

---

## Trainer Delivery

"The trainees specifically asked about AWR, ADDM, wait events, and how to apply the right solution.

Day 1 gave them the foundation.

Day 2 will answer:

> What happened in the database during the slow period, and where should we investigate first?"

---

# FINAL DAY 1 MESSAGE

Repeat this clearly:

```text
Do not tune blindly.
Do not create indexes emotionally.
Read the plan.
Check the predicates.
Compare estimates with reality.
Validate the fix with evidence.
```
