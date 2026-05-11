# Solution FIRST-1 - Banking Histogram and Plan Operation Analysis

## Objective

This solution proves how a histogram helps Oracle estimate a skewed banking status column more accurately and how that estimate affects plan interpretation.

The important DBA skill is not memorizing one expected plan. The skill is reading:

* operation
* object name
* `E-Rows`
* `A-Rows`
* buffers
* predicate information

## Step 1 - Session Settings

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

### Explanation

`statistics_level = ALL` allows `DBMS_XPLAN.DISPLAY_CURSOR` to show runtime row-source statistics such as actual rows and buffers.

## Step 2 - Prepare Predictable Banking Skew

```sql
UPDATE transactions
SET status =
  CASE
    WHEN MOD(transaction_id,20) = 0 THEN 'FAILED'
    ELSE 'SUCCESS'
  END;

COMMIT;
```

### Explanation

This creates a predictable production-style skew:

* `FAILED` is about 5% of the table
* `SUCCESS` is about 95% of the table

For a 300,000-row table, expect about 15,000 failed transactions and 285,000 successful transactions.

## Step 3 - Verify Real Data Distribution

```sql
SELECT status,
       COUNT(*) AS row_count,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct_of_table
FROM transactions
GROUP BY status
ORDER BY status;
```

### Expected Result

| Status | Row Count | Percent |
| ------ | --------- | ------- |
| FAILED | about 15,000 | about 5% |
| SUCCESS | about 285,000 | about 95% |

### Explanation

This is the actual business reality. Later, compare this with Oracle's `E-Rows`.

## Step 4 - Ensure A Status Index Exists

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

### Explanation

The index gives Oracle a possible access path for selective status lookups. The assignment is still about evidence, not blindly proving that an index is always best.

## Step 5 - Gather Stats Without Histogram

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

### Explanation

`SIZE 1 status` prevents a histogram on `STATUS`. Oracle can know that there are two values, but it may not know that one value is rare and the other is common.

## Step 6 - Confirm No Histogram

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

### Expected Result

```text
COLUMN_NAME  NUM_DISTINCT  HISTOGRAM  NUM_BUCKETS
-----------  ------------  ---------  -----------
STATUS       2             NONE       1
```

### Explanation

`NUM_DISTINCT = 2` means Oracle knows there are two status values. `HISTOGRAM = NONE` means Oracle does not have frequency detail.

## Step 7 - Run Query A Without Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* no_hist_q_a_est */
       COUNT(*)
FROM transactions
WHERE status = 'FAILED';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* no_hist_q_a */
       COUNT(*)
FROM transactions
WHERE status = 'FAILED';
```

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

### What To Look For

Focus on the operation below `SORT AGGREGATE`.

Typical operation:

```text
INDEX RANGE SCAN  IDX_TXN_STATUS
```

Expected comparison:

```text
E-Rows may be close to 150,000
A-Rows should be close to 15,000
```

### Explanation

`EXPLAIN PLAN` shows Oracle's prediction before execution. `DISPLAY_CURSOR` shows what actually ran.

Without a histogram, Oracle may estimate `FAILED` as half the table because there are two status values.

The top aggregate row returns one row because `COUNT(*)` returns one result. The useful row-source comparison is the scan operation underneath it.

## Step 8 - Run Query B Without Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* no_hist_q_b_est */
       COUNT(amount)
FROM transactions
WHERE status = 'FAILED';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* no_hist_q_b */
       COUNT(amount)
FROM transactions
WHERE status = 'FAILED';
```

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

### What To Look For

Possible operations:

```text
TABLE ACCESS FULL
```

or:

```text
TABLE ACCESS BY INDEX ROWID
INDEX RANGE SCAN IDX_TXN_STATUS
```

### Explanation

This is a detail-workload probe. `COUNT(amount)` references a column that is not part of `IDX_TXN_STATUS`, so the status index alone may not be enough. If Oracle uses the status index, it may also need table lookup operations by rowid.

## Step 9 - Run Query C Without Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* no_hist_q_c_est */
       COUNT(amount)
FROM transactions
WHERE status = 'SUCCESS';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* no_hist_q_c */
       COUNT(amount)
FROM transactions
WHERE status = 'SUCCESS';
```

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

### What To Look For

Typical operation:

```text
TABLE ACCESS FULL
```

### Explanation

`SUCCESS` returns most of the table. A full scan can be reasonable for a high-volume value because using an index plus many table rowid lookups may be more expensive.

## Step 10 - Gather Stats With Histogram

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

### Explanation

`SIZE 254 status` allows Oracle to create a histogram on the `STATUS` column. The table rows do not change. Only optimizer statistics change.

## Step 11 - Confirm Histogram Exists

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

### Expected Result

```text
COLUMN_NAME  NUM_DISTINCT  HISTOGRAM   NUM_BUCKETS
-----------  ------------  ----------  -----------
STATUS       2             FREQUENCY   2
```

Some Oracle versions may show a different histogram type. The key point is that `HISTOGRAM` should no longer be `NONE`.

## Step 12 - Rerun Query A With Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* hist_q_a_est */
       COUNT(*)
FROM transactions
WHERE status = 'FAILED';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* hist_q_a */
       COUNT(*)
FROM transactions
WHERE status = 'FAILED';
```

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

### Expected Result

```text
E-Rows should be close to 15,000
A-Rows should be close to 15,000
```

### Explanation

The histogram tells Oracle that `FAILED` is rare. The actual row count did not change. The estimate improved because Oracle now has better distribution knowledge.

## Step 13 - Rerun Query B With Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* hist_q_b_est */
       COUNT(amount)
FROM transactions
WHERE status = 'FAILED';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* hist_q_b */
       COUNT(amount)
FROM transactions
WHERE status = 'FAILED';
```

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

### Expected Result

The estimate for the `FAILED` row source should move closer to the actual failed row count.

The operation may be:

```text
TABLE ACCESS BY INDEX ROWID
INDEX RANGE SCAN IDX_TXN_STATUS
```

or still:

```text
TABLE ACCESS FULL
```

### Explanation

Do not force one expected operation. The DBA conclusion must be based on the displayed plan, buffers, and row estimates. The histogram gives Oracle a better chance to choose the right operation.

## Step 14 - Rerun Query C With Histogram

First capture the estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT /* hist_q_c_est */
       COUNT(amount)
FROM transactions
WHERE status = 'SUCCESS';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run the query and capture the runtime plan:

```sql
SELECT /*+ GATHER_PLAN_STATISTICS */ /* hist_q_c */
       COUNT(amount)
FROM transactions
WHERE status = 'SUCCESS';
```

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

### Expected Result

The estimate for `SUCCESS` should be high, close to most of the table.

Typical operation:

```text
TABLE ACCESS FULL
```

### Explanation

The histogram helps Oracle understand that `SUCCESS` is common. For a common value, a full table scan may be the correct operation.

## Completed Observation Example

Exact numbers depend on table size, block size, caching, Oracle version, and existing objects.

| Test | Histogram State | Query | Main Operation | DBA Observation |
| ---- | --------------- | ----- | -------------- | --------------- |
| 1 | No histogram | Query A | Usually `INDEX RANGE SCAN` | Count can use the status index, but `E-Rows` may overestimate failed rows |
| 2 | No histogram | Query B | `TABLE ACCESS FULL` or index plus rowid lookup | Estimate may be poor because Oracle lacks skew detail |
| 3 | No histogram | Query C | Usually `TABLE ACCESS FULL` | Success is high-volume, so full scan may be reasonable |
| 4 | With histogram | Query A | Usually `INDEX RANGE SCAN` | `E-Rows` should move closer to `A-Rows` |
| 5 | With histogram | Query B | Environment dependent | Histogram improves estimate; operation must be judged from buffers and rowid cost |
| 6 | With histogram | Query C | Usually `TABLE ACCESS FULL` | Histogram helps Oracle recognize the common value |

## Answers To Assignment Questions

1. `FAILED` is about 5% of the table.
2. `SUCCESS` is about 95% of the table.
3. Before the histogram, Oracle may estimate `FAILED` poorly, often near 50% of the table.
4. After the histogram, Oracle should estimate `FAILED` much closer to the actual row count.
5. Query A commonly uses `INDEX RANGE SCAN` on `IDX_TXN_STATUS`, because the index can satisfy `COUNT(*)`.
6. Query B may use `TABLE ACCESS FULL` or `INDEX RANGE SCAN` plus `TABLE ACCESS BY INDEX ROWID`; the actual answer must come from `DBMS_XPLAN`.
7. Query C commonly uses `TABLE ACCESS FULL`, because `SUCCESS` returns most rows.
8. An index can help for `FAILED` because it is selective. It may not help for `SUCCESS` because many rowid lookups can be more expensive than scanning the table.
9. No. The histogram does not change table data. It changes Oracle's knowledge of the data distribution.
10. The DBA should collect evidence first: distribution, statistics, execution plan, runtime plan, estimates, actual rows, buffers, and predicates.

## Final DBA Recommendation

The failed transaction query should not be tuned by guesswork. Because `STATUS` is skewed, keep accurate statistics with a histogram so Oracle can estimate `FAILED` and `SUCCESS` differently. Use `DBMS_XPLAN.DISPLAY_CURSOR` to verify the real operation and compare `E-Rows` with `A-Rows`. Consider index changes only after confirming execution frequency, buffers, concurrency impact, and whether the query returns count-only or full detail rows.
