Absolutely — here is **Day 2 — Slot 1 only**, focused on:

# AWR: Automatic Workload Repository

## 9:00 AM to 10:30 AM

This slot moves from **single SQL tuning** to **database workload diagnosis**.

---

# Day 2 — Slot 1

## AWR: Automatic Workload Repository

## Slot Objective

By the end of this slot, trainees should understand:

* What AWR is
* Why AWR is useful for banking DBAs
* What snapshots and baselines mean
* How to generate an AWR report
* How to read important AWR sections
* How to identify whether the issue is SQL, CPU, I/O, locking, or memory-related

---

# Suggested Slot Flow

| Time          | Section                                   |
| ------------- | ----------------------------------------- |
| 9:00 - 9:10   | Day 2 introduction                        |
| 9:10 - 9:25   | What is AWR?                              |
| 9:25 - 9:40   | Snapshots, baselines, workload comparison |
| 9:40 - 10:05  | Important AWR sections                    |
| 10:05 - 10:25 | Lab 5: Generate AWR report                |
| 10:25 - 10:30 | Discussion and summary                    |

---

# Slide 1: Day 2 Opening

## Slide content

## Day 2: System-Level Performance Diagnosis

Yesterday we focused on:

* Individual SQL
* Execution plans
* Indexing
* Basic SQL tuning patterns

Today we move to:

* Database workload analysis
* AWR reports
* ADDM recommendations
* SQL tuning tools
* Memory and I/O symptoms

---

## Trainer Explanation

“Yesterday we looked at SQL one by one.

Today we move one level higher.

In production, users usually do not say one SQL is slow. They say the application is slow, fund transfer is slow, reports are slow, or the whole database feels slow.

So today we learn how to diagnose performance at database workload level.”

---

# Slide 2: Slot Title

## Slide content

# AWR: Automatic Workload Repository

AWR helps DBAs answer:

* What happened in the database?
* When did the problem happen?
* Which SQL caused the load?
* What were the top waits?
* Was it CPU, I/O, locking, or SQL design?

---

## Trainer Explanation

“This slot is about AWR.

AWR is one of the most important tools for Oracle performance diagnosis.

It helps us look at database activity between two points in time.

For example, if users complain at 11 AM, we can compare database activity around that period and identify what consumed the most time.”

---

# Slide 3: What is AWR?

## Slide content

## AWR = Automatic Workload Repository

AWR stores historical performance data about the database.

It captures information such as:

* SQL performance
* Wait events
* CPU usage
* I/O activity
* Memory usage
* Segment activity
* Instance workload
* System statistics

---

## Trainer Explanation

“AWR is like a performance black box for Oracle.

It stores performance information over time.

Instead of guessing what happened, we can check the AWR report and see which SQL, wait event, or database component consumed time.

In a bank, this is very useful because performance complaints often happen during a specific business window.”

---

# Slide 4: Why Banks Use AWR

## Slide content

Banks use AWR because they need to diagnose:

* Slow fund transfers
* Slow account statement screens
* Slow branch dashboards
* End-of-day batch delays
* Month-end report slowness
* High CPU usage
* I/O bottlenecks
* Locking or wait issues
* Performance degradation over time

---

## Trainer Explanation

“In banking, performance issues are not just technical problems.

If fund transfers are slow, customers are affected.

If end-of-day processing is delayed, operations are affected.

If branch dashboards are slow, staff productivity is affected.

AWR helps DBAs find evidence instead of depending on assumptions.”

---

# Slide 5: AWR as a Medical Report

## Slide content

Think of AWR like a medical report.

Symptoms:

```text
Users say fund transfer is slow.
```

AWR helps check:

* Database time
* CPU usage
* Wait events
* SQL load
* I/O activity
* Top objects
* Workload change

---

## Trainer Explanation

“When a patient says they feel weak, a doctor does not immediately give random medicine.

The doctor checks reports.

Similarly, when users say the database is slow, the DBA should not immediately create indexes or restart the database.

AWR is one of our main diagnostic reports.”

---

# Slide 6: Snapshot Concept

## Slide content

## What is an AWR Snapshot?

A snapshot is a performance data capture at a specific point in time.

Example:

```text
Snapshot 1: 10:00 AM
Snapshot 2: 11:00 AM
```

AWR report compares activity between these snapshots.

---

## Trainer Explanation

“AWR works using snapshots.

A snapshot captures database performance data at a point in time.

When we generate an AWR report, we choose a start snapshot and an end snapshot.

The report then tells us what happened between those two snapshots.”

---

# Slide 7: Snapshot Example

## Slide content

Banking complaint:

```text
Users complained at 11:00 AM.
```

Useful AWR window:

```text
Start snapshot: 10:30 AM
End snapshot: 11:30 AM
```

This helps analyze the slow period.

---

## Trainer Explanation

“Suppose users complain that fund transfers were slow around 11 AM.

We should generate an AWR report around that time window.

If we choose the wrong time window, the report may not show the problem.

So snapshot selection is very important.”

---

# Slide 8: Baseline Concept

## Slide content

## What is a Baseline?

A baseline is a normal performance reference.

Example:

Normal workload:

```text
Monday 10 AM to 11 AM
```

Problem workload:

```text
Tuesday 10 AM to 11 AM
```

We compare both to identify what changed.

---

## Trainer Explanation

“A baseline is like normal health condition.

If we know how the database behaves during normal business hours, we can compare it with the problem period.

This helps us answer: is today really abnormal, or is this normal workload?”

---

# Slide 9: Why Baselines Matter in Banking

## Slide content

Baselines help compare:

* Normal day vs problem day
* Month-end vs regular day
* Batch window vs online banking window
* Before deployment vs after deployment
* Before statistics refresh vs after statistics refresh

---

## Trainer Explanation

“In banking, workload changes by time.

Morning branch activity may be different from night batch processing.

Month-end workload may be heavier than normal days.

Baselines help us avoid wrong conclusions.

A high workload during month-end may be expected, but a sudden plan regression after deployment is different.”

---

# Slide 10: Workload Comparison

## Slide content

AWR can help compare:

* SQL load increase
* Wait event change
* CPU usage increase
* I/O reads increase
* Buffer gets increase
* New expensive SQL
* Changed execution pattern
* Object-level activity

---

## Trainer Explanation

“When we compare workloads, we are looking for what changed.

Maybe one SQL suddenly started consuming more time.

Maybe physical reads increased.

Maybe buffer gets increased.

Maybe wait events changed from CPU to I/O.

This comparison is very useful for root cause analysis.”

---

# Slide 11: Banking Scenario

## Slide content

## Scenario

At 11 AM, users complain:

```text
Fund transfers are slow.
```

DBA needs to answer:

* Was the database overloaded?
* Which SQL consumed most DB time?
* Was it CPU, I/O, locking, or memory?
* Which module or user caused the load?
* Was this a short spike or ongoing issue?

---

## Trainer Explanation

“This is our main scenario.

Users say fund transfers are slow at 11 AM.

As DBAs, we should not guess.

We need to answer with evidence.

Was the database overloaded?

Was one SQL consuming time?

Was the issue I/O?

Was it locking?

Was it only for a few minutes?

AWR helps us investigate this.”

---

# Slide 12: Important AWR Sections

## Slide content

Important AWR sections we will focus on:

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

---

## Trainer Explanation

“AWR reports are long.

At first, they can feel overwhelming.

But we do not need to read every line at the beginning.

We will focus on the most useful sections.

These sections help us identify whether the issue is SQL, CPU, I/O, waits, or object-level activity.”

---

# Slide 13: DB Time

## Slide content

## DB Time

DB Time means total time spent by database sessions doing work or waiting.

It includes:

* CPU time
* Wait time

Simple idea:

```text
DB Time = total database workload time
```

High DB Time usually means high database load.

---

## Trainer Explanation

“DB Time is one of the most important AWR metrics.

It represents total time spent by database sessions either working on CPU or waiting for resources.

If DB Time is very high compared to elapsed time, it means many sessions were active or waiting.

In performance diagnosis, DB Time tells us the size of the problem.”

---

# Slide 14: Elapsed Time

## Slide content

## Elapsed Time

Elapsed Time is the wall-clock time between two snapshots.

Example:

```text
Start snapshot: 10:00 AM
End snapshot: 11:00 AM
Elapsed Time: 60 minutes
```

Compare DB Time with Elapsed Time.

---

## Trainer Explanation

“Elapsed time is simply the duration of the AWR report.

If the report covers one hour, elapsed time is one hour.

But DB Time can be much higher than elapsed time because many sessions can work at the same time.

For example, in one hour, 50 active sessions can generate many hours of DB Time.”

---

# Slide 15: DB Time vs Elapsed Time

## Slide content

Example:

```text
Elapsed Time: 60 minutes
DB Time: 600 minutes
```

Meaning:

* Many sessions were active
* Database had heavy workload
* Need to check top waits and top SQL

---

## Trainer Explanation

“This example means the report covers 60 minutes, but sessions together consumed 600 minutes of database time.

That means multiple sessions were active or waiting.

This is normal in busy systems, but if DB Time suddenly increases compared to baseline, that is a sign of a problem.”

---

# Slide 16: Load Profile

## Slide content

## Load Profile shows activity rate

It may include:

* DB time per second
* DB CPU per second
* Redo size
* Logical reads
* Physical reads
* Parses
* Executes
* Transactions

---

## Trainer Explanation

“Load Profile shows how much work the database did per second or per transaction.

It gives us a quick feel for workload intensity.

For example, if logical reads or executions suddenly increased, maybe application behavior changed.

If physical reads increased, maybe I/O or SQL access path became worse.”

---

# Slide 17: Top Timed Events

## Slide content

## Top Timed Events

Shows where database time was spent.

Examples:

* CPU time
* db file sequential read
* db file scattered read
* log file sync
* enq: TX - row lock contention
* direct path read
* buffer busy waits

---

## Trainer Explanation

“Top Timed Events is one of the first sections I check.

It tells us where database time went.

If CPU is high, the database is CPU-bound.

If db file sequential read is high, there may be index lookup or single-block read activity.

If row lock contention is high, it may be locking.

If log file sync is high, commit performance may be an issue.”

---

# Slide 18: Wait Event Meaning

## Slide content

Common wait examples:

| Wait Event                    | Possible Meaning                       |
| ----------------------------- | -------------------------------------- |
| DB CPU                        | CPU work                               |
| db file sequential read       | Single-block reads, often index access |
| db file scattered read        | Multi-block reads, often full scans    |
| log file sync                 | Commit wait                            |
| enq: TX - row lock contention | Row locking                            |
| direct path read              | Direct reads, often large scans        |

---

## Trainer Explanation

“Wait events tell us what sessions were waiting for.

But do not jump to conclusions too quickly.

For example, db file sequential read is often related to index access, but whether it is bad depends on volume and SQL pattern.

Wait events guide us where to investigate next.”

---

# Slide 19: SQL Ordered by Elapsed Time

## Slide content

## SQL ordered by Elapsed Time

Shows SQL statements consuming most total elapsed time.

Useful to find:

* Slow SQL
* Frequently executed SQL
* SQL causing user delay
* SQL consuming large DB time

---

## Trainer Explanation

“This section shows SQL that consumed the most elapsed time in total.

It is very useful when users complain that something is slow.

If one SQL has very high elapsed time, that SQL may be a major contributor to the problem.”

---

# Slide 20: SQL Ordered by CPU Time

## Slide content

## SQL ordered by CPU Time

Shows SQL consuming most CPU.

Useful when:

* CPU usage is high
* Queries perform heavy calculations
* SQL reads and processes many rows
* Functions or complex joins are expensive

---

## Trainer Explanation

“If the database server CPU is high, check SQL ordered by CPU Time.

This helps identify SQL using the most CPU.

A query may not read much from disk but may still consume CPU because of joins, sorting, functions, or repeated executions.”

---

# Slide 21: SQL Ordered by Gets

## Slide content

## SQL ordered by Gets

Gets usually means logical reads.

High buffer gets can indicate:

* SQL reading too many blocks from memory
* Inefficient access path
* Repeated execution
* Missing or poor filter
* High-load SQL

---

## Trainer Explanation

“SQL ordered by Gets is very important.

Logical reads may not always show as disk I/O, because data may be in memory.

But high logical reads still mean Oracle is doing a lot of work.

A query with high gets can become dangerous when it runs many times per hour.”

---

# Slide 22: SQL Ordered by Reads

## Slide content

## SQL ordered by Reads

Shows SQL causing high physical reads.

High physical reads can indicate:

* Disk I/O pressure
* Full table scans
* Large reports
* Poor access path
* Missing filtering
* Cold cache effect

---

## Trainer Explanation

“If SQL ordered by Reads shows one query with very high physical reads, that query may be causing I/O pressure.

This is common with large reports, full scans, and queries without proper filters.

In banking, large statement reports or audit log queries can appear here.”

---

# Slide 23: Instance Efficiency

## Slide content

## Instance Efficiency

Shows high-level efficiency indicators.

Examples:

* Buffer hit percentage
* Library cache hit percentage
* Parse efficiency
* Execute to parse ratio

Important:

Do not tune only by percentages.

Use this section as a signal, not final proof.

---

## Trainer Explanation

“Instance Efficiency gives quick indicators.

But be careful.

Many DBAs over-focus on percentages.

A high buffer hit ratio does not always mean database is healthy.

A low value may indicate something, but we should connect it with top waits and SQL sections.

Use it as supporting evidence.”

---

# Slide 24: Segment Statistics

## Slide content

## Segment Statistics

Shows heavily accessed objects.

Useful to identify hot:

* Tables
* Indexes
* Partitions
* LOB segments

Can show:

* Logical reads
* Physical reads
* Row lock waits
* ITL waits
* Buffer busy waits

---

## Trainer Explanation

“Segment Statistics helps us identify which objects are heavily used.

For example, maybe the transactions table is getting most logical reads.

Or one index is causing many physical reads.

Or one table has row lock waits.

This helps connect SQL-level problems to actual database objects.”

---

# Slide 25: AWR Diagnosis Flow

## Slide content

Use this AWR reading flow:

```text
1. Check snapshot window
2. Check DB Time vs Elapsed Time
3. Check Top Timed Events
4. Check SQL by Elapsed Time
5. Check SQL by CPU Time
6. Check SQL by Gets
7. Check SQL by Reads
8. Check Segment Statistics
9. Decide likely root cause
```

---

## Trainer Explanation

“When reading AWR, follow a sequence.

First confirm that the report covers the correct problem window.

Then check whether database load was high.

Then check where time was spent.

Then identify top SQL.

Then check if the issue looks like CPU, I/O, locking, or SQL design.”

---

# Slide 26: Lab 5 Objective

## Slide content

## Lab 5: Generate AWR Snapshot and Report

Participants will:

1. Create starting AWR snapshot
2. Run heavy workload queries
3. Create ending AWR snapshot
4. Generate AWR report
5. Identify top SQL and wait events

---

## Trainer Explanation

“Now we will generate our own AWR report.

We will create a start snapshot, run workload, create an end snapshot, and then generate the report.

This gives participants hands-on practice with the full AWR flow.”

---

# Slide 27: Lab Prerequisites

## Slide content

Before lab, confirm:

* Oracle Enterprise Edition
* Diagnostic Pack license available
* AWR access permissions
* Tables created from Day 1
* Workload tables have enough rows

Useful check:

```sql
SELECT COUNT(*) FROM transactions;
SELECT COUNT(*) FROM customers;
```

---

## Trainer Explanation

“AWR is part of Oracle’s diagnostic tooling and normally requires the proper Oracle license.

In a real bank, always confirm license usage with the organization.

For our lab, we also need tables with enough data so the workload appears clearly in AWR.”

---

# Slide 28: Lab Step 1 — Create Start Snapshot

## Slide content

Run as privileged user:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Then check snapshots:

```sql
SELECT snap_id, begin_interval_time, end_interval_time
FROM dba_hist_snapshot
ORDER BY snap_id DESC
FETCH FIRST 5 ROWS ONLY;
```

---

## Trainer Explanation

“This creates our start snapshot.

Think of it as marking the beginning of the test window.

After this, we will run workload queries.

Later, we create another snapshot and compare the activity between both snapshots.”

---

# Slide 29: Lab Step 2 — Run Heavy Workload Queries

## Slide content

Run workload for a few minutes.

Example workload 1: large sort

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

Example workload 2: high logical reads

```sql
SELECT COUNT(*)
FROM transactions
WHERE status = 'SUCCESS';
```

Example workload 3: customer search

```sql
SELECT *
FROM customers
WHERE LOWER(email) LIKE '%user%';
```

---

## Trainer Explanation

“These queries intentionally create workload.

The purpose is not to write good SQL.

The purpose is to generate activity that AWR can capture.

Large sort, broad filter, and function-based search can create visible load in the report.”

---

# Slide 30: Optional Workload Loop

## Slide content

To generate repeated workload:

```sql
BEGIN
  FOR i IN 1..20 LOOP
    FOR r IN (
      SELECT COUNT(*) cnt
      FROM transactions
      WHERE status = 'SUCCESS'
    ) LOOP
      NULL;
    END LOOP;
  END LOOP;
END;
/
```

Another workload:

```sql
BEGIN
  FOR i IN 1..10 LOOP
    FOR r IN (
      SELECT *
      FROM customers
      WHERE LOWER(email) LIKE '%user%'
      FETCH FIRST 100 ROWS ONLY
    ) LOOP
      NULL;
    END LOOP;
  END LOOP;
END;
/
```

---

## Trainer Explanation

“If the workload does not show strongly in AWR, we can repeat queries in a loop.

This makes the SQL execute multiple times and increases the chance that it appears in top SQL sections.

Be careful not to overload weak lab machines too much.”

---

# Slide 31: Lab Step 3 — Create End Snapshot

## Slide content

After workload completes, run:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Check latest snapshots:

```sql
SELECT snap_id, begin_interval_time, end_interval_time
FROM dba_hist_snapshot
ORDER BY snap_id DESC
FETCH FIRST 5 ROWS ONLY;
```

---

## Trainer Explanation

“This creates the end snapshot.

Now we have a start point and end point.

The AWR report will show what happened between these two snapshots.”

---

# Slide 32: Lab Step 4 — Generate AWR Report

## Slide content

Run:

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

You will select:

* Report type: `html` or `text`
* Number of days
* Begin snapshot ID
* End snapshot ID
* Report name

Recommended:

```text
html
```

---

## Trainer Explanation

“This script generates the AWR report.

HTML is easier to read, so I recommend generating an HTML report.

The script will ask for snapshot IDs.

Choose the start and end snapshot we created for this lab.”

---

# Slide 33: Lab Step 5 — First Things to Check

## Slide content

In the AWR report, first check:

1. Snapshot window
2. DB Time
3. Elapsed Time
4. Top Timed Events
5. SQL ordered by Elapsed Time
6. SQL ordered by Gets
7. SQL ordered by Reads

---

## Trainer Explanation

“When the report opens, do not jump randomly.

First confirm that the report covers the correct time window.

Then check DB Time and Top Timed Events.

After that, check SQL sections to identify which SQL contributed most.”

---

# Slide 34: Lab Task

## Slide content

Participants must identify:

* Top 3 SQL by elapsed time
* Top 3 wait events
* SQL with highest buffer gets
* SQL with highest physical reads
* Whether the problem looks like:

  * CPU
  * I/O
  * Locking
  * Memory
  * SQL design

---

## Trainer Explanation

“This is the main lab task.

Participants should not only copy values.

They should interpret them.

For example, if SQL ordered by Reads is high, maybe I/O is involved.

If SQL ordered by Gets is high, maybe SQL is doing too many logical reads.

If row lock contention appears, maybe locking is involved.”

---

# Slide 35: Lab Observation Table

## Slide content

| AWR Section         | What You Found | What It May Mean           |
| ------------------- | -------------- | -------------------------- |
| DB Time             |                | Overall database load      |
| Top Timed Events    |                | CPU/I/O/locking/wait issue |
| SQL by Elapsed Time |                | Slow/high-impact SQL       |
| SQL by CPU Time     |                | CPU-heavy SQL              |
| SQL by Gets         |                | High logical reads         |
| SQL by Reads        |                | High physical I/O          |
| Segment Statistics  |                | Hot table/index            |

---

## Trainer Explanation

“Ask participants to fill this table.

This will force them to connect AWR data with possible root cause.

The goal is not only reading numbers.

The goal is diagnosis.”

---

# Slide 36: Interpreting Results — CPU Problem

## Slide content

Possible signs of CPU issue:

* DB CPU high in Top Timed Events
* SQL ordered by CPU Time shows heavy SQL
* High executions
* Complex joins/functions/sorts
* Low I/O waits but high CPU time

Possible action:

* Tune CPU-heavy SQL
* Reduce unnecessary executions
* Check application loops
* Review query logic

---

## Trainer Explanation

“If CPU dominates, check SQL ordered by CPU Time.

Sometimes one SQL is called thousands of times.

Sometimes functions, joins, or sorting consume CPU.

The solution is usually SQL tuning or application execution control, not immediately adding memory.”

---

# Slide 37: Interpreting Results — I/O Problem

## Slide content

Possible signs of I/O issue:

* High physical reads
* `db file scattered read`
* `db file sequential read`
* Direct path reads
* SQL ordered by Reads shows heavy SQL
* Segment statistics show hot large table

Possible action:

* Tune SQL access path
* Reduce full scans
* Check indexes
* Check storage performance
* Check data volume

---

## Trainer Explanation

“If physical reads are high, we investigate I/O.

But remember: I/O issue may be caused by bad SQL.

A query scanning a huge table can create I/O pressure.

So do not blame storage immediately.

First identify the SQL causing reads.”

---

# Slide 38: Interpreting Results — Locking Problem

## Slide content

Possible signs of locking issue:

* `enq: TX - row lock contention`
* High wait time on locks
* Blocking sessions during issue window
* Slow updates or transfers
* Hot account or transaction rows

Possible action:

* Identify blocking SQL/session
* Check transaction duration
* Review application commit logic
* Avoid long uncommitted transactions

---

## Trainer Explanation

“In banking, locking can happen during fund transfers, balance updates, payment posting, or reversal processing.

If AWR shows row lock contention, the next step is to identify blocking sessions and SQL.

AWR tells us there was locking, but real-time views help investigate current blockers.”

---

# Slide 39: Interpreting Results — SQL Design Problem

## Slide content

Possible signs of SQL design issue:

* Same SQL appears high in multiple sections
* High elapsed time
* High buffer gets
* High physical reads
* Large rows processed
* Full scans on large tables
* Expensive sorts

Possible action:

* Check execution plan
* Check predicates
* Add business filters
* Review indexes
* Rewrite SQL if needed

---

## Trainer Explanation

“If the same SQL appears in elapsed time, gets, and reads, that SQL is a strong suspect.

Then we go back to Day 1 skills.

We check the execution plan, access path, predicates, and indexing.

So AWR helps us find the SQL. Execution plan helps us tune it.”

---

# Slide 40: Common Tuning Problems Covered

## Slide content

This slot covers:

## High-load SQL

AWR identifies SQL consuming DB time.

## I/O Issues

AWR shows physical reads and I/O waits.

## Short-lived Performance Problems

Snapshots capture workload during problem window.

## Performance Degradation Over Time

Baselines help compare normal vs degraded periods.

---

## Trainer Explanation

“This slot connects directly to four common tuning problems.

AWR is especially useful when the problem is not one obvious SQL, but a workload issue.

It also helps when users say: it was slow at 11 AM, but now it is fine.

If snapshots exist, we can still investigate that past period.”

---

# Slide 41: Slot 1 Summary

## Slide content

In this slot, we learned:

* AWR stores historical workload data
* AWR reports compare two snapshots
* Snapshot window selection is critical
* Baselines help compare normal and problem periods
* DB Time shows total database workload
* Top Timed Events show where time was spent
* SQL sections identify expensive SQL
* Gets show logical reads
* Reads show physical reads
* Segment stats show hot objects

---

## Trainer Explanation

“Let’s summarize.

AWR helps us move from guesswork to evidence.

When users complain, we should identify the correct time window, generate the report, check DB Time, top waits, and top SQL.

Then we decide whether the issue looks like SQL, CPU, I/O, locking, or memory.”

---

# Slide 42: Transition to Slot 2

## Slide content

Next slot:

# ADDM: Automatic Database Diagnostic Monitor

We will learn:

* What ADDM is
* How ADDM uses AWR data
* How to read ADDM findings
* Impact percentage
* Recommendations
* When to trust or validate ADDM advice

---

## Trainer Explanation

“AWR gives us the raw performance report.

In the next slot, ADDM will help interpret that data and provide recommendations.

Think of AWR as the medical test report, and ADDM as the doctor’s diagnosis.

But as DBAs, we still validate the recommendation before applying it.”

---

# Final Trainer Message for This Slot

Use this line:

> “AWR does not directly fix performance. AWR tells us where to investigate with evidence.”
