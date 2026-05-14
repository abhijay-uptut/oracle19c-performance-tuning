# Assignment 1 - Card Fraud Review Histogram and Index

# Assignment Story

A bank has a card authorization system.

Most card swipes are approved.

Very few card swipes are sent for fraud review.

The fraud operations team complains:

```text
Fraud review transactions are slow to open during peak hours.
```

As the DBA, your job is to help Oracle understand the uneven data and choose a better access path.

---

# DBA Task

You must create a test table, add an index, gather statistics, compare plans, and then apply a histogram.

Use this table name:

```text
CARD_AUTH_DEMO
```

Use this important column:

```text
AUTH_STATUS
```

Data pattern:

```text
APPROVED     = 96,000 rows
DECLINED     = 3,000 rows
FRAUD_REVIEW = 1,000 rows
```

This is skewed data.

---

# Part 1: Create Card Authorization Table

Create a table with 100,000 rows.

The table should contain:

* `auth_id`
* `auth_status`
* `merchant_id`
* `auth_amount`

Use the row distribution shown above.

---

# Part 2: Create Index

Create an index on:

```text
AUTH_STATUS
```

Use this index name:

```text
IDX_CARD_AUTH_STATUS
```

---

# Part 3: Gather Stats WITHOUT Histogram

Gather table statistics with:

```text
FOR COLUMNS SIZE 1 auth_status
```

Meaning:

```text
No histogram
```

---

# Part 4: Confirm Histogram Is Not Created

Check `USER_TAB_COL_STATISTICS`.

Expected result:

```text
AUTH_STATUS    NONE
```

---

# Part 5: Run Fraud Review Query

Run this query:

```sql
SELECT *
FROM card_auth_demo
WHERE auth_status = 'FRAUD_REVIEW';
```

Then check the execution plan using:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Compare:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

DBA question:

```text
Does Oracle estimate FRAUD_REVIEW accurately before histogram?
```

---

# Part 6: Create Histogram

Gather table statistics again with:

```text
FOR COLUMNS SIZE 254 auth_status
```

---

# Part 7: Confirm Histogram Is Created

Check `USER_TAB_COL_STATISTICS` again.

Expected result:

```text
AUTH_STATUS    FREQUENCY
```

---

# Part 8: Run Same Query Again

Run the same fraud review query again.

Check the plan again.

Compare:

```text
Before histogram: Oracle may guess average distribution
After histogram : Oracle knows FRAUD_REVIEW is rare
```

---

# Final DBA Answer Required

Write 3 short lines:

```text
1. Why was this data skewed?
2. Why was the index useful?
3. Why did the histogram help Oracle estimate rows better?
```

