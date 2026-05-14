# SQL Tuning Before/After Assignment Pack

This pack contains seven assignments based on Day 1, Day 2, and Day 3 of the Oracle SQL tuning training.

Each assignment follows the same DBA workflow:

```text
Create test data
  -> run the slow SQL
  -> capture before timing and plan
  -> apply one controlled tuning change
  -> run the same SQL again
  -> compare before and after evidence
  -> write a DBA recommendation
```

## Files

| # | Assignment | Main Training Link |
|---|---|---|
| 1 | Customer Transaction Lookup | Day 1 execution plans and composite indexes |
| 2 | Function-Based Customer Search | Day 1 function-based indexes |
| 3 | AWR SQL Before/After Comparison | Day 2 AWR SQL reports |
| 4 | SQL Tuning Advisor Validation | Day 2 SQL Tuning Advisor and invisible indexes |
| 5 | Histogram and Skewed Data | Day 3 histograms and cardinality estimates |
| 6 | Bind Peeking and Hint Risk | Day 3 bind peeking, ACS, and hint comparison |
| 7 | Bind Peeking With Merchant Skew | Day 3 bind peeking, ACS, and hint comparison |

## Common Measurement Setup

Use these settings before every test:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

After running a SQL statement, capture the actual runtime plan:

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

## Required Comparison Table

Every trainee should complete this table.

| Metric | Before | After |
|---|---:|---:|
| Elapsed time | | |
| Buffer gets | | |
| Disk reads | | |
| Main plan operation | | |
| Index used? | | |
| Estimated rows | | |
| Actual rows | | |

## Final DBA Answer Format

```text
1. Original problem:
2. Evidence collected:
3. Tuning change applied:
4. Before/after result:
5. Production risk:
6. Final recommendation:
```
