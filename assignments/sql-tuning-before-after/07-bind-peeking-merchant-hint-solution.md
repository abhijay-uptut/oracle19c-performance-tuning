# Solution 7 - Bind Peeking With Merchant Skew

## Expected Problem

The SQL text is the same:

```sql
WHERE merchant_id = :b_merchant_id
```

but the values are not equivalent:

```text
Merchant 100 = 300000 rows
Merchant 200 =   5000 rows
Merchant 300 =    500 rows
```

The best access path for a small merchant may not be the best access path for the large merchant.

## Validate Skew and Histogram

```sql
SELECT merchant_id,
       COUNT(*) AS payment_count
FROM a7_merchant_payments
GROUP BY merchant_id
ORDER BY merchant_id;
```

Expected:

```text
100 -> 300000
200 ->   5000
300 ->    500
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

## Run the Bind SQL

```sql
ALTER SESSION SET statistics_level = ALL;
VARIABLE b_merchant_id NUMBER
```

Small merchant:

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

Large merchant:

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

## Expected Observations

For merchant 300:

```text
Index access may be efficient.
Rows returned are low.
Buffer gets should usually be lower with an index path.
```

For merchant 100:

```text
Many rows match.
A full scan may be cheaper than many index-driven table lookups.
An index path can become expensive because it must visit many table rows.
```

Oracle may reuse one plan at first. Adaptive Cursor Sharing may or may not create additional child cursors in a short lab.

## Inspect Child Cursors

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

Interpretation:

```text
IS_BIND_SENSITIVE = Y means Oracle noticed bind values may affect selectivity.
IS_BIND_AWARE = Y means Oracle may use different child cursors for different bind selectivity ranges.
Multiple child cursors are possible but not guaranteed in this lab.
```

If multiple child cursors appear, inspect each one:

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

## Hint Comparison

### INDEX Hint

```sql
EXEC :b_merchant_id := 300;

SELECT /*+ INDEX(p idx_a7_payments_merchant) */ /* a7_index_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;
```

Expected for merchant 300:

```text
The INDEX hint may help because merchant 300 is selective.
```

```sql
EXEC :b_merchant_id := 100;

SELECT /*+ INDEX(p idx_a7_payments_merchant) */ /* a7_index_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;
```

Expected for merchant 100:

```text
The same INDEX hint may hurt because merchant 100 returns most rows.
```

### FULL Hint

```sql
EXEC :b_merchant_id := 300;

SELECT /*+ FULL(p) */ /* a7_full_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;
```

Expected for merchant 300:

```text
The FULL hint may be worse because it reads the whole table for a rare value.
```

```sql
EXEC :b_merchant_id := 100;

SELECT /*+ FULL(p) */ /* a7_full_hint_demo */
       SUM(p.amount)
FROM a7_merchant_payments p
WHERE p.merchant_id = :b_merchant_id;
```

Expected for merchant 100:

```text
The FULL hint may be reasonable because merchant 100 returns a very large percentage of the table.
```

## DBA Conclusion Example

```text
MERCHANT_ID is skewed because Merchant 100 has 300000 rows while Merchant 300 has only 500 rows.
The same bind SQL can need different access paths for different bind values.
The small merchant may perform well with an index, but the large merchant may perform better with a full scan.
Adaptive Cursor Sharing may create separate child cursors, but this is environment-dependent and should be verified in V$SQL.
One hard-coded INDEX hint is not safe for a shared settlement report used by merchants with very different volumes.
The safer production approach is to keep accurate histogram statistics, inspect bind-sensitive cursor behavior, and avoid blanket hints unless there is an approved short-term containment reason.
```

## Production Recommendation

```text
Do not add an INDEX hint just because it helps one selective bind value.
Check row-count skew, histogram stats, runtime plans, buffer gets, peeked binds, and child cursors.
Prefer correct statistics, suitable indexes, SQL design, SQL Plan Management, or targeted remediation over hard-coded blanket hints.
```
