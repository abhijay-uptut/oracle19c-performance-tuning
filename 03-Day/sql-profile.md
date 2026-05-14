# Banking SQL Profile Demo

## Story

Bank DBA notices this query is slow:

```sql id="vgbs8o"
SELECT COUNT(*)
FROM bank_txn_demo
WHERE LOWER(txn_status) = 'failed';
```

Problem:

* function on column
* optimizer estimates rows badly
* poor execution plan

---

# Step 1: Run slow query

```sql id="g82bfh"
SET TIMING ON;

SELECT COUNT(*)
FROM bank_txn_demo
WHERE LOWER(txn_status) = 'failed';
```

---

# Step 2: Check actual plan

```sql id="1c9af6"
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST'));
```

Teach trainees:

Look for:

* E-Rows
* A-Rows
* buffers
* full table scan

Say:

> Optimizer estimates are inaccurate.

---

# Step 3: Run SQL Tuning Advisor

```sql id="yx9vgs"
DECLARE
  l_task VARCHAR2(100);
BEGIN
  l_task := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_text   => q'[
      SELECT COUNT(*)
      FROM bank_txn_demo
      WHERE LOWER(txn_status) = 'failed'
    ]',
    user_name  => USER,
    task_name  => 'bank_profile_demo',
    time_limit => 60,
    scope      => 'COMPREHENSIVE'
  );

  DBMS_SQLTUNE.EXECUTE_TUNING_TASK('bank_profile_demo');
END;
/
```

---

# Step 4: View recommendation

```sql id="q4d6lh"
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('bank_profile_demo')
FROM dual;
```

Oracle may say:

```text id="9npkwm"
Recommendation: Accept SQL Profile
Estimated benefit: 90%
```

---

# Step 5: Accept SQL Profile

```sql id="4p8g0u"
BEGIN
  DBMS_SQLTUNE.ACCEPT_SQL_PROFILE(
    task_name => 'bank_profile_demo',
    name      => 'bank_txn_sql_profile'
  );
END;
/
```

---

# Step 6: Run query again

```sql id="ltjlwm"
SELECT COUNT(*)
FROM bank_txn_demo
WHERE LOWER(txn_status) = 'failed';
```

---

# Step 7: Check new plan

```sql id="k4q60d"
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +OUTLINE'));
```

You may see:

```text id="9zcqv8"
SQL profile "bank_txn_sql_profile" used for this statement
```

---

# Final Teaching Point

> SQL Profile does not force a plan.
> It helps Oracle estimate and optimize the SQL better.
