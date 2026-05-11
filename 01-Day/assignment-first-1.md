# Assignment FIRST-1 - Banking Histogram and Plan Operation Analysis

## Problem Statement

A banking operations team reports that the **failed transaction investigation screen** becomes slow during business hours.

The screen is used by branch operations and fraud analysts to review transactions with this condition:

```sql
WHERE status = 'FAILED'
```

The application team assumes this query should be fast because `FAILED` transactions are rare. The DBA team is not allowed to guess or tune blindly. They must prove:

* how the data is distributed
* whether Oracle understands that distribution
* which execution plan operation Oracle chooses
* whether estimated rows and actual rows are close
* whether a histogram improves optimizer estimates

Use the `TRANSACTIONS` table created during `FIRST.md`.

## Business Context

In this banking workload:

* most transactions are successful
* a small percentage of transactions fail
* failed transactions are important for investigation
* successful transactions are high-volume and usually not selective
* wrong optimizer estimates may lead Oracle to choose inefficient access paths

Your task is to analyze this like a production DBA.

## What You Have To Do

1. Verify the row distribution for `STATUS`.
2. Capture the current optimizer statistics for `TRANSACTIONS.STATUS`.
3. Run the failed transaction query **without a histogram** on `STATUS`.
4. Capture the estimated plan with `EXPLAIN PLAN`.
5. Capture the runtime plan with `DBMS_XPLAN.DISPLAY_CURSOR`.
6. Identify the main operation used by Oracle.
7. Compare `E-Rows` and `A-Rows`.
8. Gather statistics **with a histogram** on `STATUS`.
9. Confirm that a histogram exists.
10. Run the same failed transaction query again.
11. Capture the estimated plan and runtime plan again.
12. Identify whether the operation, estimate, cost, or buffers changed.
13. Explain whether the histogram changed the data or only changed Oracle's knowledge of the data.
14. Write a short DBA recommendation for the banking operations team.

## Queries To Investigate

### Query A - Failed Transaction Count

```sql
SELECT COUNT(*)
FROM transactions
WHERE status = 'FAILED';
```

### Query B - Failed Transaction Detail Workload Probe

```sql
SELECT COUNT(amount)
FROM transactions
WHERE status = 'FAILED';
```

### Query C - Successful Transaction Detail Workload Probe

```sql
SELECT COUNT(amount)
FROM transactions
WHERE status = 'SUCCESS';
```

## Observation Table

Fill this table from your `DBMS_XPLAN` output.

| Test | Histogram State | Query | Estimated Operation | Runtime Operation | Object Name | E-Rows | A-Rows | Buffers | Predicate Type | DBA Observation |
| ---- | --------------- | ----- | ------------------- | ----------------- | ----------- | ------ | ------ | ------- | -------------- | --------------- |
| 1 | No histogram | Query A | | | | | | | | |
| 2 | No histogram | Query B | | | | | | | | |
| 3 | No histogram | Query C | | | | | | | | |
| 4 | With histogram | Query A | | | | | | | | |
| 5 | With histogram | Query B | | | | | | | | |
| 6 | With histogram | Query C | | | | | | | | |

## Questions To Answer

1. What is the real percentage of `FAILED` transactions?
2. What is the real percentage of `SUCCESS` transactions?
3. Before the histogram, did Oracle estimate `FAILED` correctly?
4. After the histogram, did Oracle estimate `FAILED` more accurately?
5. Which operation did Oracle use for the failed transaction count query?
6. Which operation did Oracle use for the failed transaction detail workload probe?
7. Which operation did Oracle use for the successful transaction detail workload probe?
8. Why might an index be useful for `FAILED` but not useful for `SUCCESS`?
9. Did the histogram change the rows in the table?
10. What should the DBA recommend before changing indexes, SQL, or database parameters?

## Deliverable

Submit:

* completed observation table
* answers to the ten questions
* short DBA recommendation, maximum five sentences
