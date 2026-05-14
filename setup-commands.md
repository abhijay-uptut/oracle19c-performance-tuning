# Solution 2 - Complex Loan EMI Collections Histogram and Index

# Solution Story

The loan EMI table has uneven status values.

Most EMI records are `PAID`.

Only a small number of EMI records are `DEFAULTED`.

The real production issue is more complex:

```text
DEFAULTED, HIGH risk, and LEGAL_ACTION are not independent values.
They usually appear together.
```

The DBA creates indexes, histograms, and column-group statistics so Oracle can estimate both rare values and correlated predicates better.

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

# Part 1: Setup Complex Loan EMI Table

```sql
DROP TABLE loan_emi_demo PURGE;

CREATE TABLE loan_emi_demo AS
WITH base AS (
  SELECT LEVEL rn
  FROM dual
  CONNECT BY LEVEL <= 500000
)
SELECT
  rn emi_id,
  700000 + MOD(rn, 120000) loan_id,
  900000 + MOD(rn, 180000) customer_id,
  100 + MOD(rn, 25) branch_id,
  ADD_MONTHS(DATE '2026-04-01', -MOD(rn, 6)) emi_month,
  CASE
    WHEN rn <= 440000 THEN 'PAID'
    WHEN rn <= 475000 THEN 'DUE'
    WHEN rn <= 493000 THEN 'LATE_1_30'
    WHEN rn <= 498000 THEN 'LATE_31_60'
    ELSE 'DEFAULTED'
  END emi_status,
  CASE
    WHEN rn <= 352000 THEN 'LOW'
    WHEN rn <= 422000 THEN 'MEDIUM'
    WHEN rn <= 440000 THEN 'HIGH'
    WHEN rn <= 450000 THEN 'LOW'
    WHEN rn <= 470000 THEN 'MEDIUM'
    WHEN rn <= 475000 THEN 'HIGH'
    WHEN rn <= 477000 THEN 'LOW'
    WHEN rn <= 487000 THEN 'MEDIUM'
    WHEN rn <= 493000 THEN 'HIGH'
    WHEN rn <= 493250 THEN 'LOW'
    WHEN rn <= 494500 THEN 'MEDIUM'
    WHEN rn <= 498000 THEN 'HIGH'
    WHEN rn <= 498050 THEN 'LOW'
    WHEN rn <= 498300 THEN 'MEDIUM'
    ELSE 'HIGH'
  END risk_band,
  CASE
    WHEN rn <= 430000 THEN 'AUTO_CLEAR'
    WHEN rn <= 440000 THEN 'MANUAL_REVIEW'
    WHEN rn <= 468000 THEN 'AUTO_REMINDER'
    WHEN rn <= 475000 THEN 'MANUAL_REVIEW'
    WHEN rn <= 487000 THEN 'MANUAL_REVIEW'
    WHEN rn <= 493000 THEN 'FIELD_CALL'
    WHEN rn <= 496500 THEN 'FIELD_CALL'
    WHEN rn <= 498000 THEN 'LEGAL_NOTICE'
    WHEN rn <= 498500 THEN 'FIELD_CALL'
    ELSE 'LEGAL_ACTION'
  END collection_stage,
  CASE
    WHEN rn <= 440000 THEN 0
    WHEN rn <= 475000 THEN MOD(rn, 5)
    WHEN rn <= 493000 THEN 1 + MOD(rn, 30)
    WHEN rn <= 498000 THEN 31 + MOD(rn, 30)
    ELSE 61 + MOD(rn, 240)
  END days_past_due,
  ROUND(DBMS_RANDOM.VALUE(1000, 85000), 2) emi_amount,
  CASE
    WHEN rn <= 440000 THEN 0
    WHEN rn <= 475000 THEN ROUND(DBMS_RANDOM.VALUE(1000, 85000), 2)
    WHEN rn <= 493000 THEN ROUND(DBMS_RANDOM.VALUE(5000, 175000), 2)
    WHEN rn <= 498000 THEN ROUND(DBMS_RANDOM.VALUE(15000, 350000), 2)
    ELSE ROUND(DBMS_RANDOM.VALUE(50000, 900000), 2)
  END outstanding_amount
FROM base;
```

Check the status distribution:

```sql
SELECT emi_status, COUNT(*) row_count
FROM loan_emi_demo
GROUP BY emi_status
ORDER BY row_count DESC;
```

Expected:

```text
PAID          440000
DUE            35000
LATE_1_30      18000
LATE_31_60      5000
DEFAULTED       2000
```

Check the correlated queue:

```sql
SELECT emi_status, risk_band, collection_stage, COUNT(*) row_count
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
GROUP BY emi_status, risk_band, collection_stage
ORDER BY row_count DESC;
```

Expected learning:

```text
DEFAULTED HIGH   LEGAL_ACTION    1500
DEFAULTED MEDIUM FIELD_CALL       250
DEFAULTED HIGH   FIELD_CALL       200
DEFAULTED LOW    FIELD_CALL        50
```

---

# Part 2: Create Indexes

```sql
CREATE INDEX idx_loan_emi_status
ON loan_emi_demo(emi_status);

CREATE INDEX idx_loan_emi_coll_q
ON loan_emi_demo(emi_status, risk_band, collection_stage);
```

Why:

> The simple index supports status-only searches. The composite index supports the collections queue filter.

---

# Part 3: Gather Stats WITHOUT Histograms

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'LOAN_EMI_DEMO',
    method_opt => 'FOR ALL COLUMNS SIZE 1'
  );
END;
/
```

`SIZE 1` means:

> No histograms.

---

# Part 4: Confirm Histograms = NONE

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'LOAN_EMI_DEMO'
AND column_name IN ('EMI_STATUS', 'RISK_BAND', 'COLLECTION_STAGE')
ORDER BY column_name;
```

Expected:

```text
COLLECTION_STAGE    NONE
EMI_STATUS          NONE
RISK_BAND           NONE
```

Say:

> Oracle has basic number-of-distinct-values stats, but it does not know which values are common and which values are rare.

---

# Part 5: Run Rare Status Query

```sql
SELECT /* rare_status_no_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
```

Then check plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Check:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

Expected learning:

> Without a histogram, Oracle may estimate by average status distribution. With 5 statuses and 500,000 rows, the average is about 100,000 rows per status, even though DEFAULTED has only 2,000 rows.

---

# Part 6: Run Complex Collections Queue Query

```sql
SELECT /* queue_no_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Then:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected actual rows:

```text
1,500 rows
```

Expected learning:

> The composite index gives Oracle a useful access path, but the row estimate can still be wrong because the three predicates are not independent.

---

# Part 7: Create Histograms

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'LOAN_EMI_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 emi_status, risk_band, collection_stage'
  );
END;
/
```

Meaning:

> Oracle now learns the value distribution for each skewed column.

---

# Part 8: Confirm Histograms Created

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'LOAN_EMI_DEMO'
AND column_name IN ('EMI_STATUS', 'RISK_BAND', 'COLLECTION_STAGE')
ORDER BY column_name;
```

Expected:

```text
COLLECTION_STAGE    FREQUENCY
EMI_STATUS          FREQUENCY
RISK_BAND           FREQUENCY
```

---

# Part 9: Re-run Both Queries

Rare status query:

```sql
SELECT /* rare_status_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED';
```

Plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected learning:

> The estimate for `EMI_STATUS = 'DEFAULTED'` should move much closer to 2,000 rows.

Complex queue query:

```sql
SELECT /* queue_hist */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected learning:

> Individual histograms know the skew of each column, but Oracle may still combine selectivities as if the columns are independent.

That assumption is weak here because:

```text
LEGAL_ACTION is strongly connected to DEFAULTED.
HIGH risk is strongly connected to DEFAULTED.
```

---

# Part 10: Add Column-Group Statistics

Create the column-group extension:

```sql
SELECT DBMS_STATS.CREATE_EXTENDED_STATS(
  ownname   => USER,
  tabname   => 'LOAN_EMI_DEMO',
  extension => '(emi_status,risk_band,collection_stage)'
) extension_name
FROM dual;
```

Gather statistics again:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'LOAN_EMI_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 emi_status, risk_band, collection_stage'
  );
END;
/
```

Confirm the extension:

```sql
SELECT extension_name, extension
FROM user_stat_extensions
WHERE table_name = 'LOAN_EMI_DEMO';
```

Expected:

```text
(EMI_STATUS,RISK_BAND,COLLECTION_STAGE)
```

---

# Part 11: Re-run Complex Queue Query

```sql
SELECT /* queue_group_stats */ *
FROM loan_emi_demo
WHERE emi_status = 'DEFAULTED'
AND risk_band = 'HIGH'
AND collection_stage = 'LEGAL_ACTION';
```

Then:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Compare:

```text
No histogram         : Oracle knows only basic NDV averages
Individual histograms: Oracle knows each column's skew
Column-group stats   : Oracle also knows the combined pattern
```

Expected learning:

> Column-group statistics help Oracle estimate the three-predicate collections queue because the predicates are correlated.

---

# Final DBA Answer

```text
1. EMI_STATUS was skewed because PAID had 440,000 rows, but DEFAULTED had only 2,000 rows.
2. The composite index was useful because the morning queue filters by EMI_STATUS, RISK_BAND, and COLLECTION_STAGE together.
3. Histograms helped the DEFAULTED query because Oracle learned DEFAULTED was rare instead of using average status distribution.
4. Individual histograms could still miss the queue estimate because DEFAULTED, HIGH, and LEGAL_ACTION were correlated, not independent.
5. Column-group statistics helped because Oracle learned the combined distribution of EMI_STATUS, RISK_BAND, and COLLECTION_STAGE.
```

---

# Final Teaching Line

> Histograms fix rare-value estimates, but correlated predicates often need column-group statistics as well.