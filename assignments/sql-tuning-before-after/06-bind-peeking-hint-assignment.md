# Assignment 6 - Bind Peeking and Hint Risk

## Training Link

Day 3: bind peeking, adaptive cursor sharing, histograms, child cursors, and why hints can be risky with skewed data.

## Scenario

The same branch transaction report is used by every branch.

The application sends a bind variable:

```sql
WHERE branch_id = :b_branch_id
```

Business pattern:

```text
Branch 1 = city/head-office branch with many transactions
Branch 2 = medium branch
Branch 3 = small branch with few transactions
```

The application team wants to add an `INDEX` hint because the report is fast for the small branch. Your job is to prove whether that same hint is safe for the large branch.

## Setup

Run this setup in your own schema.

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET SERVEROUTPUT ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a6_branch_transactions PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a6_branch_transactions (
    transaction_id    NUMBER PRIMARY KEY,
    branch_id         NUMBER NOT NULL,
    customer_id       NUMBER,
    account_id        NUMBER,
    transaction_date  DATE,
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(100)
);

INSERT /*+ APPEND */ INTO a6_branch_transactions
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

INSERT /*+ APPEND */ INTO a6_branch_transactions
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

INSERT /*+ APPEND */ INTO a6_branch_transactions
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

CREATE INDEX idx_a6_branch_txn_branch
ON a6_branch_transactions(branch_id);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A6_BRANCH_TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 254 branch_id',
    cascade    => TRUE
  );
END;
/
```

## Validate Data Skew

```sql
SELECT branch_id,
       COUNT(*) AS txn_count
FROM a6_branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

Expected:

```text
BRANCH_ID 1 = 300000 rows
BRANCH_ID 2 =   5000 rows
BRANCH_ID 3 =    500 rows
```

Check histogram:

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A6_BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

Expected:

```text
HISTOGRAM = FREQUENCY
```

## Prepare Bind Variable

```sql
ALTER SESSION SET statistics_level = ALL;

VARIABLE b_branch_id NUMBER
```

## Test 1 - Same Bind SQL for Small Branch

```sql
EXEC :b_branch_id := 3;

SELECT /* a6_bind_branch_demo */
       SUM(amount)
FROM a6_branch_transactions
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

Record elapsed time, buffer gets, plan operation, estimated rows, actual rows, and peeked bind value.

## Test 2 - Same Bind SQL for Large Branch

```sql
EXEC :b_branch_id := 1;

SELECT /* a6_bind_branch_demo */
       SUM(amount)
FROM a6_branch_transactions
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

Record the same metrics again.

## Repeat Executions To Observe Cursor Behavior

Adaptive Cursor Sharing is environment-dependent, so repeated executions may or may not create multiple child cursors.

```sql
EXEC :b_branch_id := 3
SELECT /* a6_bind_branch_demo */ SUM(amount) FROM a6_branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 1
SELECT /* a6_bind_branch_demo */ SUM(amount) FROM a6_branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 3
SELECT /* a6_bind_branch_demo */ SUM(amount) FROM a6_branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 1
SELECT /* a6_bind_branch_demo */ SUM(amount) FROM a6_branch_transactions WHERE branch_id = :b_branch_id;

EXEC :b_branch_id := 2
SELECT /* a6_bind_branch_demo */ SUM(amount) FROM a6_branch_transactions WHERE branch_id = :b_branch_id;
```

Inspect child cursors:

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
WHERE sql_text LIKE '%a6_bind_branch_demo%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY sql_id, child_number;
```

## Test 3 - Force Index Hint

Run this for both branch 3 and branch 1.

```sql
EXEC :b_branch_id := 3;

SELECT /*+ INDEX(a6_branch_transactions idx_a6_branch_txn_branch) */ /* a6_index_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_branch_id := 1;

SELECT /*+ INDEX(a6_branch_transactions idx_a6_branch_txn_branch) */ /* a6_index_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

## Test 4 - Force Full Scan Hint

Run this for both branch 3 and branch 1.

```sql
EXEC :b_branch_id := 3;

SELECT /*+ FULL(a6_branch_transactions) */ /* a6_full_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_branch_id := 1;

SELECT /*+ FULL(a6_branch_transactions) */ /* a6_full_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

## Comparison Table

| Test | Branch | Elapsed time | Buffer gets | Main plan operation | E-Rows | A-Rows |
|---|---:|---:|---:|---|---:|---:|
| No hint bind SQL | 3 | | | | | |
| No hint bind SQL | 1 | | | | | |
| INDEX hint | 3 | | | | | |
| INDEX hint | 1 | | | | | |
| FULL hint | 3 | | | | | |
| FULL hint | 1 | | | | | |

## Bind Cursor Worksheet

| Item | Observation |
|---|---|
| Histogram exists? | |
| SQL ID | |
| Child cursors | |
| Bind sensitive? | |
| Bind aware? | |
| Peeked bind visible? | |
| Plan for branch 3 | |
| Plan for branch 1 | |

## Final DBA Answer

Write 6-8 lines explaining:

```text
1. Why branch_id is skewed.
2. Why the same bind SQL can behave differently for branch 1 and branch 3.
3. Whether Oracle created multiple child cursors.
4. Whether the INDEX hint helped the small branch.
5. Whether the INDEX hint hurt the large branch.
6. Whether one hard-coded hint is safe for this shared report.
```
