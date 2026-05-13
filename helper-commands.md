Part 1 - Create Dummy Table
Connect as your training user in SQL Developer or SQL*Plus.

Run:

SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE sta_assign_txn PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE sta_assign_txn (
  transaction_id    NUMBER,
  customer_id       NUMBER,
  branch_id         NUMBER,
  txn_date          DATE,
  amount            NUMBER(12,2),
  status            VARCHAR2(20),
  channel           VARCHAR2(20),
  merchant_category VARCHAR2(30)
);

INSERT /*+ APPEND */ INTO sta_assign_txn
SELECT
  level AS transaction_id,
  CASE
    WHEN level <= 25000 THEN 1001
    WHEN MOD(level, 200) = 0 THEN 2002
    ELSE MOD(level, 50000) + 1
  END AS customer_id,
  MOD(level, 80) + 1 AS branch_id,
  TRUNC(SYSDATE) - MOD(level, 730) AS txn_date,
  ROUND(DBMS_RANDOM.VALUE(5, 50000), 2) AS amount,
  CASE
    WHEN MOD(level, 100) < 3 THEN 'FAILED'
    WHEN MOD(level, 100) < 8 THEN 'PENDING'
    WHEN MOD(level, 100) < 12 THEN 'REVERSED'
    ELSE 'POSTED'
  END AS status,
  CASE MOD(level, 4)
    WHEN 0 THEN 'MOBILE'
    WHEN 1 THEN 'ATM'
    WHEN 2 THEN 'BRANCH'
    ELSE 'ONLINE'
  END AS channel,
  CASE MOD(level, 6)
    WHEN 0 THEN 'GROCERY'
    WHEN 1 THEN 'FUEL'
    WHEN 2 THEN 'TRAVEL'
    WHEN 3 THEN 'DINING'
    WHEN 4 THEN 'UTILITIES'
    ELSE 'RETAIL'
  END AS merchant_category
FROM dual
CONNECT BY level <= 300000;

COMMIT;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'STA_ASSIGN_TXN',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/

SELECT COUNT(*) AS row_count
FROM sta_assign_txn;
Expected:

ROW_COUNT = 300000
Important:

Do not create any tuning indexes yet.
Part 2 - Run Four Bad SQL Statements
Enable runtime statistics:

ALTER SESSION SET statistics_level = ALL;
Run SQL 1:

SELECT /* sta_assign_q1_customer */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM sta_assign_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
Run SQL 2:

SELECT /* sta_assign_q2_status_function */
       COUNT(*) AS failed_count
FROM sta_assign_txn
WHERE LOWER(status) = 'failed';
Run SQL 3:

SELECT /* sta_assign_q3_branch_channel */
       branch_id,
       channel,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM sta_assign_txn
WHERE branch_id = 25
AND channel = 'MOBILE'
AND txn_date >= TRUNC(SYSDATE) - 90
GROUP BY branch_id, channel;
Run SQL 4:

SELECT /* sta_assign_q4_amount_range */
       transaction_id,
       customer_id,
       amount,
       txn_date
FROM sta_assign_txn
WHERE amount BETWEEN 49000 AND 50000
ORDER BY amount DESC;
Expected before direction:

The optimizer may use TABLE ACCESS FULL because there are no supporting indexes.
