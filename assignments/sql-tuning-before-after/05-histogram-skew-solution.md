# Solution 5 - Histogram and Skewed Data Tuning

## Expected Problem

`AUTH_STATUS` is highly skewed:

```text
APPROVED is very common.
FRAUD_REVIEW is rare.
```

Without a histogram, Oracle may estimate each status value too evenly.

With 100,000 rows and 3 status values, a no-histogram estimate may be close to:

```text
100000 / 3 = 33333 rows per status
```

But the real `FRAUD_REVIEW` count is:

```text
1000 rows
```

## Before Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A5_CARD_AUTH',
    cascade    => TRUE,
    method_opt => 'FOR COLUMNS SIZE 1 auth_status'
  );
END;
/

SELECT column_name, histogram, num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A5_CARD_AUTH'
AND column_name = 'AUTH_STATUS';
```

Expected:

```text
AUTH_STATUS    NONE
```

Run the SQL:

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* a5_fraud_review_queue */
       auth_id,
       card_id,
       merchant_id,
       auth_amount,
       auth_status
FROM a5_card_auth
WHERE auth_status = 'FRAUD_REVIEW';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected before observation:

```text
Estimated rows may be much higher than actual rows.
Optimizer may not fully understand that FRAUD_REVIEW is rare.
```

## After Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A5_CARD_AUTH',
    cascade    => TRUE,
    method_opt => 'FOR COLUMNS SIZE 254 auth_status'
  );
END;
/

SELECT column_name, histogram, num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A5_CARD_AUTH'
AND column_name = 'AUTH_STATUS';
```

Expected:

```text
AUTH_STATUS    FREQUENCY
```

Run the SQL again:

```sql
SELECT /* a5_fraud_review_queue */
       auth_id,
       card_id,
       merchant_id,
       auth_amount,
       auth_status
FROM a5_card_auth
WHERE auth_status = 'FRAUD_REVIEW';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected after observation:

```text
Estimated rows should be closer to actual rows.
The optimizer has better information about the rare value.
The index on AUTH_STATUS is more clearly useful for FRAUD_REVIEW.
```

## Important Teaching Point

The histogram may not always produce a dramatic elapsed-time improvement in a small training table. The main win is estimate accuracy:

```text
Better estimates -> better plan choices -> lower risk of bad plans in larger workloads.
```

## DBA Conclusion Example

```text
AUTH_STATUS is skewed because APPROVED dominates the table and FRAUD_REVIEW is rare.
The index helps because the query searches for a small subset of rows.
The histogram helps Oracle estimate the rare value more accurately instead of using an average estimate.
In production, histograms should be used on columns where skew affects important SQL plans.
```

