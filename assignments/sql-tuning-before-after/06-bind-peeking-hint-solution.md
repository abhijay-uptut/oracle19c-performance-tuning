# Solution 6 - Bind Peeking and Hint Risk

## Expected Problem

The SQL text is the same:

```sql
WHERE branch_id = :b_branch_id
```

but the values are not equivalent:

```text
Branch 1 = 300000 rows
Branch 2 =   5000 rows
Branch 3 =    500 rows
```

The best access path for a small branch may not be the best access path for the large branch.

## Validate Skew and Histogram

```sql
SELECT branch_id,
       COUNT(*) AS txn_count
FROM a6_branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

Expected:

```text
1 -> 300000
2 ->   5000
3 ->    500
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

## Run the Bind SQL

```sql
ALTER SESSION SET statistics_level = ALL;
VARIABLE b_branch_id NUMBER
```

Small branch:

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

Large branch:

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

## Expected Observations

For branch 3:

```text
Index access may be efficient.
Rows returned are low.
Buffer gets should usually be lower with an index path.
```

For branch 1:

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
WHERE sql_text LIKE '%a6_bind_branch_demo%'
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
EXEC :b_branch_id := 3;

SELECT /*+ INDEX(a6_branch_transactions idx_a6_branch_txn_branch) */ /* a6_index_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;
```

Expected for branch 3:

```text
The INDEX hint may help because branch 3 is selective.
```

```sql
EXEC :b_branch_id := 1;

SELECT /*+ INDEX(a6_branch_transactions idx_a6_branch_txn_branch) */ /* a6_index_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;
```

Expected for branch 1:

```text
The same INDEX hint may hurt because branch 1 returns most rows.
```

### FULL Hint

```sql
EXEC :b_branch_id := 3;

SELECT /*+ FULL(a6_branch_transactions) */ /* a6_full_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;
```

Expected for branch 3:

```text
The FULL hint may be worse because it reads the whole table for a rare value.
```

```sql
EXEC :b_branch_id := 1;

SELECT /*+ FULL(a6_branch_transactions) */ /* a6_full_hint_demo */
       SUM(amount)
FROM a6_branch_transactions
WHERE branch_id = :b_branch_id;
```

Expected for branch 1:

```text
The FULL hint may be reasonable because branch 1 returns a very large percentage of the table.
```

## DBA Conclusion Example

```text
BRANCH_ID is skewed because Branch 1 has 300000 rows while Branch 3 has only 500 rows.
The same bind SQL can need different access paths for different bind values.
The small branch may perform well with an index, but the large branch may perform better with a full scan.
Adaptive Cursor Sharing may create separate child cursors, but this is environment-dependent and should be verified in V$SQL.
One hard-coded INDEX hint is not safe for a shared report used by every branch.
The safer production approach is to keep accurate histogram statistics, inspect bind-sensitive cursor behavior, and avoid blanket hints unless there is an approved short-term containment reason.
```

## Production Recommendation

```text
Do not add an INDEX hint just because it helps one selective bind value.
Check row-count skew, histogram stats, runtime plans, buffer gets, peeked binds, and child cursors.
Prefer correct statistics, suitable indexes, SQL design, SQL Plan Management, or targeted remediation over hard-coded blanket hints.
```
