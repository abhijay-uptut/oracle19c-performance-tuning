Below is a **3-day intermediate → advanced Oracle SQL & Performance Tuning curriculum** for **DBAs working at a bank in Cambodia**, mapped to the **10 common tuning problems** and Oracle tools: **EXPLAIN PLAN, DBMS_XPLAN, AWR, ADDM, SQL Tuning Advisor, SQL Access Advisor, SQL Plan Management**.

---

# Oracle SQL & Performance Tuning Training

## 3-Day Intermediate to Advanced Curriculum for Bank DBAs

## Training Goal

By the end of this training, participants should be able to:

* Read and explain Oracle execution plans confidently
* Identify expensive SQL using AWR, ADDM, and dynamic performance views
* Diagnose SQL, memory, I/O, locking, and concurrency problems
* Tune high-load SQL queries step-by-step
* Choose the right indexing strategy
* Use SQL Tuning Advisor and SQL Access Advisor
* Manage plan stability using SQL Plan Management
* Build a repeatable tuning checklist for banking workloads

---

# Common Tuning Problems Covered

These 10 tuning problems will be used as real-world lab themes:

1. Inefficient or high-load SQL statements
2. Suboptimal use of Oracle Database by the application
3. Undersized memory structures
4. Concurrency issues
5. I/O issues
6. Database configuration issues
7. Short-lived performance problems
8. Degradation of database performance over time
9. Performance regression after environment changes
10. Locking issues

---

# Suggested Lab Environment

Use one banking-style schema with tables like:

* `CUSTOMERS`
* `ACCOUNTS`
* `TRANSACTIONS`
* `LOANS`
* `BRANCHES`
* `CARDS`
* `PAYMENTS`
* `AUDIT_LOGS`
* `APP_LOGIN_EVENTS`

Recommended data size:

* Customers: 100k+
* Accounts: 200k+
* Transactions: 1M+
* Audit logs: 1M+
* Payments: 500k+

This allows realistic execution plans, full scans, index scans, joins, sort operations, and AWR snapshots.

---

# Day 1 — SQL Tuning Foundation + Execution Plan Mastery

## Day 1 Theme

Before using advanced tools, DBAs must know how to read SQL behavior manually.

Day 1 focuses on:

* Optimizer basics
* Cost, cardinality, selectivity
* Execution plans
* EXPLAIN PLAN vs DBMS_XPLAN
* Common plan mistakes
* High-load SQL diagnosis
* Index basics and function-based index usage

---

## Slot 1 — 9:00 AM to 10:30 AM

## Introduction to SQL Tuning & Oracle Optimizer

### Topics

* What is SQL tuning?
* SQL tuning vs database performance tuning
* Why banking systems become slow
* Oracle query lifecycle:

  * Parse
  * Optimize
  * Execute
  * Fetch
* Oracle Optimizer architecture
* Cost-based optimizer overview
* Important tuning concepts:

  * Cost
  * Cardinality
  * Selectivity
  * Access path
  * Join method
  * Statistics

### Banking Example

A customer statement query is slow during business hours:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
ORDER BY transaction_date DESC;
```

The goal is to understand whether the issue is:

* Bad SQL
* Missing index
* Wrong statistics
* Large sorting
* I/O load
* Application fetching too much data

### Common Tuning Problems Covered

* Inefficient or high-load SQL statements
* Suboptimal use of Oracle Database by the application

### Lab 1: Identify Expensive SQL Pattern

Participants run 3 queries:

1. Query fetching all customer transactions
2. Query using selective customer filter
3. Query using date range filter

They compare:

* Rows returned
* Execution time
* Logical reads
* Physical reads
* Plan shape

### Lab Output

Participants should answer:

* Which query is expensive?
* Is the problem SQL design or database structure?
* What information is missing before tuning?

---

## Slot 2 — 10:45 AM to 12:00 PM

## Execution Plans: EXPLAIN PLAN vs DBMS_XPLAN

### Topics

* What is an execution plan?
* How Oracle chooses access paths
* EXPLAIN PLAN basics
* DBMS_XPLAN basics
* Difference between estimated plan and actual runtime plan
* Reading important plan columns:

  * Operation
  * Name
  * Rows
  * Bytes
  * Cost
  * Time
  * Predicate Information

### Key Plan Operations

* TABLE ACCESS FULL
* INDEX RANGE SCAN
* INDEX UNIQUE SCAN
* NESTED LOOPS
* HASH JOIN
* SORT ORDER BY
* FILTER
* VIEW
* TABLE ACCESS BY INDEX ROWID

### Lab 2: Read and Compare Plans

Run:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Then run actual runtime plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

### Lab Task

Participants compare:

* Estimated rows vs actual rows
* Full table scan vs index scan
* Cost vs actual runtime
* Predicate section

### Common Tuning Problems Covered

* Inefficient SQL
* Performance regression after environment changes
* Short-lived performance problems

### Teaching Point

`EXPLAIN PLAN` is like a map before the journey.
`DBMS_XPLAN.DISPLAY_CURSOR` is like checking what actually happened during the trip.

---

## Slot 3 — 1:00 PM to 2:30 PM

## Indexing Strategies for Banking Workloads

### Topics

* Why indexes improve performance
* When indexes hurt performance
* B-tree indexes
* Composite indexes
* Unique indexes
* Function-based indexes
* Invisible indexes
* Index selectivity
* Index maintenance cost
* Indexes on transaction-heavy tables

### Banking Example

Slow query:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Even if `email` has an index, Oracle may not use it because of `LOWER(email)`.

### Lab 3: Function-Based Index

Step 1: Run slow query.

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Step 2: Check plan.

Step 3: Create function-based index.

```sql
CREATE INDEX idx_customers_lower_email
ON customers (LOWER(email));
```

Step 4: Re-run plan and compare.

### Lab Task

Participants record:

* Before plan
* After plan
* Cost difference
* Access path difference
* Runtime difference

### Common Tuning Problems Covered

* Inefficient SQL statements
* Suboptimal application query patterns
* Degradation over time due to wrong indexing

---

## Slot 4 — 2:45 PM to 5:00 PM

## Common Plan Pitfalls + Day 1 Capstone Lab

### Topics

* Full table scan: bad or acceptable?
* Index range scan vs full scan
* Wrong join order
* Bad cardinality estimate
* Missing statistics
* Sort operations
* Implicit data type conversion
* Functions on indexed columns
* `SELECT *` problem
* Queries without date filters

### Lab 4: Banking SQL Tuning Challenge

Participants get 5 problematic queries:

### Query A: Function on indexed column

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

### Query B: Missing date range

```sql
SELECT *
FROM transactions
WHERE account_id = 1001;
```

### Query C: Implicit conversion

```sql
SELECT *
FROM accounts
WHERE account_number = 1234567890;
```

But `account_number` is stored as VARCHAR2.

### Query D: Bad wildcard search

```sql
SELECT *
FROM customers
WHERE name LIKE '%raj%';
```

### Query E: Large sort

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

### Participant Tasks

For each query:

* Generate plan
* Identify issue
* Suggest fix
* Apply fix if possible
* Compare before and after

### Day 1 Outcome

Participants should now be able to:

* Read execution plans
* Understand access paths
* Identify bad SQL patterns
* Apply basic indexing fixes
* Explain cost, cardinality, and selectivity

---

# Day 2 — Oracle Diagnostic Tools: AWR, ADDM, SQL Tuning Advisor, SQL Access Advisor

## Day 2 Theme

Day 2 moves from single-query tuning to system-level diagnosis.

Focus:

* AWR reports
* ADDM recommendations
* SQL Tuning Advisor
* SQL Access Advisor
* Memory problems
* I/O problems
* Concurrency and short-lived issues

---

## Slot 1 — 9:00 AM to 10:30 AM

## AWR: Automatic Workload Repository

### Topics

* What is AWR?
* Why banks use AWR for performance diagnosis
* Snapshot concept
* Baseline concept
* Workload comparison
* Important AWR sections:

  * DB Time
  * Elapsed Time
  * Load Profile
  * Top Timed Events
  * SQL ordered by Elapsed Time
  * SQL ordered by CPU Time
  * SQL ordered by Gets
  * SQL ordered by Reads
  * Instance Efficiency
  * Wait Events
  * Segment Statistics

### Banking Scenario

At 11 AM, users complain that fund transfers are slow.

DBA needs to answer:

* Was database overloaded?
* Which SQL consumed most DB time?
* Was it CPU, I/O, locking, or memory?
* Which module/user caused the load?

### Lab 5: Generate AWR Snapshot and Report

Steps:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Run heavy workload queries.

Then:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Generate AWR report using:

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

### Lab Task

Participants identify:

* Top 3 SQL by elapsed time
* Top 3 wait events
* SQL with highest buffer gets
* SQL with highest physical reads
* Whether problem is CPU, I/O, or SQL design

### Common Tuning Problems Covered

* High-load SQL
* I/O issues
* Short-lived performance problems
* Performance degradation over time

---

## Slot 2 — 10:45 AM to 12:00 PM

## ADDM: Automatic Database Diagnostic Monitor

### Topics

* What is ADDM?
* Difference between AWR and ADDM
* How ADDM interprets AWR data
* Understanding ADDM findings
* Impact percentage
* Recommendation types:

  * SQL tuning
  * Memory tuning
  * I/O tuning
  * Configuration tuning
  * Segment tuning

### Simple Explanation

AWR is like a medical test report.
ADDM is like the doctor’s diagnosis.

### Lab 6: Run ADDM Report

Run workload between snapshots.

Then generate ADDM report:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

### Lab Task

Participants identify:

* Top ADDM finding
* Estimated impact
* Recommendation
* Whether recommendation is safe to apply
* What extra validation is needed

### Common Tuning Problems Covered

* Undersized memory structures
* I/O issues
* Database configuration issues
* Degradation over time

---

## Slot 3 — 1:00 PM to 2:30 PM

## SQL Tuning Advisor

### Topics

* What is SQL Tuning Advisor?
* When to use it
* SQL Profiles
* Statistics recommendations
* Index recommendations
* Restructuring SQL
* How to validate recommendations before applying
* Risks of blindly accepting advisor output

### Banking Scenario

One loan eligibility query runs for 40 seconds.
The DBA must tune only this SQL without changing the entire application.

### Lab 7: SQL Tuning Advisor

Create tuning task:

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

Execute task:

```sql
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('loan_query_tuning_task');
```

View report:

```sql
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('loan_query_tuning_task')
FROM dual;
```

### Lab Task

Participants evaluate:

* Did advisor suggest index?
* Did advisor suggest SQL Profile?
* Did advisor suggest statistics gathering?
* Is the recommendation safe?
* What should be tested before production?

### Common Tuning Problems Covered

* Inefficient SQL
* Regression after environment changes
* Suboptimal application usage

---

## Slot 4 — 2:45 PM to 5:00 PM

## SQL Access Advisor + Memory/I/O Diagnosis Lab

### Topics

* What is SQL Access Advisor?
* SQL Tuning Advisor vs SQL Access Advisor
* Index recommendations
* Materialized view recommendations
* Partitioning recommendations
* When not to create more indexes
* How indexes impact DML-heavy banking systems

### Lab 8: SQL Access Advisor

Use a workload of multiple banking queries:

* Daily transaction report
* Customer account summary
* Branch-wise transaction volume
* Loan EMI due report

Participants run SQL Access Advisor and evaluate recommendations.

### Additional Mini Lab: Memory and I/O Symptoms

Participants inspect:

```sql
SELECT * FROM v$system_event
ORDER BY time_waited DESC;
```

```sql
SELECT * FROM v$sysstat
WHERE name LIKE '%physical reads%';
```

```sql
SELECT * FROM v$pgastat;
```

```sql
SELECT * FROM v$sgainfo;
```

### Lab Task

Identify whether the issue looks like:

* SQL problem
* Memory pressure
* I/O pressure
* Configuration issue

### Common Tuning Problems Covered

* Undersized memory structures
* I/O issues
* Database configuration issues
* Degradation over time

### Day 2 Outcome

Participants should be able to:

* Generate and read AWR reports
* Use ADDM for diagnosis
* Use SQL Tuning Advisor safely
* Use SQL Access Advisor for workload-level recommendations
* Connect SQL symptoms with system-level bottlenecks

---

# Day 3 — Advanced SQL Tuning, Plan Stability, Concurrency & Real-World Banking Cases

## Day 3 Theme

Day 3 focuses on advanced production problems.

Focus:

* SQL Plan Management
* Plan baselines
* Plan evolution
* Bind peeking
* Adaptive cursor sharing
* Hints
* SQL Profiles
* Locking
* Concurrency
* Performance regression
* Final capstone lab

---

## Slot 1 — 9:00 AM to 10:30 AM

## SQL Plan Management

### Topics

* Why good SQL becomes slow suddenly
* Execution plan regression
* What is SQL Plan Management?
* SQL plan baselines
* Capturing plans
* Accepting plans
* Evolving plans
* When to use plan baselines
* Banking use case: stable plans for critical payment queries

### Banking Scenario

A payment settlement query was fast yesterday but slow today after statistics refresh.

Possible causes:

* New execution plan
* Changed statistics
* Different bind values
* New index
* Optimizer chose bad join method

### Lab 9: Capture and Use SQL Plan Baseline

Participants:

1. Run query with good plan
2. Capture baseline
3. Change statistics/index condition
4. Observe plan change
5. Force stable plan using baseline

Example:

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

View baselines:

```sql
SELECT sql_handle, plan_name, enabled, accepted
FROM dba_sql_plan_baselines;
```

### Common Tuning Problems Covered

* Performance regression after environment changes
* Degradation over time
* Database configuration/statistics issues

---

## Slot 2 — 10:45 AM to 12:00 PM

## Bind Peeking, Adaptive Cursor Sharing, Hints and SQL Profiles

### Topics

* What is bind peeking?
* Why same SQL can behave differently for different customers
* Skewed data problem
* Adaptive cursor sharing
* Histograms
* SQL hints
* SQL Profiles
* Difference between:

  * Hint
  * Baseline
  * SQL Profile
  * Index
* Risks of overusing hints

### Banking Scenario

Same account query:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

For a small branch, index is good.
For a large branch, full scan may be better.

One plan may not fit all values.

### Lab 10: Bind Variable and Skewed Data Lab

Create skewed branch transaction data:

* Branch 1 has 700k transactions
* Branch 2 has 5k transactions
* Branch 3 has 500 transactions

Run same bind query with different values.

Participants inspect:

```sql
SELECT sql_id, child_number, executions, is_bind_sensitive, is_bind_aware
FROM v$sql
WHERE sql_text LIKE '%branch_id%';
```

### Lab Task

Participants identify:

* Bind-sensitive SQL
* Bind-aware SQL
* Different child cursors
* Plan changes
* When histogram helps

### Common Tuning Problems Covered

* Inefficient SQL
* Suboptimal application design
* Regression after data distribution changes
* Degradation over time

---

## Slot 3 — 1:00 PM to 2:30 PM

## Concurrency, Locking and Short-Lived Performance Problems

### Topics

* Difference between concurrency and locking
* Row-level locks
* Blocking sessions
* Deadlocks
* Long-running transactions
* Hot blocks
* Buffer busy waits
* Library cache contention
* Short-lived spikes
* Why banking apps face concurrency problems
* Tools/views:

  * `v$session`
  * `v$lock`
  * `v$locked_object`
  * `dba_blockers`
  * `dba_waiters`
  * ASH if licensed

### Banking Scenario

Multiple users update same account balance during transaction processing.

Example:

```sql
UPDATE accounts
SET balance = balance - 1000
WHERE account_id = 101;
```

Another session waits because the first session has not committed.

### Lab 11: Locking Simulation

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

Now Session 2 waits.

Diagnostic queries:

```sql
SELECT sid, serial#, username, blocking_session, wait_class, event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

```sql
SELECT *
FROM dba_blockers;
```

```sql
SELECT *
FROM dba_waiters;
```

### Lab Task

Participants identify:

* Blocking session
* Waiting session
* Locked object
* SQL causing lock
* Safe resolution steps

### Common Tuning Problems Covered

* Concurrency issues
* Locking issues
* Short-lived performance problems

---

## Slot 4 — 2:45 PM to 5:00 PM

## Final Capstone: End-to-End Banking Performance Tuning Case

### Capstone Scenario

The bank’s core transaction dashboard is slow.

Symptoms:

* Users complain between 10 AM and 12 PM
* Fund transfer report takes 45 seconds
* Login audit table is growing fast
* AWR shows high DB time
* ADDM recommends SQL tuning
* Some sessions are blocked
* Query plan changed after statistics refresh
* I/O wait increased
* One report query does full table scan on 1M+ transactions

Participants must diagnose the issue like a real production DBA.

---

## Capstone Lab Structure

### Part 1: Identify Workload Problem

Use AWR:

* Top timed events
* SQL by elapsed time
* SQL by buffer gets
* SQL by physical reads

### Part 2: Analyze SQL Plan

Use:

```sql
DBMS_XPLAN.DISPLAY_CURSOR
```

Participants identify:

* Full table scan
* Wrong join method
* Missing index
* Bad cardinality
* Expensive sort

### Part 3: Tune SQL

Possible fixes:

* Add composite index
* Add function-based index
* Rewrite query
* Avoid `SELECT *`
* Add date filter
* Gather statistics
* Use SQL Profile
* Create baseline if plan regression happened

### Part 4: Diagnose Locking

Use:

* `v$session`
* `dba_blockers`
* `dba_waiters`
* `v$locked_object`

### Part 5: Validate Improvement

Compare before and after:

* Execution time
* Logical reads
* Physical reads
* Cost
* Plan operation
* AWR snapshot difference

---

# Detailed Mapping: 10 Problems to Labs

| Common Problem                       | Covered In          | Main Lab            |
| ------------------------------------ | ------------------- | ------------------- |
| Inefficient/high-load SQL            | Day 1, Day 2, Day 3 | Labs 1, 4, 5, 7     |
| Suboptimal DB use by app             | Day 1, Day 3        | Labs 3, 4, 10       |
| Undersized memory structures         | Day 2               | Labs 6, 8           |
| Concurrency issues                   | Day 3               | Lab 11              |
| I/O issues                           | Day 2, Day 3        | Labs 5, 8, Capstone |
| DB configuration issues              | Day 2, Day 3        | Labs 6, 8, 9        |
| Short-lived performance problems     | Day 2, Day 3        | Labs 5, 11          |
| Degradation over time                | Day 2, Day 3        | Labs 5, 8, 9        |
| Regression after environment changes | Day 1, Day 3        | Labs 2, 9, 10       |
| Locking issues                       | Day 3               | Lab 11              |

---

# Tool Coverage by Day

| Tool                | Day          | Usage                                            |
| ------------------- | ------------ | ------------------------------------------------ |
| EXPLAIN PLAN        | Day 1        | Estimated plan reading                           |
| DBMS_XPLAN          | Day 1, Day 3 | Actual plan analysis                             |
| AWR                 | Day 2, Day 3 | Workload-level diagnosis                         |
| ADDM                | Day 2        | Automated performance findings                   |
| SQL Tuning Advisor  | Day 2        | Single SQL tuning recommendations                |
| SQL Access Advisor  | Day 2        | Workload/index/materialized view recommendations |
| SQL Plan Management | Day 3        | Plan stability and regression control            |
| V$ Views            | Day 2, Day 3 | Runtime diagnosis, locks, sessions, waits        |

---

# Recommended Final Deliverables for Participants

At the end of training, give them these checklists/templates:

## 1. SQL Tuning Checklist

* Is the SQL returning too many rows?
* Is `SELECT *` used unnecessarily?
* Are filters selective?
* Are functions used on indexed columns?
* Are joins using correct keys?
* Are statistics fresh?
* Is cardinality estimate close to actual rows?
* Is the query doing unnecessary sorting?
* Is the plan using the expected index?
* Is the issue SQL, I/O, memory, or locking?

## 2. AWR Reading Checklist

* Check DB Time
* Check Top Timed Events
* Check SQL ordered by Elapsed Time
* Check SQL ordered by CPU Time
* Check SQL ordered by Buffer Gets
* Check SQL ordered by Physical Reads
* Check Wait Classes
* Check Instance Efficiency
* Check Segment Statistics
* Compare with previous baseline

## 3. Locking Diagnosis Checklist

* Find blocking session
* Find waiting session
* Identify locked object
* Identify SQL text
* Check transaction duration
* Contact application/user if needed
* Kill session only if approved
* Document root cause

## 4. Production Tuning Safety Checklist

Before applying any fix:

* Test in non-production
* Compare before/after plans
* Check DML impact of new indexes
* Avoid blindly accepting advisor recommendations
* Capture baseline for critical SQL
* Monitor after deployment
* Keep rollback plan ready

---

# Final 3-Day Flow Summary

| Day   | Focus                                                         | Outcome                                                  |
| ----- | ------------------------------------------------------------- | -------------------------------------------------------- |
| Day 1 | SQL tuning foundation, optimizer, execution plans, indexing   | Participants can read and tune SQL plans                 |
| Day 2 | AWR, ADDM, SQL Tuning Advisor, SQL Access Advisor             | Participants can diagnose database-level issues          |
| Day 3 | Plan management, bind peeking, concurrency, locking, capstone | Participants can handle advanced production tuning cases |

---

This structure is strong for bank DBAs because it does not only teach theory. It repeatedly connects every topic to real production problems: slow transactions, blocked sessions, bad plans, wrong indexes, high I/O, and sudden regression.
