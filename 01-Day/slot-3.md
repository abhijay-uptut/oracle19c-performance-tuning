Absolutely — here is **Day 1 — Slot 3 only**, focused on **Indexing Strategies for Banking Workloads**.

---

# Day 1 — Slot 3

## 1:00 PM to 2:30 PM

# Indexing Strategies for Banking Workloads

## Slot Objective

By the end of this slot, trainees should understand:

* Why indexes improve SQL performance
* When indexes can hurt performance
* Difference between B-tree, composite, unique, function-based, and invisible indexes
* Why selectivity matters
* Why indexes have maintenance cost
* How to test a function-based index using a real banking-style query

---

# Suggested Slot Flow

| Time        | Section                                |
| ----------- | -------------------------------------- |
| 1:00 - 1:10 | Why indexes matter                     |
| 1:10 - 1:25 | Index types overview                   |
| 1:25 - 1:40 | Selectivity and index maintenance cost |
| 1:40 - 1:55 | Function-based index concept           |
| 1:55 - 2:20 | Lab 3: Function-based index            |
| 2:20 - 2:30 | Discussion and summary                 |

---

# Slide 1: Slot Title

## Indexing Strategies for Banking Workloads

**Slide content:**

Indexes help Oracle find data faster.

In this slot, we will learn:

* Why indexes improve performance
* When indexes hurt performance
* Common index types
* Index selectivity
* Index maintenance cost
* Function-based index lab

---

## Trainer Explanation

“In the previous slot, we learned how to read execution plans.

Now we focus on one of the most common tuning tools: indexes.

But the goal is not to create indexes everywhere.

The goal is to understand when an index helps, when it hurts, and how to validate it using execution plans.”

---

# Slide 2: What is an Index?

## Slide content:

An index is a separate database structure that helps Oracle find rows faster.

Simple idea:

```text
Table = full book
Index = book index at the back
```

Instead of reading the full table, Oracle can use the index to find row locations.

---

## Trainer Explanation

“Think of a large book.

If you want to find one topic, you do not read every page.

You go to the index, find the topic, then jump to the page.

Oracle indexes work similarly.

The index helps Oracle locate matching rows without scanning the full table.”

---

# Slide 3: Why Indexes Improve Performance

## Slide content:

Indexes improve performance when:

* Query returns small percentage of rows
* WHERE condition is selective
* Join columns are indexed
* ORDER BY can use index order
* Unique lookup is needed
* Application frequently searches by same column

Example:

```sql
SELECT *
FROM customers
WHERE customer_id = 101;
```

---

## Trainer Explanation

“Indexes are useful when the query is searching for a small number of rows.

For example, finding one customer by customer ID.

In banking systems, common indexed columns are customer ID, account number, transaction ID, mobile number, email, and reference number.

But index usefulness depends on selectivity.”

---

# Slide 4: When Indexes Hurt Performance

## Slide content:

Indexes can hurt performance when:

* Too many indexes exist on a table
* Table has heavy INSERT, UPDATE, DELETE activity
* Query returns large percentage of rows
* Index is created on low-selectivity column
* Index is not used by important queries
* Index increases storage and maintenance cost

---

## Trainer Explanation

“Indexes are not free.

Every time data is inserted, updated, or deleted, Oracle may also need to update related indexes.

For transaction-heavy tables, too many indexes can slow down DML operations.

So we should not create indexes just because a query is slow.

We should check whether the index supports real workload.”

---

# Slide 5: Banking Example of Index Cost

## Slide content:

Transaction table example:

```text
TRANSACTIONS
```

Heavy operations:

* New transaction insert
* Balance update
* Payment status update
* Audit entry insert
* Reversal update

Too many indexes can slow these operations.

---

## Trainer Explanation

“In banking, some tables are read-heavy, and some are write-heavy.

A customer master table may be searched often.

A transaction table may receive continuous inserts.

If we add too many indexes on the transaction table, every new transaction becomes more expensive.

So indexing strategy must balance read performance and write cost.”

---

# Slide 6: B-tree Index

## Slide content:

## B-tree Index

Most common Oracle index type.

Good for:

* Equality filters
* Range filters
* Primary key lookups
* Date range queries
* Sorting support

Examples:

```sql
WHERE customer_id = 101
```

```sql
WHERE transaction_date BETWEEN date1 AND date2
```

---

## Trainer Explanation

“B-tree index is the default and most common index in Oracle.

Most regular indexes we create are B-tree indexes.

They work well for equality and range conditions.

For example, customer ID lookup or transaction date range search.”

---

# Slide 7: Unique Index

## Slide content:

## Unique Index

Ensures values are unique.

Common examples:

* Customer ID
* Account number
* Transaction reference number
* Card number token
* National ID/passport number, if applicable

Example:

```sql
CREATE UNIQUE INDEX idx_customers_email
ON customers(email);
```

---

## Trainer Explanation

“A unique index makes sure duplicate values are not allowed.

It also helps Oracle find one row quickly.

For example, if account number is unique, Oracle knows only one row can match.

This can lead to an INDEX UNIQUE SCAN in the execution plan.”

---

# Slide 8: Composite Index

## Slide content:

## Composite Index

An index on multiple columns.

Example:

```sql
CREATE INDEX idx_txn_customer_date
ON transactions(customer_id, transaction_date);
```

Useful when query filters by multiple columns:

```sql
WHERE customer_id = 101
AND transaction_date >= SYSDATE - 90
```

---

## Trainer Explanation

“Composite indexes are very important in real banking workloads.

Many queries filter by more than one column.

For example, customer ID plus transaction date.

The order of columns in a composite index matters.

Usually, we put the most useful filtering column first, but it depends on query patterns.”

---

# Slide 9: Composite Index Column Order

## Slide content:

Index:

```sql
(customer_id, transaction_date)
```

Good for:

```sql
WHERE customer_id = 101
```

Good for:

```sql
WHERE customer_id = 101
AND transaction_date >= SYSDATE - 90
```

Not always useful for:

```sql
WHERE transaction_date >= SYSDATE - 90
```

---

## Trainer Explanation

“In composite indexes, leading column matters.

If the index starts with customer_id, Oracle can use it efficiently when customer_id is part of the condition.

But if the query only filters by transaction_date, this index may not be very useful.

So we design composite indexes based on real SQL patterns.”

---

# Slide 10: Function-Based Index

## Slide content:

## Function-Based Index

An index created on an expression or function.

Example:

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

Useful for queries like:

```sql
WHERE LOWER(email) = 'user500@mail.com'
```

---

## Trainer Explanation

“Function-based indexes are useful when the query applies a function on a column.

If we have a normal index on email, but the query uses LOWER(email), Oracle may not use the normal email index effectively.

Because the query is not searching email directly. It is searching the result of LOWER(email).

So we create an index on the same expression.”

---

# Slide 11: Why Normal Index May Not Work

## Slide content:

Normal index:

```sql
CREATE INDEX idx_customers_email
ON customers(email);
```

Query:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Problem:

* Index is on `email`
* Query is on `LOWER(email)`
* Expression does not match normal index

---

## Trainer Explanation

“This is a very common application issue.

Developers often use LOWER or UPPER to make search case-insensitive.

But if the index is only on the original column, Oracle may not use it as expected.

That can cause full table scans on large customer tables.

This is exactly what our lab will demonstrate.”

---

# Slide 12: Invisible Index

## Slide content:

## Invisible Index

An index that exists but is ignored by optimizer by default.

Example:

```sql
CREATE INDEX idx_customers_mobile
ON customers(mobile_no)
INVISIBLE;
```

Useful for:

* Testing index impact
* Safe production validation
* Comparing plans before making index visible

---

## Trainer Explanation

“Invisible index is useful for safer testing.

You can create an index but keep it invisible.

By default, optimizer ignores it.

Then you can test its effect in a controlled session before making it visible.

This is useful in production-like environments where we do not want sudden plan changes.”

---

# Slide 13: Index Selectivity

## Slide content:

## Selectivity

Selectivity means how much a condition filters data.

High selectivity:

```sql
WHERE email = 'a@bank.com'
```

Low selectivity:

```sql
WHERE status = 'ACTIVE'
```

High selectivity columns usually make better index candidates.

---

## Trainer Explanation

“Index selectivity is very important.

If a column returns very few rows, it is highly selective.

Email is usually highly selective.

Status is usually low selective because many customers may be ACTIVE.

An index on a low-selectivity column may not help much, especially if the query returns a large portion of the table.”

---

# Slide 14: Banking Selectivity Examples

## Slide content:

| Column           | Selectivity | Index Usefulness   |
| ---------------- | ----------- | ------------------ |
| transaction_id   | Very high   | Excellent          |
| account_number   | Very high   | Excellent          |
| email            | High        | Good               |
| customer_id      | Medium/high | Good               |
| branch_id        | Low/medium  | Depends            |
| status           | Low         | Usually weak alone |
| transaction_type | Low         | Usually weak alone |

---

## Trainer Explanation

“In banking workloads, transaction ID and account number are usually very selective.

Status or transaction type usually has few values, so they are low selective.

That does not mean we never index low-selectivity columns.

It means we need to be careful.

Sometimes low-selectivity columns work well as part of a composite index.”

---

# Slide 15: Index Maintenance Cost

## Slide content:

Every index has a cost.

When table data changes, Oracle may update indexes.

Cost appears during:

* INSERT
* UPDATE
* DELETE
* Bulk load
* Data migration
* Batch jobs

More indexes = more maintenance work.

---

## Trainer Explanation

“When we create an index, read queries may become faster.

But writes may become slower.

For every insert into customers, Oracle inserts into table and also updates indexes.

For every update to indexed columns, indexes may need maintenance.

So in OLTP banking systems, we must keep indexes useful and controlled.”

---

# Slide 16: Indexes on Transaction-Heavy Tables

## Slide content:

For transaction-heavy banking tables:

Use indexes carefully on:

* Primary key
* Foreign keys
* Frequent search columns
* Important report filters
* Critical business lookup columns

Avoid:

* Too many single-column indexes
* Unused indexes
* Indexes on columns rarely searched
* Duplicate indexes
* Indexes created without workload analysis

---

## Trainer Explanation

“Transaction-heavy tables are sensitive.

They need indexes for important queries, but too many indexes can slow down transaction processing.

A common mistake is creating one index for every slow query.

Instead, we should look at the workload and design indexes that support multiple important queries.”

---

# Slide 17: Banking Example Query

## Slide content:

Slow query:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Problem:

Even if `email` has a normal index, Oracle may not use it properly because of:

```sql
LOWER(email)
```

---

## Trainer Explanation

“Now we move to our main lab example.

The application searches customer by email.

To avoid case mismatch, developer uses LOWER(email).

This is common and understandable.

But from database side, this can make the normal email index less useful.

We will prove this using execution plans.”

---

# Slide 18: Lab 3 Objective

## Slide content:

## Lab 3: Function-Based Index

We will:

1. Create a `customers` table
2. Insert sample customers
3. Create normal index on `email`
4. Run query using `LOWER(email)`
5. Check plan
6. Create function-based index
7. Re-run plan
8. Compare before and after

---

## Trainer Explanation

“This lab is very practical.

The goal is to show that index must match the way SQL is written.

If SQL uses LOWER(email), then the index should support LOWER(email).

At the end, participants should clearly see before and after plan difference.”

---

# Lab 3 Setup

## Step 1: Create Customers Table

```sql
DROP TABLE customers PURGE;

CREATE TABLE customers (
    customer_id     NUMBER PRIMARY KEY,
    full_name       VARCHAR2(100),
    email           VARCHAR2(150),
    mobile_no       VARCHAR2(20),
    status          VARCHAR2(20),
    created_date    DATE
);
```

---

## Trainer Explanation

“This table represents bank customers.

We include customer ID, name, email, mobile number, status, and created date.

Email is the main column for our lab.”

---

## Step 2: Insert Sample Data

Use `100000` rows for normal laptops.

```sql
BEGIN
  FOR i IN 1..100000 LOOP
    INSERT INTO customers (
      customer_id,
      full_name,
      email,
      mobile_no,
      status,
      created_date
    )
    VALUES (
      i,
      'Customer ' || i,
      CASE 
        WHEN MOD(i, 2) = 0 THEN 'USER' || i || '@MAIL.COM'
        ELSE 'user' || i || '@mail.com'
      END,
      '855' || LPAD(i, 8, '0'),
      CASE MOD(i, 5)
        WHEN 0 THEN 'INACTIVE'
        ELSE 'ACTIVE'
      END,
      SYSDATE - MOD(i, 1000)
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

“We insert 100,000 sample customers.

Notice email values are mixed case.

Some are uppercase, some are lowercase.

This helps us create a real case-insensitive search scenario.”

---

## Step 3: Gather Statistics

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS',
    cascade => TRUE
  );
END;
/
```

---

## Trainer Explanation

“After inserting data, we gather statistics.

This gives the optimizer updated information about the table.

Without statistics, plan comparison may not be reliable.”

---

## Step 4: Confirm Data

```sql
SELECT COUNT(*) AS total_customers
FROM customers;
```

```sql
SELECT *
FROM customers
WHERE customer_id = 500;
```

---

## Trainer Explanation

“Before testing, confirm that data exists.

We also check customer 500 because our query will search for [user500@mail.com](mailto:user500@mail.com).

Because 500 is even, the stored email may be uppercase.

That is why LOWER(email) becomes useful for case-insensitive search.”

---

# Slide 19: Step 1 — Create Normal Email Index

## Slide content:

Create normal index:

```sql
CREATE INDEX idx_customers_email
ON customers(email);
```

Gather stats:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS',
    cascade => TRUE
  );
END;
/
```

---

## Trainer Explanation

“First we create a normal index on email.

Many teams stop here and assume email search is indexed.

But we will test whether this normal index helps when the query uses LOWER(email).”

---

# Slide 20: Step 2 — Run Slow Query

## Slide content:

Run:

```sql
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';
```

Check estimated plan:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

---

## Trainer Explanation

“Now we run the case-insensitive email search.

The important part is the WHERE condition.

It is not email equals value.

It is LOWER(email) equals value.

So the normal email index may not help.”

---

# Slide 21: Expected Before Plan

## Slide content:

Expected before function-based index:

```text
TABLE ACCESS FULL CUSTOMERS
```

Predicate may show:

```text
filter(LOWER("EMAIL")='user500@mail.com')
```

Meaning:

* Oracle may scan table
* Apply LOWER function
* Then filter matching row

---

## Trainer Explanation

“If you see TABLE ACCESS FULL, that means Oracle is scanning the customers table.

The predicate may show filter with LOWER(email).

This means Oracle is applying the function and filtering rows.

For a large customer table, this can become expensive.”

---

# Slide 22: Step 3 — Create Function-Based Index

## Slide content:

Create function-based index:

```sql
CREATE INDEX idx_customers_lower_email
ON customers (LOWER(email));
```

Gather stats:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'CUSTOMERS',
    cascade => TRUE
  );
END;
/
```

---

## Trainer Explanation

“Now we create an index on the exact expression used in the query.

The query uses LOWER(email), so the index also uses LOWER(email).

This allows Oracle to search using the expression directly.”

---

# Slide 23: Step 4 — Re-run Query

## Slide content:

Run again:

```sql
EXPLAIN PLAN FOR
SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Optional actual runtime plan:

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT *
FROM customers
WHERE LOWER(email) = 'user500@mail.com';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST'));
```

---

## Trainer Explanation

“Now we run the same query again.

The SQL has not changed.

Only the database structure changed.

Now check whether Oracle uses the function-based index.

This is how we validate tuning changes.”

---

# Slide 24: Expected After Plan

## Slide content:

Expected after function-based index:

```text
INDEX RANGE SCAN IDX_CUSTOMERS_LOWER_EMAIL
TABLE ACCESS BY INDEX ROWID CUSTOMERS
```

Predicate may show:

```text
access(LOWER("EMAIL")='user500@mail.com')
```

Meaning:

* Oracle uses the function-based index
* Fewer rows are accessed
* Query becomes more efficient

---

## Trainer Explanation

“If the plan shows INDEX RANGE SCAN on IDX_CUSTOMERS_LOWER_EMAIL, our index is being used.

This means Oracle can directly search the lower-case email expression.

The predicate may change from filter to access.

That is a strong sign that the condition is being used efficiently.”

---

# Slide 25: Before vs After Comparison

## Slide content:

| Item          | Before Function-Based Index | After Function-Based Index |
| ------------- | --------------------------- | -------------------------- |
| Access path   | Full table scan             | Index range scan           |
| Predicate     | Filter                      | Access                     |
| Cost          | Higher                      | Lower                      |
| Logical reads | Higher                      | Lower                      |
| Runtime       | Slower                      | Faster                     |

---

## Trainer Explanation

“This comparison is the heart of the lab.

Before the function-based index, Oracle may scan the whole table.

After the function-based index, Oracle can use the index.

The most important comparison is not only cost.

Check access path, predicate type, logical reads, and runtime.”

---

# Slide 26: Lab Observation Table

## Slide content:

Participants should record:

| Metric                  | Before Index | After Function-Based Index |
| ----------------------- | -----------: | -------------------------: |
| Main operation          |              |                            |
| Index used?             |              |                            |
| Estimated rows          |              |                            |
| Cost                    |              |                            |
| Predicate type          |              |                            |
| Execution time          |              |                            |
| Logical reads / Buffers |              |                            |

---

## Trainer Explanation

“Ask participants to fill this table.

They should compare before and after clearly.

If they only say ‘after is faster’, that is not enough.

They should prove it using plan and metrics.”

---

# Slide 27: Lab Questions

## Slide content:

Participants should answer:

1. Did the normal email index help?
2. Why did `LOWER(email)` affect index usage?
3. What changed after creating function-based index?
4. Did predicate change from filter to access?
5. Did cost or logical reads reduce?
6. Is this index safe for production?

---

## Trainer Explanation

“These questions force participants to think like DBAs.

The important question is not just whether the index works.

The production question is: should we create it?

Will this query run frequently?

Will it improve important workload?

Will it add too much DML overhead?

These are the real-world decisions.”

---

# Slide 28: Production Caution

## Slide content:

Before creating an index in production, check:

* How frequently SQL runs
* How many rows it returns
* Existing indexes
* DML impact
* Storage impact
* Application behavior
* Similar queries
* Test environment results
* Rollback plan

---

## Trainer Explanation

“In production, do not create indexes casually.

An index may fix one query but slow down inserts and updates.

Before creating it, check whether this SQL is important and frequent.

Also check whether an existing index can already support the query.

Always test before production.”

---

# Slide 29: Common Tuning Problems Covered

## Slide content:

This slot covers:

## Inefficient SQL Statements

Example:

```sql
WHERE LOWER(email) = 'user500@mail.com'
```

Without matching index, Oracle may scan too much data.

## Suboptimal Application Query Pattern

Application uses function on column for case-insensitive search.

## Degradation Over Time

As customer table grows, full scan becomes slower.

---

## Trainer Explanation

“This lab connects to real tuning problems.

At small data size, the query may look fine.

But as the customer table grows, the same query becomes slower.

This is degradation over time.

Also, using LOWER(email) is not wrong, but it needs proper database support.”

---

# Slide 30: Slot 3 Summary

## Slide content:

In this slot, we learned:

* Indexes help Oracle find rows faster
* Indexes are useful for selective queries
* Indexes can hurt DML-heavy tables
* B-tree indexes are most common
* Composite indexes support multi-column filters
* Unique indexes support unique lookups
* Function-based indexes support expressions like `LOWER(email)`
* Invisible indexes help test index impact
* Always validate before and after

---

## Trainer Explanation

“Let’s summarize.

Indexes are powerful, but they are not magic.

A good index supports real SQL patterns.

A bad or unnecessary index adds overhead.

The key lesson from the lab is simple: the index must match the query.

If the query uses LOWER(email), a normal email index may not be enough.

A function-based index can solve that pattern.”

---

# Slide 31: Transition to Slot 4

## Slide content:

Next slot:

## Common Plan Pitfalls + Day 1 Capstone Lab

We will analyze:

* Full table scan: bad or acceptable?
* Missing date filters
* Implicit data conversion
* Functions on indexed columns
* Large sorts
* `SELECT *` problem

---

## Trainer Explanation

“In the next slot, we will combine what we learned today.

We will look at multiple problematic SQL patterns and ask:

What is wrong?

What does the plan show?

What fix should we consider?

That will become our Day 1 capstone practice.”

---

# Final Trainer Message for Slot 3

Repeat this line:

> “Do not create indexes blindly. Create indexes that match real SQL patterns and prove the improvement with plans and metrics.”
