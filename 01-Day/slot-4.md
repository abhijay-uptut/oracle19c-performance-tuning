Absolutely — here is **Day 1 — Slot 4 only**, focused on:

**Common Plan Pitfalls + Day 1 Capstone Lab**

This slot combines Day 1 learning into practical diagnosis.

---

# Day 1 — Slot 4

## 2:45 PM to 5:00 PM

# Common Plan Pitfalls + Day 1 Capstone Lab

## Slot Objective

By the end of this slot, trainees should be able to:

* Identify common SQL and execution plan mistakes
* Understand when full table scan is acceptable or problematic
* Compare index scan vs full scan
* Detect issues like bad filters, missing date range, implicit conversion, functions on indexed columns, and large sorting
* Apply basic fixes
* Compare before and after results using execution plans and runtime metrics

---

# Suggested Slot Flow

| Time        | Section                                      |
| ----------- | -------------------------------------------- |
| 2:45 - 3:05 | Common plan pitfalls                         |
| 3:05 - 3:25 | SQL anti-patterns in banking systems         |
| 3:25 - 4:30 | Lab 4: Banking SQL Tuning Challenge          |
| 4:30 - 4:50 | Group discussion and before/after comparison |
| 4:50 - 5:00 | Day 1 summary and outcomes                   |

---

# Slide 1: Slot Title

## Common Plan Pitfalls + Day 1 Capstone Lab

**Slide content:**

In this slot, we will combine Day 1 concepts:

* Execution plans
* Access paths
* Cost and cardinality
* Index usage
* SQL anti-patterns
* Before/after tuning comparison

---

## Trainer Explanation

“This is the final slot of Day 1.

Until now, we learned SQL tuning basics, optimizer thinking, execution plans, and indexing.

Now we will combine everything.

The goal is not just to read theory. The goal is to look at SQL, identify the problem, suggest a fix, and validate improvement.”

---

# Slide 2: Day 1 Recap

## Slide content:

Today we learned:

* SQL tuning means reducing unnecessary work
* Oracle uses optimizer to choose execution plans
* Cost, cardinality, and selectivity matter
* Execution plans show Oracle’s access path
* `EXPLAIN PLAN` shows estimated plan
* `DISPLAY_CURSOR` shows actual runtime plan
* Indexes help only when they match SQL patterns

---

## Trainer Explanation

“Before starting the capstone, let’s quickly recap.

SQL tuning is not guessing.

We first understand the query, then check the plan, then check rows and cost, then apply a fix, and finally validate the result.

This flow is what we will use in this lab.”

---

# Slide 3: Common Plan Pitfalls

## Slide content:

Common issues we will look for:

* Full table scan when few rows are needed
* Index range scan used for too many rows
* Wrong join order
* Bad cardinality estimate
* Missing or stale statistics
* Expensive sort operation
* Implicit data type conversion
* Function on indexed column
* `SELECT *`
* Missing date range

---

## Trainer Explanation

“These are common plan and SQL problems DBAs see in production.

Some are database design issues.

Some are SQL writing issues.

Some are application behavior issues.

In banking systems, these issues become serious because data volume is high and queries run repeatedly.”

---

# Slide 4: Full Table Scan — Bad or Acceptable?

## Slide content:

## Full table scan is acceptable when:

* Query needs most rows
* Table is small
* Reporting query scans large data intentionally
* Index access would be more expensive

## Full table scan is problematic when:

* Query needs only few rows
* Table is very large
* Filter is selective
* Query runs frequently in OLTP workload

---

## Trainer Explanation

“Full table scan is not always bad.

If I ask Oracle to return all transactions, full table scan is expected.

But if I ask for one customer or one account from a huge table, full table scan may be a problem.

So never judge the plan without understanding the query requirement.”

---

# Slide 5: Index Range Scan vs Full Scan

## Slide content:

## Index range scan is usually good when:

* Query returns few rows
* Filter is selective
* Index matches the condition

## Full scan may be better when:

* Query returns large percentage of table
* Table is small
* Index would cause too many table lookups

---

## Trainer Explanation

“Index scan is not always good either.

If Oracle uses an index to fetch 70% of the table, it may be slower than full table scan.

So our job is to ask: how many rows are expected, and how many rows are actually returned?

That is why E-Rows and A-Rows are important.”

---

# Slide 6: Wrong Join Order

## Slide content:

Wrong join order happens when Oracle starts with the wrong table.

Example:

```sql
SELECT c.full_name, t.amount
FROM customers c
JOIN transactions t
ON c.customer_id = t.customer_id
WHERE c.email = 'user100@mail.com';
```

Better approach:

* Start with selective customer row
* Then find matching transactions

---

## Trainer Explanation

“In joins, Oracle decides which table to start with.

If one table has a very selective filter, usually Oracle should start there.

For example, email may return one customer.

Then Oracle can use that customer ID to get transactions.

If Oracle starts with a huge transaction table first, the plan may become expensive.”

---

# Slide 7: Bad Cardinality Estimate

## Slide content:

Cardinality estimate problem:

```text
Oracle expected: 10 rows
Actual result: 100,000 rows
```

Why this is bad:

* Wrong access path
* Wrong join method
* Wrong join order
* Wrong memory estimate
* Wrong cost

---

## Trainer Explanation

“Bad cardinality estimate is one of the root causes of bad plans.

If Oracle expects few rows, it may choose nested loops or index access.

But if the actual result is huge, that plan may perform badly.

Wrong cardinality often comes from stale statistics, skewed data, or complex predicates.”

---

# Slide 8: Missing or Stale Statistics

## Slide content:

Statistics tell optimizer about data.

Missing or stale statistics can cause:

* Wrong row estimates
* Wrong cost
* Wrong access path
* Wrong join method
* Plan instability

Refresh table statistics:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'TABLE_NAME',
    cascade => TRUE
  );
END;
/
```

---

## Trainer Explanation

“The optimizer depends on statistics.

If statistics are old, Oracle may think a table has 10,000 rows when it actually has 10 million.

That can lead to a poor plan.

In production, statistics management is very important, especially after large data loads or data cleanup.”

---

# Slide 9: Sort Operations

## Slide content:

Sorts appear because of:

* `ORDER BY`
* `GROUP BY`
* `DISTINCT`
* Sort merge join
* Analytic functions

Sorts become expensive when:

* Many rows are sorted
* Memory is insufficient
* Sort spills to disk

Example:

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

---

## Trainer Explanation

“Sorting is normal, but large sorting can be expensive.

If we sort all transactions just to show the latest records, that is poor design.

In banking dashboards and reports, sorting and grouping can consume a lot of memory and temporary space.

So always check whether the sort is necessary and whether the query can reduce rows before sorting.”

---

# Slide 10: Implicit Data Type Conversion

## Slide content:

Problem example:

```sql
SELECT *
FROM accounts
WHERE account_number = 1234567890;
```

But `account_number` is stored as `VARCHAR2`.

Better:

```sql
SELECT *
FROM accounts
WHERE account_number = '1234567890';
```

---

## Trainer Explanation

“This is a very common issue.

If a column is VARCHAR2, compare it with a string value.

If we compare VARCHAR2 column with a number, Oracle may perform implicit conversion.

This can prevent proper index usage and may even cause errors in some cases.

So data type matching matters.”

---

# Slide 11: Functions on Indexed Columns

## Slide content:

Problem:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

If index is only on:

```sql
email
```

Oracle may not use it efficiently.

Possible fix:

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

---

## Trainer Explanation

“We already saw this in Slot 3.

If the query applies a function on the column, a normal index may not help.

The index must match the expression used in the query.

This is why function-based index exists.”

---

# Slide 12: SELECT * Problem

## Slide content:

Problem:

```sql
SELECT *
FROM transactions
WHERE account_id = 1001;
```

Issues:

* Fetches unnecessary columns
* More bytes transferred
* More memory usage
* More network cost
* May require table access even when index has enough data

Better:

```sql
SELECT transaction_id, transaction_date, amount, status
FROM transactions
WHERE account_id = 1001;
```

---

## Trainer Explanation

“SELECT star is convenient, but in production it can be expensive.

If the screen needs only transaction date, amount, and status, then do not fetch all columns.

Fetching extra columns increases data transfer and application processing.

In some cases, selecting fewer columns can allow Oracle to use a more efficient access path.”

---

# Slide 13: Queries Without Date Filters

## Slide content:

Problem:

```sql
SELECT *
FROM transactions
WHERE account_id = 1001;
```

Better:

```sql
SELECT *
FROM transactions
WHERE account_id = 1001
AND transaction_date >= ADD_MONTHS(SYSDATE, -3);
```

Why?

* Reduces rows
* Reduces reads
* Better business control
* Better user experience

---

## Trainer Explanation

“Banking transaction tables grow continuously.

If the application fetches full account history every time, the query becomes slower as data grows.

Adding a date range makes the query more business-friendly and performance-friendly.

Many screens should default to recent data, with option to search older history separately.”

---

# Slide 14: Day 1 Tuning Workflow

## Slide content:

Use this workflow:

```text
1. Understand SQL purpose
2. Check rows returned
3. Generate execution plan
4. Identify access path
5. Check predicates
6. Check cost and cardinality
7. Apply possible fix
8. Compare before and after
```

---

## Trainer Explanation

“This is the process we will follow in the capstone lab.

Do not randomly change SQL.

Follow a step-by-step method.

Understand the business purpose first, then plan, then evidence, then fix, then validation.”

---

# Slide 15: Lab 4 Objective

## Slide content:

## Banking SQL Tuning Challenge

Participants will analyze 5 problematic queries:

* Query A: Function on indexed column
* Query B: Missing date range
* Query C: Implicit conversion
* Query D: Bad wildcard search
* Query E: Large sort

For each query:

* Generate plan
* Identify issue
* Suggest fix
* Apply fix if possible
* Compare before and after

---

## Trainer Explanation

“This is the Day 1 capstone.

Each query represents a common real-world banking SQL issue.

The task is not only to run the SQL.

The task is to explain what is wrong and how to prove improvement.”

---

# Lab Setup

Use the `customers` table from Slot 3 and `transactions` table from Slot 1.

Now create `accounts` table for Query C.

## Create Accounts Table

```sql
DROP TABLE accounts PURGE;

CREATE TABLE accounts (
    account_id      NUMBER PRIMARY KEY,
    account_number  VARCHAR2(30),
    customer_id     NUMBER,
    branch_id       NUMBER,
    account_type    VARCHAR2(20),
    balance         NUMBER(14,2),
    status          VARCHAR2(20),
    opened_date     DATE
);
```

---

## Trainer Explanation

“We already have customers and transactions tables.

For this lab, we also need an accounts table.

Notice that account_number is stored as VARCHAR2.

That is important because our implicit conversion example compares it with a number.”

---

## Insert Accounts Data

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO accounts (
      account_id,
      account_number,
      customer_id,
      branch_id,
      account_type,
      balance,
      status,
      opened_date
    )
    VALUES (
      i,
      TO_CHAR(1000000000 + i),
      MOD(i, 5000) + 1,
      MOD(i, 50) + 1,
      CASE MOD(i, 3)
        WHEN 0 THEN 'SAVINGS'
        WHEN 1 THEN 'CURRENT'
        ELSE 'LOAN'
      END,
      ROUND(DBMS_RANDOM.VALUE(100, 500000), 2),
      CASE MOD(i, 5)
        WHEN 0 THEN 'INACTIVE'
        ELSE 'ACTIVE'
      END,
      SYSDATE - MOD(i, 2000)
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

“This script creates 100,000 account records.

Each account has a string account number.

This helps us demonstrate how comparing the wrong data type can affect query behavior.”

---

## Create Basic Indexes

```sql
CREATE INDEX idx_accounts_account_number
ON accounts(account_number);

CREATE INDEX idx_transactions_account_id
ON transactions(account_id);

CREATE INDEX idx_transactions_txn_date
ON transactions(transaction_date);

CREATE INDEX idx_customers_email
ON customers(email);

CREATE INDEX idx_customers_name
ON customers(full_name);
```

---

## Trainer Explanation

“These are basic indexes to support the lab.

We intentionally create normal indexes.

Some queries will still not use them efficiently because the SQL pattern is problematic.

That is the learning point.”

---

## Gather Statistics

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'ACCOUNTS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'TRANSACTIONS', cascade => TRUE);
END;
/
```

---

## Trainer Explanation

“After creating and loading tables, always gather statistics.

This keeps optimizer information fresh.

Now our execution plan comparisons become more reliable.”

---

# Slide 16: Lab Instructions

## Slide content:

For each query:

1. Run the query
2. Generate estimated plan
3. Check main operation
4. Check predicate section
5. Identify issue
6. Suggest fix
7. Apply fix if safe
8. Re-run plan
9. Compare before and after

---

## Trainer Explanation

“Tell participants to work systematically.

They should not jump directly to the fix.

First observe the plan.

Then identify the problem.

Then suggest the fix.

Then test and compare.”

---

# Helpful Plan Commands

## Estimated Plan

```sql
EXPLAIN PLAN FOR
-- paste query here
;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

## Actual Runtime Plan

```sql
ALTER SESSION SET statistics_level = ALL;

-- run query here

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

# Slide 17: Query A — Function on Indexed Column

## Slide content:

Problem query:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

Possible issue:

* Normal email index may not be used
* Function is applied on column
* Full scan may happen

---

## Trainer Explanation

“This is the same type of issue we saw in Slot 3.

Even if email has an index, the query uses LOWER(email).

So the normal email index may not be enough.

Ask participants to prove this through the plan.”

---

## Query A — Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected issue:

```text
TABLE ACCESS FULL CUSTOMERS
```

Predicate:

```text
filter(LOWER("EMAIL")='user100@mail.com')
```

---

## Query A — Possible Fix

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CUSTOMERS', cascade => TRUE);
END;
/
```

Re-test:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected after:

```text
INDEX RANGE SCAN IDX_CUSTOMERS_LOWER_EMAIL
```

---

## Trainer Explanation

“The fix is a function-based index.

After creating it, the predicate may become an access predicate.

That shows Oracle can now use the expression efficiently.”

---

# Slide 18: Query B — Missing Date Range

## Slide content:

Problem query:

```sql
SELECT *
FROM transactions
WHERE account_id = 1001;
```

Possible issue:

* Fetches full account history
* May return too many rows
* No time boundary
* Performance degrades as data grows

---

## Trainer Explanation

“This query is not syntactically wrong.

It may even use an index on account_id.

But from application design side, it can still be problematic.

If one account has many years of transactions, this query fetches full history.

That may not be needed for the screen.”

---

## Query B — Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 1001;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Check row count:

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 1001;
```

---

## Query B — Possible Fix

Better business-focused query:

```sql
SELECT *
FROM transactions
WHERE account_id = 1001
AND transaction_date >= ADD_MONTHS(SYSDATE, -3);
```

Plan:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
WHERE account_id = 1001
AND transaction_date >= ADD_MONTHS(SYSDATE, -3);

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Optional better supporting index:

```sql
CREATE INDEX idx_txn_account_date
ON transactions(account_id, transaction_date);
```

---

## Trainer Explanation

“The first fix is not always an index.

Sometimes the first fix is improving the business filter.

For account statement screens, defaulting to last 3 months is often better than fetching all history.

After that, a composite index on account_id and transaction_date may support this pattern.”

---

# Slide 19: Query C — Implicit Conversion

## Slide content:

Problem query:

```sql
SELECT *
FROM accounts
WHERE account_number = 1234567890;
```

But `account_number` is stored as:

```sql
VARCHAR2
```

Issue:

* Number compared with string column
* Implicit conversion may happen
* Index usage can be affected

---

## Trainer Explanation

“This query looks simple, but it has a hidden issue.

The column account_number is VARCHAR2.

But the value is written as a number.

Oracle may convert one side internally.

This can prevent clean index usage or cause unexpected behavior.

Always compare same data type with same data type.”

---

## Query C — Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = 1234567890;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Check predicate section carefully.

You may see conversion like:

```text
TO_NUMBER("ACCOUNT_NUMBER")=1234567890
```

---

## Query C — Better Query

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = '1234567890';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected better predicate:

```text
access("ACCOUNT_NUMBER"='1234567890')
```

---

## Trainer Explanation

“The fix is simple: use quotes because the column is VARCHAR2.

Now the predicate matches the column data type.

This makes it easier for Oracle to use the index correctly.”

---

# Slide 20: Query D — Bad Wildcard Search

## Slide content:

Problem query:

```sql
SELECT *
FROM customers
WHERE full_name LIKE '%raj%';
```

Issue:

* Leading wildcard prevents normal index usage
* Oracle cannot jump to beginning of value
* May cause full scan

---

## Trainer Explanation

“This is a very common search problem.

If the pattern starts with `%`, Oracle does not know where the matching text starts.

A normal B-tree index is useful when search starts from the beginning, like `raj%`.

But `%raj%` means raj can appear anywhere.

So Oracle may scan many rows.”

---

## Query D — Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%raj%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected:

```text
TABLE ACCESS FULL CUSTOMERS
```

---

## Query D — Possible Fix Options

Depending on requirement:

## Option 1: Prefix search

```sql
SELECT *
FROM customers
WHERE full_name LIKE 'Customer 100%';
```

## Option 2: Oracle Text index for contains search

```sql
CREATE INDEX idx_customers_name_text
ON customers(full_name)
INDEXTYPE IS CTXSYS.CONTEXT;
```

Then search using:

```sql
SELECT *
FROM customers
WHERE CONTAINS(full_name, 'raj') > 0;
```

---

## Trainer Explanation

“For normal B-tree index, prefix search is easier to optimize.

But if the business really needs contains search, like searching name from middle, Oracle Text may be a better solution.

This shows that not every problem is solved by a normal index.”

---

# Slide 21: Query E — Large Sort

## Slide content:

Problem query:

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

Issue:

* Sorts entire transaction table
* Returns all rows
* High memory usage
* May use temporary tablespace
* Bad for application screens

---

## Trainer Explanation

“This query asks Oracle to sort the entire transactions table.

In a banking system, this can be huge.

If the screen only needs latest transactions, this query is too broad.

The issue is not only sorting, but also missing filter and missing limit.”

---

## Query E — Before Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected operation:

```text
SORT ORDER BY
TABLE ACCESS FULL TRANSACTIONS
```

---

## Query E — Possible Fix

If screen needs latest 100 transactions:

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

Better with business filter:

```sql
SELECT *
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

Optional supporting index:

```sql
CREATE INDEX idx_txn_date_desc
ON transactions(transaction_date DESC);
```

---

## Trainer Explanation

“The fix depends on business requirement.

If the user only needs latest 100 transactions, use FETCH FIRST.

If the user needs recent period, add date filter.

If this query is very frequent, an index on transaction_date may help.

Again, we do not index blindly. We match the index to the query pattern.”

---

# Slide 22: Capstone Observation Table

## Slide content:

Participants should fill:

| Query | Main Issue          | Before Plan | Suggested Fix | After Plan | Improvement |
| ----- | ------------------- | ----------- | ------------- | ---------- | ----------- |
| A     | Function on column  |             |               |            |             |
| B     | Missing date range  |             |               |            |             |
| C     | Implicit conversion |             |               |            |             |
| D     | Leading wildcard    |             |               |            |             |
| E     | Large sort          |             |               |            |             |

---

## Trainer Explanation

“This table is their capstone worksheet.

For each query, they must record the problem, not just the SQL output.

This helps them practice real DBA thinking.”

---

# Slide 23: What Counts as Improvement?

## Slide content:

Improvement can be seen through:

* Better access path
* Lower cost
* Lower logical reads
* Fewer rows processed
* Less sorting
* Better predicate usage
* Lower execution time
* Better business filter

---

## Trainer Explanation

“Improvement is not only lower cost.

Sometimes cost reduces, but runtime does not.

Sometimes the best improvement is reducing rows returned.

Sometimes the best improvement is changing filter logic.

Always validate using multiple signals.”

---

# Slide 24: Common Mistakes During Tuning

## Slide content:

Avoid these mistakes:

* Creating index without checking workload
* Thinking full table scan is always bad
* Thinking index scan is always good
* Ignoring row count
* Ignoring application requirement
* Ignoring DML impact
* Comparing only cost
* Not checking predicate information
* Not testing before and after

---

## Trainer Explanation

“These are common beginner mistakes.

A DBA should not act like a command executor.

A DBA should act like an investigator.

Every tuning change should have evidence and validation.”

---

# Slide 25: Group Discussion

## Slide content:

Discuss:

1. Which query was easiest to diagnose?
2. Which query was most dangerous for production?
3. Which issue was caused by SQL design?
4. Which issue was caused by application behavior?
5. Which issue required database structure change?
6. Which fix needs production caution?

---

## Trainer Explanation

“Use this slide for interaction.

Let participants explain their thinking.

The goal is to make them speak like DBAs: ‘I observed this plan, I found this issue, I tested this fix, and this improved the result.’”

---

# Slide 26: Day 1 Outcome Check

## Slide content:

By the end of Day 1, participants should be able to:

* Read basic execution plans
* Understand access paths
* Identify full table scan, index scan, and sort operations
* Explain cost, cardinality, and selectivity
* Identify bad SQL patterns
* Apply basic indexing fixes
* Compare before and after plans

---

## Trainer Explanation

“This is our Day 1 outcome.

They do not need to become experts today.

But they should be comfortable reading a basic execution plan and identifying obvious SQL problems.

Tomorrow, we will move to diagnostic tools like AWR, ADDM, SQL Tuning Advisor, and SQL Access Advisor.”

---

# Slide 27: Day 1 Final Summary

## Slide content:

Day 1 key message:

```text
Do not tune blindly.
Understand the SQL.
Read the plan.
Check the data volume.
Identify the access path.
Apply the right fix.
Validate before and after.
```

---

## Trainer Explanation

“This is the main lesson of Day 1.

SQL tuning is not guesswork.

It is a structured investigation.

If you follow this process, you will avoid risky production changes and make better tuning decisions.”

---

# Slide 28: Transition to Day 2

## Slide content:

Tomorrow we move from single SQL analysis to database-level diagnosis.

Day 2 focus:

* AWR
* ADDM
* SQL Tuning Advisor
* SQL Access Advisor
* Memory and I/O symptoms
* Workload-level tuning

---

## Trainer Explanation

“Today we focused mainly on individual SQL and execution plans.

Tomorrow we will learn how to diagnose bigger database-level problems.

AWR and ADDM will help us answer: what happened in the database during a slow period?”

---

# Lab 4 Full Participant Worksheet

## Query A: Function on Indexed Column

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';
```

### Check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Possible Fix

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

### Re-check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user100@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Expected Learning

The index must match the expression used in the SQL.

---

## Query B: Missing Date Range

```sql
SELECT *
FROM transactions
WHERE account_id = 1001;
```

### Check Rows

```sql
SELECT COUNT(*)
FROM transactions
WHERE account_id = 1001;
```

### Better Query

```sql
SELECT *
FROM transactions
WHERE account_id = 1001
AND transaction_date >= ADD_MONTHS(SYSDATE, -3);
```

### Optional Index

```sql
CREATE INDEX idx_txn_account_date
ON transactions(account_id, transaction_date);
```

### Expected Learning

Business filters reduce unnecessary data access.

---

## Query C: Implicit Conversion

```sql
SELECT *
FROM accounts
WHERE account_number = 1234567890;
```

### Check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = 1234567890;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Better Query

```sql
SELECT *
FROM accounts
WHERE account_number = '1234567890';
```

### Re-check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM accounts
WHERE account_number = '1234567890';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Expected Learning

Match query value type with column data type.

---

## Query D: Bad Wildcard Search

```sql
SELECT *
FROM customers
WHERE full_name LIKE '%raj%';
```

### Check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE full_name LIKE '%raj%';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Alternative Prefix Search

```sql
SELECT *
FROM customers
WHERE full_name LIKE 'Customer 100%';
```

### Expected Learning

Leading wildcard prevents normal B-tree index usage.

---

## Query E: Large Sort

```sql
SELECT *
FROM transactions
ORDER BY transaction_date DESC;
```

### Check Plan

```sql
EXPLAIN PLAN FOR
SELECT *
FROM transactions
ORDER BY transaction_date DESC;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Better Query

```sql
SELECT *
FROM transactions
WHERE transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

### Expected Learning

Reduce rows before sorting. Avoid sorting full table for screen-level queries.

---

# Final Day 1 Trainer Closing Line

Use this at the end:

> “Today we learned how to read SQL behavior manually. Tomorrow, we will learn how to use Oracle’s diagnostic tools to find the biggest problems in the whole database workload.”
