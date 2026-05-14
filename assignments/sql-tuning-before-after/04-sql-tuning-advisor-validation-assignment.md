# Assignment 4 - SQL Tuning Advisor Validation

## Training Link

Day 2: SQL Tuning Advisor, safe recommendation validation, invisible indexes, before/after proof.

## Scenario

The application team reports that a customer transaction lookup is slow.

The SQL is:

```sql
SELECT /* a4_sta_customer_txn */
       txn_id,
       customer_id,
       txn_date,
       amount,
       status
FROM a4_customer_txn
WHERE customer_id = 2001
AND txn_date >= ADD_MONTHS(TRUNC(SYSDATE), -12)
ORDER BY txn_date DESC;
```

Your task is to capture the before plan, run SQL Tuning Advisor if privileges allow, and validate the likely recommendation safely using an invisible index.

## Safety Note

SQL Tuning Advisor is an Oracle Tuning Pack feature. Use it only in a licensed training environment.

If advisor privileges are not available, complete the manual validation with invisible indexes.

## Setup

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a4_customer_txn PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a4_customer_txn (
    txn_id      NUMBER PRIMARY KEY,
    customer_id NUMBER,
    account_id  NUMBER,
    branch_id   NUMBER,
    txn_date    DATE,
    amount      NUMBER(12,2),
    status      VARCHAR2(20),
    channel     VARCHAR2(20)
);

BEGIN
  FOR i IN 1..260000 LOOP
    INSERT INTO a4_customer_txn VALUES (
      i,
      CASE
        WHEN i <= 30000 THEN 2001
        ELSE MOD(i, 30000) + 1
      END,
      MOD(i, 60000) + 1,
      MOD(i, 80) + 1,
      SYSDATE - MOD(i, 1000),
      ROUND(DBMS_RANDOM.VALUE(5, 90000), 2),
      CASE
        WHEN MOD(i,100) < 4 THEN 'FAILED'
        WHEN MOD(i,100) < 12 THEN 'PENDING'
        ELSE 'POSTED'
      END,
      CASE MOD(i,4)
        WHEN 0 THEN 'ATM'
        WHEN 1 THEN 'MOBILE'
        WHEN 2 THEN 'BRANCH'
        ELSE 'INTERNET'
      END
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
    tabname => 'A4_CUSTOMER_TXN',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## Tasks

1. Run the tagged SQL once.
2. Find its SQL ID.
3. Capture before elapsed time and actual plan.
4. Run SQL Tuning Advisor for the SQL ID if privileges allow.
5. Record the recommendation type and suggested command.
6. Do not create a visible production index immediately.
7. Create a candidate invisible index.
8. Enable invisible indexes only in your test session.
9. Run the same SQL again.
10. Compare before and after.

## Find SQL ID

```sql
SELECT sql_id, plan_hash_value, executions, buffer_gets, disk_reads, elapsed_time
FROM v$sql
WHERE sql_text LIKE '%a4_sta_customer_txn%'
AND sql_text NOT LIKE '%v$sql%';
```

## Advisor Skeleton

Replace `&&sql_id` with your SQL ID.

```sql
VARIABLE task_name VARCHAR2(100);

BEGIN
  :task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => '&&sql_id',
    scope       => 'COMPREHENSIVE',
    time_limit  => 60,
    task_name   => 'A4_STA_CUSTOMER_TXN_TASK'
  );
END;
/

EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK(task_name => 'A4_STA_CUSTOMER_TXN_TASK');

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('A4_STA_CUSTOMER_TXN_TASK')
FROM dual;
```

## Comparison Table

| Metric | Before | After |
|---|---:|---:|
| SQL ID | | |
| Elapsed time | | |
| Buffer gets | | |
| Disk reads | | |
| Main plan operation | | |
| Index used? | | |
| Advisor recommendation | | |

## Final DBA Answer

Write 5-7 lines explaining whether the advisor recommendation was valid and whether the invisible-index test proved improvement.

