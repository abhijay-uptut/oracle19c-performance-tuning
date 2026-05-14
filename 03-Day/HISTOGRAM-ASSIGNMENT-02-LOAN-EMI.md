# Assignment 2 - Complex Loan EMI Collections Histogram and Index

# Assignment Story

A bank has a daily loan EMI collections dashboard.

The table stores current and historical EMI rows for many branches.

Most EMI records are healthy, but a small queue needs urgent collections action.

The collections manager complains:

```text
The morning legal-action queue is slow, and Oracle keeps estimating the row count badly.
```

As the DBA, your job is to help Oracle understand both:

* uneven status data
* correlated collections data

This is more complex than a single rare value lookup.

---

# DBA Task

You must create a test table, add useful indexes, gather statistics, compare plans, apply histograms, and then add column-group statistics for correlated predicates.

Use this table name:

```text
LOAN_EMI_DEMO
```

Important columns:

```text
EMI_STATUS
RISK_BAND
COLLECTION_STAGE
```

Main EMI status pattern:

```text
PAID       = 440,000 rows
DUE        =  35,000 rows
LATE_1_30  =  18,000 rows
LATE_31_60 =   5,000 rows
DEFAULTED  =   2,000 rows
```

This is skewed data.

The complex part:

```text
Most DEFAULTED rows are HIGH risk.
Most HIGH risk DEFAULTED rows are in LEGAL_ACTION.
LEGAL_ACTION almost never appears for normal EMI rows.
```

This means the columns are correlated.

---

# Part 1: Create Complex Loan EMI Table

Create a table with 500,000 rows.

The table should contain:

* `emi_id`
* `loan_id`
* `customer_id`
* `branch_id`
* `emi_month`
* `emi_status`
* `risk_band`
* `collection_stage`
* `days_past_due`
* `emi_amount`
* `outstanding_amount`

Use the status distribution shown above.

Also create this correlated DEFAULTED pattern:

```text
DEFAULTED rows       = 2,000
DEFAULTED HIGH risk  = 1,700
DEFAULTED LEGAL_ACTION rows = 1,500
```

---

# Part 2: Create Indexes

Create a simple index on:

```text
EMI_STATUS
```

Use this index name:

```text
IDX_LOAN_EMI_STATUS
```

Create a composite index for the collections queue:

```text
EMI_STATUS, RISK_BAND, COLLECTION_STAGE
```

Use this index name:

```text
IDX_LOAN_EMI_COLL_Q
```

---

# Part 3: Gather Stats WITHOUT Histograms

Gather table statistics with no histograms.

Use:

```text
FOR ALL COLUMNS SIZE 1
```

Meaning:

```text
No column histograms
```

---

# Part 4: Confirm Histograms Are Not Created

Check `USER_TAB_COL_STATISTICS`.

Check these columns:

```text
EMI_STATUS
RISK_BAND
COLLECTION_STAGE
```

Expected result:

```text
EMI_STATUS          NONE
RISK_BAND           NONE
COLLECTION_STAGE    NONE
```

---

# Part 5: Run Rare Status Query

Run this query:

```sql
SELECT /* rare_status_no_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
```

Then check the execution plan using:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Compare:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

DBA question:

```text
Without a histogram, does Oracle estimate DEFAULTED rows correctly?
```

---

# Part 6: Run Complex Collections Queue Query

Run this query:

```sql
SELECT /* queue_no_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Check the plan again.

DBA question:

```text
Does Oracle estimate the combined queue correctly before histograms?
```

Expected actual rows:

```text
1,500 rows
```

---

# Part 7: Create Histograms

Gather table statistics again with histograms on the three skewed columns:

```text
EMI_STATUS
RISK_BAND
COLLECTION_STAGE
```

Use a histogram size of 254.

---

# Part 8: Confirm Histograms Are Created

Check `USER_TAB_COL_STATISTICS` again.

Expected result:

```text
EMI_STATUS          FREQUENCY
RISK_BAND           FREQUENCY
COLLECTION_STAGE    FREQUENCY
```

---

# Part 9: Re-run Both Queries

Run the rare status query again:

```sql
SELECT /* rare_status_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
```

Then run the complex queue query again:

```sql
SELECT /* queue_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Compare:

```text
Rare status query:
Before histogram: Oracle may use average status distribution
After histogram : Oracle should know DEFAULTED is rare

Complex queue query:
Histograms help each column separately
But Oracle may still estimate poorly because the columns are correlated
```

---

# Part 10: Add Column-Group Statistics

Create extended statistics for this column group:

```text
(EMI_STATUS, RISK_BAND, COLLECTION_STAGE)
```

Then gather table statistics again.

Confirm the extension exists in:

```text
USER_STAT_EXTENSIONS
```

---

# Part 11: Re-run Complex Queue Query

Run:

```sql
SELECT /* queue_group_stats */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Check the plan again.

Compare:

```text
No histogram        : weak estimate
Individual histograms: better column-level knowledge, but still may miss correlation
Column-group stats  : better estimate for the combined predicate
```

---

# Final DBA Answer Required

Write 5 short lines:

```text
1. Why was EMI_STATUS skewed?
2. Why was the composite index useful?
3. Why did histograms help the DEFAULTED query?
4. Why might individual histograms still miss the complex queue estimate?
5. Why did column-group statistics help?
```
