Absolutely — here is **Day 2 — Slot 4 only**, focused on:

# SQL Access Advisor + Memory/I/O Diagnosis Lab

## 2:45 PM to 5:00 PM

---

# Day 2 — Slot 4

## SQL Access Advisor + Memory/I/O Diagnosis Lab

## Slot Objective

By the end of this slot, trainees should understand:

* What SQL Access Advisor does
* Difference between SQL Tuning Advisor and SQL Access Advisor
* How workload-level recommendations are generated
* When index recommendations are useful
* When more indexes become harmful
* How materialized views and partitioning can help reporting workloads
* How to inspect basic memory and I/O symptoms using dynamic performance views

---

# Suggested Slot Flow

| Time        | Section                           |
| ----------- | --------------------------------- |
| 2:45 - 3:05 | SQL Access Advisor concept        |
| 3:05 - 3:25 | Recommendation types              |
| 3:25 - 3:45 | Index cost in banking systems     |
| 3:45 - 4:25 | Lab 8: SQL Access Advisor         |
| 4:25 - 4:45 | Mini Lab: Memory and I/O symptoms |
| 4:45 - 5:00 | Day 2 summary                     |

---

# Slide 1: Slot Title

## SQL Access Advisor + Memory/I/O Diagnosis Lab

**Slide content:**

In this slot, we will learn:

* SQL Access Advisor
* Workload-level tuning recommendations
* Index, materialized view, and partitioning suggestions
* When not to create more indexes
* Basic memory and I/O diagnosis

---

## Trainer Explanation

“In the previous slot, we used SQL Tuning Advisor for one SQL.

Now we move to workload-level tuning.

In real banking systems, we rarely tune only one query in isolation.

A dashboard, report module, or batch process may run many queries together.

SQL Access Advisor helps us evaluate a group of SQL statements and recommend better access structures.”

---

# Slide 2: What is SQL Access Advisor?

## Slide content:

SQL Access Advisor analyzes a workload and recommends access structures.

It may recommend:

* Indexes
* Materialized views
* Materialized view logs
* Partitioning strategies

Goal:

```text
Improve performance for a group of SQL statements
```

---

## Trainer Explanation

“SQL Access Advisor is different from SQL Tuning Advisor.

It looks at a workload, not just one SQL.

A workload means a set of SQL statements that represent a real business process.

For example, daily transaction report, branch dashboard, customer summary, and loan EMI report.

It then suggests access structures that may improve the workload.”

---

# Slide 3: Why Banks Need Workload-Level Tuning

## Slide content:

Banking systems often have groups of related queries:

* Branch dashboards
* Customer 360 view
* Loan reporting
* Daily reconciliation
* End-of-day processing
* Audit reports
* Transaction monitoring

Tuning one SQL may not be enough.

---

## Trainer Explanation

“In banking, one screen may run many queries.

A branch dashboard may show transaction count, total amount, failed transactions, loan collections, and account summaries.

If we tune only one query, the full screen may still be slow.

Workload-level tuning helps us improve a group of related SQL statements together.”

---

# Slide 4: SQL Tuning Advisor vs SQL Access Advisor

## Slide content:

| Area            | SQL Tuning Advisor             | SQL Access Advisor                     |
| --------------- | ------------------------------ | -------------------------------------- |
| Focus           | One SQL                        | Multiple SQL workload                  |
| Main purpose    | Tune statement                 | Improve access structures              |
| Recommendations | Profile, stats, index, rewrite | Index, materialized view, partitioning |
| Best for        | Specific slow SQL              | Reports/dashboards/workload            |
| Risk            | SQL-specific change            | Wider database impact                  |

---

## Trainer Explanation

“This comparison is important.

SQL Tuning Advisor is like a doctor checking one patient.

SQL Access Advisor is like analyzing traffic for an entire road network.

It may recommend new roads, shortcuts, or dedicated lanes.

In database terms, those are indexes, materialized views, or partitioning.”

---

# Slide 5: When to Use SQL Access Advisor

## Slide content:

Use SQL Access Advisor when:

* Multiple reports are slow
* Dashboard queries repeat often
* Many SQLs scan the same large tables
* Workload has similar filters or joins
* Reports aggregate large data
* You need index/materialized view recommendations
* You want workload-level access design

---

## Trainer Explanation

“SQL Access Advisor is useful when many queries are related.

For example, if multiple reports filter by branch_id and transaction_date, the advisor may suggest an index or materialized view.

It helps us think beyond one query and design access structures for a workload.”

---

# Slide 6: Recommendation Type — Indexes

## Slide content:

SQL Access Advisor may recommend indexes for:

* Frequently filtered columns
* Join columns
* Date range columns
* Grouping columns
* Sorting columns
* Composite access patterns

Example:

```sql
CREATE INDEX idx_txn_branch_date
ON transactions(branch_id, transaction_date);
```

---

## Trainer Explanation

“Indexes are the most common recommendation.

If the workload repeatedly filters transactions by branch and date, a composite index may help.

But again, the index must match real workload.

Do not create every suggested index blindly.”

---

# Slide 7: Recommendation Type — Materialized Views

## Slide content:

A materialized view stores precomputed query results.

Useful for:

* Daily summaries
* Branch-wise totals
* Monthly reports
* Aggregated dashboards
* Expensive joins
* Repeated reporting queries

Example use case:

```text
Branch-wise transaction total per day
```

---

## Trainer Explanation

“A materialized view is like storing a ready-made report table.

Instead of calculating totals from millions of transactions every time, Oracle can read precomputed results.

This is very useful for reports and dashboards.

But materialized views need refresh strategy, storage, and maintenance.”

---

# Slide 8: Materialized View Example

## Slide content:

Example:

```sql
CREATE MATERIALIZED VIEW mv_branch_daily_txn
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT branch_id,
       TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
GROUP BY branch_id, TRUNC(transaction_date);
```

Useful for:

```text
Daily branch transaction report
```

---

## Trainer Explanation

“This materialized view stores daily branch transaction totals.

Instead of scanning the full transactions table each time, reports can read from this summary.

This is powerful for dashboards, but we must decide how often it refreshes.

For banking reports, refresh timing is very important.”

---

# Slide 9: Recommendation Type — Partitioning

## Slide content:

Partitioning divides large tables into smaller logical parts.

Useful for:

* Large transaction tables
* Date-based data
* Monthly reports
* Data archival
* Faster pruning
* Easier maintenance

Example:

```text
Transactions partitioned by month
```

---

## Trainer Explanation

“Partitioning is very useful for large banking tables.

Transaction tables naturally grow by date.

If reports usually filter by date, partitioning by month can help Oracle scan only relevant partitions.

But partitioning is a bigger design decision and needs proper planning.”

---

# Slide 10: Partitioning Example Concept

## Slide content:

Without partitioning:

```text
Scan huge TRANSACTIONS table
```

With monthly partitioning:

```text
Scan only Jan 2026 partition
Scan only Feb 2026 partition
```

Benefit:

* Less data scanned
* Easier archival
* Better maintenance
* Faster date-based reports

---

## Trainer Explanation

“Imagine a file cabinet.

Without partitioning, all documents are in one huge drawer.

With partitioning, documents are arranged month-wise.

If you need March data, you open only the March drawer.

That is the basic idea.”

---

# Slide 11: When Not to Create More Indexes

## Slide content:

Do not create more indexes when:

* Existing indexes already support the query
* Table is DML-heavy
* Index helps only rarely used query
* Column has low selectivity
* Similar duplicate index exists
* Storage cost is high
* Batch inserts are already slow
* Recommendation is not tested

---

## Trainer Explanation

“This is a very important production lesson.

More indexes do not always mean better performance.

Every index has maintenance cost.

If a table receives thousands of inserts per minute, extra indexes can slow it down.

So index decisions must consider both read and write workload.”

---

# Slide 12: Index Impact on DML-Heavy Banking Systems

## Slide content:

DML-heavy tables:

* `transactions`
* `payments`
* `audit_logs`
* `fund_transfers`
* `loan_emi_payments`

Extra indexes affect:

* INSERT speed
* UPDATE speed
* DELETE speed
* Storage usage
* Redo generation
* Batch load time

---

## Trainer Explanation

“In banking, transaction-heavy tables are sensitive.

Every new transaction insert may need to update multiple indexes.

This increases redo, storage, and execution time.

So we must balance read performance and write performance.

A report index should not damage core transaction processing.”

---

# Slide 13: Workload for Lab 8

## Slide content:

We will use multiple banking queries:

1. Daily transaction report
2. Customer account summary
3. Branch-wise transaction volume
4. Loan EMI due report

Goal:

```text
Evaluate SQL Access Advisor recommendations for workload-level tuning
```

---

## Trainer Explanation

“This lab uses multiple queries.

The idea is to simulate a small reporting workload.

We are not tuning one SQL only.

We want to see what access structures Oracle may recommend for the group.”

---

# Slide 14: Lab 8 Objective

## Slide content:

Participants will:

* Create or identify workload SQL
* Run SQL Access Advisor
* Review recommendations
* Identify suggested indexes/materialized views
* Evaluate risk and benefit
* Decide whether recommendations are safe

---

## Trainer Explanation

“The goal is not just to generate a report.

The goal is to evaluate it.

If the advisor recommends three indexes, participants should ask: which one is useful, which one is risky, and which one should be tested first?”

---

# Slide 15: Lab Prerequisites

## Slide content:

Before lab, confirm:

* Required privileges
* Proper Oracle license/permission
* Tables exist:

  * `transactions`
  * `customers`
  * `accounts`
  * `loans` or `loan_payments`
* Statistics are gathered
* Workload queries are available

---

## Trainer Explanation

“SQL Access Advisor also requires proper licensing and privileges.

In real bank environments, always confirm approval before using licensed packs.

For lab, we need tables and data ready.”

---

# Slide 16: Optional Loan Payments Table

## Slide content:

If loan table does not exist, create sample table:

```sql
DROP TABLE loan_payments PURGE;

CREATE TABLE loan_payments (
    payment_id     NUMBER PRIMARY KEY,
    customer_id    NUMBER,
    loan_id        NUMBER,
    branch_id      NUMBER,
    due_date       DATE,
    paid_date      DATE,
    emi_amount     NUMBER(12,2),
    status         VARCHAR2(20)
);
```

---

## Trainer Explanation

“For the loan EMI due report, we need a simple loan payment table.

This table stores EMI due dates, payment status, amount, and branch.

It is enough for our lab scenario.”

---

# Slide 17: Insert Loan Payment Data

## Slide content:

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO loan_payments (
      payment_id, customer_id, loan_id, branch_id,
      due_date, paid_date, emi_amount, status
    )
    VALUES (
      i,
      MOD(i, 5000) + 1,
      MOD(i, 20000) + 1,
      MOD(i, 50) + 1,
      SYSDATE - MOD(i, 365),
      CASE WHEN MOD(i, 4) = 0 THEN NULL ELSE SYSDATE - MOD(i, 300) END,
      ROUND(DBMS_RANDOM.VALUE(100, 5000), 2),
      CASE MOD(i, 4)
        WHEN 0 THEN 'DUE'
        WHEN 1 THEN 'PAID'
        WHEN 2 THEN 'OVERDUE'
        ELSE 'PENDING'
      END
    );

    IF MOD(i, 10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/
COMMIT;
```

---

## Trainer Explanation

“This creates sample EMI/payment data.

Some rows are due, some paid, some overdue.

This helps us create a realistic banking report query.”

---

# Slide 18: Gather Statistics

## Slide content:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'LOAN_PAYMENTS', cascade => TRUE);
END;
/
```

---

## Trainer Explanation

“Before advisor analysis, gather statistics.

The advisor depends on optimizer information.

Bad or missing statistics can lead to poor recommendations.”

---

# Slide 19: Workload Query 1 — Daily Transaction Report

## Slide content:

```sql
SELECT TRUNC(transaction_date) AS txn_day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE, -1)
GROUP BY TRUNC(transaction_date)
ORDER BY txn_day;
```

Purpose:

```text
Daily transaction summary for last month
```

---

## Trainer Explanation

“This query summarizes transaction volume by day.

It is common for operations and reporting teams.

It filters by date, groups by day, and sorts result.

The advisor may suggest an index, materialized view, or partitioning depending on workload and table size.”

---

# Slide 20: Workload Query 2 — Customer Account Summary

## Slide content:

```sql
SELECT c.customer_id,
       c.full_name,
       COUNT(a.account_id) AS total_accounts,
       SUM(a.balance) AS total_balance
FROM customers c
JOIN accounts a
  ON c.customer_id = a.customer_id
WHERE c.status = 'ACTIVE'
GROUP BY c.customer_id, c.full_name;
```

Purpose:

```text
Customer-level account summary
```

---

## Trainer Explanation

“This query joins customers and accounts.

It summarizes accounts and balances for active customers.

The advisor may look at join columns, filtering column, and grouping pattern.”

---

# Slide 21: Workload Query 3 — Branch-Wise Transaction Volume

## Slide content:

```sql
SELECT branch_id,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE, -3)
GROUP BY branch_id
ORDER BY total_amount DESC;
```

Purpose:

```text
Branch performance dashboard
```

---

## Trainer Explanation

“This query is useful for branch-wise dashboard.

It filters recent transactions and groups by branch.

This type of query may benefit from branch/date access structures or summary tables.”

---

# Slide 22: Workload Query 4 — Loan EMI Due Report

## Slide content:

```sql
SELECT branch_id,
       COUNT(*) AS due_count,
       SUM(emi_amount) AS total_due
FROM loan_payments
WHERE status IN ('DUE', 'OVERDUE')
AND due_date <= SYSDATE
GROUP BY branch_id
ORDER BY total_due DESC;
```

Purpose:

```text
Loan EMI due and overdue report
```

---

## Trainer Explanation

“This query shows EMI due or overdue by branch.

It is a typical banking collection report.

It filters by status and due date, then groups by branch.

The advisor may suggest an index on status, due_date, or branch_id depending on data distribution.”

---

# Slide 23: Lab 8 — Create Advisor Task

## Slide content:

Create task:

```sql
DECLARE
  l_task_id NUMBER;
BEGIN
  l_task_id := DBMS_ADVISOR.CREATE_TASK(
    advisor_name => 'SQL Access Advisor',
    task_name    => 'bank_workload_access_task'
  );
END;
/
```

---

## Trainer Explanation

“This creates a SQL Access Advisor task.

The task will hold our workload and analysis settings.

Think of it as creating a container for advisor analysis.”

---

# Slide 24: Add Workload SQL

## Slide content:

Example using SQL text:

```sql
DECLARE
  l_sql CLOB;
BEGIN
  l_sql := q'[
    SELECT branch_id,
           COUNT(*) AS txn_count,
           SUM(amount) AS total_amount
    FROM transactions
    WHERE transaction_date >= ADD_MONTHS(SYSDATE, -3)
    GROUP BY branch_id
    ORDER BY total_amount DESC
  ]';

  DBMS_ADVISOR.ADD_SQLWKLD_STATEMENT(
    workload_name => 'BANK_WORKLOAD',
    module        => 'BANK_REPORTS',
    action        => 'BRANCH_TXN_VOLUME',
    sql_text      => l_sql
  );
END;
/
```

---

## Trainer Explanation

“SQL Access Advisor works from workload.

Depending on environment and Oracle version, workload setup can be done using SQL workload objects or advisor interfaces.

The key concept is: we feed multiple SQL statements to the advisor.

If setup becomes too complex in class, you can also demonstrate using Enterprise Manager or a prepared script.”

---

# Slide 25: Practical Trainer Note

## Slide content:

If SQL Access Advisor setup is complex in your lab environment:

Use this fallback approach:

1. Show workload queries
2. Generate execution plans
3. Manually identify repeated access patterns
4. Discuss what advisor would likely recommend
5. Compare with advisor report if available

---

## Trainer Explanation

“This is important.

SQL Access Advisor setup can vary by environment.

If participants face privilege or package issues, do not get stuck.

The learning goal is workload-level access design.

You can still teach the concept using workload queries and execution plans.”

---

# Slide 26: Execute Advisor Task

## Slide content:

Generic flow:

```sql
BEGIN
  DBMS_ADVISOR.EXECUTE_TASK(
    task_name => 'bank_workload_access_task'
  );
END;
/
```

Check task status:

```sql
SELECT task_name, status
FROM dba_advisor_tasks
WHERE task_name = 'bank_workload_access_task';
```

---

## Trainer Explanation

“After workload is added and task is configured, execute the advisor task.

Then check whether it completed.

If it fails, check privileges, workload setup, or advisor parameters.”

---

# Slide 27: View Recommendations

## Slide content:

```sql
SELECT rec_id,
       rank,
       benefit
FROM dba_advisor_recommendations
WHERE task_name = 'bank_workload_access_task'
ORDER BY rank;
```

View actions:

```sql
SELECT rec_id,
       action_id,
       command,
       attr1,
       attr2
FROM dba_advisor_actions
WHERE task_name = 'bank_workload_access_task'
ORDER BY rec_id, action_id;
```

---

## Trainer Explanation

“These views show recommendations and actions.

Look for what Oracle suggests.

It may suggest indexes, materialized views, or other structures.

But again, this is not automatic approval.”

---

# Slide 28: Evaluate Recommendations

## Slide content:

For each recommendation, ask:

* Which SQL benefits?
* What is estimated benefit?
* Is it index/materialized view/partitioning?
* Is the table DML-heavy?
* Does similar index already exist?
* What is maintenance cost?
* Is the recommendation safe?

---

## Trainer Explanation

“This is the real DBA work.

The advisor may give many recommendations.

Participants must decide which recommendation makes sense.

A high-benefit index on a DML-heavy table may still be risky.

A materialized view may help reports but needs refresh design.”

---

# Slide 29: Lab 8 Worksheet

## Slide content:

| Recommendation | Type              | Benefit | Affected SQL | Risk | Test Needed |
| -------------- | ----------------- | ------: | ------------ | ---- | ----------- |
|                | Index             |         |              |      |             |
|                | Materialized View |         |              |      |             |
|                | Partitioning      |         |              |      |             |

---

## Trainer Explanation

“Ask participants to fill this worksheet.

Do not allow them to simply say ‘advisor suggested index’.

They must explain benefit and risk.

This helps them think like production DBAs.”

---

# Slide 30: Mini Lab — Memory and I/O Symptoms

## Slide content:

Now we inspect system-level symptoms using views:

* `v$system_event`
* `v$sysstat`
* `v$pgastat`
* `v$sgainfo`

Goal:

```text
Identify whether issue looks like SQL, memory, I/O, or configuration
```

---

## Trainer Explanation

“Now we shift to a mini lab.

AWR and ADDM are report-based.

But DBAs also use dynamic performance views to inspect current or cumulative symptoms.

We will check basic memory and I/O indicators.”

---

# Slide 31: v$system_event

## Slide content:

```sql
SELECT *
FROM v$system_event
ORDER BY time_waited DESC;
```

Purpose:

* Shows cumulative wait events
* Helps identify major wait categories
* Useful for spotting I/O, locking, commit, or concurrency waits

---

## Trainer Explanation

“This view shows wait events accumulated by the instance.

Sort by time_waited to see where sessions have spent time waiting.

If I/O waits are high, investigate SQL and storage.

If row lock waits are high, investigate locking.

This is not a full diagnosis by itself, but it gives direction.”

---

# Slide 32: Common Wait Event Signals

## Slide content:

| Wait Event                    | Possible Direction          |
| ----------------------------- | --------------------------- |
| db file sequential read       | Index/single-block I/O      |
| db file scattered read        | Full scans/multiblock reads |
| direct path read              | Large scans/direct reads    |
| log file sync                 | Commit latency              |
| enq: TX - row lock contention | Locking                     |
| buffer busy waits             | Hot blocks/concurrency      |

---

## Trainer Explanation

“This table helps interpret common wait events.

Do not memorize blindly.

Use it as a starting point.

For example, db file scattered read may indicate full scans, but you still need to find which SQL is causing those scans.”

---

# Slide 33: v$sysstat — Physical Reads

## Slide content:

```sql
SELECT *
FROM v$sysstat
WHERE name LIKE '%physical reads%';
```

Purpose:

* Shows physical read statistics
* Helps understand disk read activity
* Useful for I/O investigation

---

## Trainer Explanation

“This query shows physical read-related statistics.

Physical reads mean data blocks had to be read from disk or storage, not just memory.

High physical reads can indicate large scans, poor access paths, or cold cache.

But again, connect this with SQL and AWR sections.”

---

# Slide 34: v$pgastat

## Slide content:

```sql
SELECT *
FROM v$pgastat;
```

Purpose:

* Shows PGA memory usage
* Helps diagnose sort/hash memory pressure
* Useful for checking workarea behavior

Look for:

* aggregate PGA target parameter
* total PGA allocated
* cache hit percentage
* over allocation count

---

## Trainer Explanation

“PGA is used for operations like sorting, hashing, and session memory.

If reports do large sorts or hash joins, PGA pressure may appear.

If memory is insufficient, operations may spill to TEMP, causing slower performance.

This view helps us inspect PGA-level symptoms.”

---

# Slide 35: v$sgainfo

## Slide content:

```sql
SELECT *
FROM v$sgainfo;
```

Purpose:

* Shows SGA component sizes
* Helps understand memory allocation
* Useful for checking buffer cache, shared pool, large pool

Important components:

* Buffer Cache
* Shared Pool
* Large Pool
* Redo Buffers

---

## Trainer Explanation

“SGA is shared memory for the database instance.

Buffer cache stores data blocks.

Shared pool stores parsed SQL and execution plans.

If shared pool is under pressure, parsing may increase.

If buffer cache is too small, physical reads may increase.

This view gives basic SGA size information.”

---

# Slide 36: Mini Lab Task

## Slide content:

Participants should answer:

| Check          | Observation | Possible Meaning             |
| -------------- | ----------- | ---------------------------- |
| Top wait event |             | CPU/I/O/locking/commit issue |
| Physical reads |             | I/O pressure or heavy scans  |
| PGA stats      |             | Sort/hash memory pressure    |
| SGA info       |             | Memory sizing/config context |

Final diagnosis:

```text
SQL problem / Memory pressure / I/O pressure / Configuration issue
```

---

## Trainer Explanation

“This worksheet is about interpretation.

Participants should not just paste output.

They should say what the output suggests.

For example: high physical reads plus SQL ordered by reads may indicate I/O caused by SQL access pattern.”

---

# Slide 37: How to Decide the Problem Type

## Slide content:

## SQL Problem

* Same SQL high in AWR sections
* High buffer gets
* High reads
* Bad plan

## Memory Pressure

* Sorts spill
* PGA pressure
* Shared pool pressure
* Excessive parsing

## I/O Pressure

* High physical reads
* I/O wait events
* Hot segments

## Configuration Issue

* Memory settings unsuitable
* Parameter-related ADDM recommendation
* Repeated system-level symptoms

---

## Trainer Explanation

“This slide gives a simple diagnosis framework.

Usually problems overlap.

For example, bad SQL can cause I/O pressure.

So do not treat these categories as separate boxes.

Use them to decide where to investigate next.”

---

# Slide 38: Common Tuning Problems Covered

## Slide content:

This slot covers:

* Undersized memory structures
* I/O issues
* Database configuration issues
* Performance degradation over time

How?

* SQL Access Advisor shows access design problems
* Memory views show memory pressure
* I/O views show read symptoms
* Baselines and AWR help compare degradation

---

## Trainer Explanation

“This slot connects system-level symptoms with workload design.

If performance degrades over time, maybe transaction tables grew and access structures no longer support the workload.

If I/O increased, maybe reports scan too much data.

If memory pressure appears, maybe sorts and hash joins are too large.”

---

# Slide 39: Day 2 Outcome

## Slide content:

By the end of Day 2, participants should be able to:

* Generate and read AWR reports
* Use ADDM for diagnosis
* Use SQL Tuning Advisor safely
* Use SQL Access Advisor for workload-level recommendations
* Connect SQL symptoms with system-level bottlenecks

---

## Trainer Explanation

“This is the Day 2 outcome.

Yesterday, we learned single SQL and execution plans.

Today, we learned system-level diagnosis.

Now participants should be able to move from user complaint to AWR, ADDM, advisor tools, and basic memory/I/O checks.”

---

# Slide 40: Day 2 Final Summary

## Slide content:

Day 2 key flow:

```text
User complaint
   ↓
AWR report
   ↓
ADDM diagnosis
   ↓
SQL Tuning Advisor for one SQL
   ↓
SQL Access Advisor for workload
   ↓
Memory/I/O views for system symptoms
   ↓
Validate before applying fix
```

---

## Trainer Explanation

“This is the complete Day 2 flow.

AWR tells us what happened.

ADDM gives diagnosis.

SQL Tuning Advisor helps tune one SQL.

SQL Access Advisor helps with workload access design.

Dynamic views help inspect memory and I/O symptoms.

But every recommendation must be validated.”

---

# Slide 41: Transition to Day 3

## Slide content:

Tomorrow we move to advanced production tuning:

* SQL Plan Management
* Plan baselines
* Plan evolution
* Bind peeking
* Adaptive cursor sharing
* Hints and SQL Profiles
* Locking and concurrency
* Final banking case study

---

## Trainer Explanation

“Tomorrow we focus on advanced production issues.

Sometimes SQL is tuned, but the plan changes later.

Sometimes the same SQL behaves differently for different bind values.

Sometimes locking and concurrency create slowness.

Day 3 will cover those real-world advanced cases.”

---

# Final Trainer Message for Day 2

Use this closing line:

> “Day 1 taught us how to read one SQL. Day 2 taught us how to diagnose the whole workload.”
