Absolutely. Here is **Day 1 — Slot 1 only**, cleanly scoped.

No deep execution plan teaching.
No index creation.
No fixing yet.
Only **thinking, observing, and collecting evidence before tuning**.

---

# Day 1 — Slot 1

## 9:00 AM to 10:30 AM

# Introduction to SQL Tuning & Oracle Optimizer

## Slot Objective

By the end of this slot, trainees should understand:

* What SQL tuning means
* How SQL tuning is different from database performance tuning
* Why banking systems become slow
* How Oracle processes a SQL statement
* What the optimizer does
* Basic tuning terms like cost, cardinality, selectivity, access path, join method, and statistics
* How to identify an expensive SQL pattern before applying any fix

---

# Suggested Slot Flow

| Time          | Section                            |
| ------------- | ---------------------------------- |
| 9:00 - 9:10   | Slot introduction                  |
| 9:10 - 9:25   | What is SQL tuning?                |
| 9:25 - 9:40   | SQL tuning vs database tuning      |
| 9:40 - 10:00  | Oracle query lifecycle + optimizer |
| 10:00 - 10:15 | Important tuning concepts          |
| 10:15 - 10:30 | Banking example + lab briefing     |

The hands-on lab can continue immediately after explanation or be used as the transition into Slot 2.

---

# Slide 1: Slot Title

## Introduction to SQL Tuning & Oracle Optimizer

**Slide content:**

Before using advanced tuning tools, we first need to understand how Oracle thinks.

In this slot, we will learn:

* What SQL tuning means
* Why SQL becomes slow
* How Oracle processes SQL
* What the optimizer does
* What evidence to collect before tuning

---

## Trainer Explanation

“Before we start using tools like AWR, ADDM, SQL Tuning Advisor, or even detailed execution plans, we need to build the right foundation.

Many times, when a query is slow, people immediately say: create an index, add a hint, or rewrite the SQL.

But in production, that is risky.

A good DBA first observes the problem, collects evidence, understands how Oracle is processing the SQL, and only then applies a fix.

So this first slot is about building that tuning mindset.”

---

# Slide 2: What is SQL Tuning?

## Slide content:

SQL tuning means improving the way a SQL statement runs.

The goal is to reduce unnecessary database work.

A well-tuned SQL should use:

* Less CPU
* Less memory
* Less disk I/O
* Fewer logical reads
* Better execution path
* Less execution time

---

## Trainer Explanation

“SQL tuning is not only about making a query fast.

A query may run in 2 seconds today, but if it reads 10 lakh rows unnecessarily, it can become a problem when many users run it together.

So SQL tuning means making the SQL efficient.

Efficient means Oracle should do only the work required, not extra work.

For example, if we need the last 3 months of transactions for one customer, Oracle should not scan 5 years of data for all customers.”

---

# Slide 3: Simple SQL Tuning Example

## Slide content:

Problem query:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
ORDER BY transaction_date DESC;
```

Possible questions:

* How many rows does this customer have?
* Is Oracle reading too much data?
* Is sorting expensive?
* Is the query returning unnecessary columns?
* Is the application fetching too much history?
* Is the issue SQL, data volume, or system load?

---

## Trainer Explanation

“Let’s take a very common banking example: customer statement.

A user opens the customer statement screen, and the application runs this query.

At first glance, this query looks normal.

It filters by customer and sorts by transaction date.

But we cannot say whether it is good or bad just by looking at it.

Maybe customer 101 has only 20 transactions. Then it is fine.

Maybe customer 101 has 5 lakh transactions. Then it can be expensive.

Maybe the application only needs the latest 50 records, but the SQL is fetching everything.

So the first rule is: never tune based only on opinion. Tune based on evidence.”

---

# Slide 4: SQL Tuning vs Database Performance Tuning

## Slide content:

## SQL Tuning

Focuses on one SQL statement or a group of SQL statements.

Examples:

* Query reads too many rows
* Query has poor filters
* Query uses expensive sorting
* Query has bad join logic
* Query returns unnecessary data

## Database Performance Tuning

Focuses on the whole database environment.

Examples:

* CPU pressure
* Memory shortage
* Disk I/O bottleneck
* Locking
* Concurrency
* Configuration issues

---

## Trainer Explanation

“SQL tuning and database performance tuning are related, but they are not the same.

SQL tuning is like fixing one bad route.

Database performance tuning is like managing the entire city traffic system.

If one SQL is badly written and consuming 70% of database time, then tuning that SQL can improve the whole system.

But sometimes SQL is fine, and the real issue is memory, disk, locking, or too many users.

As DBAs, we must learn to separate these two.”

---

# Slide 5: Why Banking Systems Become Slow

## Slide content:

Banking systems become slow because of:

* Large transaction tables
* High number of users
* End-of-day or month-end reports
* Poor SQL design
* Application fetching too much data
* Missing or stale statistics
* Heavy sorting and grouping
* Locking between sessions
* I/O pressure
* Sudden data growth

---

## Trainer Explanation

“In a banking system, data grows every day.

Transactions, audit logs, fund transfers, account statements, loan payments — these tables keep increasing.

A query that was fast 6 months ago can become slow today because the data volume changed.

Also, banking applications usually have many users working at the same time.

So even a small inefficient query can become a big issue when hundreds of users run it repeatedly.

That is why we tune not only for one execution, but for repeated production workload.”

---

# Slide 6: Banking Performance Examples

## Slide content:

| Banking Area       | Possible Performance Problem  |
| ------------------ | ----------------------------- |
| Customer statement | Too many transactions fetched |
| Fund transfer      | Locking or slow update        |
| Audit report       | Large table scan              |
| Branch dashboard   | Multiple heavy queries        |
| Loan report        | Complex joins and sorting     |
| Login history      | Fast-growing audit data       |

---

## Trainer Explanation

“Let’s connect this to real banking work.

A customer statement screen may be slow because it is fetching too much history.

A fund transfer may be slow because another session is locking the same account row.

A branch dashboard may be slow because it runs 10 heavy queries at once.

A loan report may be slow because it joins many large tables.

So when someone says ‘database is slow’, we should ask: which module, which SQL, which time, which user, and what changed?”

---

# Slide 7: Oracle Query Lifecycle

## Slide content:

When Oracle receives a SQL statement, it goes through four major stages:

1. Parse
2. Optimize
3. Execute
4. Fetch

```text
SQL submitted
   ↓
Parse
   ↓
Optimize
   ↓
Execute
   ↓
Fetch rows
```

---

## Trainer Explanation

“Now let’s understand what happens internally when Oracle receives a SQL query.

Oracle does not simply run the SQL immediately.

First it parses the SQL.

Then it optimizes it.

Then it executes the chosen plan.

Then it returns rows to the application.

Performance problems can happen in any of these stages.

For example, parsing can be expensive if the application does not use bind variables.

Optimization can go wrong if statistics are stale.

Execution can be slow if Oracle reads too many blocks.

Fetching can be slow if the application asks for too many rows.”

---

# Slide 8: Stage 1 — Parse

## Slide content:

During parse, Oracle checks:

* Is SQL syntax valid?
* Do tables and columns exist?
* Does the user have permission?
* Is the same SQL already available in shared pool?
* Can Oracle reuse an existing cursor?

Example:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

---

## Trainer Explanation

“Parsing is the first stage.

Oracle checks whether the SQL is valid.

It checks table names, column names, permissions, and whether this SQL has already been parsed before.

In banking applications, if SQL is written with hard-coded values again and again, Oracle may parse too much.

For example:

```sql
WHERE customer_id = 101
WHERE customer_id = 102
WHERE customer_id = 103
```

These may be treated as different SQL statements.

Later we will discuss bind variables, but for now remember: parsing is also part of performance.”

---

# Slide 9: Stage 2 — Optimize

## Slide content:

During optimization, Oracle decides how to run the SQL.

The optimizer chooses:

* Which table to access first
* Whether to use full scan or index
* Which join method to use
* Whether sorting is needed
* Estimated number of rows
* Estimated cost

---

## Trainer Explanation

“This is one of the most important stages.

The optimizer is Oracle’s decision-making engine.

It looks at the SQL, table statistics, indexes, data distribution, and then decides the execution approach.

For the same query, Oracle may have many possible ways to run it.

The optimizer tries to choose the cheapest option based on available information.

But if the information is wrong, the decision can also be wrong.”

---

# Slide 10: Stage 3 — Execute

## Slide content:

During execution, Oracle actually runs the chosen plan.

It may:

* Read table blocks
* Read index blocks
* Filter rows
* Join tables
* Sort rows
* Aggregate data
* Apply conditions

---

## Trainer Explanation

“After optimization, Oracle executes the selected plan.

This is where actual work happens.

Oracle may read data from memory, or it may need to read from disk.

It may filter rows, join tables, sort data, or group data.

When we say a query is expensive, we usually mean this execution stage is doing too much work.

But the reason may come from earlier stages, like wrong optimizer estimates.”

---

# Slide 11: Stage 4 — Fetch

## Slide content:

During fetch, Oracle returns rows to the application.

Performance can be affected by:

* Number of rows returned
* Network round trips
* Application fetch size
* `SELECT *`
* No pagination
* Too much historical data

---

## Trainer Explanation

“Fetching is often ignored, but it is very important.

Sometimes Oracle executes the query quickly, but the application fetches too many rows.

For example, the screen only displays 50 transactions, but SQL returns 50,000 rows.

That is not only a database problem. That is also an application design problem.

This is why we ask: how much data is actually needed by the business screen?”

---

# Slide 12: Oracle Optimizer Architecture

## Slide content:

The optimizer uses many inputs to choose a plan:

* SQL text
* Table statistics
* Column statistics
* Index statistics
* System statistics
* Object size
* Available indexes
* Data distribution
* Optimizer parameters

Output:

* Execution plan

---

## Trainer Explanation

“Think of the optimizer like Google Maps.

If you want to go from one place to another, Google Maps checks distance, traffic, roads, and time.

Oracle optimizer does something similar.

It checks data size, indexes, statistics, filters, joins, and estimates the best route to get the data.

The final output of the optimizer is the execution plan.

We will study execution plans deeply in Slot 2. For now, just understand that the optimizer is responsible for choosing how SQL will run.”

---

# Slide 13: Cost-Based Optimizer Overview

## Slide content:

Oracle mainly uses the Cost-Based Optimizer, also called CBO.

CBO compares possible plans and chooses the one with the lowest estimated cost.

Cost is based on estimated:

* CPU work
* I/O work
* Number of rows
* Number of blocks
* Sort work
* Join work

---

## Trainer Explanation

“The Cost-Based Optimizer estimates the cost of different possible plans.

For example, should Oracle scan the whole transactions table?

Or should it use an index?

Should it join table A first or table B first?

Oracle estimates the cost of each option and chooses the plan with the lowest cost.

But remember: cost is an estimate, not actual time.

A low-cost plan can still perform badly if Oracle’s estimates are wrong.”

---

# Slide 14: Important Concept — Cost

## Slide content:

## Cost

Cost means Oracle’s estimated amount of work for a plan.

Important:

* Cost is not equal to seconds
* Cost is used to compare plans
* Lower cost usually means less expected work
* Wrong estimates can produce wrong cost

Example:

```text
Plan A cost: 50
Plan B cost: 500
```

Oracle usually chooses Plan A.

---

## Trainer Explanation

“When beginners see cost, they often think cost means execution time.

That is not correct.

Cost is Oracle’s internal estimate of work.

It helps Oracle compare plans.

If one plan has cost 50 and another has cost 500, Oracle will usually choose the lower-cost plan.

But cost depends on statistics and estimates.

So if statistics are wrong, cost can mislead the optimizer.”

---

# Slide 15: Important Concept — Cardinality

## Slide content:

## Cardinality

Cardinality means estimated number of rows returned by an operation.

Example:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

If Oracle estimates this will return 200 rows, cardinality is 200.

Why it matters:

* Wrong cardinality can cause wrong plans
* Join method depends on estimated rows
* Index choice depends on estimated rows

---

## Trainer Explanation

“Cardinality is one of the most important concepts in SQL tuning.

It means how many rows Oracle expects.

If Oracle expects 10 rows, it may choose an index.

If Oracle expects 10 lakh rows, it may choose a full scan.

So if Oracle estimates the row count incorrectly, the plan can become wrong.

Many performance issues start with wrong cardinality estimation.”

---

# Slide 16: Important Concept — Selectivity

## Slide content:

## Selectivity

Selectivity means how much a condition filters the data.

Highly selective condition:

```sql
WHERE transaction_id = 99999
```

Low selective condition:

```sql
WHERE status = 'SUCCESS'
```

In banking tables, many rows may have status `SUCCESS`.

---

## Trainer Explanation

“Selectivity tells us how narrow or broad a filter is.

If a condition returns very few rows, it is highly selective.

If a condition returns many rows, it is low selective.

For example, transaction ID is usually unique, so it is highly selective.

But status equals SUCCESS may return 80% or 90% of the table.

So not every filter is useful.

This is important when we later discuss indexes.”

---

# Slide 17: Important Concept — Access Path

## Slide content:

## Access Path

Access path means how Oracle accesses the data.

Common examples:

* Full table scan
* Index scan
* Rowid access

Simple idea:

```text
Access path = route used to reach the data
```

---

## Trainer Explanation

“Access path means how Oracle reaches the data.

Does it read the full table?

Does it use an index?

Does it find row locations and then visit the table?

In this slot, we only need to understand the concept.

In Slot 2, we will learn how to read these access paths in execution plans properly.”

---

# Slide 18: Important Concept — Join Method

## Slide content:

## Join Method

Join method means how Oracle combines rows from two or more tables.

Common join methods:

* Nested loops
* Hash join
* Merge join

Example:

```sql
SELECT c.customer_name, t.amount
FROM customers c
JOIN transactions t
ON c.customer_id = t.customer_id;
```

---

## Trainer Explanation

“When SQL uses multiple tables, Oracle needs to decide how to join them.

For small row sets, one method may be better.

For large row sets, another method may be better.

We will go deeper into join methods later.

For now, remember: join method is another optimizer decision, and wrong row estimates can lead to wrong join choices.”

---

# Slide 19: Important Concept — Statistics

## Slide content:

## Statistics

Statistics describe the data to the optimizer.

Statistics include:

* Number of rows
* Number of blocks
* Number of distinct values
* Column data distribution
* Index information
* Table size

Without good statistics, Oracle may make poor decisions.

---

## Trainer Explanation

“The optimizer does not know your business directly.

It depends on statistics to understand the data.

For example, how many rows are in the transactions table?

How many different customers exist?

How many transactions does each customer have?

If statistics are old or missing, Oracle may think a table is small when it is actually huge.

That can lead to a bad execution plan.

So statistics are like the optimizer’s knowledge base.”

---

# Slide 20: Banking Example — Slow Customer Statement

## Slide content:

Business problem:

A customer statement screen is slow during business hours.

SQL:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
ORDER BY transaction_date DESC;
```

Possible causes:

* Bad SQL
* Missing index
* Wrong statistics
* Large sorting
* I/O load
* Application fetching too much data

---

## Trainer Explanation

“Now let’s bring all the concepts together.

The business says: customer statement screen is slow.

The SQL is filtering by customer ID and ordering by transaction date.

This may look simple, but many things can go wrong.

Maybe the customer has too many transactions.

Maybe the application fetches all history instead of recent history.

Maybe Oracle has wrong statistics.

Maybe the query sorts a huge number of rows.

Maybe the database is under I/O pressure during business hours.

At this point, our job is not to fix immediately.

Our job is to identify what evidence is missing.”

---

# Slide 21: What Should We Check First?

## Slide content:

Before tuning, ask:

* How many rows does the query return?
* How long does it take?
* Is it slow for one customer or many customers?
* Is it slow always or only during peak hours?
* Is the application fetching too much data?
* Is sorting required?
* What is the basic plan shape?
* Are statistics fresh?
* What changed recently?

---

## Trainer Explanation

“This slide is very important.

In production, tuning should start with questions.

If a query is slow only during peak hours, maybe load or I/O is the issue.

If it is slow for one customer only, maybe that customer has huge data.

If it became slow after deployment, maybe plan changed.

If the application fetches 5 years of data, maybe SQL design is the problem.

So before solution, we need diagnosis.”

---

# Slide 22: Common Tuning Problems Covered in This Slot

## Slide content:

This slot focuses on two common tuning problems:

## 1. Inefficient or High-Load SQL Statements

Example:

```sql
SELECT *
FROM transactions;
```

Problem:

* Reads too much data
* Returns too many rows
* Consumes unnecessary resources

## 2. Suboptimal Use of Oracle by Application

Example:

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

Problem:

* Application may fetch full history when only recent records are needed

---

## Trainer Explanation

“From the 10 common tuning problems, Slot 1 focuses mainly on two.

First: inefficient or high-load SQL.

This means SQL that causes Oracle to do too much work.

Second: suboptimal application usage.

This means the application is asking the database in a poor way.

For example, the application may display only 20 rows, but SQL fetches 20,000 rows.

This is not only a database problem. It is also application behavior.”

---

# Slide 23: Demo Objective

## Slide content:

## Demo: Identify Expensive SQL Pattern

We will compare three query patterns:

1. Fetch all transactions
2. Fetch transactions for one customer
3. Fetch recent transactions for one customer

We will observe:

* Rows returned
* Execution time
* Logical reads
* Physical reads
* Basic plan shape

---

## Trainer Explanation

“In this demo, we are not fixing the query yet.

We are only observing.

The goal is to understand how different SQL patterns create different amounts of database work.

One query may return the whole table.

Another query may filter by customer.

Another query may filter by customer and date range.

Our question is: which pattern is more efficient, and what evidence supports that?”

---

# Slide 24: Demo Setup Table

## Slide content:

We will use a banking-style table:

```sql
transactions
```

Important columns:

* `transaction_id`
* `customer_id`
* `account_id`
* `branch_id`
* `transaction_date`
* `transaction_type`
* `amount`
* `status`

---

## Trainer Explanation

“We will use a simplified transaction table.

This table represents customer banking transactions.

In real banking systems, such tables can become very large.

For training, we will create enough data to observe performance differences.

The exact size depends on your lab machine, but even 100,000 to 500,000 rows is enough for learning.”

---

# Demo / Lab Setup Script

## Step 1: Create Table

```sql
DROP TABLE transactions PURGE;

CREATE TABLE transactions (
    transaction_id    NUMBER PRIMARY KEY,
    customer_id       NUMBER NOT NULL,
    account_id        NUMBER NOT NULL,
    branch_id         NUMBER NOT NULL,
    transaction_date  DATE NOT NULL,
    transaction_type  VARCHAR2(20),
    amount            NUMBER(12,2),
    status            VARCHAR2(20),
    remarks           VARCHAR2(200)
);
```

---

## Trainer Explanation

“This script creates our training table.

If the table already exists, we drop it first.

This is only for lab practice, not production.

In production, we never casually drop tables.”

---

## Step 2: Insert Sample Data

For normal machines, use `100000`.

For stronger machines, use `500000`.

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO transactions (
      transaction_id,
      customer_id,
      account_id,
      branch_id,
      transaction_date,
      transaction_type,
      amount,
      status,
      remarks
    )
    VALUES (
      i,
      MOD(i, 5000) + 1,
      MOD(i, 20000) + 1,
      MOD(i, 50) + 1,
      SYSDATE - MOD(i, 730),
      CASE MOD(i, 4)
        WHEN 0 THEN 'DEBIT'
        WHEN 1 THEN 'CREDIT'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'ATM'
      END,
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      CASE MOD(i, 5)
        WHEN 0 THEN 'FAILED'
        ELSE 'SUCCESS'
      END,
      'Banking transaction test data'
    );

    IF MOD(i, 10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/
```

```sql
COMMIT;
```

---

## Trainer Explanation

“This inserts sample banking transaction data.

We are creating different customers, accounts, branches, transaction dates, transaction types, and statuses.

The data is not perfect production data, but it is enough to create a realistic performance learning scenario.

Notice that transaction dates are spread across around 730 days, almost 2 years.

That will help us compare full history versus recent history.”

---

## Step 3: Gather Statistics

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

## Trainer Explanation

“After loading data, we gather statistics.

This gives the optimizer information about the table.

Without statistics, Oracle may not estimate properly.

In this slot, we are not going deep into statistics, but remember: optimizer decisions depend heavily on statistics.”

---

## Step 4: Confirm Data

```sql
SELECT COUNT(*) AS total_transactions
FROM transactions;
```

Expected result:

```text
100000
```

Check number of customers:

```sql
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM transactions;
```

Check date range:

```sql
SELECT MIN(transaction_date), MAX(transaction_date)
FROM transactions;
```

---

## Trainer Explanation

“Before running performance queries, always understand the data.

How many rows exist?

How many customers exist?

What is the date range?

This matters because SQL tuning depends on data volume and data distribution.

Without knowing data size, we are guessing.”

---

# Slide 25: Lab Query 1 — Fetch All Transactions

## Slide content:

## Query 1: Fetch all transactions

```sql
SELECT *
FROM transactions;
```

Observation:

* Returns all rows
* Reads the whole table
* High data volume
* Usually expensive for application screens

---

## Trainer Explanation

“This is the broadest query.

It asks Oracle to return all transactions.

For a small table, this may look fine.

But in banking, transaction tables can have millions or billions of records.

So this query pattern is dangerous for application screens.

This is usually a sign that the application is fetching too much data.”

---

## Lab Command for Query 1

To avoid printing too many rows, use:

```sql
SET TIMING ON

SELECT COUNT(*)
FROM transactions;
```

Optional basic plan shape:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

## What Trainees Should Record

* Rows returned
* Execution time
* Basic plan shape
* Whether this query is business-friendly or too broad

Expected basic plan shape:

```text
TABLE ACCESS FULL
```

Do not explain full plan deeply yet. That is Slot 2.

---

# Slide 26: Lab Query 2 — Customer Filter

## Slide content:

## Query 2: Fetch one customer’s transactions

```sql
SELECT *
FROM transactions
WHERE customer_id = 101;
```

Observation:

* More selective than Query 1
* Returns fewer rows
* Better business meaning
* Still may read more data than expected

---

## Trainer Explanation

“This query is better than fetching all transactions because it filters by one customer.

But we still need to check how many rows it returns.

Maybe customer 101 has only 20 transactions.

Maybe customer 101 has 20,000 transactions.

So we first measure the rows and execution time.

Again, we are not fixing anything yet.”

---

## Lab Command for Query 2

```sql
SET TIMING ON

SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101;
```

Optional basic plan shape:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE customer_id = 101;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

## What Trainees Should Record

* Rows returned
* Execution time
* Basic plan shape
* Is this better than Query 1?
* Is the query still potentially expensive?

---

# Slide 27: Lab Query 3 — Customer + Date Range

## Slide content:

## Query 3: Fetch recent transactions for one customer

```sql
SELECT *
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC;
```

Observation:

* More business-focused
* Returns recent records only
* Reduces unnecessary data
* Still needs evidence before tuning

---

## Trainer Explanation

“This query is even better from an application design point of view.

Instead of fetching the full customer history, it fetches recent transactions only.

Many banking screens do not need all historical transactions by default.

They usually show recent 30 days, 90 days, or latest 50 records.

So this query pattern is more controlled.

But again, we will not assume it is perfect.

We measure rows, time, and basic plan shape.”

---

## Lab Command for Query 3

```sql
SET TIMING ON

SELECT COUNT(*)
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE, -3);
```

Optional basic plan shape:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

## What Trainees Should Record

* Rows returned
* Execution time
* Basic plan shape
* Is the query more focused?
* Is sorting involved?
* What information is still missing?

---

# Slide 28: Logical Reads and Physical Reads

## Slide content:

## Two Useful Metrics

## Logical Reads

Blocks read from memory/buffer cache.

Usually shown as:

```text
consistent gets
```

## Physical Reads

Blocks read from disk.

Usually shown as:

```text
physical reads
```

Why this matters:

* High logical reads = Oracle is doing a lot of work
* High physical reads = Oracle is reading from disk
* Both help identify expensive SQL

---

## Trainer Explanation

“Execution time alone is not enough.

A query may be fast because data is already cached.

But if it has high logical reads, it is still doing a lot of database work.

Logical reads mean Oracle is reading blocks from memory.

Physical reads mean Oracle had to read blocks from disk.

In production, a query with high logical reads can become dangerous when many users run it repeatedly.”

---

## How to Enable Basic Statistics

Try:

```sql
SET AUTOTRACE ON STATISTICS
```

Then run the query.

Look for:

```text
consistent gets
physical reads
```

If AUTOTRACE is not available, just record rows and execution time for now. Detailed runtime plan comes in Slot 2.

---

# Slide 29: Lab Observation Table

## Slide content:

Participants should fill this table:

| Query                          | Rows Returned | Execution Time | Logical Reads | Physical Reads | Basic Plan Shape | Observation |
| ------------------------------ | ------------: | -------------: | ------------: | -------------: | ---------------- | ----------- |
| Query 1: All transactions      |               |                |               |                |                  |             |
| Query 2: One customer          |               |                |               |                |                  |             |
| Query 3: Customer + date range |               |                |               |                |                  |             |

---

## Trainer Explanation

“This table is the main output of Lab 1.

The purpose is not to find the final fix.

The purpose is to compare SQL patterns.

Which query asks for too much data?

Which query is more selective?

Which query is more suitable for an application screen?

Which query still needs deeper plan analysis?

This is how tuning starts: with observation.”

---

# Slide 30: Lab Output Questions

## Slide content:

Participants should answer:

1. Which query is expensive?
2. Why is it expensive?
3. Is the problem SQL design or database structure?
4. Is the application fetching too much data?
5. What information is missing before tuning?
6. What should we check in the execution plan later?

---

## Trainer Explanation

“Now we want trainees to think like DBAs.

Do not just say Query 1 is slow.

Explain why.

Is it returning too many rows?

Is it reading too much data?

Is the business requirement unclear?

Is the application asking for full history?

Do we need pagination?

Do we need date filters?

Do we need to check plan details?

The goal is to build diagnosis thinking.”

---

# Slide 31: Expected Lab Discussion

## Slide content:

Expected findings:

## Query 1

```sql
SELECT *
FROM transactions;
```

Likely problem:

* Too broad
* Returns all data
* Application design issue if used in screen

## Query 2

```sql
WHERE customer_id = 101
```

Likely better:

* More focused
* Customer-specific
* Still may require deeper plan analysis

## Query 3

```sql
WHERE customer_id = 101
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
```

Likely best pattern:

* Customer-specific
* Time-bound
* More suitable for customer statement screen

---

## Trainer Explanation

“Query 1 is usually the worst pattern for an application screen because it fetches everything.

Query 2 is better because it filters by customer.

Query 3 is usually better because it filters by customer and time period.

But notice: we are not saying Query 3 is fully tuned.

We are only saying it is a better SQL pattern.

In the next slots, we will learn how Oracle executes it, whether it uses the right access path, and how indexing can improve it.”

---

# Slide 32: What Information is Missing Before Tuning?

## Slide content:

Before applying any fix, we still need:

* Actual execution plan
* Estimated vs actual rows
* Existing indexes
* Table and index statistics
* Data distribution
* Peak-hour workload
* Wait events
* Application requirement
* Number of executions per hour
* Recent changes

---

## Trainer Explanation

“This is a key production lesson.

Even after running these three queries, we still do not know everything.

We need to know existing indexes.

We need to know actual plan.

We need to know if statistics are fresh.

We need to know whether this SQL runs once per day or 10,000 times per hour.

We need to know if it became slow after a deployment or statistics refresh.

So tuning is not one command.

Tuning is investigation.”

---

# Slide 33: Slot 1 Summary

## Slide content:

In this slot, we learned:

* SQL tuning means reducing unnecessary work
* SQL tuning is different from full database tuning
* Banking systems slow down due to data growth, concurrency, poor SQL, and system pressure
* Oracle processes SQL through parse, optimize, execute, and fetch
* Optimizer chooses a plan using cost-based decisions
* Cost, cardinality, selectivity, access path, join method, and statistics are core concepts
* Before tuning, collect evidence

---

## Trainer Explanation

“Let’s summarize.

Today’s first slot was not about fixing SQL.

It was about understanding how to think.

If someone says a banking screen is slow, we should not immediately create an index or change the SQL.

We first understand what the SQL is doing, how much data it returns, how much work Oracle performs, and what evidence is missing.

This foundation will help us in the next slot, where we properly read execution plans.”

---

# Slide 34: Transition to Slot 2

## Slide content:

Next slot:

## Execution Plans: EXPLAIN PLAN vs DBMS_XPLAN

We will learn:

* What an execution plan is
* How to generate a plan
* How to read important plan columns
* Difference between estimated and actual runtime plan
* Common plan operations

---

## Trainer Explanation

“In Slot 1, we learned what to observe.

In Slot 2, we will learn how to read Oracle’s execution plan properly.

That is where we will understand what Oracle is actually doing internally — whether it is scanning the full table, using an index, sorting data, or joining tables.

So now we move from tuning mindset to plan reading.”

---

# Final Trainer Note for Slot 1

Your main message in this slot should be:

> “Do not tune blindly. First understand the SQL, the data, the optimizer, and the evidence.”

Keep repeating this idea.

The trainees should leave Slot 1 with one habit:

```text
Problem → Observe → Measure → Understand → Then Tune
```

Not:

```text
Problem → Create Index
```
