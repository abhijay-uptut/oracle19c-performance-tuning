Here's your **training demo flow**.

# SQL Access Advisor Demo Flow

## Goal

Show trainees how Oracle can analyze a workload and recommend physical access structures such as indexes or materialized views.

Simple comparison:

```text
SQL Tuning Advisor  = improves one SQL statement
SQL Access Advisor  = improves access paths for a workload
```

Prerequisite:

> Run this as a user with permission to use `DBMS_ADVISOR` and SQL Tuning Sets.

---

## Step 1: Create demo table

```sql
DROP TABLE access_demo PURGE;

CREATE TABLE access_demo (
  id NUMBER,
  customer_id NUMBER,
  status VARCHAR2(20),
  amount NUMBER,
  created_at DATE,
  region VARCHAR2(20)
);
```

Say:

> We are creating a fresh table so the Access Advisor demo is clean and predictable.

---

## Step 2: Insert sample data

```sql
INSERT INTO access_demo
SELECT
  level,
  MOD(level, 10000),
  CASE
    WHEN MOD(level, 20) = 0 THEN 'FAILED'
    WHEN MOD(level, 5) = 0 THEN 'PENDING'
    ELSE 'SUCCESS'
  END,
  ROUND(DBMS_RANDOM.VALUE(100, 50000)),
  SYSDATE - MOD(level, 365),
  CASE
    WHEN MOD(level, 4) = 0 THEN 'NORTH'
    WHEN MOD(level, 4) = 1 THEN 'SOUTH'
    WHEN MOD(level, 4) = 2 THEN 'EAST'
    ELSE 'WEST'
  END
FROM dual
CONNECT BY level <= 300000;

COMMIT;
```

Say:

> We inserted 300,000 rows. The data has repeated values in status, customer, date, and region so Oracle has useful access-path choices to evaluate.

---

## Step 3: Gather table statistics

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ACCESS_DEMO'
  );
END;
/
```

Say:

> Statistics help Oracle understand the table size and data distribution before the advisor analyzes the workload.

---

## Step 4: Run workload SQL

```sql
SET TIMING ON

SELECT COUNT(*)
FROM access_demo
WHERE status = 'FAILED';

SELECT customer_id, COUNT(*)
FROM access_demo
WHERE status = 'FAILED'
GROUP BY customer_id;

SELECT region, SUM(amount)
FROM access_demo
WHERE created_at >= SYSDATE - 30
GROUP BY region;

SELECT customer_id, SUM(amount)
FROM access_demo
WHERE region = 'NORTH'
AND status = 'SUCCESS'
GROUP BY customer_id;
```

Say:

> SQL Access Advisor does not just study one SQL. We are creating a small workload with several queries that represent how the application uses the table.

---

## Step 5: Create SQL Tuning Set

```sql
BEGIN
  DBMS_SQLTUNE.DROP_SQLSET('access_demo_sts');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SQLTUNE.CREATE_SQLSET(
    sqlset_name => 'access_demo_sts',
    description => 'Workload for SQL Access Advisor demo'
  );
END;
/
```

Say:

> A SQL Tuning Set is like a basket where we store SQL statements for analysis.

---

## Step 6: Load SQL from cursor cache into STS

```sql
DECLARE
  l_cursor DBMS_SQLTUNE.SQLSET_CURSOR;
BEGIN
  OPEN l_cursor FOR
    SELECT VALUE(p)
    FROM TABLE(
      DBMS_SQLTUNE.SELECT_CURSOR_CACHE(
        basic_filter => q'[
          UPPER(sql_text) LIKE '%ACCESS_DEMO%'
          AND UPPER(sql_text) NOT LIKE '%DBMS_SQLTUNE%'
          AND UPPER(sql_text) NOT LIKE '%DBMS_ADVISOR%'
          AND UPPER(sql_text) NOT LIKE '%V$SQL%'
        ]'
      )
    ) p;

  DBMS_SQLTUNE.LOAD_SQLSET(
    sqlset_name     => 'access_demo_sts',
    populate_cursor => l_cursor
  );
END;
/
```

Say:

> We are taking recently executed ACCESS_DEMO SQL from memory and putting it into the workload basket.

---

## Step 7: Confirm workload was captured

```sql
SELECT sql_id, executions, sql_text
FROM TABLE(DBMS_SQLTUNE.SELECT_SQLSET('access_demo_sts'));
```

Say:

> This confirms which SQL statements are inside the SQL Tuning Set.

If this returns no rows, rerun the workload SQL from Step 4 and then rerun Step 6.

---

## Step 8: Create SQL Access Advisor task

```sql
BEGIN
  DBMS_ADVISOR.DELETE_TASK('access_demo_task');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_ADVISOR.CREATE_TASK(
    advisor_name => DBMS_ADVISOR.SQLACCESS_ADVISOR,
    task_name    => 'access_demo_task',
    task_desc    => 'SQL Access Advisor demo task'
  );
END;
/
```

Say:

> This creates the advisor task. Think of it as opening a new investigation file.

---

## Step 9: Attach STS to Access Advisor

```sql
BEGIN
  DBMS_ADVISOR.ADD_STS_REF(
    task_name     => 'access_demo_task',
    sts_owner     => USER,
    workload_name => 'access_demo_sts'
  );
END;
/
```

Say:

> Now SQL Access Advisor knows which workload it should study.

---

## Step 10: Set advisor options

```sql
BEGIN
  DBMS_ADVISOR.SET_TASK_PARAMETER(
    task_name => 'access_demo_task',
    parameter => 'ANALYSIS_SCOPE',
    value     => 'ALL'
  );

  DBMS_ADVISOR.SET_TASK_PARAMETER(
    task_name => 'access_demo_task',
    parameter => 'MODE',
    value     => 'COMPREHENSIVE'
  );
END;
/
```

Say:

> We are asking Oracle to do a comprehensive analysis and consider all available access recommendations.

---

## Step 11: Execute advisor task

```sql
BEGIN
  DBMS_ADVISOR.EXECUTE_TASK(
    task_name => 'access_demo_task'
  );
END;
/
```

Say:

> Oracle now checks whether indexes, materialized views, or other access structures can improve this workload.

---

## Step 12: Read the report

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
SET PAGESIZE 1000

SELECT DBMS_ADVISOR.GET_TASK_REPORT(
  'access_demo_task',
  'TEXT',
  'ALL',
  'ALL'
) AS report
FROM dual;
```

Say:

> The report shows findings, recommendations, estimated benefit, and the SQL statements affected by each recommendation.

---

## Step 13: Get executable recommendation script

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
SET PAGESIZE 1000

SELECT DBMS_ADVISOR.GET_TASK_SCRIPT('access_demo_task') AS script
FROM dual;
```

Say:

> This gives the actual SQL script Oracle suggests, such as CREATE INDEX or CREATE MATERIALIZED VIEW statements.

Important training point:

> Do not blindly run the script in production. Review the object names, storage impact, DML overhead, and maintenance cost first.

---

## Step 14: Explain a typical recommendation

Point to a recommendation like:

```sql
CREATE INDEX ...
ON ACCESS_DEMO(...);
```

Say:

> Oracle is recommending an access path because several workload statements filter, group, or aggregate by these columns.

Then compare:

```text
Before: Queries may need full table scans.
After:  Oracle may use an index or materialized view to reach the needed rows faster.
```

Simple line:

> Access Advisor is not fixing SQL syntax. It is recommending better physical design for the workload.

---

## Step 15: Optional manual test

If the recommendation is a simple index, create it manually after reviewing the script.

Example only:

```sql
CREATE INDEX idx_access_demo_status
ON access_demo(status);
```

Then gather statistics again:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ACCESS_DEMO'
  );
END;
/
```

Rerun one workload query:

```sql
SELECT COUNT(*)
FROM access_demo
WHERE status = 'FAILED';
```

Say:

> Now Oracle has a better access path available for this part of the workload.

---

## Step 16: Cleanup

```sql
BEGIN
  DBMS_ADVISOR.DELETE_TASK('access_demo_task');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

BEGIN
  DBMS_SQLTUNE.DROP_SQLSET('access_demo_sts');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

DROP TABLE access_demo PURGE;
```

Say:

> Cleanup removes the advisor task, the SQL Tuning Set, and the demo table.

---

## Final teaching line

```text
Use SQL Tuning Advisor when one SQL is slow.
Use SQL Access Advisor when a workload needs a better indexing or materialized view strategy.
```
