# Solution 1 - Card Fraud Review Histogram and Index

# Solution Story

The card authorization table has uneven status values.

Most rows are `APPROVED`.

Only a small number of rows are `FRAUD_REVIEW`.

The DBA creates an index and a histogram so Oracle can estimate the rare fraud review rows better.

---

# Part 0: Session Settings

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
ALTER SESSION SET statistics_level = ALL;
```

---

# Part 1: Setup Card Authorization Table

```sql
DROP TABLE card_auth_demo PURGE;

CREATE TABLE card_auth_demo AS
SELECT
  LEVEL auth_id,
  CASE
    WHEN LEVEL <= 96000 THEN 'APPROVED'
    WHEN LEVEL <= 99000 THEN 'DECLINED'
    ELSE 'FRAUD_REVIEW'
  END auth_status,
  TRUNC(DBMS_RANDOM.VALUE(1000, 9999)) merchant_id,
  ROUND(DBMS_RANDOM.VALUE(10, 20000), 2) auth_amount
FROM dual
CONNECT BY LEVEL <= 100000;
```

Meaning:

```text
APPROVED     = 96,000 rows
DECLINED     = 3,000 rows
FRAUD_REVIEW = 1,000 rows
```

Check the data:

```sql
SELECT auth_status, COUNT(*) row_count
FROM card_auth_demo
GROUP BY auth_status
ORDER BY row_count DESC;
```

---

# Part 2: Create Index

```sql
CREATE INDEX idx_card_auth_status
ON card_auth_demo(auth_status);
```

Why:

> The fraud team searches by `AUTH_STATUS`, so the index gives Oracle an access path for rare status values.

---

# Part 3: Gather Stats WITHOUT Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'CARD_AUTH_DEMO',
    method_opt => 'FOR COLUMNS SIZE 1 auth_status'
  );
END;
/
```

`SIZE 1` means:

> No histogram.

---

# Part 4: Confirm Histogram = NONE

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'CARD_AUTH_DEMO'
AND column_name = 'AUTH_STATUS';
```

Expected:

```text
AUTH_STATUS    NONE
```

Say:

> Oracle has basic stats, but it may not understand that FRAUD_REVIEW is much rarer than APPROVED.

---

# Part 5: Run Fraud Review Query

```sql
SELECT *
FROM card_auth_demo
WHERE auth_status = 'FRAUD_REVIEW';
```

Then check plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Check:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

Expected learning:

> Without histogram, Oracle may estimate rows using average distribution across status values.

---

# Part 6: Create Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'CARD_AUTH_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 auth_status'
  );
END;
/
```

Meaning:

> Oracle now learns the real distribution of `AUTH_STATUS`.

---

# Part 7: Confirm Histogram Created

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'CARD_AUTH_DEMO'
AND column_name = 'AUTH_STATUS';
```

Expected:

```text
AUTH_STATUS    FREQUENCY
```

---

# Part 8: Run Same Query Again

```sql
SELECT *
FROM card_auth_demo
WHERE auth_status = 'FRAUD_REVIEW';
```

Then:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Now compare:

```text
Before histogram: Oracle may use average estimate
After histogram : Oracle knows FRAUD_REVIEW has only 1,000 rows
```

---

# Final DBA Answer

```text
1. The data was skewed because APPROVED had 96,000 rows, but FRAUD_REVIEW had only 1,000 rows.
2. The index was useful because the query filtered on AUTH_STATUS and needed rare FRAUD_REVIEW rows.
3. The histogram helped Oracle estimate the rare status more accurately instead of assuming even distribution.
```

---

# Final Teaching Line

> Histogram plus a useful index helps Oracle understand rare fraud review rows and choose a smarter execution plan.

