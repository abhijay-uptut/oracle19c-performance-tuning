# Assignment 1 - Customer Transaction Lookup Tuning

## Training Link

Day 1: execution plans, `DBMS_XPLAN`, composite indexes, column order, before/after validation.

## Scenario

The customer support team says the customer statement screen is slow.

The application runs this SQL:

```sql
SELECT /* a1_customer_statement */
       transaction_id,
       customer_id,
       account_id,
       transaction_date,
       amount,
       status
FROM a1_transactions
WHERE customer_id = 1001
ORDER BY transaction_date DESC;
```

Your task is to prove whether a better access path can reduce time and logical reads.

## Setup

Run this setup in your own schema.

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a1_transactions PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a1_transactions (
    transaction_id    NUMBER PRIMARY KEY,
    customer_id       NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    transaction_type  VARCHAR2(20),
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(100)
);

BEGIN
  FOR i IN 1..250000 LOOP
    INSERT INTO a1_transactions VALUES (
      i,
      CASE
        WHEN i <= 25000 THEN 1001
        ELSE MOD(i, 20000) + 1
      END,
      MOD(i, 50000) + 1,
      MOD(i, 80) + 1,
      SYSDATE - MOD(i, 730),
      CASE MOD(i,4)
        WHEN 0 THEN 'DEBIT'
        WHEN 1 THEN 'CREDIT'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'BILLPAY'
      END,
      ROUND(DBMS_RANDOM.VALUE(10, 50000), 2),
      CASE
        WHEN MOD(i,100) < 2 THEN 'FAILED'
        WHEN MOD(i,100) < 8 THEN 'PENDING'
        ELSE 'POSTED'
      END,
      'training row'
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'A1_TRANSACTIONS',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## Validate Data

```sql
SELECT COUNT(*) AS total_rows
FROM a1_transactions;

SELECT customer_id, COUNT(*) AS row_count
FROM a1_transactions
WHERE customer_id = 1001
GROUP BY customer_id;
```

## Tasks

1. Run the customer statement SQL before creating any new index.
2. Capture elapsed time.
3. Capture the actual runtime plan using `DBMS_XPLAN.DISPLAY_CURSOR`.
4. Record the main access path, buffer gets, disk reads, estimated rows, and actual rows.
5. Decide what composite index should support both the filter and the sort.
6. Create the index.
7. Gather table statistics.
8. Run the same SQL again.
9. Complete the before/after comparison table.

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
1. Why the original query was expensive.
2. Which index you created.
3. Why the index column order is correct.
4. Whether elapsed time and buffer gets improved.
5. Whether the index has any write/DML cost.
```

