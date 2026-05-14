# Assignment 3 - AWR SQL Before/After Comparison

## Training Link

Day 2: AWR snapshots, AWR SQL report, SQL ID, and historical before/after evidence.

## Scenario

The branch operations dashboard is slow during business hours.

The dashboard SQL is:

```sql
SELECT /* a3_branch_dashboard */
       branch_id,
       status,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM a3_branch_txn
WHERE branch_id = 10
AND txn_date >= ADD_MONTHS(TRUNC(SYSDATE), -6)
GROUP BY branch_id, status;
```

Your task is to generate enough workload for AWR, compare the SQL before and after indexing, and prove the improvement using an AWR SQL report.

## Safety Note

AWR is an Oracle Diagnostic Pack feature. Use it only in a licensed training environment.

If AWR access is not available, complete the same before/after comparison using `DBMS_XPLAN.DISPLAY_CURSOR`.

## Setup

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE a3_branch_txn PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE a3_branch_txn (
    txn_id      NUMBER PRIMARY KEY,
    branch_id   NUMBER,
    customer_id NUMBER,
    txn_date    DATE,
    amount      NUMBER(12,2),
    status      VARCHAR2(20),
    channel     VARCHAR2(20)
);

BEGIN
  FOR i IN 1..300000 LOOP
    INSERT INTO a3_branch_txn VALUES (
      i,
      CASE
        WHEN i <= 60000 THEN 10
        ELSE MOD(i, 80) + 1
      END,
      MOD(i, 40000) + 1,
      SYSDATE - MOD(i, 900),
      ROUND(DBMS_RANDOM.VALUE(10, 75000), 2),
      CASE
        WHEN MOD(i,100) < 3 THEN 'FAILED'
        WHEN MOD(i,100) < 10 THEN 'PENDING'
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
    tabname => 'A3_BRANCH_TXN',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## Workload SQL

Run this SQL multiple times before and after the index:

```sql
SELECT /* a3_branch_dashboard */
       branch_id,
       status,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM a3_branch_txn
WHERE branch_id = 10
AND txn_date >= ADD_MONTHS(TRUNC(SYSDATE), -6)
GROUP BY branch_id, status;
```

## Tasks

1. Take AWR snapshot 1.
2. Run the workload SQL at least 20 times.
3. Take AWR snapshot 2.
4. Find the SQL ID using the comment tag `a3_branch_dashboard`.
5. Capture the before plan and AWR evidence.
6. Create an index that supports branch and date filtering.
7. Gather statistics.
8. Run the same workload SQL at least 20 times.
9. Take AWR snapshot 3.
10. Generate an AWR SQL report for the SQL ID.
11. Compare before and after.

## Useful SQL

Find the SQL ID:

```sql
SELECT sql_id, plan_hash_value, executions, buffer_gets, disk_reads, elapsed_time
FROM v$sql
WHERE sql_text LIKE '%a3_branch_dashboard%'
AND sql_text NOT LIKE '%v$sql%';
```

Take a snapshot as SYS or a privileged user:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Generate AWR SQL report:

```sql
@?/rdbms/admin/awrsqrpt.sql
```

## Comparison Table

| Metric | Before | After |
|---|---:|---:|
| Snapshot range | | |
| SQL ID | | |
| Plan hash value | | |
| Executions | | |
| Elapsed time per exec | | |
| Buffer gets per exec | | |
| Disk reads per exec | | |
| Main plan operation | | |

## Final DBA Answer

Write 5-7 lines explaining whether AWR proves the tuning change improved the dashboard workload.

