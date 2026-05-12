Here’s your **training demo flow**.

# SQL Tuning Advisor Demo Flow

## Goal

Show trainees how Oracle can analyze one slow SQL and recommend improvement.

---

## Step 1: Create demo table

```sql
DROP TABLE tune_demo PURGE;

CREATE TABLE tune_demo (
  id NUMBER,
  customer_id NUMBER,
  status VARCHAR2(20),
  amount NUMBER,
  created_at DATE
);
```

Say:

> We are creating a fresh table so the demo is clean and predictable.

---

## Step 2: Insert sample data

```sql
INSERT INTO tune_demo
SELECT
  level,
  MOD(level, 10000),
  CASE 
    WHEN MOD(level, 20) = 0 THEN 'FAILED'
    ELSE 'SUCCESS'
  END,
  ROUND(DBMS_RANDOM.VALUE(100, 50000)),
  SYSDATE - MOD(level, 365)
FROM dual
CONNECT BY level <= 300000;

COMMIT;
```

Say:

> We inserted 300,000 rows. Most rows are SUCCESS, fewer rows are FAILED.

---

## Step 3: Gather table statistics

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TUNE_DEMO'
  );
END;
/
```

Say:

> Statistics help Oracle understand the table size and data distribution.

---

## Step 4: Run the slow SQL

```sql
SET TIMING ON

SELECT COUNT(*)
FROM tune_demo
WHERE LOWER(status) = 'failed';
```

Say:

> This query uses LOWER(status). Because of this function, Oracle may not use a normal index efficiently.

---

## Step 5: Find SQL_ID

```sql
SELECT sql_id, sql_text
FROM v$sql
WHERE UPPER(sql_text) LIKE '%TUNE_DEMO%'
AND UPPER(sql_text) LIKE '%LOWER(STATUS)%'
AND sql_text NOT LIKE '%v$sql%';
```

Say:

> SQL_ID is like a ticket number for this SQL inside Oracle.

Copy the SQL_ID.

Example:

```text
7cmh7p1hx2cbp
```

---

## Step 6: Create SQL Tuning Advisor task

```sql
BEGIN
  DBMS_SQLTUNE.DROP_TUNING_TASK('tune_demo_task');
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/
```

```sql
DECLARE
  l_task_name VARCHAR2(100);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id     => '7cmh7p1hx2cbp',
    scope      => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit => 60,
    task_name  => 'tune_demo_task'
  );

  DBMS_OUTPUT.PUT_LINE('Task created: ' || l_task_name);
END;
/
```

Say:

> Now we are asking Oracle to analyze this specific SQL_ID.

---

## Step 7: Execute tuning task

```sql
BEGIN
  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('tune_demo_task');
END;
/
```

Say:

> Oracle will now check if this SQL can be improved.

---

## Step 8: Read the report

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
SET PAGESIZE 1000

SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('tune_demo_task')
FROM dual;
```

Say:

> The report has three important parts: general info, findings, and explain plans.

---

## Step 9: Explain the recommendation

Point to this part:

```sql
CREATE INDEX ... ON TUNE_DEMO(LOWER("STATUS"));
```

Say:

> Oracle recommends a function-based index because our WHERE condition uses LOWER(status).

---

## Step 10: Explain before vs after plan

Original:

```text
TABLE ACCESS FULL
Cost: 413
```

Say:

> Oracle was scanning the whole table.

New suggested plan:

```text
INDEX FAST FULL SCAN
Cost: 203
```

Say:

> With the index, Oracle scans a smaller structure, so the cost reduces.

Simple line:

> Cost went from 413 to 203, around 50% estimated improvement.

---

## Step 11: Create the recommended index

```sql
CREATE INDEX idx_tune_demo_lower_status
ON tune_demo (LOWER(status));
```

---

## Step 12: Gather stats again

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TUNE_DEMO'
  );
END;
/
```

---

## Step 13: Rerun the query

```sql
SELECT COUNT(*)
FROM tune_demo
WHERE LOWER(status) = 'failed';
```

Say:

> Now Oracle has a better access path.

---