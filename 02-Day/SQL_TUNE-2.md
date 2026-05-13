# Assignment: ADDM + SQL Tuning Advisor Demo Flow

## Goal

Show trainees this flow:

```text
Bad SQL
↓
AWR snapshots
↓
ADDM report
↓
Find SQL_ID manually
↓
SQL Tuning Advisor
↓
Apply index fix
```

---

## Step 1: Take first AWR snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Say:

> This is our starting point.

---

## Step 2: Create demo table

```sql
DROP TABLE addm_demo PURGE;

CREATE TABLE addm_demo (
  id NUMBER,
  customer_id NUMBER,
  amount NUMBER,
  created_at DATE
);
```

Say:

> We are creating a clean table for the demo.

---

## Step 3: Insert sample data

```sql
INSERT INTO addm_demo
SELECT
  level,
  MOD(level, 10000),
  ROUND(DBMS_RANDOM.VALUE(100, 50000)),
  SYSDATE - MOD(level, 365)
FROM dual
CONNECT BY level <= 300000;

COMMIT;
```

Say:

> We inserted 300,000 rows with many customer IDs.

---

## Step 4: Gather stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ADDM_DEMO'
  );
END;
/
```

Say:

> Stats help Oracle understand table size and data distribution.

---

## Step 5: Run bad SQL workload

```sql
SET TIMING ON

SELECT COUNT(*)
FROM addm_demo
WHERE customer_id = 9999;
```

Run this 5–10 times.

Say:

> This query searches by customer_id, but we have no index. Oracle may scan the full table.

---

## Step 6: Take second AWR snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Say:

> Now Oracle has before and after snapshots.

---

## Step 7: Check snapshot IDs

```sql
SELECT snap_id, begin_interval_time, end_interval_time
FROM dba_hist_snapshot
ORDER BY snap_id DESC
FETCH FIRST 5 ROWS ONLY;
```

Say:

> Pick the two snapshots around our workload.

---

## Step 8: Generate ADDM report

```sql
@?/rdbms/admin/addmrpt.sql
```

Example input:

```text
Begin Snapshot Id: 52
End Snapshot Id: 53
Report Name: addm_demo_report.txt
```

Say:

> ADDM analyzes the activity between these snapshots.

---

## Step 9: Read ADDM report

Focus only on:

```text
Activity During the Analysis Period
Findings Section
Recommendations
```

Expected finding:

```text
Finding 1: SQL statements consuming significant database time
Recommendation: Run SQL Tuning Advisor
```

Say:

> ADDM tells us where Oracle noticed the problem.

---

## Step 10: Find SQL_ID manually

```sql
SELECT sql_id,
       executions,
       elapsed_time,
       buffer_gets,
       sql_text
FROM v$sql
WHERE UPPER(sql_text) LIKE '%ADDM_DEMO%'
AND UPPER(sql_text) LIKE '%CUSTOMER_ID = 9999%'
AND sql_text NOT LIKE '%V$SQL%'
ORDER BY last_active_time DESC;
```

Example:

```text
SQL_ID        EXECUTIONS   BUFFER_GETS
abc123xyz     10           900000
```

Say:

> SQL_ID is Oracle’s identifier for this query.

Copy your SQL_ID.

---

## Step 11: Drop old tuning task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('addm_sql_tune_task');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/
```

---

## Step 12: Create SQL Tuning Advisor task

Replace `abc123xyz` with your SQL_ID.

```sql
DECLARE
  l_task VARCHAR2(100);
BEGIN
  l_task := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id     => 'abc123xyz',
    scope      => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit => 60,
    task_name  => 'addm_sql_tune_task'
  );

  DBMS_OUTPUT.PUT_LINE('Task created: ' || l_task);
END;
/
```

Say:

> Now we ask Oracle to analyze this exact SQL.

---

## Step 13: Execute tuning task

```sql
BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('addm_sql_tune_task');
END;
/
```

---

## Step 14: Check task status

```sql
SELECT task_name, status, advisor_name
FROM dba_advisor_tasks
WHERE task_name = 'addm_sql_tune_task';
```

Expected:

```text
COMPLETED
```

---

## Step 15: Read tuning report

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
SET PAGESIZE 1000

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('addm_sql_tune_task')
FROM dual;
```

Say:

> The report shows findings, recommendations, rationale, and execution plans.

---

## Step 16: Expected recommendation

You may see:

```text
Recommendation:
Create index on ADDM_DEMO(CUSTOMER_ID)
```

Say:

> Oracle recommends an index because we filter using customer_id.

---

## Step 17: Apply fix

```sql
CREATE INDEX idx_addm_demo_customer_id
ON addm_demo(customer_id);
```

Say:

> Earlier Oracle scanned the full table. Now it can directly find matching customer_id rows.

---

## Step 18: Gather stats again

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ADDM_DEMO'
  );
END;
/
```

---

## Step 19: Rerun query

```sql
SELECT COUNT(*)
FROM addm_demo
WHERE customer_id = 9999;
```

Say:

> Now compare timing before and after the index.

---

## Final Teaching Summary

```text
AWR = captures database workload
ADDM = explains major performance issues
V$SQL = helps find SQL_ID manually
SQL Tuning Advisor = gives SQL-level recommendation
Index = gives Oracle faster access path
```
