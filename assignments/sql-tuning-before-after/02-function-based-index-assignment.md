# Assignment 2 - Function-Based Customer Search

## Training Link

Day 1: function-based indexes, SQL anti-patterns, and evidence-based plan comparison.

## Scenario

The customer search screen allows case-insensitive name lookup.

The application runs:

```sql
SELECT /* a2_customer_name_search */
       customer_id,
       full_name,
       mobile_no,
       status
FROM a2_customers
WHERE UPPER(full_name) = 'SOK CHAN';
```

The DBA team created a normal index on `FULL_NAME`, but the query is still slow.

Your task is to prove why the normal index may not help and then test the right index.

## Setup

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a2_customers PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a2_customers (
    customer_id   NUMBER PRIMARY KEY,
    full_name     VARCHAR2(100),
    mobile_no     VARCHAR2(30),
    branch_id     NUMBER,
    status        VARCHAR2(20),
    created_date  DATE
);

BEGIN
  FOR i IN 1..180000 LOOP
    INSERT INTO a2_customers VALUES (
      i,
      CASE
        WHEN i IN (101, 50101, 120101) THEN 'Sok Chan'
        WHEN MOD(i,7) = 0 THEN 'Dara Sok'
        WHEN MOD(i,7) = 1 THEN 'Chan Vuthy'
        WHEN MOD(i,7) = 2 THEN 'Srey Mom'
        WHEN MOD(i,7) = 3 THEN 'Piseth Long'
        WHEN MOD(i,7) = 4 THEN 'Bopha Lim'
        WHEN MOD(i,7) = 5 THEN 'Vanna Chea'
        ELSE 'Rithy Heng'
      END,
      '855' || LPAD(i, 9, '0'),
      MOD(i, 80) + 1,
      CASE WHEN MOD(i,20) = 0 THEN 'INACTIVE' ELSE 'ACTIVE' END,
      SYSDATE - MOD(i, 1500)
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

CREATE INDEX idx_a2_customers_name
ON a2_customers(full_name);

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'A2_CUSTOMERS',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## Tasks

1. Run the search SQL with only the normal `FULL_NAME` index available.
2. Capture elapsed time and actual plan.
3. Check whether `IDX_A2_CUSTOMERS_NAME` is used.
4. Explain why `UPPER(full_name)` changes the access path.
5. Create a suitable function-based index.
6. Gather statistics.
7. Run the same SQL again.
8. Compare before and after.

## Comparison Table

| Metric | Before | After |
|---|---:|---:|
| Elapsed time | | |
| Buffer gets | | |
| Disk reads | | |
| Main plan operation | | |
| Index used? | | |
| Estimated rows | | |
| Actual rows | | |

## Final DBA Answer

Write 4-6 lines explaining:

```text
1. Why the normal index was not enough.
2. Which function-based index fixed the access path.
3. Whether buffer gets and time improved.
4. What application coding alternative could avoid this issue.
```

