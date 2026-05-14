# Solution 1 - Customer Transaction Lookup Tuning

## Expected Problem

Before tuning, Oracle may scan a large portion of `A1_TRANSACTIONS` and then sort rows by `TRANSACTION_DATE DESC`.

The SQL filters by:

```text
CUSTOMER_ID
```

and sorts by:

```text
TRANSACTION_DATE DESC
```

So the candidate index should start with the equality predicate and then include the ordering column.

## Before Test

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* a1_customer_statement */
       transaction_id,
       customer_id,
       account_id,
       transaction_date,
       amount,
       status
FROM a1_transactions
WHERE customer_id = 1001
ORDER BY transaction_date DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected before observations:

```text
Possible TABLE ACCESS FULL
Possible SORT ORDER BY
Higher buffer gets
Longer elapsed time
```

## Tuning Change

```sql
CREATE INDEX idx_a1_txn_customer_date
ON a1_transactions(customer_id, transaction_date DESC);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'A1_TRANSACTIONS',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## After Test

```sql
SELECT /* a1_customer_statement */
       transaction_id,
       customer_id,
       account_id,
       transaction_date,
       amount,
       status
FROM a1_transactions
WHERE customer_id = 1001
ORDER BY transaction_date DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected after observations:

```text
INDEX RANGE SCAN on IDX_A1_TXN_CUSTOMER_DATE
Less sorting work, depending on selected columns and plan
Lower buffer gets
Lower elapsed time
```

## Why This Index Is Correct

```text
CUSTOMER_ID is first because it is the equality filter.
TRANSACTION_DATE DESC is second because the SQL orders by recent transactions.
The index supports customer-specific retrieval in the required order.
```

## Production Note

This index helps customer statement lookup but adds DML overhead to inserts and updates on `CUSTOMER_ID` or `TRANSACTION_DATE`. In production, check execution frequency and existing similar indexes before approving it.

