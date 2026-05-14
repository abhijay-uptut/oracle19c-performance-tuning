# Solution 4 - SQL Tuning Advisor Validation

## Expected Problem

The SQL filters by customer and date, then orders by date descending:

```text
CUSTOMER_ID = 2001
TXN_DATE >= last 12 months
ORDER BY TXN_DATE DESC
```

Without a supporting index, Oracle may scan too many rows and sort.

## Before Test

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* a4_sta_customer_txn */
       txn_id,
       customer_id,
       txn_date,
       amount,
       status
FROM a4_customer_txn
WHERE customer_id = 2001
AND txn_date >= ADD_MONTHS(TRUNC(SYSDATE), -12)
ORDER BY txn_date DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Find SQL ID:

```sql
SELECT sql_id, plan_hash_value, executions, buffer_gets, disk_reads, elapsed_time
FROM v$sql
WHERE sql_text LIKE '%a4_sta_customer_txn%'
AND sql_text NOT LIKE '%v$sql%';
```

## Expected Advisor Direction

SQL Tuning Advisor may recommend one or more of:

```text
Create an index
Gather better statistics
Accept a SQL Profile
Rewrite SQL
```

For this assignment, the likely useful physical access path is:

```text
A4_CUSTOMER_TXN(CUSTOMER_ID, TXN_DATE DESC)
```

## Safe Validation With Invisible Index

```sql
CREATE INDEX idx_a4_customer_txn_cdate_inv
ON a4_customer_txn(customer_id, txn_date DESC)
INVISIBLE;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'A4_CUSTOMER_TXN',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/

ALTER SESSION SET optimizer_use_invisible_indexes = TRUE;
```

## After Test

```sql
SELECT /* a4_sta_customer_txn */
       txn_id,
       customer_id,
       txn_date,
       amount,
       status
FROM a4_customer_txn
WHERE customer_id = 2001
AND txn_date >= ADD_MONTHS(TRUNC(SYSDATE), -12)
ORDER BY txn_date DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected after observations:

```text
INDEX RANGE SCAN on IDX_A4_CUSTOMER_TXN_CDATE_INV
Lower buffer gets
Lower elapsed time
Less sorting work, depending on optimizer choice
```

## Make Index Visible Only After Approval

If the test proves improvement and the DML cost is acceptable:

```sql
ALTER INDEX idx_a4_customer_txn_cdate_inv VISIBLE;
```

If the test does not prove improvement:

```sql
DROP INDEX idx_a4_customer_txn_cdate_inv;
```

## DBA Conclusion Example

```text
The advisor recommendation was not accepted blindly.
The candidate index was first tested as invisible and enabled only in the test session.
The after plan should show an index range scan with lower buffer gets and elapsed time.
If the workload frequency justifies the DML overhead, the index can be made visible after change approval.
```

