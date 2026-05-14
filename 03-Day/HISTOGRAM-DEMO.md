Yes — use this as your **banking histogram demo**.

# Demo Story

A bank has a `BANK_TXN_DEMO` table.

Most transactions are successful.

Few transactions fail.

DBA wants to check failed transactions fast.

---

# Part 0: Setup Bank Table

```sql
DROP TABLE bank_txn_demo PURGE;

CREATE TABLE bank_txn_demo AS
SELECT
  LEVEL txn_id,
  CASE
    WHEN LEVEL <= 95000 THEN 'SUCCESS'
    ELSE 'FAILED'
  END txn_status,
  ROUND(DBMS_RANDOM.VALUE(100, 50000), 2) amount
FROM dual
CONNECT BY LEVEL <= 100000;
```

Meaning:

```text
SUCCESS = 95,000 rows
FAILED  = 5,000 rows
```

This is **skewed data**.

---

# Part 1: Create Index

```sql
CREATE INDEX idx_bank_txn_status
ON bank_txn_demo(txn_status);
```

---

# Part 2: Gather Stats WITHOUT Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'BANK_TXN_DEMO',
    method_opt => 'FOR COLUMNS SIZE 1 txn_status'
  );
END;
/
```

`SIZE 1` means:

> No histogram.

---

# Part 3: Confirm Histogram = NONE

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

Expected:

```text
TXN_STATUS    NONE
```

Say:

> Oracle has basic stats, but it does not know SUCCESS is very common and FAILED is rare.

---

# Part 4: Run Failed Transaction Query

```sql
SELECT *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

Then check plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Explain:

> Before histogram, Oracle may estimate rows wrongly because it assumes values are evenly spread.

Check:

```text
E-Rows = estimated rows
A-Rows = actual rows
```

---

# Part 5: Create Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'BANK_TXN_DEMO',
    method_opt => 'FOR COLUMNS SIZE 254 txn_status'
  );
END;
/
```

Meaning:

> Now Oracle learns the real distribution of transaction status.

---

# Part 6: Confirm Histogram Created

```sql
SELECT column_name, histogram
FROM user_tab_col_statistics
WHERE table_name = 'BANK_TXN_DEMO'
AND column_name = 'TXN_STATUS';
```

Expected:

```text
TXN_STATUS    FREQUENCY
```

---

# Part 7: Run Same Query Again

```sql
SELECT *
FROM bank_txn_demo
WHERE txn_status = 'FAILED';
```

Then:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Now compare:

```text
Before histogram: Oracle guessed distribution
After histogram : Oracle knows FAILED is rare
```

---

# Final Teaching Line

> Histogram helps Oracle understand uneven banking data, so it can estimate rows better and choose a smarter execution plan.
