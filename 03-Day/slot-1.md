Absolutely — here is **Day 3 — Slot 1 only**, focused on:

# SQL Plan Management

## 9:00 AM to 10:30 AM

---

# Day 3 — Slot 1

## SQL Plan Management

## Slot Objective

By the end of this slot, trainees should understand:

* Why a good SQL can suddenly become slow
* What execution plan regression means
* What SQL Plan Management is
* What SQL plan baselines are
* How to capture, accept, and evolve plans
* When to use plan baselines
* How plan baselines help stabilize critical banking SQL

---

# Suggested Slot Flow

| Time          | Section                                   |
| ------------- | ----------------------------------------- |
| 9:00 - 9:10   | Day 3 opening                             |
| 9:10 - 9:25   | Why good SQL becomes slow suddenly        |
| 9:25 - 9:45   | SQL Plan Management concepts              |
| 9:45 - 10:05  | Baselines, accepted plans, plan evolution |
| 10:05 - 10:25 | Lab 9: Capture and use SQL plan baseline  |
| 10:25 - 10:30 | Summary                                   |

---

# Slide 1: Day 3 Opening

## Slide content

## Day 3: Advanced Production Tuning

Today we focus on advanced production issues:

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

“Day 1 was about understanding SQL and execution plans.

Day 2 was about diagnosing workload-level problems using AWR, ADDM, and advisors.

Day 3 is about advanced production problems.

These are the problems where SQL was working fine yesterday, but today it is suddenly slow. Or the same SQL behaves differently for different users. Or sessions block each other.

We will start with SQL Plan Management.”

---

# Slide 2: Slot Title

## Slide content

# SQL Plan Management

This slot focuses on:

* Execution plan regression
* SQL plan baselines
* Capturing good plans
* Accepting plans
* Evolving plans
* Keeping critical SQL stable

---

## Trainer Explanation

“SQL Plan Management is mainly about plan stability.

In production, sometimes the SQL text has not changed, the application has not changed, but the performance changes.

Very often, the reason is that the optimizer picked a different execution plan.

SQL Plan Management helps us control this risk.”

---

# Slide 3: Why Good SQL Becomes Slow Suddenly

## Slide content

A SQL can become slow suddenly because of:

* Statistics refresh
* Data volume change
* Data distribution change
* New index
* Dropped index
* Bind value difference
* Optimizer parameter change
* Database upgrade
* Patch update
* Different execution plan

---

## Trainer Explanation

“This is a common production situation.

The business says: this payment query was fast yesterday, but today it is slow.

The SQL text may be exactly the same.

But Oracle may choose a new plan because something changed.

Maybe statistics were refreshed overnight.

Maybe a new index was added.

Maybe the data distribution changed.

Maybe the query received a different bind value.

So the root issue may be execution plan change.”

---

# Slide 4: What is Execution Plan Regression?

## Slide content

## Execution Plan Regression

Plan regression means Oracle changes from a good plan to a worse plan.

Example:

```text id="d3s1_regression_001"
Yesterday:
Index range scan → 1 second

Today:
Full table scan → 40 seconds
```

SQL text is same, but plan changed.

---

## Trainer Explanation

“Execution plan regression means the SQL starts using a worse plan.

This is dangerous because nothing obvious may look changed to the application team.

The query is the same, but performance is different.

As DBAs, we compare the old good plan and the new bad plan.”

---

# Slide 5: Banking Scenario

## Slide content

## Scenario

A payment settlement query was fast yesterday but slow today after statistics refresh.

Possible causes:

* New execution plan
* Changed statistics
* Different bind values
* New index
* Optimizer chose bad join method

---

## Trainer Explanation

“Let’s use a banking scenario.

Payment settlement is a critical process.

Yesterday it completed quickly.

Today, after statistics refresh, it became slow.

This is a classic plan regression case.

The optimizer may have received new statistics and decided to use a different access path or join method.

Our goal is to stabilize the good plan.”

---

# Slide 6: Why Plan Stability Matters in Banking

## Slide content

Critical banking SQL needs stable performance:

* Payment settlement
* Fund transfer posting
* Account balance update
* Loan EMI processing
* End-of-day batch
* Regulatory reports
* Fraud monitoring queries

For these queries, sudden plan changes can cause business impact.

---

## Trainer Explanation

“In banking, some SQL statements are business-critical.

If a normal report is slow, it is painful.

But if payment settlement or fund transfer posting is slow, it becomes a serious operational issue.

For such SQL, we care not only about fastest performance, but also predictable performance.”

---

# Slide 7: What is SQL Plan Management?

## Slide content

## SQL Plan Management, also called SPM

SQL Plan Management helps prevent unwanted execution plan changes.

It allows Oracle to:

* Capture known good plans
* Store them as baselines
* Use accepted plans
* Test new plans before using them
* Evolve better plans safely

---

## Trainer Explanation

“SQL Plan Management is Oracle’s way of controlling execution plan stability.

It does not stop Oracle from finding new plans.

But it helps Oracle avoid using unverified bad plans.

A known good plan can be stored as a baseline.

Then Oracle can prefer accepted plans for that SQL.”

---

# Slide 8: Simple Explanation

## Slide content

Think of SPM like approved routes.

```text id="d3s1_route_001"
Old route: Tested and reliable
New route: May be faster, but not verified
```

SPM says:

```text id="d3s1_route_002"
Use approved route unless the new route is tested and accepted.
```

---

## Trainer Explanation

“Imagine a bank cash vehicle route.

You do not suddenly change the route just because a map says another road may be faster.

You first verify safety and reliability.

Similarly, SPM helps Oracle use approved execution plans unless a new plan is tested and accepted.”

---

# Slide 9: What is a SQL Plan Baseline?

## Slide content

## SQL Plan Baseline

A SQL plan baseline is a stored accepted execution plan for a SQL statement.

It helps Oracle choose a stable plan.

A baseline contains:

* SQL signature
* Plan information
* Enabled status
* Accepted status
* Plan name
* SQL handle

---

## Trainer Explanation

“A SQL plan baseline stores a known plan for a SQL.

Oracle can use it later to keep the execution plan stable.

Baselines are not just text notes. They are stored metadata that Oracle optimizer can use during plan selection.

The important fields are enabled and accepted.”

---

# Slide 10: Enabled vs Accepted

## Slide content

## Enabled

The plan is available for use.

## Accepted

The plan is approved as safe for use.

Common status:

| Enabled | Accepted | Meaning                |
| ------- | -------- | ---------------------- |
| YES     | YES      | Usable approved plan   |
| YES     | NO       | Known but not approved |
| NO      | YES/NO   | Not available for use  |

---

## Trainer Explanation

“Enabled means Oracle can consider the plan.

Accepted means the plan is approved.

A plan can exist but not be accepted.

By default, Oracle should use accepted plans.

New plans can be captured but need to be evolved or accepted before they become trusted.”

---

# Slide 11: Capturing Plans

## Slide content

Plans can be captured from:

* Cursor cache
* SQL tuning set
* AWR
* Existing stored outlines, in some cases
* Automatic plan capture, if enabled

Common lab method:

```text id="d3s1_capture_001"
Run SQL → Get SQL_ID → Load plan from cursor cache
```

---

## Trainer Explanation

“In our lab, we will use cursor cache.

That means we run the SQL so the plan is available in memory.

Then we use SQL ID to load the plan into a baseline.

In production, plans can also come from SQL tuning sets or AWR.”

---

# Slide 12: Accepting Plans

## Slide content

Accepted plans are approved for optimizer use.

Why acceptance matters:

* Prevents untested plans from being used
* Gives stability
* Reduces risk of sudden regression
* Helps critical SQL stay predictable

---

## Trainer Explanation

“Accepting a plan means we trust it.

For critical banking SQL, we may want only tested plans to be accepted.

This helps prevent sudden optimizer decisions from changing production behavior.”

---

# Slide 13: Evolving Plans

## Slide content

## Plan Evolution

Plan evolution means testing new plans before accepting them.

Oracle can compare:

```text id="d3s1_evolve_001"
Existing accepted plan
vs
New candidate plan
```

If the new plan performs better, it can be accepted.

---

## Trainer Explanation

“SPM does not mean we freeze performance forever.

Sometimes new plans are genuinely better.

Plan evolution allows Oracle or DBAs to test new plans.

If the new plan is better, it can be accepted.

This gives both stability and improvement.”

---

# Slide 14: When to Use Plan Baselines

## Slide content

Use plan baselines when:

* Critical SQL must be stable
* SQL had plan regression
* Performance changed after stats refresh
* Database upgrade may change plans
* New indexes may affect optimizer choices
* Application SQL cannot be changed
* Business process needs predictable runtime

---

## Trainer Explanation

“Plan baselines are useful for high-risk SQL.

Do not use them for every SQL in the database.

Use them where plan stability matters.

For example, payment settlement, end-of-day processing, or critical dashboards.”

---

# Slide 15: When Not to Use Plan Baselines

## Slide content

Do not overuse baselines when:

* SQL is not business-critical
* Plan issue is caused by bad SQL design
* Statistics are badly maintained
* Indexing strategy is poor
* Data model needs correction
* You are hiding the real problem
* Many plans are changing due to unstable workload

---

## Trainer Explanation

“Plan baselines are not a replacement for good SQL design.

If SQL is badly written, fix SQL.

If statistics are always stale, fix statistics process.

If indexing is poor, improve access design.

Baselines are for stability, not for hiding all tuning problems.”

---

# Slide 16: SQL Plan Baseline vs SQL Profile vs Hint

## Slide content

| Feature           | Purpose                                           |
| ----------------- | ------------------------------------------------- |
| SQL Plan Baseline | Controls accepted plans                           |
| SQL Profile       | Gives optimizer extra information                 |
| Hint              | Suggests or forces optimizer behavior in SQL text |
| Index             | Provides access structure                         |

---

## Trainer Explanation

“This distinction is important.

A baseline controls which plan is allowed.

A SQL Profile helps optimizer estimate better.

A hint changes SQL behavior directly.

An index changes physical access possibilities.

They solve different problems.”

---

# Slide 17: Banking Use Case

## Slide content

## Stable Plans for Critical Payment Queries

Example critical query:

```sql id="d3s1_payment_query_001"
SELECT payment_id, customer_id, amount, status
FROM payments
WHERE settlement_date = TRUNC(SYSDATE)
AND status = 'PENDING';
```

Risk:

* Plan changes after stats refresh
* Query becomes slow during settlement window
* Payment processing gets delayed

---

## Trainer Explanation

“This is a simple payment settlement example.

The query fetches pending payments for today.

If this query suddenly changes plan and becomes slow, payment processing may be delayed.

A baseline can help keep the known good plan stable.”

---

# Slide 18: Lab 9 Objective

## Slide content

## Lab 9: Capture and Use SQL Plan Baseline

Participants will:

1. Run query with good plan
2. Capture plan baseline
3. View baseline
4. Change condition or environment
5. Observe possible plan change
6. Use baseline for stability

---

## Trainer Explanation

“In this lab, we will practice the baseline workflow.

The exact plan change may vary by environment.

So the important part is learning the process: run SQL, capture SQL ID, load plan, view baseline, and understand how it protects plan stability.”

---

# Slide 19: Lab Setup — Payments Table

## Slide content

Create sample table:

```sql id="d3s1_create_payments_001"
DROP TABLE payments PURGE;

CREATE TABLE payments (
    payment_id       NUMBER PRIMARY KEY,
    customer_id      NUMBER,
    account_id       NUMBER,
    branch_id        NUMBER,
    settlement_date  DATE,
    amount           NUMBER(12,2),
    status           VARCHAR2(20),
    created_date     DATE
);
```

---

## Trainer Explanation

“We create a payments table for the lab.

This represents settlement or payment processing data.

The important columns for our scenario are settlement_date and status.”

---

# Slide 20: Insert Sample Payment Data

## Slide content

```sql id="d3s1_insert_payments_001"
BEGIN
  FOR i IN 1..200000 LOOP
    INSERT INTO payments (
      payment_id, customer_id, account_id, branch_id,
      settlement_date, amount, status, created_date
    )
    VALUES (
      i,
      MOD(i, 5000) + 1,
      MOD(i, 20000) + 1,
      MOD(i, 50) + 1,
      TRUNC(SYSDATE) - MOD(i, 30),
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      CASE MOD(i, 10)
        WHEN 0 THEN 'PENDING'
        WHEN 1 THEN 'FAILED'
        ELSE 'SETTLED'
      END,
      SYSDATE - MOD(i, 60)
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

“This inserts sample payment data across recent settlement dates.

Most records are settled, some are pending, and some failed.

This gives us data distribution for the optimizer to work with.”

---

# Slide 21: Gather Statistics

## Slide content

```sql id="d3s1_gather_stats_001"
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'PAYMENTS',
    cascade => TRUE
  );
END;
/
```

---

## Trainer Explanation

“We gather statistics so the optimizer has information about the table.

Since this slot discusses plan changes after statistics refresh, it is important to understand that stats influence optimizer decisions.”

---

# Slide 22: Create Supporting Index

## Slide content

Create index for good plan:

```sql id="d3s1_create_index_001"
CREATE INDEX idx_payments_status_date
ON payments(status, settlement_date);
```

Gather stats again:

```sql id="d3s1_gather_stats_002"
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'PAYMENTS', cascade => TRUE);
END;
/
```

---

## Trainer Explanation

“This index supports the payment settlement query because the query filters by status and settlement date.

In our lab, this can help create a good index-based plan.

We will capture that plan as a baseline.”

---

# Slide 23: Run Query with Good Plan

## Slide content

```sql id="d3s1_run_good_query_001"
ALTER SESSION SET statistics_level = ALL;

SELECT payment_id, customer_id, amount, status
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

Check plan:

```sql id="d3s1_check_plan_001"
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE'));
```

---

## Trainer Explanation

“Now we run the payment query.

Then we check the actual plan.

Ideally, we want to see the index being used.

If the plan is good and efficient, this is a candidate plan to capture.”

---

# Slide 24: Find SQL ID

## Slide content

Find SQL ID:

```sql id="d3s1_find_sqlid_001"
SELECT sql_id,
       plan_hash_value,
       executions,
       elapsed_time,
       buffer_gets,
       SUBSTR(sql_text, 1, 100) AS sql_text
FROM v$sql
WHERE sql_text LIKE '%FROM payments%'
AND sql_text LIKE '%PENDING%'
ORDER BY last_active_time DESC;
```

---

## Trainer Explanation

“To capture the plan, we need SQL ID.

We search V$SQL using part of the query text.

Plan hash value is also useful because it identifies the plan shape.

In production, we may get SQL ID from AWR, monitoring tools, or application logs.”

---

# Slide 25: Capture Baseline from Cursor Cache

## Slide content

Replace `your_sql_id`:

```sql id="d3s1_capture_baseline_001"
DECLARE
  l_plans_loaded PLS_INTEGER;
BEGIN
  l_plans_loaded := DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(
    sql_id => 'your_sql_id'
  );

  DBMS_OUTPUT.PUT_LINE('Plans loaded: ' || l_plans_loaded);
END;
/
```

---

## Trainer Explanation

“This command loads the plan from cursor cache into SQL Plan Management.

The SQL must have been executed recently so that its plan is still in cursor cache.

The output tells us how many plans were loaded.

If it loads zero plans, check SQL ID and cursor availability.”

---

# Slide 26: View Baselines

## Slide content

```sql id="d3s1_view_baseline_001"
SELECT sql_handle,
       plan_name,
       enabled,
       accepted
FROM dba_sql_plan_baselines;
```

More detail:

```sql id="d3s1_view_baseline_detail_001"
SELECT sql_handle,
       plan_name,
       enabled,
       accepted,
       fixed,
       created,
       last_executed
FROM dba_sql_plan_baselines
ORDER BY created DESC;
```

---

## Trainer Explanation

“Now we check whether the baseline exists.

Look at enabled and accepted.

If enabled is YES and accepted is YES, Oracle can use this plan.

This confirms that the plan has been captured.”

---

# Slide 27: Observe Plan Stability

## Slide content

Run the same query again:

```sql id="d3s1_rerun_query_001"
SELECT payment_id, customer_id, amount, status
FROM payments
WHERE status = 'PENDING'
AND settlement_date = TRUNC(SYSDATE);
```

Check plan:

```sql id="d3s1_rerun_plan_001"
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL, NULL, 'ALLSTATS LAST +PREDICATE +NOTE'));
```

Look for note:

```text id="d3s1_note_001"
SQL plan baseline used
```

---

## Trainer Explanation

“When we run the query again, check the plan notes.

If Oracle uses the baseline, the plan output may show a note that SQL plan baseline was used.

This confirms that SPM is influencing plan selection.”

---

# Slide 28: Simulate Environment Change

## Slide content

Possible simulation options:

Option 1: Drop or make index invisible:

```sql id="d3s1_invisible_index_001"
ALTER INDEX idx_payments_status_date INVISIBLE;
```

Option 2: Gather stats again:

```sql id="d3s1_stats_refresh_001"
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'PAYMENTS', cascade => TRUE);
END;
/
```

Then re-run query and check plan.

---

## Trainer Explanation

“In real life, plan changes can happen after stats refresh, new index, dropped index, or data change.

In the lab, we can simulate change.

Making an index invisible or refreshing stats can influence optimizer choices.

But remember: if the baseline plan requires an index that is invisible or unavailable, Oracle may not be able to use that exact plan.

So lab behavior may vary.”

---

# Slide 29: Important Lab Note

## Slide content

Plan baseline behavior may vary depending on:

* Oracle version
* Existing indexes
* Statistics
* Data volume
* Optimizer settings
* Whether required access structures exist
* Cursor cache availability

Main learning:

```text id="d3s1_lab_note_001"
Capture good plan → Store baseline → Use accepted plan for stability
```

---

## Trainer Explanation

“This is important for you as trainer.

Do not promise that every lab machine will show the exact same plan change.

Oracle optimizer behavior depends on environment.

The main learning is the workflow and concept, not forcing one identical output everywhere.”

---

# Slide 30: Accepting and Evolving Plans

## Slide content

View evolve report:

```sql id="d3s1_evolve_report_001"
SET LONG 100000
SELECT DBMS_SPM.EVOLVE_SQL_PLAN_BASELINE(
  sql_handle => 'your_sql_handle'
) AS report
FROM dual;
```

Purpose:

* Test new plans
* Compare with accepted plan
* Accept better plan if verified

---

## Trainer Explanation

“Plan evolution is how we safely allow better plans.

If Oracle finds a new candidate plan, we can test it.

If it performs better, we can accept it.

This prevents random plan changes while still allowing improvement.”

---

# Slide 31: Fixed Baselines

## Slide content

A fixed baseline gives stronger preference to a plan.

Check fixed status:

```sql id="d3s1_fixed_check_001"
SELECT sql_handle, plan_name, fixed
FROM dba_sql_plan_baselines;
```

Use carefully.

Fixed baselines can help emergencies but may block better plans.

---

## Trainer Explanation

“Fixed baselines are stronger.

They tell Oracle to strongly prefer that plan.

This can be useful during emergency regression.

But overuse can prevent better plans from being used later.

Use fixed baselines carefully.”

---

# Slide 32: Lab Task Worksheet

## Slide content

Participants should record:

| Task                                   | Observation |
| -------------------------------------- | ----------- |
| SQL ID                                 |             |
| Plan hash value before baseline        |             |
| Baseline created?                      |             |
| SQL handle                             |             |
| Plan name                              |             |
| Enabled?                               |             |
| Accepted?                              |             |
| Baseline used after rerun?             |             |
| Plan changed after environment change? |             |

---

## Trainer Explanation

“This worksheet helps participants document the process.

The important output is not only that a baseline exists.

They should also know SQL ID, plan hash value, baseline status, and whether the baseline was used.”

---

# Slide 33: When Baseline Helps

## Slide content

Plan baseline helps when:

* Good plan is known
* Bad plan appeared after change
* SQL is business-critical
* Application SQL cannot be changed
* Need quick stabilization
* Database upgrade risk exists
* Stats refresh caused regression

---

## Trainer Explanation

“Baselines are very useful for stabilizing known critical SQL.

If a payment query regresses after stats refresh, capturing or restoring a good plan can be a practical fix.

But it should still be followed by root cause analysis.”

---

# Slide 34: When Baseline Is Not Enough

## Slide content

Baseline may not solve:

* Bad SQL logic
* Missing required indexes
* Huge data growth
* Wrong business filters
* Locking issues
* I/O bottlenecks
* Memory pressure
* Application fetching too much data

---

## Trainer Explanation

“SPM controls plans, but it does not fix everything.

If the query returns too much data, baseline cannot change business logic.

If there is locking, baseline will not solve blockers.

If storage is slow, baseline may not be enough.

So use baselines for plan stability, not as a universal fix.”

---

# Slide 35: Production Safety Checklist

## Slide content

Before using baselines in production:

* Confirm SQL is business-critical
* Capture current good plan
* Compare old and new plans
* Test baseline in non-production
* Check required indexes exist
* Monitor after applying
* Document rollback
* Review periodically

---

## Trainer Explanation

“In production, plan baselines should be managed carefully.

They are powerful but need governance.

If many baselines are created and never reviewed, they may become technical debt.

Review them periodically.”

---

# Slide 36: Common Tuning Problems Covered

## Slide content

This slot covers:

## Performance Regression After Environment Changes

Plan changed after stats refresh, upgrade, or index change.

## Degradation Over Time

Data growth or distribution change affects optimizer choices.

## Database Configuration/Statistics Issues

Statistics or optimizer settings may trigger plan changes.

---

## Trainer Explanation

“This slot maps directly to plan regression problems.

When performance changes after environment changes, SQL Plan Management helps stabilize known good behavior.

It is especially useful after statistics refreshes, upgrades, and new index deployments.”

---

# Slide 37: Slot 1 Summary

## Slide content

In this slot, we learned:

* SQL can become slow because execution plan changed
* Plan regression means good plan changed to bad plan
* SQL Plan Management helps stabilize plans
* SQL plan baselines store accepted plans
* Plans can be captured from cursor cache
* New plans can be evolved safely
* Baselines are useful for critical banking SQL

---

## Trainer Explanation

“Let’s summarize.

A SQL can become slow even when the SQL text is unchanged.

The optimizer may choose a different plan because of changed statistics, data, bind values, or indexes.

SQL Plan Management helps protect critical SQL from unexpected plan changes.

But baselines should be used carefully and validated.”

---

# Slide 38: Transition to Slot 2

## Slide content

Next slot:

# Bind Peeking, Adaptive Cursor Sharing, Hints and SQL Profiles

We will learn:

* Why same SQL behaves differently for different bind values
* What bind peeking is
* What adaptive cursor sharing does
* When hints and SQL Profiles are useful
* Risks of forcing plans

---

## Trainer Explanation

“In this slot, we learned how to stabilize plans.

In the next slot, we will learn why the same SQL can behave differently for different bind values.

That leads us to bind peeking and adaptive cursor sharing.”

---

# Final Trainer Message for Slot 1

Use this line:

> “SQL Plan Management is not about making SQL faster first. It is about keeping critical SQL stable and preventing surprise regressions.”
