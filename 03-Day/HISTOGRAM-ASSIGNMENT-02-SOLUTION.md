# Solution 2 - Loan EMI Default Histogram and Index

# Solution Story

The loan EMI table has uneven status values.

Most EMI records are `PAID`.

Only a small number of EMI records are `DEFAULTED`.

The DBA creates an index and a histogram so Oracle can estimate defaulted EMI rows better.

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

# Part 1: Setup Loan EMI Table

```sql
DROP TABLE loan_emi_demo PURGE;

CREATE TABLE loan_emi_demo AS
SELECT
  LEVEL emi_id,
  500000 + MOD(LEVEL, 20000) loan_id,
  CASE
    WHEN LEVEL <= 90000 THEN 'PAID'
    WHEN LEVEL <= 98000 THEN 'DUE'
    ELSE 'DEFAULTED'
  END emi_status,
  ROUND(DBMS_RANDOM.VALUE(1000, 75000), 2) emi_amount
FROM dual
CONNECT BY LEVEL <= 100000;
```

Meaning:

```text
PAID      = 90,000 rows
DUE       = 8,000 rows
DEFAULTED = 2,000 rows
```

Check the data:

```sql
SELECT emi_status, COUNT(*) row_count
FROM loan_emi_demo
GROUP BY emi_status
ORDER BY row_count DESC;
```

---

# Part 2: Create Index

```sql
CREATE INDEX idx_loan_emi_status
ON loan_emi_demo(emi_status);
```

Why:

> The collections team searches by `EMI_STATUS`, so the index gives Oracle an access path for rare defaulted rows.

---

# Part 3: Gather Stats WITHOUT Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'LOAN_EMI_DEMO',
    method_opt => 'FOR COLUMNS SIZE 1 emi_status'
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
WHERE table_name = 'LOAN_EMI_DEMO'
AND column_name = 'EMI_STATUS';
```

Expected:

```text
EMI_STATUS    NONE
```

Say:

> Oracle has basic stats, but it may not understand that DEFAULTED is much rarer than PAID.

---

# Part 5: Run Defaulted EMI Query

```sql
SELECT *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
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

> Without histogram, Oracle may estimate rows using average distribution across EMI status values.

---

# Part 6: Create Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'LOAN_EMI_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 emi_status'
  );
END;
/
```

Meaning:

> Oracle now learns the real distribution of `EMI_STATUS`.

---

# Part 7: Confirm Histogram Created

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'LOAN_EMI_DEMO'
AND column_name = 'EMI_STATUS';
```

Expected:

```text
EMI_STATUS    FREQUENCY
```

---

# Part 8: Run Same Query Again

```sql
SELECT *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
```

Then:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Now compare:

```text
Before histogram: Oracle may use average estimate
After histogram : Oracle knows DEFAULTED has only 2,000 rows
```

---

# Final DBA Answer

```text
1. The data was skewed because PAID had 90,000 rows, but DEFAULTED had only 2,000 rows.
2. The index was useful because the query filtered on EMI_STATUS and needed rare DEFAULTED rows.
3. The histogram helped Oracle estimate the rare status more accurately instead of assuming even distribution.
```

---

# Final Teaching Line

> Histogram plus a useful index helps Oracle understand rare loan default rows and choose a smarter execution plan.

