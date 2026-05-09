Absolutely — here is **Day 2 — Slot 2 only**, focused on:

# ADDM: Automatic Database Diagnostic Monitor

## 10:45 AM to 12:00 PM

---

# Day 2 — Slot 2

## ADDM: Automatic Database Diagnostic Monitor

## Slot Objective

By the end of this slot, trainees should understand:

* What ADDM is
* How ADDM is different from AWR
* How ADDM interprets AWR data
* How to read ADDM findings
* What impact percentage means
* Common recommendation types
* How to generate an ADDM report
* Why ADDM recommendations must be validated before applying

---

# Suggested Slot Flow

| Time          | Section                           |
| ------------- | --------------------------------- |
| 10:45 - 10:55 | What is ADDM?                     |
| 10:55 - 11:10 | AWR vs ADDM                       |
| 11:10 - 11:25 | Findings, impact, recommendations |
| 11:25 - 11:45 | Lab 6: Generate ADDM report       |
| 11:45 - 11:55 | Interpret report                  |
| 11:55 - 12:00 | Summary                           |

---

# Slide 1: Slot Title

## ADDM: Automatic Database Diagnostic Monitor

**Slide content:**

ADDM helps DBAs understand performance problems from AWR data.

In this slot, we will learn:

* What ADDM is
* How ADDM uses AWR
* How to read findings
* What impact percentage means
* How to validate recommendations

---

## Trainer Explanation

“In the previous slot, we learned AWR.

AWR gives us a detailed performance report.

But AWR can be long and difficult to read.

ADDM helps by analyzing AWR data and giving findings and recommendations.

So this slot is about moving from raw report reading to diagnosis.”

---

# Slide 2: What is ADDM?

## Slide content

## ADDM = Automatic Database Diagnostic Monitor

ADDM analyzes database performance between two AWR snapshots.

It identifies:

* Performance bottlenecks
* Root cause areas
* High-impact SQL
* Wait problems
* Memory issues
* I/O issues
* Configuration problems
* Recommended actions

---

## Trainer Explanation

“ADDM is Oracle’s diagnostic advisor.

It looks at AWR snapshot data and tries to identify what caused performance issues.

Instead of reading every AWR section manually, ADDM gives us a summarized diagnosis.

But remember: ADDM is an advisor, not a final decision-maker.”

---

# Slide 3: Simple Explanation

## Slide content

```text
AWR = medical test report

ADDM = doctor’s diagnosis
```

AWR shows:

* Data
* Metrics
* Waits
* SQL activity

ADDM explains:

* What may be wrong
* Why it matters
* Estimated impact
* What action to consider

---

## Trainer Explanation

“This is the easiest way to remember.

AWR is like your blood test, X-ray, and health report.

It gives numbers.

ADDM is like the doctor looking at those reports and saying: this seems to be the main issue.

But even doctors validate before surgery.

Similarly, DBAs validate before applying changes.”

---

# Slide 4: AWR vs ADDM

## Slide content

| Item            | AWR                  | ADDM                         |
| --------------- | -------------------- | ---------------------------- |
| Type            | Performance report   | Diagnostic advisor           |
| Input           | Snapshot data        | AWR snapshot data            |
| Output          | Metrics and sections | Findings and recommendations |
| Purpose         | Investigation        | Interpretation               |
| Manual effort   | Higher               | Lower                        |
| Final decision? | No                   | No                           |

---

## Trainer Explanation

“AWR gives us detailed data.

ADDM reads that data and gives recommendations.

AWR answers: what happened?

ADDM tries to answer: what is the likely problem and what should we do?

But neither tool replaces DBA judgment.”

---

# Slide 5: How ADDM Works

## Slide content

ADDM uses AWR snapshots.

Flow:

```text
AWR Snapshot 1
      ↓
Workload happens
      ↓
AWR Snapshot 2
      ↓
ADDM analyzes the interval
      ↓
Findings + recommendations
```

---

## Trainer Explanation

“ADDM needs two snapshots.

It analyzes database activity between those snapshots.

So the quality of ADDM diagnosis depends on choosing the correct time window.

If the performance issue happened at 11 AM, but we analyze 2 PM to 3 PM, ADDM may not show the real issue.”

---

# Slide 6: Why ADDM is Useful for Bank DBAs

## Slide content

Bank DBAs use ADDM to quickly identify:

* Slow SQL impact
* I/O bottlenecks
* Memory pressure
* Commit latency
* Locking symptoms
* Configuration issues
* Segment-level problems
* Workload degradation

---

## Trainer Explanation

“In a bank, performance issues need quick diagnosis.

If fund transfers are slow, we cannot spend hours randomly checking everything.

ADDM helps narrow the investigation.

It can tell us if the main issue is SQL, I/O, memory, configuration, or something else.”

---

# Slide 7: Understanding ADDM Findings

## Slide content

An ADDM report usually contains:

* Finding name
* Finding description
* Impact
* Recommendation
* Rationale
* Related SQL or object
* Suggested action

Example finding:

```text
SQL statements were consuming significant database time.
```

---

## Trainer Explanation

“ADDM report is organized into findings.

Each finding describes a problem area.

For example, ADDM may say SQL statements are consuming significant DB time.

Then it may recommend SQL tuning.

The important part is to understand the finding, impact, and recommendation together.”

---

# Slide 8: Impact Percentage

## Slide content

## Impact Percentage

Impact shows how much database time may be affected by a finding.

Example:

```text
Finding impact: 45% of DB time
```

Meaning:

* This finding is important
* Fixing it may improve performance
* Higher impact usually means higher priority

---

## Trainer Explanation

“Impact percentage helps us prioritize.

If one finding has 45% impact and another has 3%, we usually investigate the 45% finding first.

But impact does not mean the fix is always safe.

It only tells us potential performance importance.”

---

# Slide 9: Impact Example

## Slide content

Example:

| Finding                      | Impact |
| ---------------------------- | -----: |
| High-load SQL                |    52% |
| I/O waits                    |    28% |
| Memory resize recommendation |     5% |

Priority:

1. Investigate high-load SQL
2. Check I/O waits
3. Review memory recommendation

---

## Trainer Explanation

“This table shows how we prioritize.

The highest impact finding usually gets attention first.

But findings may be connected.

For example, high-load SQL may be causing I/O waits.

So fixing SQL may also reduce I/O.”

---

# Slide 10: Recommendation Type — SQL Tuning

## Slide content

## SQL Tuning Recommendation

ADDM may recommend:

* Tune specific SQL ID
* Run SQL Tuning Advisor
* Add or review indexes
* Review execution plan
* Gather statistics
* Rewrite SQL

---

## Trainer Explanation

“This is one of the most common ADDM recommendations.

If ADDM finds SQL consuming major DB time, it may suggest tuning that SQL.

This connects with Day 1.

We would take the SQL ID, check the execution plan, review predicates, and validate improvements.”

---

# Slide 11: Recommendation Type — Memory Tuning

## Slide content

## Memory Tuning Recommendation

ADDM may identify:

* Shared pool pressure
* Buffer cache pressure
* PGA pressure
* Excessive parsing
* Sorts spilling to disk

Possible actions:

* Review SGA/PGA sizing
* Check memory advisors
* Reduce hard parsing
* Tune SQL causing large sorts

---

## Trainer Explanation

“Memory issues can appear in multiple forms.

For example, too much parsing may affect shared pool.

Large sorts may use PGA and spill to temp.

But we should not blindly increase memory.

First understand what is causing memory pressure.”

---

# Slide 12: Recommendation Type — I/O Tuning

## Slide content

## I/O Tuning Recommendation

ADDM may identify:

* High physical reads
* Slow single-block reads
* Slow multi-block reads
* Direct path read activity
* Hot data files or segments

Possible actions:

* Tune SQL causing reads
* Improve indexes
* Review storage performance
* Check segment activity
* Consider partitioning for large tables

---

## Trainer Explanation

“If ADDM says I/O is a problem, do not immediately blame storage.

Often bad SQL causes too many reads.

First identify which SQL or segment is causing I/O.

Then decide whether the fix is SQL tuning, indexing, partitioning, or storage-level improvement.”

---

# Slide 13: Recommendation Type — Configuration Tuning

## Slide content

## Configuration Tuning Recommendation

ADDM may recommend reviewing:

* Initialization parameters
* Memory settings
* Parallel execution settings
* Cursor sharing
* Statistics collection
* Redo/log configuration

---

## Trainer Explanation

“Configuration issues can affect the whole database.

But configuration changes are risky in production.

Always validate with senior DBA approval, test environment, and rollback plan.

Do not change parameters just because ADDM suggested something.”

---

# Slide 14: Recommendation Type — Segment Tuning

## Slide content

## Segment Tuning Recommendation

ADDM may identify hot objects:

* Tables
* Indexes
* Partitions
* LOB segments

Possible issues:

* High logical reads
* High physical reads
* Row lock waits
* Buffer busy waits
* Space or growth issues

---

## Trainer Explanation

“Segment tuning means the issue is related to a specific object.

For example, the transactions table may be heavily scanned.

Or one index may be causing many reads.

This helps us connect performance symptoms with actual database objects.”

---

# Slide 15: ADDM Does Not Replace DBA Judgment

## Slide content

ADDM recommendations must be validated.

Before applying:

* Check affected SQL
* Review execution plan
* Confirm business impact
* Test in lower environment
* Check DML impact
* Check risk
* Prepare rollback
* Monitor after change

---

## Trainer Explanation

“This is very important.

ADDM can recommend useful actions, but it does not understand full business context.

For example, it may suggest an index.

But that index may slow down a transaction-heavy table.

So DBA judgment is still required.”

---

# Slide 16: Banking Scenario

## Slide content

Scenario:

At 11 AM, users complain:

```text
Fund transfers are slow.
```

ADDM should help answer:

* What was the top finding?
* How much DB time was affected?
* Was the issue SQL, I/O, memory, or configuration?
* What action did ADDM recommend?
* Is the recommendation safe?

---

## Trainer Explanation

“Let’s connect ADDM to our banking scenario.

Users say fund transfer is slow.

AWR gives us the raw data.

ADDM helps summarize the likely cause.

But our job is to read the finding carefully and decide what to validate next.”

---

# Slide 17: Lab 6 Objective

## Slide content

## Lab 6: Run ADDM Report

Participants will:

1. Use snapshots from workload window
2. Generate ADDM report
3. Identify top finding
4. Read estimated impact
5. Review recommendation
6. Decide validation steps

---

## Trainer Explanation

“In this lab, we will generate an ADDM report for a workload window.

Ideally, use the same snapshots created during the AWR lab.

That way, participants can compare AWR raw data with ADDM diagnosis.”

---

# Slide 18: Lab Prerequisites

## Slide content

Before running ADDM:

* AWR snapshots must exist
* Workload should run between snapshots
* User should have required privileges
* Diagnostic Pack licensing should be confirmed

Check snapshots:

```sql
SELECT snap_id, begin_interval_time, end_interval_time
FROM dba_hist_snapshot
ORDER BY snap_id DESC
FETCH FIRST 10 ROWS ONLY;
```

---

## Trainer Explanation

“First confirm snapshots exist.

We need the begin and end snapshot IDs.

Also remember: in real banking environments, Diagnostic Pack license must be approved before using AWR or ADDM.”

---

# Slide 19: Lab Step 1 — Run Workload

## Slide content

If not already done, run workload between snapshots.

Create start snapshot:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Run sample workload:

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

```sql
SELECT COUNT(*)
FROM transactions
WHERE status = 'SUCCESS';
```

Create end snapshot:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

---

## Trainer Explanation

“If we already generated workload in the AWR lab, we can reuse those snapshots.

If not, create a start snapshot, run workload, then create an end snapshot.

ADDM will analyze the activity between those snapshots.”

---

# Slide 20: Lab Step 2 — Generate ADDM Report

## Slide content

Run:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

You will select:

* Begin snapshot ID
* End snapshot ID
* Report name

Example report name:

```text
addm_fund_transfer_test.txt
```

---

## Trainer Explanation

“This script generates the ADDM report.

It will ask for begin and end snapshots.

Choose the same interval where workload or issue happened.

Then give a report name.”

---

# Slide 21: Lab Step 3 — Read Report Header

## Slide content

First confirm:

* Database name
* Instance name
* Host name
* Snapshot range
* Analysis period
* DB time
* Report duration

---

## Trainer Explanation

“Before reading findings, first confirm the report is for the right database and correct time window.

This sounds basic, but it is important.

Many wrong diagnoses happen because people analyze the wrong time period.”

---

# Slide 22: Lab Step 4 — Identify Top Finding

## Slide content

Look for:

```text
FINDING 1
```

Record:

* Finding name
* Impact percentage
* Description
* Related SQL/object
* Recommendation

---

## Trainer Explanation

“Start with Finding 1.

Usually the highest-impact issue appears first.

Read the finding carefully.

Do not only copy the recommendation.

Understand what ADDM says is the cause.”

---

# Slide 23: Lab Step 5 — Read Recommendation

## Slide content

For each recommendation, ask:

* What action is suggested?
* Which SQL/object is affected?
* Is it safe?
* What could go wrong?
* How will we test?
* What evidence supports it?

---

## Trainer Explanation

“Recommendations are not commands to execute immediately.

They are suggestions.

For example, ADDM may recommend SQL tuning or memory change.

Before applying, we ask: what is the risk, what will we test, and how will we measure improvement?”

---

# Slide 24: Lab Task

## Slide content

Participants must identify:

| Item                                  | Answer |
| ------------------------------------- | ------ |
| Top ADDM finding                      |        |
| Estimated impact                      |        |
| Recommendation                        |        |
| Related SQL/object                    |        |
| Is it safe to apply directly?         |        |
| What validation is needed?            |        |
| What evidence from AWR supports this? |        |

---

## Trainer Explanation

“This table is the main output of the lab.

Participants should connect ADDM with AWR.

If ADDM says high-load SQL, check whether the same SQL appeared in AWR SQL ordered by elapsed time, gets, or reads.”

---

# Slide 25: Example ADDM Interpretation — High SQL Load

## Slide content

Example finding:

```text
SQL statements were consuming significant database time.
```

Possible meaning:

* One or more SQL statements are expensive
* SQL may have high elapsed time
* SQL may have high CPU
* SQL may have high logical reads

Validation:

* Check SQL ID
* Check execution plan
* Check AWR SQL sections
* Test SQL tuning changes

---

## Trainer Explanation

“If ADDM says high SQL load, this connects directly to Day 1.

We take the SQL ID and check execution plan.

Then we look at rows, cost, predicates, gets, and reads.

This is how ADDM points us to the next investigation step.”

---

# Slide 26: Example ADDM Interpretation — I/O Issue

## Slide content

Example finding:

```text
Database file reads were consuming significant database time.
```

Possible meaning:

* High physical reads
* Slow storage
* Full scans
* Inefficient SQL
* Large object access

Validation:

* Check SQL ordered by Reads
* Check segment statistics
* Check execution plans
* Check storage latency

---

## Trainer Explanation

“If ADDM shows I/O issue, first find which SQL caused reads.

Maybe the storage is slow.

But maybe the SQL is reading too much data.

Always connect I/O waits to SQL and segments before deciding the fix.”

---

# Slide 27: Example ADDM Interpretation — Memory Issue

## Slide content

Example finding:

```text
The database was performing excessive parsing or memory operations.
```

Possible meaning:

* Shared pool pressure
* Hard parsing
* Missing bind variables
* PGA pressure
* Large sorts

Validation:

* Check parse statistics
* Check SQL executions
* Check application bind usage
* Check memory advisors
* Check sort/temp usage

---

## Trainer Explanation

“If ADDM shows memory issue, avoid immediately increasing memory.

Ask why memory pressure exists.

Is the application not using bind variables?

Are reports sorting huge data?

Are many sessions running heavy queries?

The cause may still be SQL or application behavior.”

---

# Slide 28: Example ADDM Interpretation — Configuration Issue

## Slide content

Example finding:

```text
Database configuration contributed to performance.
```

Possible meaning:

* Parameter setting issue
* Memory configuration
* Parallelism issue
* Redo/log setting
* Statistics job problem

Validation:

* Review recommendation carefully
* Check current parameter values
* Test in non-production
* Get approval before production change

---

## Trainer Explanation

“Configuration recommendations require extra caution.

Changing parameters can affect the whole database.

In a bank, this should go through proper change management.

Always test and document rollback steps.”

---

# Slide 29: What Not To Do With ADDM

## Slide content

Do not:

* Apply recommendations blindly
* Tune only based on impact percentage
* Ignore business context
* Ignore workload type
* Create indexes without DML impact check
* Change memory/config directly in production
* Ignore AWR evidence
* Skip before/after validation

---

## Trainer Explanation

“This slide is important for production safety.

ADDM is powerful, but blind changes are dangerous.

A recommendation that looks good technically may hurt another workload.

So use ADDM as guidance, not automatic action.”

---

# Slide 30: ADDM Validation Workflow

## Slide content

Use this workflow:

```text
1. Identify finding
2. Check impact
3. Read recommendation
4. Find related SQL/object
5. Verify in AWR
6. Check execution plan or system metric
7. Test fix
8. Compare before/after
9. Apply safely if approved
```

---

## Trainer Explanation

“This is the professional workflow.

ADDM gives direction.

AWR and execution plans give evidence.

Testing gives confidence.

Only then should we apply changes.”

---

# Slide 31: Common Tuning Problems Covered

## Slide content

This slot covers:

## Undersized Memory Structures

ADDM may detect memory pressure or parsing issues.

## I/O Issues

ADDM may detect read/write bottlenecks.

## Database Configuration Issues

ADDM may recommend parameter or configuration review.

## Degradation Over Time

ADDM findings can be compared across periods.

---

## Trainer Explanation

“This slot maps to four common tuning problems.

ADDM is useful because it can detect not only SQL issues, but also memory, I/O, and configuration patterns.

It is also useful for degradation analysis when compared over time.”

---

# Slide 32: Slot 2 Summary

## Slide content

In this slot, we learned:

* ADDM analyzes AWR snapshot data
* AWR is the report; ADDM is the diagnosis
* ADDM findings include impact and recommendations
* Impact percentage helps prioritize
* Recommendation types include:

  * SQL tuning
  * Memory tuning
  * I/O tuning
  * Configuration tuning
  * Segment tuning
* ADDM recommendations must be validated

---

## Trainer Explanation

“Let’s summarize.

ADDM helps us quickly understand what Oracle thinks is the main performance issue.

But ADDM does not replace DBA thinking.

Our job is to validate its findings using AWR, execution plans, system views, and safe testing.”

---

# Slide 33: Transition to Slot 3

## Slide content

Next slot:

# SQL Tuning Advisor

We will learn:

* How to tune one specific SQL
* How SQL Tuning Advisor works
* What SQL Profiles are
* How to review advisor recommendations safely
* When to accept or reject recommendations

---

## Trainer Explanation

“In this slot, ADDM may point us to a problematic SQL.

In the next slot, we will learn how to take one SQL and run SQL Tuning Advisor on it.

So the flow is: AWR finds workload problem, ADDM gives diagnosis, SQL Tuning Advisor helps investigate a specific SQL.”

---

# Final Trainer Message for Slot 2

Use this closing line:

> “ADDM gives recommendations, not final decisions. A DBA must validate every recommendation before applying it.”
