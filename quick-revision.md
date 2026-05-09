Yes — don’t try to “master Oracle tuning” in 5 hours.
Your goal is to become **delivery-ready**: know the story, commands, expected outputs, and what to say when something differs.

Here’s your crash plan.

# Your Priority Order

## Must Know First

1. **Execution plans**
2. **Indexes**
3. **AWR**
4. **ADDM**
5. **SQL Tuning Advisor**
6. **SQL Plan Management**
7. **Bind peeking / adaptive cursor sharing**
8. **Locking diagnosis**

Everything else is supporting knowledge.

---

# 5-Hour Study Plan Before Flight

## Hour 1 — SQL Tuning Foundation + Execution Plans

Study:

* Parse → Optimize → Execute → Fetch
* Cost, cardinality, selectivity
* Full table scan vs index scan
* `EXPLAIN PLAN`
* `DBMS_XPLAN.DISPLAY`
* `DBMS_XPLAN.DISPLAY_CURSOR`

Practice these commands:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

Must understand:

* `E-Rows` = Oracle estimate
* `A-Rows` = actual rows
* `Cost` ≠ time
* `Buffers` = logical reads
* `Reads` = physical reads
* `access` predicate is better than only `filter`

---

## Hour 2 — Indexing

Study:

* B-tree index
* Composite index
* Unique index
* Function-based index
* Invisible index
* Selectivity
* DML cost of indexes

Must practice:

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

Before/after query:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Your core explanation:

> Index must match the query pattern. If SQL uses `LOWER(email)`, normal `email` index may not help. Function-based index supports that expression.

Must remember:

* Too many indexes slow inserts/updates/deletes
* Index scan is not always good
* Full table scan is not always bad

---

## Hour 3 — AWR + ADDM

Study only the important sections.

### AWR must-know

AWR = historical performance report between snapshots.

Commands:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

AWR sections to explain:

* DB Time
* Elapsed Time
* Top Timed Events
* SQL ordered by Elapsed Time
* SQL ordered by CPU Time
* SQL ordered by Gets
* SQL ordered by Reads
* Segment Statistics

Your explanation:

> AWR tells us what happened in the database during a time window.

### ADDM must-know

ADDM = diagnosis based on AWR.

Command:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

Your explanation:

> AWR is the medical report. ADDM is the doctor’s diagnosis.

Must know:

* Finding
* Impact %
* Recommendation
* Validate before applying

---

## Hour 4 — SQL Tuning Advisor + SQL Access Advisor

### SQL Tuning Advisor

Used for **one SQL**.

Know this flow:

```sql
DECLARE
  l_task_name VARCHAR2(100);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => 'your_sql_id',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'loan_query_tuning_task'
  );
END;
/
```

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('loan_query_tuning_task');
```

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('loan_query_tuning_task')
FROM dual;
```

Recommendations it may give:

* SQL Profile
* Index
* Statistics
* SQL rewrite

Core warning:

> Advisor gives suggestions, not final decisions.

### SQL Access Advisor

Used for **workload/multiple SQLs**.

Understand conceptually:

* Recommends indexes
* Materialized views
* Partitioning
* Useful for reports/dashboards

You don’t need to master every package command. Just explain the purpose clearly.

---

## Hour 5 — Day 3 Advanced Topics

Study these in simple terms.

### SQL Plan Management

Problem:

> SQL was fast yesterday, slow today, because plan changed.

Baseline = approved plan.

Command:

```sql
DECLARE
  l_plans_loaded PLS_INTEGER;
BEGIN
  l_plans_loaded := DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(
    sql_id => 'your_sql_id'
  );
END;
/
```

```sql
SELECT sql_handle, plan_name, enabled, accepted
FROM dba_sql_plan_baselines;
```

Core line:

> SPM is not mainly for making SQL faster. It is for keeping critical SQL stable.

---

### Bind Peeking

Problem:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

Branch 1 has 700k rows.
Branch 3 has 500 rows.

One plan may not fit both.

Know:

* Bind peeking = Oracle checks bind value during hard parse
* Skewed data = uneven distribution
* Adaptive cursor sharing = Oracle may create different child cursors
* Histogram = helps Oracle understand skew

View:

```sql
SELECT sql_id, child_number, executions, is_bind_sensitive, is_bind_aware
FROM v$sql
WHERE sql_text LIKE '%branch_id%';
```

---

### Locking

Must know this perfectly.

Session 1:

```sql
UPDATE accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

Do not commit.

Session 2:

```sql
UPDATE accounts
SET balance = balance + 1000
WHERE account_id = 101;
```

Session 2 waits.

Diagnosis:

```sql
SELECT sid, serial#, username, blocking_session, wait_class, event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

```sql
SELECT * FROM dba_blockers;
```

```sql
SELECT * FROM dba_waiters;
```

Core line:

> If a query is slow, ask: is it working slowly, or is it waiting?

---

# 6-Hour Flight Study Plan

Do not code on the flight. Use it for mental rehearsal.

## Flight Hour 1

Read Day 1 slides aloud mentally.

Focus on:

* Optimizer
* Execution plans
* Indexes
* Capstone issues

## Flight Hour 2

Memorize plan operations:

* `TABLE ACCESS FULL`
* `INDEX RANGE SCAN`
* `INDEX UNIQUE SCAN`
* `TABLE ACCESS BY INDEX ROWID`
* `NESTED LOOPS`
* `HASH JOIN`
* `SORT ORDER BY`
* `FILTER`

## Flight Hour 3

Read Day 2 flow:

```text
User complaint
↓
AWR
↓
ADDM
↓
SQL Tuning Advisor
↓
SQL Access Advisor
↓
Memory/I/O views
```

## Flight Hour 4

Read Day 3 flow:

```text
Plan changed → SPM
Different bind values → ACS/histogram
Sessions waiting → locking views
```

## Flight Hour 5

Practice explaining each tool in 30 seconds:

* AWR
* ADDM
* SQL Tuning Advisor
* SQL Access Advisor
* SQL Plan Management
* SQL Profile
* Histogram
* Locking views

## Flight Hour 6

Rehearse labs:

* What command you run
* What output you expect
* What you will say if output differs

Use this line if lab output differs:

> “Oracle optimizer behavior can vary depending on data volume, statistics, version, and environment. The important learning here is the diagnosis process.”

---

# Your Emergency Cheat Sheet

## AWR

> What happened during this time window?

## ADDM

> What does Oracle think is the main problem?

## SQL Tuning Advisor

> How can we tune this one SQL?

## SQL Access Advisor

> What access structures can improve this workload?

## DBMS_XPLAN

> What plan did Oracle use?

## SQL Plan Baseline

> How do we keep a good plan stable?

## SQL Profile

> How do we give optimizer better information?

## Histogram

> How does Oracle understand skewed data?

## Locking views

> Who is blocking whom?

---

# What You Must Not Say

Avoid saying:

* “Full table scan is always bad”
* “Index scan is always good”
* “Cost means seconds”
* “ADDM recommendation should be directly applied”
* “Create index for every slow query”
* “Inactive session is harmless”
* “AWR fixes performance”

Say instead:

> “We validate with evidence.”

That one line will protect you in the training.
