# Day 1 — Slot 1 (FINAL ENTERPRISE VERSION)

## 9:00 AM – 10:30 AM

# SQL Tuning Mindset, Workload Observation & Oracle Optimizer Foundations

---

# PRIMARY OBJECTIVE OF THIS SLOT

By the end of this slot, trainees should:

* think like performance engineers instead of syntax-focused DBAs
* understand how Oracle evaluates SQL
* learn how to investigate SQL before tuning
* identify inefficient workload patterns
* understand optimizer decision basics
* correlate SQL patterns with database work
* learn how DBAs collect evidence from Oracle

---

# SLOT DESIGN PHILOSOPHY

This slot is intentionally:

* investigation-heavy
* demo-driven
* discussion-oriented
* production-focused

NOT:

* certification-style lecture delivery

---

# FINAL TIME STRUCTURE

| Time          | Section                                 |
| ------------- | --------------------------------------- |
| 9:00 – 9:10   | Opening + Production mindset            |
| 9:10 – 9:35   | LIVE Demo: bad workload patterns        |
| 9:35 – 9:50   | Discussion + evidence collection        |
| 9:50 – 10:10  | Oracle optimizer foundations            |
| 10:10 – 10:20 | Optimizer mistake demo                  |
| 10:20 – 10:30 | DBA investigation workflow + transition |

---

# SECTION 1 — OPENING (9:00 – 9:10)

# Slide 1 — Workshop Opening

## Slide Content

# Oracle SQL Tuning Workshop

## Day 1 — Think Before You Tune

```text
Problem → Observe → Measure → Understand → Then Tune
```

---

## Trainer Delivery

“Most production tuning failures happen because teams tune too early.

Someone sees slow SQL and immediately:

* creates indexes,
* adds hints,
* rewrites queries,
* changes parameters.

Sometimes performance improves temporarily.

But in enterprise systems, blind tuning usually creates:

* unstable plans,
* application regressions,
* excessive indexes,
* maintenance overhead,
* inconsistent runtime behavior.

In this workshop, we will approach tuning differently.

We will first learn:

* how to observe workload,
* how Oracle thinks,
* how optimizer decisions happen,
* and how DBAs collect evidence before changing anything.”

---

# Slide 2 — Production Banking Scenario

## Slide Content

## Real Production Complaint

> “Customer statement screen is slow during business hours.”

Possible causes:

* inefficient SQL
* too much data fetched
* stale statistics
* sorting overhead
* concurrency
* disk I/O
* application behavior
* plan instability

---

## Trainer Delivery

“In real banking environments, the complaint is never:

> ‘nested loop join is bad.’

The complaint is:

> ‘screen is slow.’

As DBAs, we must:

* identify workload,
* isolate SQL,
* measure resource usage,
* understand optimizer behavior,
* and THEN decide what to tune.”

---

# SECTION 2 — LIVE DEMO FIRST (9:10 – 9:35)

# IMPORTANT

Do NOT explain optimizer deeply yet.

First:

* create engagement,
* create curiosity,
* create workload comparison.

---

# Slide 3 — Demo Objective

## Slide Content

# Demo Goal

We will compare:

1. Full table workload
2. Customer-filtered workload
3. Time-bound workload

We will measure:

* rows
* timing
* logical reads
* physical reads
* plan shape

---

## Trainer Delivery

“We are not fixing anything yet.

We are only observing workload patterns.

Our question is:

> Which SQL pattern creates more database work?”

---

# LIVE LAB SETUP

# Step 1 — Create Table

```sql
DROP TABLE transactions PURGE;

CREATE TABLE transactions (
    transaction_id    NUMBER PRIMARY KEY,
    customer_id       NUMBER,
    account_id        NUMBER,
    branch_id         NUMBER,
    transaction_date  DATE,
    transaction_type  VARCHAR2(20),
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(200)
);
```

---

# Step 2 — Insert Data

```sql
BEGIN
  FOR i IN 1..300000 LOOP
    INSERT INTO transactions VALUES (
      i,
      MOD(i,5000)+1,
      MOD(i,20000)+1,
      MOD(i,50)+1,
      SYSDATE - MOD(i,730),
      CASE MOD(i,4)
        WHEN 0 THEN 'DEBIT'
        WHEN 1 THEN 'CREDIT'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'ATM'
      END,
      ROUND(DBMS_RANDOM.VALUE(100,100000),2),
      CASE
        WHEN MOD(i,20) = 0 THEN 'FAILED'
        ELSE 'SUCCESS'
      END,
      'Training transaction'
    );

    IF MOD(i,10000)=0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/
```

---

# Step 3 — Gather Statistics

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );
END;
/
```

---

# Step 4 — Enable Runtime Metrics

```sql
SET TIMING ON
SET AUTOTRACE TRACEONLY STATISTICS
```

---

# Slide 4 — Query Pattern 1

## Slide Content

# Query 1 — Broad Workload

```sql
SELECT *
FROM transactions;
```

---

## Trainer Delivery

“This is one of the most dangerous production patterns.

The application asks for everything.

In banking systems, this can become catastrophic under concurrency.”

---

# Run Query

```sql
SELECT *
FROM transactions;
```

OR safer:

```sql
SELECT COUNT(*)
FROM transactions;
```

---

# Ask The Room

Ask:

* “Would this survive in a production banking dashboard?”
* “What resource becomes expensive first?”
* “CPU, memory, I/O, or network?”
* “Would indexing alone solve this?”

---

# Slide 5 — Query Pattern 2

## Slide Content

# Query 2 — Customer-Specific

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

---

## Trainer Delivery

“This is already better.

But better does not necessarily mean efficient.

We still need evidence.”

---

# Run Query

```sql
SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101;
```

---

# Ask The Room

* “How many rows do you expect?”
* “Would Oracle likely prefer index or full scan?”
* “What information is still missing?”

---

# Slide 6 — Query Pattern 3

## Slide Content

# Query 3 — Business-Focused

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE,-3)
ORDER BY transaction_date DESC;
```

---

## Trainer Delivery

“This is closer to real application behavior.

Most banking screens do not need:

* 5 years of history,
* unlimited rows,
* full transaction dump.”

---

# Run Query

```sql
SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE,-3);
```

---

# Ask The Room

* “Did workload reduce?”
* “Did logical reads reduce?”
* “Would sort still matter?”
* “What would happen under 1000 concurrent users?”

---

# Slide 7 — Observation Table

## Slide Content

| Query           | Rows | Timing | Logical Reads | Physical Reads | Observation |
| --------------- | ---- | ------ | ------------- | -------------- | ----------- |
| Full table      |      |        |               |                |             |
| Customer filter |      |        |               |                |             |
| Customer + date |      |        |               |                |             |

---

## Trainer Delivery

“This table is the real starting point of SQL tuning.

Not:

* index creation,
* hints,
* parameter changes.

First:

* observe workload,
* compare resource usage,
* understand business pattern.”

---

# SECTION 3 — HOW DBAs COLLECT EVIDENCE (9:35 – 9:50)

# Slide 8 — How Production DBAs Find Expensive SQL

## Slide Content

# Dynamic Performance Views

Example:

```sql
SELECT sql_id,
       executions,
       ROUND(elapsed_time/1000000,2) AS elapsed_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text,1,80) AS sql_text
FROM v$sql
WHERE LOWER(sql_text) LIKE '%transactions%'
ORDER BY buffer_gets DESC;
```

---

## Trainer Delivery

“Production DBAs do not randomly guess which SQL is slow.

Oracle already records workload information.

Views like:

* V$SQL,
* V$SESSION,
* AWR,
* ASH,

help identify:

* expensive SQL,
* repeated SQL,
* high I/O SQL,
* high CPU SQL.”

---

# Live Demo

Run:

```sql
SELECT sql_id,
       executions,
       elapsed_time,
       buffer_gets
FROM v$sql
WHERE sql_text LIKE '%transactions%';
```

---

# Ask The Room

* “Which metric matters more?”
* “High elapsed time or high executions?”
* “Can a fast query still be dangerous?”

---

# Slide 9 — SQL Tuning vs Database Tuning

## Slide Content

| SQL Tuning      | Database Tuning |
| --------------- | --------------- |
| query-specific  | instance-wide   |
| access paths    | memory          |
| joins           | I/O subsystem   |
| cardinality     | concurrency     |
| indexes         | parameters      |
| execution plans | wait events     |

---

## Trainer Delivery

“One bad SQL can consume 70% of database resources.

But sometimes SQL is fine and the real problem is:

* memory pressure,
* disk latency,
* locking,
* concurrency.

Senior DBAs must separate:

* SQL issue
  vs
* system issue.”

---

# SECTION 4 — OPTIMIZER FOUNDATIONS (9:50 – 10:10)

# IMPORTANT

Keep theory SHORT.

Relate every concept to earlier demo.

---

# Slide 10 — Oracle Query Lifecycle

## Slide Content

```text
SQL
 ↓
Parse
 ↓
Optimize
 ↓
Execute
 ↓
Fetch
```

---

## Trainer Delivery

“Every SQL goes through:

* parse,
* optimize,
* execute,
* fetch.

Performance issues can happen in any stage.”

---

# Slide 11 — Cost-Based Optimizer

## Slide Content

# Oracle Cost-Based Optimizer (CBO)

The optimizer estimates:

* rows
* CPU work
* I/O work
* join cost
* sort cost

Then chooses:

```text
lowest estimated cost plan
```

---

## Trainer Delivery

“The optimizer is Oracle’s decision engine.

It does not know your business.

It depends on statistics and estimates.”

---

# Slide 12 — Cardinality

## Slide Content

# Cardinality

Estimated rows returned.

Example:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

Optimizer estimate:

```text
200 rows
```

---

## Trainer Delivery

“Cardinality is one of the most important tuning concepts.

Wrong row estimates often produce wrong plans.”

---

# Slide 13 — Selectivity

## Slide Content

# Selectivity

How much a condition filters data.

High selectivity:

```sql
WHERE transaction_id = 99999
```

Low selectivity:

```sql
WHERE status='SUCCESS'
```

---

## Trainer Delivery

“Not every filter is useful.

If 95% rows are SUCCESS,
then filtering on SUCCESS may still read most of the table.”

---

# Slide 14 — Statistics

## Slide Content

# Statistics

Optimizer depends on:

* row count
* distinct values
* data distribution
* table size
* index information

Without good statistics:

```text
good SQL can still get bad plans
```

---

## Trainer Delivery

“Statistics are the optimizer’s knowledge base.”

---

# SECTION 5 — CONTROLLED STATISTICS DEMO (10:10 – 10:20)

# Slide 15 — Skewed Data & Histograms

## Slide Content

# Same Data, Different Optimizer Knowledge

```sql
WHERE status='FAILED'
```

vs

```sql
WHERE status='SUCCESS'
```

The table contains skew:

```text
SUCCESS = most rows
FAILED  = few rows
```

---

# Demo Goal

Show that the optimizer can make different decisions when it understands data distribution.

---

# Step 1 — Ensure Status Index Exists

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_STATUS';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_status ON transactions(status)';
  END IF;
END;
/
```

---

# Step 2 — Confirm Data Skew

```sql
SELECT COUNT(*)
FROM transactions
WHERE status='FAILED';
```

Then:

```sql
SELECT COUNT(*)
FROM transactions
WHERE status='SUCCESS';
```

Expected pattern:

```text
FAILED  = small row set
SUCCESS = large row set
```

---

# Step 3 — Gather Stats WITHOUT Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 1 status',
    cascade    => TRUE
  );
END;
/
```

---

# Step 4 — Check Column Statistics

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

Expected:

```text
HISTOGRAM = NONE
```

---

# Step 5 — Generate Plan For Rare Value

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Ask:

* “How many rows does Oracle estimate?”
* “Does Oracle know FAILED is rare?”
* “What assumption is Oracle making?”

---

# Step 6 — Gather Stats WITH Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 254 status',
    cascade    => TRUE
  );
END;
/
```

---

# Step 7 — Check Column Statistics Again

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

Expected:

```text
HISTOGRAM = FREQUENCY
```

---

# Step 8 — Recheck Plan For Rare Value

```sql
EXPLAIN PLAN FOR
SELECT COUNT(*)
FROM transactions
WHERE status='FAILED';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Now compare:

* estimated rows before histogram
* estimated rows after histogram
* access path
* cost

Expected result with 300,000 rows:

```text
Without histogram: Oracle may estimate close to 150,000 rows
With histogram:    Oracle should estimate close to 15,000 rows
```

If you scale the table size, expect the same pattern: without histogram Oracle may estimate around 50% of the table; with histogram Oracle should estimate around 5%.

Trainer note:

The demo succeeds even if the access path does not change. The critical lesson is that E-Rows changed because Oracle received better data distribution information. If the access path also changes, use that as an extra teaching point.

---

# Ask The Room

* “Why can same column behave differently?”
* “Why did better statistics change optimizer knowledge?”
* “Would the status index help both values equally?”
* “Why does selectivity matter?”

---

## Trainer Delivery

“This is where optimizer thinking starts becoming real.

Same column.
Same table.
Same SQL shape.

But different optimizer knowledge.

Without a histogram, Oracle may treat both values as roughly equal.

With a histogram, Oracle can understand that:

* FAILED is rare,
* SUCCESS is common.

That difference affects cardinality estimates, access path decisions, and sometimes the final execution plan.

This is why senior DBAs do not simply ask:

> Are statistics fresh?

They ask:

> Are statistics representative of the data distribution?”

---

# SECTION 6 — DBA THINKING FRAMEWORK (10:20 – 10:30)

# Slide 16 — Before You Tune

## Slide Content

Before changing anything:

* check rows
* check workload
* check execution frequency
* check logical reads
* check physical reads
* check concurrency
* check business requirement
* check plan shape
* check statistics

---

## Trainer Delivery

“A senior DBA does not tune emotionally.

A senior DBA tunes based on evidence.”

---

# Slide 17 — Final Framework

## Slide Content

# Enterprise SQL Tuning Workflow

```text
Problem
 ↓
Observe
 ↓
Measure
 ↓
Understand
 ↓
Validate
 ↓
Then Tune
```

---

## Trainer Delivery

“This mindset will guide the entire workshop.

Tomorrow and Day 3 become much easier once this investigation mindset becomes natural.”

---

# TRANSITION TO SLOT 2

## Next Slot

# Execution Plans & DBMS_XPLAN

We will learn:

* how Oracle actually executes SQL
* full scans vs index scans
* join operations
* estimated vs actual rows
* runtime plan analysis
* plan interpretation techniques


# Day 1 — Slot 2 (FINAL ENTERPRISE VERSION)

## 10:45 AM – 12:00 PM

# Execution Plans, Runtime Plans & Oracle Decision Analysis

---

# PRIMARY OBJECTIVE OF THIS SLOT

By the end of this slot, trainees should be able to:

* read Oracle execution plans confidently
* differentiate estimated plans vs actual runtime behavior
* identify expensive plan operations
* compare optimizer estimates with runtime reality
* understand why plans become inefficient
* analyze Oracle decisions instead of memorizing operations
* begin diagnosing bad plans like production DBAs

---

# SLOT DESIGN PHILOSOPHY

This slot is:

* highly demo-driven
* runtime-focused
* investigation-oriented
* DBA-practical

NOT:

* plan memorization
* certification-style theory
* operation-definition lecture

---

# FINAL TIME STRUCTURE

| Time          | Section                               |
| ------------- | ------------------------------------- |
| 10:45 – 10:55 | Why execution plans matter            |
| 10:55 – 11:15 | LIVE demo: estimated vs actual plan   |
| 11:15 – 11:30 | Reading important plan sections       |
| 11:30 – 11:45 | Runtime mismatch & optimizer mistakes |
| 11:45 – 11:55 | Lab: diagnose plan behavior           |
| 11:55 – 12:00 | Summary + transition                  |

---

# SECTION 1 — WHY EXECUTION PLANS MATTER (10:45 – 10:55)

# Slide 18 — Opening

## Slide Content

# Execution Plans & Runtime Plans

```text id="vlz3k9"
Oracle performance problems are usually decision problems.
```

---

## Trainer Delivery

“In Slot 1, we observed workload patterns.

Now we move into Oracle’s decision engine.

When SQL is slow, we ask:

* What path did Oracle choose?
* Why did Oracle choose it?
* Was the estimate correct?
* Did runtime behavior match expectation?

Execution plans help answer these questions.”

---

# Slide 19 — Real Production Scenario

## Slide Content

## Banking Incident

> “Customer statement query suddenly became slow after weekend deployment.”

Possible causes:

* plan changed
* statistics changed
* data volume changed
* optimizer estimate changed
* access path changed
* bind variable behavior changed

---

## Trainer Delivery

“In production, many SQL issues are not caused by code changes.

Sometimes:

* same SQL,
* same index,
* same table,

but Oracle chooses a different plan.

Understanding execution plans helps us identify:

* what changed,
* why performance changed,
* and whether Oracle made a good decision.”

---

# SECTION 2 — LIVE DEMO FIRST (10:55 – 11:15)

# IMPORTANT

DO NOT begin with definitions.

Start with:

* actual SQL,
* actual plan,
* actual runtime evidence.

---

# Slide 20 — Demo Objective

## Slide Content

# Demo Goal

We will compare:

* estimated execution plan
* actual runtime plan

We will observe:

* access path
* estimated rows
* actual rows
* logical reads
* predicate usage
* optimizer decisions

---

## Trainer Delivery

“The most important skill today is this:

```text id="swxj9d"
What Oracle expected
vs
What actually happened
```

That difference explains many performance issues.”

---

# Demo Setup

Use Slot 1 `transactions` table.

---

# Step 1 — Create Supporting Index

```sql id="84jprf"
CREATE INDEX idx_txn_account
ON transactions(account_id);
```

---

# Step 2 — Gather Stats

```sql id="jlwm85"
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TRANSACTIONS',
    cascade => TRUE
  );
END;
/
```

---

# Step 3 — Enable Runtime Statistics

```sql id="5a48k8"
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

---

# Slide 21 — Query Under Investigation

## Slide Content

```sql id="jlwm7v"
SELECT *
FROM transactions
WHERE account_id = 5001;
```

---

## Trainer Delivery

“This is a realistic banking workload.

A teller application,
customer dashboard,
fraud engine,
or backend service

may repeatedly execute this query.”

---

# Step 4 — Generate Estimated Plan

```sql id="jznkxt"
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

# Ask The Room

* “What access path do you expect?”
* “Would index necessarily be used?”
* “Would full scan always be bad?”
* “What information is still missing?”

---

# Slide 22 — Actual Runtime Plan

## Slide Content

```sql id="6s9zfd"
SELECT *
FROM transactions
WHERE account_id = 5001;
```

Then:

```sql id="h0z5xa"
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST'
  )
);
```

---

## Trainer Delivery

“EXPLAIN PLAN only predicts.

DISPLAY_CURSOR shows:

* what actually executed,
* actual rows,
* logical reads,
* runtime statistics.”

---

# Ask The Room

* “Did Oracle use the same plan?”
* “Are estimated rows close to actual rows?”
* “Would this still behave well under concurrency?”

---

# SECTION 3 — HOW TO READ PLANS LIKE DBAs (11:15 – 11:30)

# IMPORTANT

Teach ONLY important columns.

Do NOT overload them.

---

# Slide 23 — Plan Reading Priority

## Slide Content

# Read Plans In This Order

1. Access path
2. Estimated rows
3. Actual rows
4. Join method
5. Predicate section
6. Logical reads
7. Cost

---

## Trainer Delivery

“Many beginners look at cost first.

Senior DBAs usually look at:

* access path,
* row estimates,
* runtime mismatch,
* buffers,
* predicate usage.”

---

# Slide 24 — Important Plan Operations

## Slide Content

| Operation             | Meaning                  |
| --------------------- | ------------------------ |
| TABLE ACCESS FULL     | scans table              |
| INDEX RANGE SCAN      | scans part of index      |
| INDEX UNIQUE SCAN     | unique lookup            |
| TABLE ACCESS BY ROWID | table lookup after index |
| NESTED LOOPS          | row-by-row join          |
| HASH JOIN             | large-volume join        |
| SORT ORDER BY         | sorting operation        |

---

## Trainer Delivery

“Do not memorize operations blindly.

Always ask:

```text id="h1ah8v"
Why did Oracle choose this?
```

That is the real DBA skill.”

---

# Slide 25 — Full Table Scan

## Slide Content

# TABLE ACCESS FULL

Not always bad.

Good when:

* large percentage of table needed
* table is small
* index is not selective
* optimizer estimates scan cheaper

---

## Trainer Delivery

“One of the biggest tuning mistakes:
forcing indexes everywhere.

If SQL needs 70% of the table,
full scan may actually be correct.”

---

# Ask The Room

* “Would index help Query 1 from Slot 1?”
* “Would full scan make sense there?”

---

# Slide 26 — INDEX RANGE SCAN

## Slide Content

# INDEX RANGE SCAN

Usually good when:

* filter is selective
* small row set needed
* index matches predicate

Example:

```sql id="jlwm7v"
WHERE account_id = 5001
```

---

## Trainer Delivery

“Index scan is useful when Oracle can avoid reading most of the table.”

---

# Slide 27 — Predicate Information

## Slide Content

# Predicate Information

Two important types:

```text id="k7r9ia"
access
filter
```

---

## Trainer Delivery

“Access predicate helps Oracle reach rows efficiently.

Filter predicate often means:
Oracle already read rows,
then removed unwanted rows afterward.”

---

# Example

```text id="s8cdmb"
access("ACCOUNT_ID"=5001)
```

vs

```text id="eiy6yu"
filter("STATUS"='FAILED')
```

---

# SECTION 4 — OPTIMIZER MISMATCH & BAD DECISIONS (11:30 – 11:45)

# Slide 28 — E-Rows vs A-Rows

## Slide Content

# Most Important Comparison

| Metric | Meaning        |
| ------ | -------------- |
| E-Rows | estimated rows |
| A-Rows | actual rows    |

Problem example:

```text id="krg5cm"
E-Rows = 10
A-Rows = 100000
```

---

## Trainer Delivery

“This mismatch is one of the biggest causes of bad plans.”

---

# Live Demo — E-Rows vs A-Rows With Controlled Stats

## Step 1 — Ensure Skew Exists

```sql id="nfdqkq"
UPDATE transactions
SET status =
  CASE
    WHEN MOD(transaction_id,20) = 0 THEN 'FAILED'
    ELSE 'SUCCESS'
  END;

COMMIT;
```

---

# Step 2 — Ensure Status Index Exists

```sql
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*)
  INTO v_count
  FROM user_indexes
  WHERE index_name = 'IDX_TXN_STATUS';

  IF v_count = 0 THEN
    EXECUTE IMMEDIATE
      'CREATE INDEX idx_txn_status ON transactions(status)';
  END IF;
END;
/
```

Trainer note:

Use `COUNT(*)` for this demo because the status index can satisfy the query cleanly. For `SELECT *`, Oracle may prefer a full scan because table lookups by ROWID can become expensive.

---

# Step 3 — Gather Stats WITHOUT Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 1 status',
    cascade    => TRUE
  );
END;
/
```

---

# Step 4 — Confirm No Histogram

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

Expected:

```text
HISTOGRAM = NONE
```

---

# Step 5 — Run Rare-Value Query With Runtime Stats

```sql
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

```sql
SELECT /* no_hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';
```

Then:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Expected teaching point:

```text
Oracle may estimate roughly half the table because it only knows there are 2 values.
Actual rows are much lower.
```

---

# Step 6 — Gather Stats WITH Histogram

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'TRANSACTIONS',
    method_opt => 'FOR COLUMNS SIZE 254 status',
    cascade    => TRUE
  );
END;
/
```

---

# Step 7 — Confirm Histogram Exists

```sql
SELECT column_name,
       num_distinct,
       histogram,
       num_buckets
FROM user_tab_col_statistics
WHERE table_name = 'TRANSACTIONS'
AND column_name = 'STATUS';
```

Expected:

```text
HISTOGRAM = FREQUENCY
```

---

# Step 8 — Rerun Rare-Value Query

Use a different SQL comment so Oracle creates a fresh cursor for easy comparison.

```sql
SELECT /* hist_failed */ COUNT(*)
FROM transactions
WHERE status='FAILED';
```

Then:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Now compare:

* E-Rows before histogram
* E-Rows after histogram
* A-Rows
* access path
* buffers
* predicate information

Expected result with 300,000 rows:

```text
Without histogram: E-Rows may be close to 150,000
With histogram:    E-Rows should be close to 15,000
A-Rows:            should show the real FAILED row count
```

If you scale the table size, expect the same pattern: without histogram Oracle may estimate around 50% of the table; with histogram Oracle should estimate around 5%.

Trainer note:

Do not promise that the plan shape must change. The reliable teaching point is the estimate correction. If Oracle also changes access path or cost significantly, discuss why that happened.

---

# Ask The Room

* “Did optimizer estimate correctly?”
* “What changed after the histogram?”
* “Did the data change, or did Oracle knowledge change?”
* “Would the same index be equally useful for SUCCESS?”

---

## Trainer Delivery

“This is where execution plan analysis becomes real.

Same column.
Same table.
Same data.

But different statistics quality.

Before the histogram, Oracle knows there are two status values, but may not know the distribution.

After the histogram, Oracle understands the skew.

That is why E-Rows vs A-Rows is not just a plan-reading skill.

It tells us whether the optimizer’s assumptions match reality.”

---

# Slide 29 — Cost Is NOT Runtime

## Slide Content

# Cost ≠ Seconds

Cost is:

```text id="b1n5ur"
optimizer estimate of work
```

Runtime depends on:

* cache
* CPU
* concurrency
* disk
* waits
* workload

---

## Trainer Delivery

“A low-cost query can still run slowly under concurrency.

A high-cost query may still be acceptable if it runs once daily.

Always connect plans with business workload.”

---

# Slide 30 — Runtime Evidence Matters

## Slide Content

Important runtime metrics:

* Buffers
* Reads
* A-Rows
* Starts
* Elapsed time

---

## Trainer Delivery

“Real tuning happens with runtime evidence,
not estimated diagrams.”

---

# SECTION 5 — LAB: DBA PLAN ANALYSIS (11:45 – 11:55)

# Slide 31 — Lab Objective

## Slide Content

# Lab Goal

Participants will:

* generate estimated plan
* generate runtime plan
* compare estimates vs reality
* identify access path
* analyze predicate behavior

---

# Lab Query A

```sql id="jlwm7v"
SELECT *
FROM transactions
WHERE account_id = 5001;
```

---

# Lab Query B

```sql id="3r0qzn"
SELECT *
FROM transactions
WHERE status='SUCCESS';
```

---

# Lab Query C

```sql id="v9h6y3"
SELECT *
FROM transactions
WHERE status='FAILED';
```

---

# Trainee Observation Table

| Query          | Access Path | E-Rows | A-Rows | Buffers | Predicate | Observation |
| -------------- | ----------- | ------ | ------ | ------- | --------- | ----------- |
| account_id     |             |        |        |         |           |             |
| status=SUCCESS |             |        |        |         |           |             |
| status=FAILED  |             |        |        |         |           |             |

---

# Ask The Room

* “Which query is most selective?”
* “Which query creates unnecessary work?”
* “Did Oracle choose appropriate access path?”
* “Would adding index automatically solve everything?”

---

# SECTION 6 — SUMMARY & TRANSITION (11:55 – 12:00)

# Slide 32 — Final DBA Message

## Slide Content

```text id="9w01e5"
Execution plans explain Oracle decisions.

Runtime plans explain Oracle reality.
```

---

## Trainer Delivery

“Never stop at EXPLAIN PLAN.

Always validate runtime behavior.”

---

# Slide 33 — Enterprise DBA Workflow

## Slide Content

```text id="j8z3jg"
SQL Problem
 ↓
Capture Plan
 ↓
Compare Estimates
 ↓
Analyze Runtime
 ↓
Identify Wrong Assumption
 ↓
Then Tune
```

---

## Trainer Delivery

“This is the workflow used in real production troubleshooting.”

---

# TRANSITION TO SLOT 3

# Next Slot

## Indexing Strategies for Enterprise Banking Workloads

We will learn:

* B-tree indexes
* composite indexes
* selective indexing
* covering indexes
* index overhead
* index misuse
* invisible indexes
* why some indexes hurt performance
