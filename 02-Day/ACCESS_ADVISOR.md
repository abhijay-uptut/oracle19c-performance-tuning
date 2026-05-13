Yes — use this as your **Access Advisor demo flow**.

Access Advisor is slightly different:

**SQL Tuning Advisor = improves one SQL**
**Access Advisor = recommends indexes/materialized views for a workload**

Oracle docs say SQL Access Advisor needs a **workload**, usually from SQL cache or SQL Tuning Set. ([Oracle Docs][1])

# SQL Access Advisor Demo Flow

## Step 1: Use same table

Use your existing `TUNE_DEMO`.

```sql
SELECT COUNT(*)
FROM tune_demo
WHERE LOWER(status) = 'failed';
```

Also run:

```sql
SELECT customer_id, COUNT(*)
FROM tune_demo
WHERE status = 'FAILED'
GROUP BY customer_id;
```

Say:

> Now we are creating a small workload, not just one SQL.

---

## Step 2: Create SQL Tuning Set

```sql
BEGIN
  DBMS_SQLTUNE.CREATE_SQLSET(
    sqlset_name => 'access_demo_sts'
  );
END;
/
```

Say:

> SQL Tuning Set is like a basket where we store SQL statements for analysis.

---

## Step 3: Load SQL from cache into STS

```sql
DECLARE
  cur DBMS_SQLTUNE.SQLSET_CURSOR;
BEGIN
  OPEN cur FOR
    SELECT VALUE(p)
    FROM TABLE(
      DBMS_SQLTUNE.SELECT_CURSOR_CACHE(
        'sql_text LIKE ''%tune_demo%'' AND sql_text NOT LIKE ''%DBMS_SQLTUNE%'''
      )
    ) p;

  DBMS_SQLTUNE.LOAD_SQLSET(
    sqlset_name     => 'access_demo_sts',
    populate_cursor => cur
  );
END;
/
```

Say:

> We are taking recently executed `tune_demo` SQL from memory and putting it into the workload basket.

---

## Step 4: Create Access Advisor task

```sql
DECLARE
  task_id NUMBER;
BEGIN
  DBMS_ADVISOR.CREATE_TASK(
    advisor_name => DBMS_ADVISOR.SQLACCESS_ADVISOR,
    task_id      => task_id,
    task_name    => 'access_demo_task'
  );
END;
/
```

Say:

> This creates the advisor task. Think of it as opening a new investigation file.

---

## Step 5: Attach STS to Access Advisor

```sql
BEGIN
  DBMS_ADVISOR.ADD_STS_REF(
    task_name => 'access_demo_task',
    owner_name => USER,
    sts_name => 'access_demo_sts'
  );
END;
/
```

Say:

> Now Access Advisor knows which workload it should study.

---

## Step 6: Execute task

```sql
BEGIN
  DBMS_ADVISOR.EXECUTE_TASK(
    task_name => 'access_demo_task'
  );
END;
/
```

Say:

> Oracle now checks if indexes or materialized views can improve this workload.

---

## Step 7: View report

```sql
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
SET PAGESIZE 1000

SELECT DBMS_ADVISOR.GET_TASK_REPORT(
  'access_demo_task',
  'TEXT',
  'ALL'
) AS report
FROM dual;
```

Say:

> This report gives physical design recommendations.

---

## Step 8: Get executable script

```sql
SELECT DBMS_ADVISOR.GET_TASK_SCRIPT(
  'access_demo_task'
) AS script
FROM dual;
```

Say:

> This gives the actual SQL script Oracle suggests, like CREATE INDEX statements.

---

## Step 9: What to explain to trainees

Say:

> SQL Tuning Advisor looks at one SQL and says: “How can I fix this query?”
> Access Advisor looks at many SQLs and says: “How should I design indexes/materialized views for this workload?”

---

## Cleanup if needed

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
```

Training line:

> Use SQL Tuning Advisor when one SQL is slow. Use Access Advisor when many queries need better indexing strategy.

[1]: https://docs.oracle.com/en/database/oracle/oracle-database/19/tgsql/sql-access-advisor.html?utm_source=chatgpt.com "26 Optimizing Access Paths with SQL Access Advisor"
