Absolutely — here is **Day 1 — Slot 2 only**, focused on **Execution Plans: EXPLAIN PLAN vs DBMS_XPLAN**.

No indexing strategy deep dive.
No function-based index.
No plan fixing yet.
This slot is about **reading and comparing plans**.

---

# Day 1 — Slot 2

## 10:45 AM to 12:00 PM

# Execution Plans: EXPLAIN PLAN vs DBMS_XPLAN

## Slot Objective

By the end of this slot, trainees should be able to:

* Understand what an execution plan is
* Generate an estimated execution plan using `EXPLAIN PLAN`
* Generate an actual runtime plan using `DBMS_XPLAN.DISPLAY_CURSOR`
* Read basic plan columns
* Identify common plan operations
* Compare estimated rows vs actual rows
* Understand why cost is not the same as runtime

---

# Suggested Slot Flow

| Time          | Section                       |
| ------------- | ----------------------------- |
| 10:45 - 10:55 | What is an execution plan?    |
| 10:55 - 11:10 | EXPLAIN PLAN basics           |
| 11:10 - 11:25 | DBMS_XPLAN basics             |
| 11:25 - 11:40 | Reading plan columns          |
| 11:40 - 11:55 | Lab 2: Read and compare plans |
| 11:55 - 12:00 | Summary and discussion        |

---

# Slide 1: Slot Title

## Execution Plans: EXPLAIN PLAN vs DBMS_XPLAN

**Slide content:**

In this slot, we will learn how to read Oracle execution plans.

We will cover:

* What an execution plan is
* EXPLAIN PLAN
* DBMS_XPLAN
* Estimated plan vs actual runtime plan
* Important plan columns
* Common plan operations

---

## Trainer Explanation

“In Slot 1, we learned the tuning mindset.

We learned that we should not tune blindly.

Now we move to the first real diagnostic skill: reading execution plans.

An execution plan tells us how Oracle plans to get the data.

If a SQL is slow, the execution plan is one of the first things we should check.”

---

# Slide 2: What is an Execution Plan?

## Slide content:

An execution plan is Oracle’s step-by-step method for running a SQL statement.

It shows:

* Which table Oracle reads
* Whether Oracle uses full scan or index
* Join order
* Join method
* Sort operations
* Estimated rows
* Estimated cost
* Filter conditions

---

## Trainer Explanation

“An execution plan is like Oracle’s route map.

If SQL is asking for data, Oracle needs to decide the path.

Should it scan the full table?

Should it use an index?

Should it join table A first or table B first?

Should it sort the data?

The execution plan shows these decisions.

As DBAs, we read the plan to understand whether Oracle is taking an efficient route or an expensive route.”

---

# Slide 3: Simple Analogy

## Slide content:

Execution plan is like a travel route.

Same destination, different routes:

* Short road
* Long road
* Highway
* Traffic route
* Toll route

Same SQL, different plans:

* Full table scan
* Index scan
* Nested loops
* Hash join
* Sort operation

---

## Trainer Explanation

“Think about Google Maps.

You enter one destination, but there can be multiple routes.

One route may be shorter, one may be faster, one may avoid traffic.

Oracle also has many possible ways to run the same SQL.

The optimizer chooses one route.

That selected route is the execution plan.”

---

# Slide 4: Why Execution Plans Matter

## Slide content:

Execution plans help us answer:

* Is Oracle reading too much data?
* Is Oracle using an index?
* Is Oracle scanning the full table?
* Is Oracle sorting a lot of rows?
* Is the join method suitable?
* Are estimated rows close to actual rows?
* Is the optimizer making a wrong assumption?

---

## Trainer Explanation

“When a query is slow, execution plan gives us evidence.

Without a plan, we are guessing.

The plan helps us see whether Oracle is scanning too much data, missing an index, sorting too much, or choosing a poor join method.

But remember, the plan does not tell the whole story alone.

We also compare it with actual runtime statistics.”

---

# Slide 5: How Oracle Chooses Access Paths

## Slide content:

Oracle chooses access paths based on:

* SQL condition
* Table size
* Available indexes
* Statistics
* Selectivity
* Cost estimate
* Data distribution

Access path means:

```text
How Oracle reaches the data
```

Examples:

* Full table scan
* Index scan
* Rowid access

---

## Trainer Explanation

“Access path means the route Oracle uses to reach the rows.

If the condition is highly selective, Oracle may use an index.

If the query needs a large portion of the table, full table scan may be better.

This is important: full table scan is not always bad, and index scan is not always good.

Oracle decides based on cost and statistics.”

---

# Slide 6: Full Table Scan vs Index Scan

## Slide content:

## Full Table Scan

Oracle reads the table blocks directly.

Good when:

* Query needs many rows
* Table is small
* Index is not useful

## Index Scan

Oracle reads index first, then table rows.

Good when:

* Query needs few rows
* Filter is selective
* Index matches condition

---

## Trainer Explanation

“Beginners often think full table scan is always bad.

That is not true.

If the query needs 80% of the table, reading the full table may be faster than using an index.

Index scan is useful when the query needs a small number of rows.

So our job is not to blindly force index usage.

Our job is to check whether the chosen access path makes sense.”

---

# Slide 7: EXPLAIN PLAN Basics

## Slide content:

`EXPLAIN PLAN` shows the estimated execution plan.

Syntax:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

It shows what Oracle expects to do before actual execution.

---

## Trainer Explanation

“EXPLAIN PLAN asks Oracle: how would you run this SQL?

It does not actually run the query.

It only shows the estimated plan.

This is useful before executing a query, especially if the query is heavy.

But because it is estimated, it may not always match what happens during real execution.”

---

# Slide 8: EXPLAIN PLAN Limitation

## Slide content:

`EXPLAIN PLAN` may not show actual runtime behavior.

It does not show:

* Actual rows processed
* Actual buffer reads
* Actual execution statistics
* Runtime bind value impact
* Final adaptive plan behavior in some cases

Important:

```text
EXPLAIN PLAN = estimated route before journey
```

---

## Trainer Explanation

“This is very important.

EXPLAIN PLAN is useful, but it is not the full truth.

It is like checking a travel route before leaving.

But during the actual journey, traffic may be different.

Similarly, during actual SQL execution, Oracle may process more rows than expected, or runtime conditions may change.

That is why we also need DBMS_XPLAN.DISPLAY_CURSOR.”

---

# Slide 9: DBMS_XPLAN Basics

## Slide content:

`DBMS_XPLAN` is a package used to display execution plans.

Common options:

```sql
DBMS_XPLAN.DISPLAY
```

Shows plan from `EXPLAIN PLAN`.

```sql
DBMS_XPLAN.DISPLAY_CURSOR
```

Shows actual cursor execution plan from memory.

---

## Trainer Explanation

“DBMS_XPLAN is the standard way to display Oracle execution plans in readable format.

When we use EXPLAIN PLAN, we display it using DBMS_XPLAN.DISPLAY.

When we want to check the plan used by an actually executed SQL, we use DBMS_XPLAN.DISPLAY_CURSOR.

For tuning, DISPLAY_CURSOR is often more useful because it can show runtime evidence.”

---

# Slide 10: Actual Runtime Plan

## Slide content:

To see actual runtime plan:

```sql
ALTER SESSION SET statistics_level = ALL;
```

Run the SQL:

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

Then run:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

---

## Trainer Explanation

“This gives us the actual plan from the cursor cache.

The option `ALLSTATS LAST` shows statistics from the last execution.

This helps us compare estimated rows and actual rows.

If estimated rows are very different from actual rows, that is a sign that optimizer estimation may be wrong.

That can lead to poor plan choices.”

---

# Slide 11: Estimated Plan vs Actual Runtime Plan

## Slide content:

| Item               | EXPLAIN PLAN  | DISPLAY_CURSOR     |
| ------------------ | ------------- | ------------------ |
| Runs SQL?          | No            | SQL must run first |
| Shows estimate?    | Yes           | Yes                |
| Shows actual rows? | No            | Yes, with ALLSTATS |
| Good for           | Pre-check     | Real diagnosis     |
| Limitation         | Estimate only | Needs executed SQL |

---

## Trainer Explanation

“This table is very important.

EXPLAIN PLAN gives us the plan Oracle expects to use.

DISPLAY_CURSOR shows what happened when SQL actually ran.

For serious tuning, we usually want the actual runtime plan.

But EXPLAIN PLAN is still useful when we want to quickly inspect possible plan shape.”

---

# Slide 12: Main Teaching Point

## Slide content:

```text
EXPLAIN PLAN is like a map before the journey.

DBMS_XPLAN.DISPLAY_CURSOR is like checking what actually happened during the trip.
```

---

## Trainer Explanation

“This is the simplest way to remember the difference.

Before a journey, maps can predict the best route.

But after the journey, you know the real traffic, delays, and time taken.

Similarly, EXPLAIN PLAN predicts.

DISPLAY_CURSOR shows actual execution evidence.”

---

# Slide 13: Reading Important Plan Columns

## Slide content:

Important columns:

* `Id`
* `Operation`
* `Name`
* `Rows`
* `Bytes`
* `Cost`
* `Time`

Extra section:

* Predicate Information

---

## Trainer Explanation

“When you first see an execution plan, it can look scary.

But do not try to understand everything at once.

Start with the key columns.

Operation tells what Oracle is doing.

Name tells which table or index is involved.

Rows shows estimated rows.

Cost shows estimated work.

Predicate Information tells which conditions are used for access or filtering.”

---

# Slide 14: Operation Column

## Slide content:

`Operation` tells what Oracle is doing.

Examples:

* TABLE ACCESS FULL
* INDEX RANGE SCAN
* NESTED LOOPS
* HASH JOIN
* SORT ORDER BY
* FILTER

---

## Trainer Explanation

“The Operation column is the most important starting point.

It tells us the action Oracle performs at each step.

For example, TABLE ACCESS FULL means Oracle is scanning the table.

INDEX RANGE SCAN means Oracle is scanning part of an index.

SORT ORDER BY means Oracle is sorting data.

When reading plans, start with operations.”

---

# Slide 15: Name Column

## Slide content:

`Name` tells which object is being accessed.

Examples:

| Operation                   | Name            |
| --------------------------- | --------------- |
| TABLE ACCESS FULL           | TRANSACTIONS    |
| INDEX RANGE SCAN            | IDX_TXN_ACCOUNT |
| TABLE ACCESS BY INDEX ROWID | TRANSACTIONS    |

---

## Trainer Explanation

“The Name column shows the object name.

If Oracle is reading a table, name will show the table name.

If Oracle is using an index, name will show the index name.

This helps us understand which table or index is involved in that step.”

---

# Slide 16: Rows Column

## Slide content:

`Rows` means estimated number of rows.

Example:

```text
Rows = 20
```

Oracle estimates 20 rows from that step.

Important:

* Rows is usually estimated
* Wrong row estimate can cause wrong plan
* Compare estimated rows with actual rows

---

## Trainer Explanation

“Rows is cardinality estimate.

This is one of the most important things in the plan.

If Oracle estimates 10 rows but actually gets 1 million rows, it may choose a bad plan.

Many tuning problems are actually estimation problems.

That is why in the lab we compare estimated rows and actual rows.”

---

# Slide 17: Bytes Column

## Slide content:

`Bytes` means estimated amount of data returned from a step.

It depends on:

* Number of rows
* Row size
* Selected columns

Example:

```sql
SELECT *
```

Usually returns more bytes than selecting only required columns.

---

## Trainer Explanation

“Bytes tells estimated data volume.

If we use SELECT star, Oracle may return more data than needed.

More data means more memory, more network transfer, and more application processing.

So bytes helps us understand data volume.

It is not always the main issue, but it gives useful context.”

---

# Slide 18: Cost Column

## Slide content:

`Cost` is Oracle’s estimated work.

Important:

* Cost is not seconds
* Cost is used to compare plans
* Lower cost usually means less estimated work
* Wrong statistics can create wrong cost

---

## Trainer Explanation

“Cost is not execution time.

Do not say cost 100 means 100 seconds.

Cost is an internal estimate used by Oracle to compare possible plans.

It depends on estimated CPU, I/O, rows, and statistics.

So cost helps us understand optimizer thinking, but actual runtime must be checked separately.”

---

# Slide 19: Time Column

## Slide content:

`Time` is Oracle’s estimated time for that operation.

Important:

* It is also an estimate
* It may not match real execution time
* Use actual execution time for diagnosis

---

## Trainer Explanation

“The Time column in EXPLAIN PLAN is estimated time.

It may show 1 second, but the query may run longer.

So do not depend only on this column.

Use it as a rough indication, not final truth.”

---

# Slide 20: Predicate Information

## Slide content:

Predicate Information shows how conditions are applied.

Two common types:

```text
access
filter
```

## Access Predicate

Used to access rows efficiently.

## Filter Predicate

Applied after rows are read.

---

## Trainer Explanation

“Predicate Information is very useful.

It tells us whether Oracle is using a condition to access data or just filtering after reading data.

Access predicate is generally better because it helps Oracle reach rows directly.

Filter predicate may mean Oracle reads many rows first and then removes unwanted rows.

In Slot 2, just understand the difference. Later we will use this deeply during tuning.”

---

# Slide 21: Key Plan Operation — TABLE ACCESS FULL

## Slide content:

## TABLE ACCESS FULL

Oracle reads the table blocks directly.

Example:

```text
TABLE ACCESS FULL TRANSACTIONS
```

Common when:

* No useful index exists
* Query needs many rows
* Table is small
* Optimizer thinks full scan is cheaper

---

## Trainer Explanation

“TABLE ACCESS FULL means Oracle scans the table.

This is not automatically bad.

If you ask for all transactions, full scan is correct.

If you ask for one transaction from a huge table, full scan may be a problem.

So always connect the plan operation with the business requirement.”

---

# Slide 22: Key Plan Operation — INDEX RANGE SCAN

## Slide content:

## INDEX RANGE SCAN

Oracle scans a range of values from an index.

Example:

```text
INDEX RANGE SCAN IDX_TXN_ACCOUNT
```

Common when:

```sql
WHERE account_id = 5001
```

or

```sql
WHERE transaction_date BETWEEN date1 AND date2
```

---

## Trainer Explanation

“INDEX RANGE SCAN means Oracle is reading a range from an index.

This is common for non-unique filters.

For example, one account may have many transactions.

So Oracle scans the matching part of the index.

This is usually good when the query returns a small percentage of the table.”

---

# Slide 23: Key Plan Operation — INDEX UNIQUE SCAN

## Slide content:

## INDEX UNIQUE SCAN

Oracle uses a unique index to find one row.

Common when filtering by:

* Primary key
* Unique key

Example:

```sql
WHERE transaction_id = 10001
```

Expected:

```text
INDEX UNIQUE SCAN
```

---

## Trainer Explanation

“INDEX UNIQUE SCAN is used when Oracle knows the condition can return only one row.

For example, primary key lookup.

This is usually very efficient.

In banking, examples include transaction ID, customer ID if unique in customer master, account number if unique, or reference number.”

---

# Slide 24: Key Plan Operation — TABLE ACCESS BY INDEX ROWID

## Slide content:

## TABLE ACCESS BY INDEX ROWID

Oracle first finds row locations from the index, then visits the table.

Flow:

```text
Index scan
   ↓
Get ROWID
   ↓
Visit table row
```

---

## Trainer Explanation

“When Oracle uses an index, the index may not contain all required columns.

So Oracle first scans the index, gets row locations, and then visits the table using ROWID.

This operation is common after index scans.

It is fine for small row counts.

But if Oracle has to visit too many table rows, it can become expensive.”

---

# Slide 25: Key Plan Operation — NESTED LOOPS

## Slide content:

## NESTED LOOPS

Oracle reads rows from one table, then looks up matching rows in another table.

Good when:

* First table returns few rows
* Second table has useful index
* Join result is small

---

## Trainer Explanation

“Nested loops are like this:

For each row from table A, Oracle looks into table B.

This is very good when table A returns few rows and table B has an index.

But if table A returns many rows, nested loops can become expensive.

We will understand this more when we tune joins.”

---

# Slide 26: Key Plan Operation — HASH JOIN

## Slide content:

## HASH JOIN

Oracle builds a hash table from one input and joins it with another input.

Good when:

* Joining large data sets
* No highly selective index is useful
* Large reports or batch queries

---

## Trainer Explanation

“Hash join is commonly used for larger joins.

It is often seen in reporting queries, batch jobs, and dashboard queries.

It can be efficient for large data sets, but it may use memory.

Again, no join method is always good or always bad.

It depends on data volume.”

---

# Slide 27: Key Plan Operation — SORT ORDER BY

## Slide content:

## SORT ORDER BY

Oracle sorts rows for `ORDER BY`.

Example:

```sql
ORDER BY transaction_date DESC
```

Sorting can be expensive when:

* Many rows are sorted
* Memory is insufficient
* Sort spills to disk

---

## Trainer Explanation

“SORT ORDER BY appears when Oracle needs to sort result rows.

Sorting small data is fine.

Sorting millions of rows can be expensive.

In banking reports, sorting and grouping are common performance points.

In our customer statement query, ordering by transaction date may cause sorting.”

---

# Slide 28: Key Plan Operation — FILTER

## Slide content:

## FILTER

Oracle applies a condition to remove rows.

Example:

```text
FILTER
```

Can appear with:

* Subqueries
* Conditions
* Runtime checks

---

## Trainer Explanation

“FILTER means Oracle is applying a condition.

Sometimes filters are simple.

Sometimes filters are related to subqueries.

For now, remember that filter means Oracle is removing rows based on some condition.

Later, we will check whether filtering happens early or late.”

---

# Slide 29: Key Plan Operation — VIEW

## Slide content:

## VIEW

Oracle processes an inline view or transformed query block.

Example:

```sql
SELECT *
FROM (
  SELECT *
  FROM transactions
  WHERE status = 'SUCCESS'
);
```

Plan may show:

```text
VIEW
```

---

## Trainer Explanation

“VIEW in execution plan does not always mean database view object.

It can also mean an inline view or internal query block.

Oracle may transform queries internally.

So if you see VIEW in the plan, it means Oracle is processing a derived result set.”

---

# Slide 30: How to Read a Plan Tree

## Slide content:

Basic rule:

* Child operations happen first
* Parent operations consume child results
* Read from inside/deeper steps upward

Example:

```text
SELECT STATEMENT
  TABLE ACCESS FULL TRANSACTIONS
```

Oracle first scans `TRANSACTIONS`, then returns result.

---

## Trainer Explanation

“Execution plans are shown like a tree.

The lower or indented operations usually happen first.

Parent operations use the result of child operations.

At beginner level, do not worry about every detail.

Start by finding table access, index access, joins, and sorts.”

---

# Slide 31: Demo Query

## Slide content:

We will use this query:

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

We will check:

* Estimated plan
* Actual runtime plan
* Estimated rows
* Actual rows
* Predicate information

---

## Trainer Explanation

“This is our demo query.

It asks for transactions of one account.

This is a realistic banking query.

A customer, teller, or backend service may need to see transactions for a specific account.

Now we will check what Oracle expects to do and what actually happens.”

---

# Slide 32: Demo Step 1 — EXPLAIN PLAN

## Slide content:

Run:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Observe:

* Operation
* Name
* Rows
* Bytes
* Cost
* Predicate Information

---

## Trainer Explanation

“First, we use EXPLAIN PLAN.

This does not run the query.

It only asks Oracle to show the estimated plan.

We will look at the plan shape and identify whether Oracle expects to scan the table or use an index.

Do not focus on perfect tuning yet. Focus on reading.”

---

# Slide 33: Demo Step 2 — Actual Runtime Plan

## Slide content:

Run:

```sql
ALTER SESSION SET statistics_level = ALL;
```

Then execute:

```sql
SELECT *
FROM transactions
WHERE account_id = 5001;
```

Then run:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

---

## Trainer Explanation

“Now we run the actual query.

After that, DISPLAY_CURSOR shows the execution plan from the cursor cache.

With `ALLSTATS LAST`, we can see actual runtime information from the last execution.

This helps us compare estimates with reality.”

---

# Slide 34: Important Columns in DISPLAY_CURSOR

## Slide content:

With `ALLSTATS LAST`, you may see:

* `E-Rows` = Estimated rows
* `A-Rows` = Actual rows
* `Buffers` = Logical reads
* `Reads` = Physical reads
* `Starts` = Number of operation starts

---

## Trainer Explanation

“In DISPLAY_CURSOR with ALLSTATS, we get more useful columns.

E-Rows means estimated rows.

A-Rows means actual rows.

Buffers usually represent logical reads.

Reads usually represent physical disk reads.

This is very useful because now we can check if Oracle’s estimate was close to actual result.”

---

# Slide 35: Estimated Rows vs Actual Rows

## Slide content:

Example:

| Metric | Meaning                |
| ------ | ---------------------- |
| E-Rows | What Oracle expected   |
| A-Rows | What actually happened |

Problem example:

```text
E-Rows = 10
A-Rows = 100000
```

This means Oracle badly underestimated the result.

---

## Trainer Explanation

“This is one of the most important comparisons in tuning.

If E-Rows and A-Rows are close, optimizer had a good estimate.

If they are very different, optimizer may choose the wrong plan.

For example, if Oracle expects 10 rows, it may choose nested loops or index access.

But if actual rows are 100,000, that plan may become expensive.”

---

# Slide 36: Cost vs Actual Runtime

## Slide content:

Cost is estimated work.

Runtime is actual execution time.

They are related, but not the same.

A query can have:

* Low cost but slow runtime
* High cost but acceptable runtime
* Same cost but different runtime under load

---

## Trainer Explanation

“Do not say cost equals time.

Cost is estimate.

Runtime depends on real factors like cache, disk, CPU, concurrency, and waits.

During peak banking hours, the same query may run slower because the system is busy.

So we use cost to understand optimizer thinking, but we use runtime stats to understand reality.”

---

# Slide 37: Predicate Section

## Slide content:

Example predicate section:

```text
Predicate Information:
1 - filter("ACCOUNT_ID"=5001)
```

or:

```text
Predicate Information:
2 - access("ACCOUNT_ID"=5001)
```

Meaning:

* `access` = used to access data
* `filter` = applied after reading rows

---

## Trainer Explanation

“Predicate section tells us how Oracle applies the WHERE condition.

If the predicate is used as access, Oracle uses it to reach the data directly.

If it is used as filter, Oracle may read rows first and filter later.

This matters a lot when tuning.

For now, just remember: access is generally stronger than filter.”

---

# Slide 38: Lab 2 Objective

## Slide content:

## Lab 2: Read and Compare Plans

Participants will:

1. Run estimated plan using `EXPLAIN PLAN`
2. Run actual query
3. Display actual runtime plan
4. Compare estimated and actual behavior

Main comparison:

* Estimated rows vs actual rows
* Full table scan vs index scan
* Cost vs actual runtime
* Predicate section

---

## Trainer Explanation

“This lab is not about fixing yet.

It is about reading and comparing.

We want to build confidence with execution plans.

By the end of this lab, trainees should be able to say: Oracle estimated this, but actually this happened.”

---

# Lab 2 Setup

Use the same `transactions` table created in Slot 1.

If not created, create minimal setup again.

## Confirm table exists:

```sql
SELECT COUNT(*)
FROM transactions;
```

## Make sure statistics exist:

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

# Lab 2 Part A: Run EXPLAIN PLAN

## Query

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 5001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

## Trainees should record:

| Field          | Value         |
| -------------- | ------------- |
| Main operation |               |
| Table name     |               |
| Estimated rows |               |
| Cost           |               |
| Predicate type | access/filter |

---

## Trainer Explanation

“Ask everyone to run the EXPLAIN PLAN command first.

Tell them to identify the main operation.

Is it TABLE ACCESS FULL?

Is it using any index?

What rows does Oracle estimate?

What is the cost?

Do not worry if their values differ from yours. Different data size and stats can produce different numbers.”

---

# Lab 2 Part B: Run Actual Query

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT *
FROM transactions
WHERE account_id = 5001;
```

If too many rows appear, use this for controlled output:

```sql
SELECT *
FROM transactions
WHERE account_id = 5001
FETCH FIRST 20 ROWS ONLY;
```

But for full runtime comparison, the original query is better.

---

## Trainer Explanation

“Now we execute the actual SQL.

The original query gives the real full execution.

If output is too large, we can use FETCH FIRST 20 ROWS ONLY for display comfort.

But explain to trainees that adding FETCH changes the query behavior, so for proper comparison, use the original query when possible.”

---

# Lab 2 Part C: Display Actual Runtime Plan

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

If plan does not show actual rows, use:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

## Trainer Explanation

“Now we display the actual runtime plan.

We use NULL values because we want the last SQL executed in this session.

If it does not show full details, we add `+PREDICATE`.

In real troubleshooting, we often use SQL_ID to get a specific SQL plan, but that is not needed for this beginner lab.”

---

# Lab 2 Observation Table

Ask trainees to fill this.

| Comparison Point      | EXPLAIN PLAN  | DISPLAY_CURSOR |
| --------------------- | ------------- | -------------- |
| Main operation        |               |                |
| Object name           |               |                |
| Estimated rows        |               |                |
| Actual rows           | Not available |                |
| Cost                  |               |                |
| Logical reads/Buffers | Not available |                |
| Predicate             |               |                |
| Runtime evidence      | No            | Yes            |

---

# Lab 2 Questions

## Question 1

What is the main operation?

Expected answer may be:

```text
TABLE ACCESS FULL
```

or, if index exists:

```text
INDEX RANGE SCAN
```

---

## Question 2

Does EXPLAIN PLAN show actual rows?

Expected answer:

No. EXPLAIN PLAN shows estimated rows only.

---

## Question 3

Where do we see actual rows?

Expected answer:

In `DBMS_XPLAN.DISPLAY_CURSOR` with `ALLSTATS LAST`, using `A-Rows`.

---

## Question 4

Is cost equal to actual execution time?

Expected answer:

No. Cost is Oracle’s estimate of work, not seconds.

---

## Question 5

What does Predicate Information tell us?

Expected answer:

It shows how Oracle applied the WHERE condition, such as access or filter.

---

# Expected Lab Discussion

## Case 1: Full Table Scan Appears

If plan shows:

```text
TABLE ACCESS FULL TRANSACTIONS
```

Say:

“This means Oracle scanned the table to find rows for account_id 5001.

This may happen because no useful index exists, or Oracle thinks scanning the table is cheaper.

We will learn indexing strategy in Slot 3.”

---

## Case 2: Index Scan Appears

If plan shows:

```text
INDEX RANGE SCAN
TABLE ACCESS BY INDEX ROWID
```

Say:

“This means Oracle used an index to find matching rows, then visited the table for full row data.

This is usually expected when the filter is selective.

But we still check actual rows and buffers before declaring it good.”

---

## Case 3: Estimated Rows and Actual Rows Differ

If you see:

```text
E-Rows = 10
A-Rows = 5000
```

Say:

“Oracle expected 10 rows, but actually got 5000.

This means optimizer estimation is wrong.

Possible reasons may include stale statistics, skewed data, or missing histogram.

We will explore these later.”

---

# Slide 39: Common Tuning Problems Covered

## Slide content:

This slot connects to:

## Inefficient SQL

Execution plan shows if SQL reads too much data.

## Performance Regression

Plan comparison helps detect if SQL plan changed after:

* Statistics refresh
* New index
* Data growth
* Upgrade
* Deployment

## Short-Lived Performance Problems

Actual runtime plans help investigate what happened during execution.

---

## Trainer Explanation

“Execution plans help with many real problems.

For inefficient SQL, the plan shows expensive operations.

For regression, comparing old and new plans can show what changed.

For short-lived issues, actual runtime plan and cursor information can help us understand what happened during that execution.”

---

# Slide 40: Slot 2 Summary

## Slide content:

In this slot, we learned:

* Execution plan shows how Oracle runs SQL
* EXPLAIN PLAN shows estimated plan
* DISPLAY_CURSOR shows actual executed plan
* Important columns:

  * Operation
  * Name
  * Rows
  * Bytes
  * Cost
  * Time
  * Predicate Information
* E-Rows vs A-Rows is very important
* Cost is not equal to runtime
* Full scan is not always bad
* Index scan is not always good

---

## Trainer Explanation

“Let’s summarize.

Execution plan reading is a core DBA skill.

But do not just look for full table scan and panic.

Understand the business query, row count, access path, predicate, cost, and actual rows.

A good tuning decision comes from comparing estimate with reality.”

---

# Slide 41: Transition to Slot 3

## Slide content:

Next slot:

## Indexing Strategies for Banking Workloads

We will learn:

* Why indexes improve performance
* When indexes hurt performance
* B-tree indexes
* Composite indexes
* Function-based indexes
* Invisible indexes
* Index maintenance cost

---

## Trainer Explanation

“In this slot, we learned how to read whether Oracle is using full scan or index scan.

In the next slot, we will learn how indexes work, when they help, and when they hurt.

That will help us understand how to support important banking queries with the right access structure.”

---

# Final Trainer Message for Slot 2

Repeat this line:

> “EXPLAIN PLAN tells us what Oracle expects. DISPLAY_CURSOR tells us what actually happened.”

That is the key memory point for this slot.
