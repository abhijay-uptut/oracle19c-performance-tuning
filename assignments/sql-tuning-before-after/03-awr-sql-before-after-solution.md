# Solution 3 - AWR SQL Before/After Comparison

## Expected Problem

The dashboard filters by:

```text
BRANCH_ID
TXN_DATE
```

Before tuning, Oracle may scan many rows for Branch 10 and then group the result.

## Before Workload

Take snapshot 1:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Run the workload 20 times:

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

Take snapshot 2:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Find the SQL ID:

```sql
SELECT sql_id, plan_hash_value, executions, buffer_gets, disk_reads, elapsed_time
FROM v$sql
WHERE sql_text LIKE '%a3_branch_dashboard%'
AND sql_text NOT LIKE '%v$sql%';
```

## Tuning Change

```sql
CREATE INDEX idx_a3_branch_txn_bdate_status
ON a3_branch_txn(branch_id, txn_date, status);

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

## After Workload

Run the same workload 20 times:

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

Take snapshot 3:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Generate the AWR SQL report:

```sql
@?/rdbms/admin/awrsqrpt.sql
```

Use:

```text
Before window: snapshot 1 to snapshot 2
After window : snapshot 2 to snapshot 3
SQL ID       : SQL ID from V$SQL
```

## Expected After Observations

```text
INDEX RANGE SCAN on IDX_A3_BRANCH_TXN_BDATE_STATUS
Lower buffer gets per execution
Lower elapsed time per execution
Possibly same SQL ID with different plan hash value
```

## DBA Conclusion Example

```text
The branch dashboard SQL was expensive because it filtered Branch 10 and six months of data without a supporting access path.
The index on (BRANCH_ID, TXN_DATE, STATUS) reduced the scanned rows before grouping.
AWR SQL evidence should show lower elapsed time per execution and lower buffer gets per execution in the after window.
The index has DML cost, so it should be approved only if this dashboard is frequent or business-critical.
```

