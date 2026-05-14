# Assignment 7 - Bind Peeking With Merchant Skew

## Training Link

Day 3: bind peeking, adaptive cursor sharing, histograms, child cursors, and why hints can be risky with skewed data.

## Scenario

The same merchant settlement report is used by merchants of very different sizes.

The application sends a bind variable:

```sql
WHERE merchant_id = :b_merchant_id
```

Business pattern:

```text
Merchant 100 = national supermarket chain with many payments
Merchant 200 = regional store group with medium payment volume
Merchant 300 = small kiosk with few payments
```

The application team wants to add an `INDEX` hint because the report is fast for the small merchant. Your job is to prove whether that same hint is safe for the large merchant.

## Setup

Run this setup in your own schema.

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET SERVEROUTPUT ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a7_merchant_payments PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a7_merchant_payments (
    payment_id         NUMBER PRIMARY KEY,
    merchant_id        NUMBER NOT NULL,
    terminal_id        NUMBER,
    customer_id        NUMBER,
    payment_date       DATE,
    amount             NUMBER(12,2),
    settlement_status  VARCHAR2(20),
    channel            VARCHAR2(20),
    remarks            VARCHAR2(100)
);

INSERT /*+ APPEND */ INTO a7_merchant_payments
SELECT LEVEL,
       100,
       MOD(LEVEL,500) + 1,
       MOD(LEVEL,80000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(5,2500),2),
       CASE WHEN MOD(LEVEL,8) = 0 THEN 'PENDING' ELSE 'SETTLED' END,
       CASE WHEN MOD(LEVEL,3) = 0 THEN 'ONLINE' ELSE 'POS' END,
       'large merchant'
FROM dual
CONNECT BY LEVEL <= 300000;

COMMIT;

INSERT /*+ APPEND */ INTO a7_merchant_payments
SELECT 300000 + LEVEL,
       200,
       MOD(LEVEL,50) + 1,
       MOD(LEVEL,10000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(5,2500),2),
       'SETTLED',
       CASE WHEN MOD(LEVEL,4) = 0 THEN 'ONLINE' ELSE 'POS' END,
       'medium merchant'
FROM dual
CONNECT BY LEVEL <= 5000;

COMMIT;

INSERT /*+ APPEND */ INTO a7_merchant_payments
SELECT 305000 + LEVEL,
       300,
       MOD(LEVEL,10) + 1,
       MOD(LEVEL,1000) + 1,
       SYSDATE - MOD(LEVEL,365),
       ROUND(DBMS_RANDOM.VALUE(5,2500),2),
       'SETTLED',
       'POS',
       'small merchant'
FROM dual
CONNECT BY LEVEL <= 500;

COMMIT;

CREATE INDEX idx_a7_payments_merchant
ON a7_merchant_payments(merchant_id);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A7_MERCHANT_PAYMENTS',
    method_opt => 'FOR COLUMNS SIZE 254 merchant_id',
    cascade    => TRUE
  );
END;
/
```

## Validate Data Skew

```sql
SELECT merchant_id,
       COUNT(*) AS payment_count
FROM a7_merchant_payments
GROUP BY merchant_id
ORDER BY merchant_id;
```

Expected:

```text
MERCHANT_ID 100 = 300000 rows
MERCHANT_ID 200 =   5000 rows
MERCHANT_ID 300 =    500 rows
```

Check histogram:

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A7_MERCHANT_PAYMENTS'
AND column_name = 'MERCHANT_ID';
```

Expected:

```text
HISTOGRAM = FREQUENCY
```

## Prepare Bind Variable

```sql
ALTER SESSION SET statistics_level = ALL;

VARIABLE b_merchant_id NUMBER
```

## Test 1 - Same Bind SQL for Small Merchant

```sql
EXEC :b_merchant_id := 300;

SELECT /* a7_bind_merchant_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

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

## Test 2 - Same Bind SQL for Large Merchant

```sql
EXEC :b_merchant_id := 100;

SELECT /* a7_bind_merchant_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

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
EXEC :b_merchant_id := 300
SELECT /* a7_bind_merchant_demo */ SUM(p.amount) FROM a7_merchant_payments p WHERE p.merchant_id = :b_merchant_id;

EXEC :b_merchant_id := 100
SELECT /* a7_bind_merchant_demo */ SUM(p.amount) FROM a7_merchant_payments p WHERE p.merchant_id = :b_merchant_id;

EXEC :b_merchant_id := 300
SELECT /* a7_bind_merchant_demo */ SUM(p.amount) FROM a7_merchant_payments p WHERE p.merchant_id = :b_merchant_id;

EXEC :b_merchant_id := 100
SELECT /* a7_bind_merchant_demo */ SUM(p.amount) FROM a7_merchant_payments p WHERE p.merchant_id = :b_merchant_id;

EXEC :b_merchant_id := 200
SELECT /* a7_bind_merchant_demo */ SUM(p.amount) FROM a7_merchant_payments p WHERE p.merchant_id = :b_merchant_id;
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
WHERE sql_text LIKE '%a7_bind_merchant_demo%'
AND sql_text NOT LIKE '%v$sql%'
ORDER BY sql_id, child_number;
```

## Test 3 - Force Index Hint

Run this for both merchant 300 and merchant 100.

```sql
EXEC :b_merchant_id := 300;

SELECT /*+ INDEX(p idx_a7_payments_merchant) */ /* a7_index_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_merchant_id := 100;

SELECT /*+ INDEX(p idx_a7_payments_merchant) */ /* a7_index_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

## Test 4 - Force Full Scan Hint

Run this for both merchant 300 and merchant 100.

```sql
EXEC :b_merchant_id := 300;

SELECT /*+ FULL(p) */ /* a7_full_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

```sql
EXEC :b_merchant_id := 100;

SELECT /*+ FULL(p) */ /* a7_full_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

## Comparison Table

| Test | Merchant | Elapsed time | Buffer gets | Main plan operation | E-Rows | A-Rows |
|---|---:|---:|---:|---|---:|---:|
| No hint bind SQL | 300 | | | | | |
| No hint bind SQL | 100 | | | | | |
| INDEX hint | 300 | | | | | |
| INDEX hint | 100 | | | | | |
| FULL hint | 300 | | | | | |
| FULL hint | 100 | | | | | |

## Bind Cursor Worksheet

| Item | Observation |
|---|---|
| Histogram exists? | |
| SQL ID | |
| Child cursors | |
| Bind sensitive? | |
| Bind aware? | |
| Peeked bind visible? | |
| Plan for merchant 300 | |
| Plan for merchant 100 | |

## Final DBA Answer

Write 6-8 lines explaining:

```text
1. Why merchant_id is skewed.
2. Why the same bind SQL can behave differently for merchant 100 and merchant 300.
3. Whether Oracle created multiple child cursors.
4. Whether the INDEX hint helped the small merchant.
5. Whether the INDEX hint hurt the large merchant.
6. Whether one hard-coded hint is safe for this shared settlement report.
```
