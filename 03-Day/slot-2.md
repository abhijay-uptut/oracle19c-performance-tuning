# Day 3 — Slot 2

## 10:45 AM to 12:00 PM

# Bind Peeking, Adaptive Cursor Sharing, Hints and SQL Profiles

## Slot Objective

By the end of this slot, trainees should understand:

* What bind peeking is
* Why the same SQL can perform differently for different bind values
* What skewed data means
* How adaptive cursor sharing helps
* When histograms are useful
* What SQL hints and SQL Profiles do
* Difference between hint, baseline, SQL Profile, and index
* Why overusing hints is risky

---

# Suggested Slot Flow

| Time          | Section                                  |
| ------------- | ---------------------------------------- |
| 10:45 - 10:55 | Problem: Same SQL, different performance |
| 10:55 - 11:10 | Bind peeking and skewed data             |
| 11:10 - 11:25 | Adaptive cursor sharing and histograms   |
| 11:25 - 11:40 | Hints, SQL Profiles, baselines, indexes  |
| 11:40 - 11:58 | Lab 10: Bind variable and skewed data    |
| 11:58 - 12:00 | Summary                                  |

---

# Slide 1: Slot Title

## Bind Peeking, Adaptive Cursor Sharing, Hints and SQL Profiles

**Slide content:**

In this slot, we will learn:

* Why same SQL can behave differently
* Bind peeking
* Skewed data
* Adaptive cursor sharing
* Histograms
* SQL hints
* SQL Profiles
* Risks of forcing plans

---

## Trainer Explanation

“In the previous slot, we discussed plan stability using SQL Plan Management.

Now we discuss another common production problem: the same SQL behaves differently for different input values.

For example, the query is same, but for one branch it runs fast, and for another branch it runs slow.

This usually happens because data distribution is not equal.”

---

# Slide 2: The Core Problem

## Slide content:

Same SQL:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

Different values:

```text
branch_id = 1  → many rows
branch_id = 3  → few rows
```

Problem:

```text
One execution plan may not be good for all values.
```

---

## Trainer Explanation

“This is the core problem.

The SQL text is same.

Only the bind value changes.

But branch 1 may have lakhs of transactions, while branch 3 may have only a few hundred.

For branch 3, index access may be excellent.

For branch 1, full table scan may be better.

So one plan may not fit every bind value.”

---

# Slide 3: Banking Scenario

## Slide content:

## Scenario

A branch transaction query is used by the application:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

Data distribution:

* Branch 1: very large branch
* Branch 2: medium branch
* Branch 3: small branch

Issue:

* Query is fast for small branches
* Query is slow for large branch
* Same SQL, different bind values

---

## Trainer Explanation

“In a real bank, not all branches have equal data.

Main city branches may have huge transaction volume.

Small rural branches may have very small volume.

If the optimizer treats all branch values as equal, it may choose a plan that is good for one branch but bad for another.”

---

# Slide 4: What is a Bind Variable?

## Slide content:

A bind variable is a placeholder for a value.

Example:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

Benefits:

* Reduces hard parsing
* Allows SQL reuse
* Improves shared pool efficiency
* Helps application scalability

---

## Trainer Explanation

“Bind variables are good.

Instead of creating a new SQL for every branch ID, the application sends the same SQL with different values.

This helps Oracle reuse parsed SQL and reduces hard parsing.

But bind variables also create a challenge: the optimizer may not always know which value will be used.”

---

# Slide 5: What is Bind Peeking?

## Slide content:

## Bind Peeking

Bind peeking means Oracle looks at the bind value during hard parse and uses it to choose a plan.

Example:

First execution:

```text
branch_id = 3
```

Oracle may choose index plan.

Later execution:

```text
branch_id = 1
```

Same plan may be reused, even if full scan would be better.

---

## Trainer Explanation

“When SQL is parsed for the first time, Oracle may peek at the bind value.

If the first value is branch 3, and branch 3 has very few rows, Oracle may choose an index plan.

Later, if branch 1 has huge rows, Oracle may still reuse that same plan.

That can cause poor performance.”

---

# Slide 6: Why Bind Peeking Can Cause Problems

## Slide content:

Bind peeking can cause issues when:

* Data is skewed
* First bind value is not representative
* One plan is reused for very different values
* Some values return few rows
* Some values return many rows

Result:

```text
Good plan for one value
Bad plan for another value
```

---

## Trainer Explanation

“Bind peeking is not always bad.

It becomes a problem when data is uneven.

If every branch has similar transaction count, one plan may work fine.

But if branch 1 has 700,000 rows and branch 3 has 500 rows, the optimizer needs different thinking.”

---

# Slide 7: What is Skewed Data?

## Slide content:

## Skewed Data

Skewed data means values are not evenly distributed.

Example:

| Branch   | Transactions |
| -------- | -----------: |
| Branch 1 |      700,000 |
| Branch 2 |        5,000 |
| Branch 3 |          500 |

This is skewed because one value dominates the table.

---

## Trainer Explanation

“Skewed data means some values appear much more than others.

In this example, branch 1 has most of the data.

Branch 3 has very little data.

If Oracle assumes every branch has equal rows, it may estimate incorrectly.

Wrong estimate can lead to wrong plan.”

---

# Slide 8: Plan Choice for Different Branches

## Slide content:

## Small Branch

```sql
WHERE branch_id = 3
```

Likely better:

```text
Index range scan
```

Because few rows are returned.

## Large Branch

```sql
WHERE branch_id = 1
```

Likely better:

```text
Full table scan
```

Because many rows are returned.

---

## Trainer Explanation

“For a small branch, an index is useful because Oracle can quickly find a small number of rows.

For a very large branch, index access may be inefficient because Oracle has to visit too many table rows.

A full scan may be better for large branch data.

That is why one plan may not be ideal for every value.”

---

# Slide 9: What is Adaptive Cursor Sharing?

## Slide content:

## Adaptive Cursor Sharing

Adaptive Cursor Sharing allows Oracle to create different child cursors for the same SQL when bind values need different plans.

It helps when:

* SQL uses bind variables
* Data is skewed
* Different bind values need different plans

---

## Trainer Explanation

“Adaptive Cursor Sharing is Oracle’s way of handling this problem.

Oracle may notice that different bind values behave differently.

Then it can create different child cursors for the same SQL.

Each child cursor may have a different plan suitable for a range of bind values.”

---

# Slide 10: Parent Cursor vs Child Cursor

## Slide content:

Same SQL text:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

Parent cursor:

```text
SQL text identity
```

Child cursors:

```text
Different execution plans or environments
```

Example:

| Child Cursor | Bind Type    | Plan       |
| ------------ | ------------ | ---------- |
| 0            | Small branch | Index scan |
| 1            | Large branch | Full scan  |

---

## Trainer Explanation

“The parent cursor represents the SQL text.

Child cursors represent different executable versions of that SQL.

Oracle may create different child cursors because bind values, optimizer settings, or execution environments differ.

In adaptive cursor sharing, different child cursors may appear for different bind selectivity patterns.”

---

# Slide 11: Bind Sensitive and Bind Aware

## Slide content:

In `V$SQL`, check:

```sql
is_bind_sensitive
is_bind_aware
```

## Bind Sensitive

Oracle noticed bind values may affect plan choice.

## Bind Aware

Oracle is actively using different plans based on bind value behavior.

---

## Trainer Explanation

“These two columns are important in our lab.

Bind sensitive means Oracle knows bind values matter.

Bind aware means Oracle has adapted and may use different child cursors for different bind patterns.

We will inspect these columns in V$SQL.”

---

# Slide 12: What are Histograms?

## Slide content:

## Histogram

A histogram tells Oracle about data distribution in a column.

Useful when:

* Data is skewed
* Some values are very common
* Some values are rare
* Equality predicates use skewed columns

Example:

```text
branch_id = 1 is very common
branch_id = 3 is rare
```

---

## Trainer Explanation

“Normal statistics may tell Oracle number of rows and number of distinct values.

But if the distribution is uneven, Oracle needs more detail.

A histogram helps Oracle understand that branch 1 is very common and branch 3 is rare.

This can improve cardinality estimates.”

---

# Slide 13: When Histograms Help

## Slide content:

Histograms help when:

* Column has skewed values
* Query filters on that column
* Different values return very different row counts
* Wrong cardinality causes bad plans

Example:

```sql
WHERE branch_id = :branch_id
```

Histograms may help Oracle estimate different branch values better.

---

## Trainer Explanation

“Histograms are useful when values are not evenly distributed.

But histograms are not needed for every column.

If data is evenly distributed, histogram may not add much value.

In production, unnecessary histograms can also create plan instability.

So use them when there is a clear skew problem.”

---

# Slide 14: SQL Hints

## Slide content:

## SQL Hint

A hint is an instruction inside SQL to influence optimizer behavior.

Example:

```sql
SELECT /*+ INDEX(transactions idx_txn_branch) */ *
FROM transactions
WHERE branch_id = :branch_id;
```

Common hints:

* `INDEX`
* `FULL`
* `USE_NL`
* `USE_HASH`
* `LEADING`

---

## Trainer Explanation

“Hints tell the optimizer what we prefer.

For example, use this index, use full scan, use hash join, or use nested loops.

Hints can be useful in emergencies or very controlled SQL.

But hints can also become dangerous if overused.”

---

# Slide 15: Risks of Overusing Hints

## Slide content:

Hints can be risky because:

* They hard-code optimizer behavior
* Data volume changes over time
* Indexes may change
* Good hint today may be bad tomorrow
* Hints can hide root cause
* Application SQL becomes harder to maintain

---

## Trainer Explanation

“A hint is like forcing a route.

Today that route may be good.

But after data grows or traffic changes, the same route may be bad.

In banking systems, data changes every day.

So hints should be used carefully, not everywhere.”

---

# Slide 16: SQL Profiles

## Slide content:

## SQL Profile

A SQL Profile gives optimizer extra information to choose a better plan.

It does not change SQL text.

It can help when:

* Cardinality estimate is wrong
* Optimizer needs better correction
* Application SQL cannot be changed
* SQL Tuning Advisor recommends it

---

## Trainer Explanation

“A SQL Profile is different from a hint.

It does not directly say: use this exact index.

It gives the optimizer additional information so it can estimate better.

SQL Profiles usually come from SQL Tuning Advisor recommendations.”

---

# Slide 17: Hint vs Baseline vs SQL Profile vs Index

## Slide content:

| Option      | Purpose                     | Changes SQL Text? | Main Risk                    |
| ----------- | --------------------------- | ----------------- | ---------------------------- |
| Hint        | Influence/force optimizer   | Yes               | Hard-coded plan behavior     |
| Baseline    | Control accepted plans      | No                | May block better plans       |
| SQL Profile | Improve optimizer estimates | No                | May affect future executions |
| Index       | Add access path             | No                | DML/storage overhead         |

---

## Trainer Explanation

“This comparison is very important.

Hints influence optimizer from inside SQL.

Baselines control which plans are accepted.

SQL Profiles improve optimizer estimates.

Indexes add physical access paths.

They are not the same thing, and we should choose based on the real problem.”

---

# Slide 18: Which Tool Should We Use?

## Slide content:

Use based on problem:

| Problem                | Possible Tool                       |
| ---------------------- | ----------------------------------- |
| Wrong estimate         | Histogram / SQL Profile             |
| Sudden plan regression | SQL Plan Baseline                   |
| Missing access path    | Index                               |
| Emergency plan control | Hint or Baseline                    |
| Skewed bind values     | Adaptive Cursor Sharing / Histogram |
| Bad SQL design         | Rewrite SQL                         |

---

## Trainer Explanation

“Do not use one tool for every problem.

If the problem is wrong estimate, histogram or SQL Profile may help.

If the problem is missing access path, index may help.

If the problem is sudden regression, baseline may help.

If SQL design is bad, rewrite may be the best fix.”

---

# Slide 19: Lab 10 Objective

## Slide content:

## Lab 10: Bind Variable and Skewed Data Lab

Participants will:

* Create skewed branch transaction data
* Run same bind query with different values
* Inspect bind-sensitive SQL
* Inspect bind-aware SQL
* Check child cursors
* Observe plan behavior

---

## Trainer Explanation

“In this lab, we will intentionally create skewed data.

Branch 1 will have many rows.

Branch 2 will have medium rows.

Branch 3 will have few rows.

Then we run the same bind SQL with different branch values and observe Oracle behavior.”

---

# Slide 20: Lab Setup — Create Table

## Slide content:

```sql
DROP TABLE branch_transactions PURGE;

CREATE TABLE branch_transactions (
    transaction_id    NUMBER PRIMARY KEY,
    branch_id         NUMBER NOT NULL,
    customer_id       NUMBER,
    account_id        NUMBER,
    transaction_date  DATE,
    amount            NUMBER(12,2),
    status            VARCHAR2(20)
);
```

---

## Trainer Explanation

“We create a separate table for this lab so we do not disturb previous tables.

The key column here is branch_id.

We will create uneven data distribution on branch_id.”

---

# Slide 21: Insert Skewed Data — Branch 1

## Slide content:

Branch 1: large branch

```sql
BEGIN
  FOR i IN 1..700000 LOOP
    INSERT INTO branch_transactions
    VALUES (
      i,
      1,
      MOD(i, 50000) + 1,
      MOD(i, 100000) + 1,
      SYSDATE - MOD(i, 365),
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      CASE MOD(i, 5)
        WHEN 0 THEN 'FAILED'
        ELSE 'SUCCESS'
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

“This inserts 700,000 rows for branch 1.

Branch 1 represents a large high-volume branch.

This will be our common value.”

---

# Slide 22: Insert Skewed Data — Branch 2 and 3

## Slide content:

Branch 2: medium branch
Branch 3: small branch

```sql
BEGIN
  FOR i IN 700001..705000 LOOP
    INSERT INTO branch_transactions
    VALUES (
      i, 2,
      MOD(i, 50000) + 1,
      MOD(i, 100000) + 1,
      SYSDATE - MOD(i, 365),
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      'SUCCESS'
    );
  END LOOP;

  FOR i IN 705001..705500 LOOP
    INSERT INTO branch_transactions
    VALUES (
      i, 3,
      MOD(i, 50000) + 1,
      MOD(i, 100000) + 1,
      SYSDATE - MOD(i, 365),
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      'SUCCESS'
    );
  END LOOP;

  COMMIT;
END;
/
```

---

## Trainer Explanation

“Now we insert 5,000 rows for branch 2 and 500 rows for branch 3.

So our data is clearly skewed.

Branch 1 dominates the table.

Branch 3 is rare.”

---

# Slide 23: Verify Data Distribution

## Slide content:

```sql
SELECT branch_id, COUNT(*) AS txn_count
FROM branch_transactions
GROUP BY branch_id
ORDER BY branch_id;
```

Expected:

| Branch |   Rows |
| ------ | -----: |
| 1      | 700000 |
| 2      |   5000 |
| 3      |    500 |

---

## Trainer Explanation

“Always verify the data.

This query confirms that the branch distribution is uneven.

This uneven distribution is the reason one plan may not fit all values.”

---

# Slide 24: Create Index

## Slide content:

```sql
CREATE INDEX idx_branch_txn_branch
ON branch_transactions(branch_id);
```

Gather stats:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'BRANCH_TRANSACTIONS',
    cascade => TRUE,
    method_opt => 'FOR COLUMNS branch_id SIZE AUTO'
  );
END;
/
```

---

## Trainer Explanation

“We create an index on branch_id.

Then we gather statistics and allow Oracle to create histogram if needed using SIZE AUTO.

This helps optimizer understand skewed data better.”

---

# Slide 25: Check Histogram Information

## Slide content:

```sql
SELECT column_name,
       histogram,
       num_buckets,
       num_distinct
FROM user_tab_col_statistics
WHERE table_name = 'BRANCH_TRANSACTIONS'
AND column_name = 'BRANCH_ID';
```

---

## Trainer Explanation

“This query checks whether Oracle created a histogram on branch_id.

If histogram exists, Oracle may estimate branch values more accurately.

If no histogram appears, lab output may still work, but estimates may be less precise.”

---

# Slide 26: Prepare Bind Variable

## Slide content:

In SQL*Plus or SQL Developer script mode:

```sql
VARIABLE b_branch_id NUMBER;
```

Then assign value:

```sql
EXEC :b_branch_id := 3;
```

Run query:

```sql
SELECT *
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

---

## Trainer Explanation

“We now use a bind variable.

This simulates application behavior.

The SQL text remains the same, but the value changes.”

---

# Slide 27: Run Query for Small Branch

## Slide content:

```sql
ALTER SESSION SET statistics_level = ALL;

EXEC :b_branch_id := 3;

SELECT *
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

Check plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

## Trainer Explanation

“First we run the query for branch 3.

Branch 3 has only 500 rows.

We expect index access may be suitable.

Check the plan, E-Rows, A-Rows, buffers, and predicate.”

---

# Slide 28: Run Query for Large Branch

## Slide content:

```sql
EXEC :b_branch_id := 1;

SELECT *
FROM branch_transactions
WHERE branch_id = :b_branch_id;
```

Check plan:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

## Trainer Explanation

“Now run the same SQL for branch 1.

Branch 1 has 700,000 rows.

For this value, full table scan may be more efficient than index access.

Now compare whether Oracle uses same plan or a different plan.”

---

# Slide 29: Inspect V$SQL

## Slide content:

```sql
SELECT sql_id,
       child_number,
       executions,
       is_bind_sensitive,
       is_bind_aware
FROM v$sql
WHERE sql_text LIKE '%branch_id = :B_BRANCH_ID%'
   OR sql_text LIKE '%branch_id = :b_branch_id%';
```

Alternative broader search:

```sql
SELECT sql_id,
       child_number,
       executions,
       is_bind_sensitive,
       is_bind_aware,
       SUBSTR(sql_text, 1, 80) AS sql_text
FROM v$sql
WHERE LOWER(sql_text) LIKE '%branch_transactions%'
AND LOWER(sql_text) LIKE '%branch_id%';
```

---

## Trainer Explanation

“Now we inspect V$SQL.

We want to see whether Oracle marked this SQL as bind sensitive or bind aware.

Also check if multiple child cursors exist.

Different child numbers may indicate different execution versions of the same SQL.”

---

# Slide 30: What Participants Should Look For

## Slide content:

Participants should identify:

* SQL ID
* Child number
* Executions
* `IS_BIND_SENSITIVE`
* `IS_BIND_AWARE`
* Plan for branch 1
* Plan for branch 3
* Whether multiple child cursors exist

---

## Trainer Explanation

“This is the main observation.

If the SQL is bind sensitive, Oracle noticed bind values matter.

If it is bind aware, Oracle may be adapting plans.

If multiple child cursors exist, check whether different child cursors have different plans.”

---

# Slide 31: Check Plans by SQL ID

## Slide content:

Use SQL ID from `V$SQL`:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('your_sql_id', NULL, 'ALLSTATS LAST +PREDICATE'));
```

For specific child cursor:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('your_sql_id', child_number, 'ALLSTATS LAST +PREDICATE'));
```

---

## Trainer Explanation

“When there are multiple child cursors, we can inspect each child separately.

This helps us see whether Oracle used one plan for small branch and another plan for large branch.

That is the core learning of this lab.”

---

# Slide 32: Expected Observations

## Slide content:

Possible result:

| Branch |   Rows | Possible Plan                 |
| ------ | -----: | ----------------------------- |
| 1      | 700000 | Full table scan               |
| 2      |   5000 | Index range scan or full scan |
| 3      |    500 | Index range scan              |

Possible `V$SQL` indicators:

```text
IS_BIND_SENSITIVE = Y
IS_BIND_AWARE = Y
```

---

## Trainer Explanation

“Your exact output may vary.

Oracle version, stats, histograms, and cursor cache behavior affect the result.

But conceptually, we expect branch 3 to prefer index access and branch 1 to prefer full scan.

If Oracle adapts, you may see bind-aware behavior.”

---

# Slide 33: If Bind Aware Does Not Appear

## Slide content:

If `IS_BIND_AWARE` is not `Y`, possible reasons:

* Not enough executions yet
* Data size too small
* Histogram not created
* Optimizer did not see enough difference
* Oracle version/settings behavior
* Cursor aged out
* Query changed slightly

Try:

* Execute multiple times with different values
* Regather stats with histogram
* Increase data skew
* Check exact SQL text

---

## Trainer Explanation

“This is important for the trainer.

Adaptive cursor sharing may not appear immediately.

Oracle needs evidence across executions.

If it does not show bind aware, do not panic.

Use it as a discussion point: Oracle adapts when it has enough reason and enough execution evidence.”

---

# Slide 34: Lab Task Worksheet

## Slide content:

| Task                | Observation |
| ------------------- | ----------- |
| Branch 1 row count  |             |
| Branch 2 row count  |             |
| Branch 3 row count  |             |
| Branch 1 plan       |             |
| Branch 3 plan       |             |
| SQL ID              |             |
| Child cursors found |             |
| Bind sensitive?     |             |
| Bind aware?         |             |
| Histogram exists?   |             |

---

## Trainer Explanation

“This worksheet helps participants record evidence.

The goal is to connect data distribution with plan behavior.

They should explain why one plan may be good for one value and bad for another.”

---

# Slide 35: When Histogram Helps

## Slide content:

Histogram helps when:

* Branch values are uneven
* Optimizer needs value-level information
* Some branches return huge rows
* Some branches return few rows
* Plan should depend on value selectivity

Histogram may not help when:

* Data is evenly distributed
* Column is not used in filters
* Query does not depend on value selectivity

---

## Trainer Explanation

“Histograms help optimizer understand skew.

In this lab, branch_id is a good histogram candidate because branch 1 and branch 3 are very different.

But in production, do not create histograms everywhere.

Use them where skew affects plan choice.”

---

# Slide 36: Production Risk Example

## Slide content:

Problem:

```sql
SELECT *
FROM transactions
WHERE branch_id = :branch_id;
```

If first execution uses:

```text
branch_id = 3
```

Oracle may choose index plan.

Later:

```text
branch_id = 1
```

Index plan may be reused and become slow.

Production impact:

* Branch dashboard slow
* Reports delayed
* CPU/I/O increases

---

## Trainer Explanation

“This is how bind peeking problems appear in production.

The first execution influences the plan.

Later executions with different values may suffer.

Adaptive cursor sharing and histograms are Oracle’s ways to reduce this risk.”

---

# Slide 37: Hints in This Scenario

## Slide content:

Possible hint:

```sql
SELECT /*+ FULL(branch_transactions) */ *
FROM branch_transactions
WHERE branch_id = :branch_id;
```

Problem:

* Good for branch 1
* Bad for branch 3

Another hint:

```sql
SELECT /*+ INDEX(branch_transactions idx_branch_txn_branch) */ *
FROM branch_transactions
WHERE branch_id = :branch_id;
```

Problem:

* Good for branch 3
* Bad for branch 1

---

## Trainer Explanation

“This shows why hints are risky.

If we force full scan, branch 1 may improve but branch 3 may suffer.

If we force index, branch 3 may improve but branch 1 may suffer.

When values are skewed, a single forced plan may not be correct.”

---

# Slide 38: Better Thinking Than Hints

## Slide content:

Instead of blindly hinting:

* Check data distribution
* Check histograms
* Check bind sensitivity
* Check adaptive cursor sharing
* Check actual plans for different values
* Consider SQL Profile or baseline carefully
* Consider query design change if needed

---

## Trainer Explanation

“This is the professional approach.

Do not use hints as the first fix.

First understand why plans differ.

If the issue is skew, histograms and adaptive cursor sharing may help.

If the issue is regression, baseline may help.

If query design is wrong, rewrite may be better.”

---

# Slide 39: Common Tuning Problems Covered

## Slide content:

This slot covers:

## Inefficient SQL

Wrong plan for bind value can make SQL inefficient.

## Suboptimal Application Design

Same query may be used for very different data volumes.

## Regression After Data Distribution Changes

As one branch grows, old plan may become bad.

## Degradation Over Time

Data skew increases over time and affects plan quality.

---

## Trainer Explanation

“This slot maps to multiple real-world problems.

A query may be fine initially, but as one branch grows, the plan may become inefficient.

Application design may also be too generic.

The same SQL is used for small and large branches, but the data behavior is very different.”

---

# Slide 40: Slot 2 Summary

## Slide content:

In this slot, we learned:

* Bind variables improve SQL reuse
* Bind peeking lets Oracle inspect bind values during parse
* Skewed data can make one plan unsuitable for all values
* Adaptive cursor sharing can create different child cursors
* Histograms help optimizer understand data distribution
* Hints force behavior and can be risky
* SQL Profiles, baselines, hints, and indexes solve different problems

---

## Trainer Explanation

“Let’s summarize.

Bind variables are good, but skewed data can create plan challenges.

If one branch has many rows and another has few rows, the optimizer may need different plans.

Adaptive cursor sharing and histograms help Oracle handle this.

Hints should be used carefully because one forced plan may hurt some values.”

---

# Slide 41: Transition to Slot 3

## Slide content:

Next slot:

# Concurrency, Locking and Short-Lived Performance Problems

We will learn:

* Row locks
* Blocking sessions
* Deadlocks
* Hot rows
* Long-running transactions
* How to diagnose blocking using dynamic views

---

## Trainer Explanation

“In this slot, we focused on optimizer behavior and bind values.

In the next slot, we move to another major production problem: locking and concurrency.

Sometimes SQL is not slow because of plan.

It is slow because it is waiting for another session.”

---

# Final Trainer Message for Slot 2

Use this line:

> “Bind variables help scalability, but skewed data can make one shared plan unsafe for every value.”
