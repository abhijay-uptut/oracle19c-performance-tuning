# Assignment 2 - Loan EMI Default Histogram and Index

# Assignment Story

A bank has a loan EMI monitoring system.

Most EMI records are paid on time.

Only a small number of EMI records are defaulted.

The collections team complains:

```text
Defaulted EMI cases are slow to search in the morning review screen.
```

As the DBA, your job is to help Oracle understand the uneven EMI status data and improve the query access path.

---

# DBA Task

You must create a test table, add an index, gather statistics, compare plans, and then apply a histogram.

Use this table name:

```text
LOAN_EMI_DEMO
```

Use this important column:

```text
EMI_STATUS
```

Data pattern:

```text
PAID      = 90,000 rows
DUE       = 8,000 rows
DEFAULTED = 2,000 rows
```

This is skewed data.

---

# Part 1: Create Loan EMI Table

Create a table with 100,000 rows.

The table should contain:

* `emi_id`
* `loan_id`
* `emi_status`
* `emi_amount`

Use the row distribution shown above.

---

# Part 2: Create Index

Create an index on:

```text
EMI_STATUS
```

Use this index name:

```text
IDX_LOAN_EMI_STATUS
```

---

# Part 3: Gather Stats WITHOUT Histogram

Gather table statistics with:

```text
FOR COLUMNS SIZE 1 emi_status
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
EMI_STATUS    NONE
```

---

# Part 5: Run Defaulted EMI Query

Run this query:

```sql
SELECT *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
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
Does Oracle estimate DEFAULTED rows correctly before histogram?
```

---

# Part 6: Create Histogram

Gather table statistics again with:

```text
FOR COLUMNS SIZE 254 emi_status
```

---

# Part 7: Confirm Histogram Is Created

Check `USER_TAB_COL_STATISTICS` again.

Expected result:

```text
EMI_STATUS    FREQUENCY
```

---

# Part 8: Run Same Query Again

Run the same defaulted EMI query again.

Check the plan again.

Compare:

```text
Before histogram: Oracle may guess average distribution
After histogram : Oracle knows DEFAULTED is rare
```

---

# Final DBA Answer Required

Write 3 short lines:

```text
1. Why was this data skewed?
2. Why was the index useful?
3. Why did the histogram help Oracle estimate rows better?
```

