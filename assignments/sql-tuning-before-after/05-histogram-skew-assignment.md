# Assignment 5 - Histogram and Skewed Data Tuning

## Training Link

Day 3: histograms, skewed data, optimizer estimates, and plan quality.

## Scenario

Most card authorizations are approved. Very few are held for fraud review.

The fraud operations team runs:

```sql
SELECT /* a5_fraud_review_queue */
       auth_id,
       card_id,
       merchant_id,
       auth_amount,
       auth_status
FROM a5_card_auth
WHERE auth_status = 'FRAUD_REVIEW';
```

Your task is to prove whether a histogram helps Oracle estimate rare values more accurately.

## Setup

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a5_card_auth PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a5_card_auth (
    auth_id      NUMBER PRIMARY KEY,
    card_id      NUMBER,
    merchant_id  NUMBER,
    auth_amount  NUMBER(12,2),
    auth_status  VARCHAR2(30),
    auth_time    DATE
);

BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO a5_card_auth VALUES (
      i,
      MOD(i, 30000) + 1,
      MOD(i, 5000) + 1,
      ROUND(DBMS_RANDOM.VALUE(1, 250000), 2),
      CASE
        WHEN i <= 96000 THEN 'APPROVED'
        WHEN i <= 99000 THEN 'DECLINED'
        ELSE 'FRAUD_REVIEW'
      END,
      SYSDATE - MOD(i, 365)
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

CREATE INDEX idx_a5_card_auth_status
ON a5_card_auth(auth_status);
```

## Validate Data Skew

```sql
SELECT auth_status, COUNT(*) AS row_count
FROM a5_card_auth
GROUP BY auth_status
ORDER BY auth_status;
```

Expected distribution:

```text
APPROVED      96000
DECLINED       3000
FRAUD_REVIEW   1000
```

## Tasks

1. Gather statistics without a histogram.
2. Confirm histogram is `NONE`.
3. Run the fraud review SQL.
4. Capture elapsed time and actual plan.
5. Compare estimated rows and actual rows.
6. Gather statistics with a histogram.
7. Confirm histogram is created.
8. Run the same SQL again.
9. Compare estimated rows, actual rows, plan, and elapsed time.

## Gather Stats Without Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A5_CARD_AUTH',
    cascade    => TRUE,
    method_opt => 'FOR COLUMNS SIZE 1 auth_status'
  );
END;
/
```

Confirm:

```sql
SELECT column_name, histogram, num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A5_CARD_AUTH'
AND column_name = 'AUTH_STATUS';
```

## Gather Stats With Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'A5_CARD_AUTH',
    cascade    => TRUE,
    method_opt => 'FOR COLUMNS SIZE 254 auth_status'
  );
END;
/
```

Confirm:

```sql
SELECT column_name, histogram, num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'A5_CARD_AUTH'
AND column_name = 'AUTH_STATUS';
```

## Comparison Table

| Metric | Before Histogram | After Histogram |
|---|---:|---:|
| Elapsed time | | |
| Buffer gets | | |
| Disk reads | | |
| Main plan operation | | |
| Index used? | | |
| Estimated rows | | |
| Actual rows | | |
| Histogram type | | |

## Final DBA Answer

Write 4-6 lines explaining:

```text
1. Why AUTH_STATUS is skewed.
2. Why an index on AUTH_STATUS may help rare values.
3. Why the histogram helps estimates.
4. Whether elapsed time improved or the main improvement was estimate accuracy.
```

