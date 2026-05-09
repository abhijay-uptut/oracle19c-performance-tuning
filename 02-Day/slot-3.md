Absolutely — here is **Day 2 — Slot 3 only**, focused on:

# SQL Tuning Advisor

## 1:00 PM to 2:30 PM

---

# Day 2 — Slot 3

## SQL Tuning Advisor

## Slot Objective

By the end of this slot, trainees should understand:

* What SQL Tuning Advisor is
* When to use it
* How it analyzes one SQL statement
* What SQL Profiles are
* What advisor recommendations mean
* How to validate recommendations before applying
* Why blindly accepting advisor output is risky
* How to create, execute, and review a SQL tuning task

---

# Suggested Slot Flow

| Time        | Section                           |
| ----------- | --------------------------------- |
| 1:00 - 1:10 | What is SQL Tuning Advisor?       |
| 1:10 - 1:25 | Advisor recommendation types      |
| 1:25 - 1:40 | SQL Profiles and validation       |
| 1:40 - 2:10 | Lab 7: Create and run tuning task |
| 2:10 - 2:25 | Review advisor report             |
| 2:25 - 2:30 | Summary                           |

---

# Slide 1: Slot Title

## SQL Tuning Advisor

**Slide content:**

SQL Tuning Advisor helps analyze and tune one specific SQL statement.

In this slot, we will learn:

* When to use SQL Tuning Advisor
* What recommendations it gives
* What SQL Profiles are
* How to validate advisor output
* How to run a tuning task

---

## Trainer Explanation

“In the previous slots, we learned AWR and ADDM.

AWR helps us find workload-level problems.

ADDM helps us understand likely causes and recommendations.

Now suppose ADDM or AWR points us to one specific SQL ID.

This is where SQL Tuning Advisor becomes useful.

It helps us analyze one SQL statement deeply.”

---

# Slide 2: What is SQL Tuning Advisor?

## Slide content

## SQL Tuning Advisor

SQL Tuning Advisor is an Oracle advisor that analyzes a SQL statement and suggests tuning actions.

It can recommend:

* SQL Profile
* Index creation
* Statistics gathering
* SQL restructuring
* Alternative execution approach

---

## Trainer Explanation

“SQL Tuning Advisor is designed for single SQL tuning.

It looks at one SQL statement and checks whether Oracle can improve its execution.

It may recommend creating an index, gathering statistics, accepting a SQL Profile, or rewriting part of the SQL.

But like all advisors, its output must be reviewed carefully.”

---

# Slide 3: Where SQL Tuning Advisor Fits

## Slide content

Performance diagnosis flow:

```text id="day2s3_flow_001"
AWR finds expensive SQL
        ↓
ADDM recommends SQL tuning
        ↓
SQL Tuning Advisor analyzes specific SQL
        ↓
DBA validates recommendation
        ↓
Fix is tested and applied safely
```

---

## Trainer Explanation

“This is the correct flow.

We do not randomly run SQL Tuning Advisor on every SQL.

First, AWR or ADDM shows us which SQL matters.

Then we run SQL Tuning Advisor for that SQL.

After that, we validate the recommendation before applying anything in production.”

---

# Slide 4: When to Use SQL Tuning Advisor

## Slide content

Use SQL Tuning Advisor when:

* One SQL consumes high DB time
* One SQL appears in AWR top SQL
* ADDM recommends tuning a SQL
* Query suddenly became slow
* Execution plan changed
* SQL has high buffer gets or physical reads
* Business-critical SQL needs optimization

---

## Trainer Explanation

“SQL Tuning Advisor is best when we already know the SQL causing the issue.

For example, if one loan eligibility query is taking 40 seconds and appears in AWR top SQL, that is a good candidate.

But if the whole database is slow due to I/O or locking, SQL Tuning Advisor alone may not solve the problem.”

---

# Slide 5: When Not to Use It First

## Slide content

Do not start with SQL Tuning Advisor when:

* Root cause is unknown
* Issue is locking or blocking
* Database has severe I/O problem
* Server CPU is saturated by many SQLs
* Application is fetching unnecessary data
* SQL is not business-important
* You have not checked AWR/ADDM evidence

---

## Trainer Explanation

“SQL Tuning Advisor is useful, but it is not the first answer for every issue.

If users say the entire system is slow, first check AWR.

If the problem is locking, you need locking diagnosis.

If the problem is application fetching millions of rows, advisor may not understand the business requirement.

So use the right tool at the right stage.”

---

# Slide 6: Banking Scenario

## Slide content

## Scenario

A loan eligibility query runs for 40 seconds.

Business impact:

* Loan officer waits on screen
* Customer onboarding is delayed
* Branch productivity is affected

DBA goal:

```text id="day2s3_goal_001"
Tune only this SQL without changing the entire application.
```

---

## Trainer Explanation

“Let’s take a banking example.

A loan eligibility screen checks customer profile, income, credit history, existing loans, and transaction behavior.

One query takes 40 seconds.

The business wants this specific screen to improve.

We do not want to change the full application.

So SQL Tuning Advisor can help analyze this one SQL.”

---

# Slide 7: What SQL Tuning Advisor Checks

## Slide content

SQL Tuning Advisor may check:

* Optimizer statistics
* Access paths
* Index possibilities
* Join order
* SQL structure
* Cardinality estimates
* Potential SQL Profile
* Estimated benefit of recommendation

---

## Trainer Explanation

“The advisor checks multiple things.

It may find that statistics are stale.

It may find that an index can help.

It may find that the optimizer needs extra information through a SQL Profile.

It may also suggest restructuring SQL.

But the DBA must understand what kind of recommendation is being made.”

---

# Slide 8: Recommendation Type — Statistics

## Slide content

## Statistics Recommendation

Advisor may recommend:

```text id="day2s3_stats_001"
Gather optimizer statistics
```

Possible reason:

* Table stats are stale
* Index stats are missing
* Column data distribution changed
* Optimizer estimates are wrong

---

## Trainer Explanation

“If statistics are old or missing, the optimizer may choose a bad plan.

SQL Tuning Advisor may recommend gathering statistics.

This is usually safer than many other changes, but still should be tested.

In production, statistics gathering can also change plans for many SQLs, so we must be careful.”

---

# Slide 9: Recommendation Type — Index

## Slide content

## Index Recommendation

Advisor may recommend creating an index.

Example:

```sql id="day2s3_index_001"
CREATE INDEX idx_loan_customer_status
ON loans(customer_id, loan_status);
```

Possible benefit:

* Less full table scan
* Faster filtering
* Better join access
* Lower logical reads

---

## Trainer Explanation

“Index recommendations are common.

But never blindly create the index.

Ask: how often does this SQL run?

Is the table write-heavy?

Does a similar index already exist?

Will the index slow down inserts or updates?

Does it help only one query or multiple important queries?”

---

# Slide 10: Recommendation Type — SQL Profile

## Slide content

## SQL Profile

A SQL Profile gives the optimizer extra information to choose a better plan.

It does not change SQL text.

It helps correct optimizer estimates.

Useful when:

* Optimizer misestimates rows
* Query plan is poor
* SQL text cannot be changed easily
* Application code cannot be modified quickly

---

## Trainer Explanation

“A SQL Profile is not the same as an index.

It does not store data.

It does not rewrite SQL text.

It gives additional information to the optimizer so it can choose a better plan.

This is useful when we cannot change application SQL easily.”

---

# Slide 11: SQL Profile — Simple Analogy

## Slide content

SQL Profile is like giving the optimizer better guidance.

```text id="day2s3_profile_001"
Without profile:
Optimizer makes decision with incomplete knowledge.

With profile:
Optimizer gets extra correction information.
```

---

## Trainer Explanation

“Think of the optimizer like a driver using a map.

If the map has wrong traffic information, the driver may choose the wrong route.

A SQL Profile gives the optimizer better guidance.

But it still needs validation because it can affect future executions of that SQL.”

---

# Slide 12: SQL Profile vs Index vs Hint

## Slide content

| Item        | What it does                       | Changes SQL text? |
| ----------- | ---------------------------------- | ----------------- |
| Index       | Adds access structure              | No                |
| Hint        | Forces/suggests optimizer behavior | Yes               |
| SQL Profile | Gives optimizer extra information  | No                |
| Statistics  | Updates data knowledge             | No                |

---

## Trainer Explanation

“This comparison is useful.

An index changes database structure.

A hint changes SQL text.

A SQL Profile changes optimizer guidance without changing the application SQL.

Statistics update optimizer knowledge.

Each option has a different risk and use case.”

---

# Slide 13: Recommendation Type — SQL Restructuring

## Slide content

Advisor may suggest rewriting SQL.

Examples:

* Remove unnecessary columns
* Simplify subqueries
* Rewrite joins
* Avoid functions on columns
* Add selective predicates
* Reduce unnecessary sorting

---

## Trainer Explanation

“Sometimes the best fix is SQL restructuring.

For example, the query may be logically correct but inefficient.

Maybe it uses unnecessary subqueries.

Maybe it fetches too many columns.

Maybe it filters late instead of early.

Advisor may suggest restructuring, but the application team usually needs to validate business correctness.”

---

# Slide 14: Why Validation is Important

## Slide content

Before applying recommendations, validate:

* Does it improve execution time?
* Does it reduce logical reads?
* Does it reduce physical reads?
* Does the execution plan improve?
* Does it affect other SQLs?
* Is it safe for DML-heavy tables?
* Can we rollback?

---

## Trainer Explanation

“This is a production safety slide.

Advisor output is not automatically correct for your business.

An index may improve one query but hurt transaction inserts.

A SQL Profile may improve one bind value but not another.

Statistics gathering may change many plans.

So always validate before production.”

---

# Slide 15: Risks of Blindly Accepting Advisor Output

## Slide content

Risks include:

* Extra indexes slowing down DML
* More storage usage
* Plan changes for other SQL
* SQL Profile causing unexpected plan behavior
* Fix helps test case but not real workload
* Recommendation ignores business context
* No rollback plan

---

## Trainer Explanation

“In banking systems, blind tuning is dangerous.

One index may slow down fund transfer inserts.

One profile may change behavior for a critical SQL.

One statistics refresh may change many plans.

So the DBA must test, document, and apply changes safely.”

---

# Slide 16: Recommended Validation Workflow

## Slide content

Use this workflow:

```text id="day2s3_validation_001"
1. Identify SQL ID
2. Capture current plan and metrics
3. Run SQL Tuning Advisor
4. Review recommendation
5. Test recommendation in lower environment
6. Compare before/after
7. Check side effects
8. Prepare rollback
9. Apply with approval
10. Monitor after change
```

---

## Trainer Explanation

“This is the workflow I want participants to remember.

Advisor is only one step.

The real DBA work is validation.

Before and after comparison is mandatory.

In banks, approval and rollback planning are also very important.”

---

# Slide 17: Lab 7 Objective

## Slide content

## Lab 7: SQL Tuning Advisor

Participants will:

1. Find a SQL ID
2. Create a tuning task
3. Execute the tuning task
4. View advisor report
5. Evaluate recommendations
6. Decide validation steps

---

## Trainer Explanation

“Now we will run SQL Tuning Advisor.

The goal is not to blindly accept anything.

The goal is to learn the process and evaluate advisor recommendations like a DBA.”

---

# Slide 18: Lab Prerequisites

## Slide content

Before lab, confirm:

* Oracle Enterprise Edition
* Tuning Pack license/permission
* Required privileges
* Workload SQL executed at least once
* SQL ID available from cursor cache or AWR

Useful views:

```sql id="day2s3_views_001"
V$SQL
DBA_HIST_SQLSTAT
DBA_ADVISOR_TASKS
```

---

## Trainer Explanation

“SQL Tuning Advisor requires proper license and privileges.

In production banks, always confirm licensing and approval.

For the lab, we need a SQL ID.

The SQL must exist in memory or AWR history so the advisor can analyze it.”

---

# Slide 19: Create Lab SQL

## Slide content

Run this sample loan eligibility query:

```sql id="day2s3_loan_query_001"
SELECT c.customer_id,
       c.full_name,
       c.status,
       COUNT(t.transaction_id) AS txn_count,
       SUM(t.amount) AS total_amount
FROM customers c
JOIN transactions t
  ON c.customer_id = t.customer_id
WHERE c.status = 'ACTIVE'
AND t.transaction_date >= ADD_MONTHS(SYSDATE, -12)
GROUP BY c.customer_id, c.full_name, c.status
ORDER BY total_amount DESC;
```

---

## Trainer Explanation

“This query simulates a loan eligibility workload.

It joins customers and transactions.

It checks active customers and last 12 months of transaction activity.

Then it aggregates transaction count and total amount.

This kind of query can become expensive on large data.”

---

# Slide 20: Find SQL ID

## Slide content

Find the SQL ID from `V$SQL`:

```sql id="day2s3_find_sqlid_001"
SELECT sql_id,
       executions,
       elapsed_time,
       cpu_time,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text, 1, 80) AS sql_text
FROM v$sql
WHERE LOWER(sql_text) LIKE '%loan%'
   OR LOWER(sql_text) LIKE '%total_amount%'
ORDER BY last_active_time DESC;
```

Alternative:

```sql id="day2s3_find_sqlid_002"
SELECT sql_id,
       executions,
       elapsed_time,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text, 1, 100) AS sql_text
FROM v$sql
WHERE sql_text LIKE '%ADD_MONTHS(SYSDATE, -12)%'
ORDER BY last_active_time DESC;
```

---

## Trainer Explanation

“After running the SQL, we need its SQL ID.

We search V$SQL using part of the SQL text.

In real production, we may get SQL ID from AWR, ADDM, monitoring tools, or application logs.

Once we have SQL ID, we can create the tuning task.”

---

# Slide 21: Check Current Plan First

## Slide content

Before advisor, capture current plan:

```sql id="day2s3_current_plan_001"
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR('your_sql_id', NULL, 'ALLSTATS LAST +PREDICATE'));
```

Record:

* Current access path
* Join method
* Estimated rows
* Actual rows
* Buffers
* Reads
* Cost

---

## Trainer Explanation

“Before running the advisor, capture the current plan.

Why?

Because we need a baseline.

If we later apply a recommendation, we compare against this original plan.

Without before data, we cannot prove improvement.”

---

# Slide 22: Create Tuning Task

## Slide content

Create tuning task:

```sql id="day2s3_create_task_001"
DECLARE
  l_task_name VARCHAR2(100);
BEGIN
  l_task_name := DBMS_SQLTUNE.CREATE_TUNING_TASK(
    sql_id      => 'your_sql_id',
    scope       => DBMS_SQLTUNE.SCOPE_COMPREHENSIVE,
    time_limit  => 60,
    task_name   => 'loan_query_tuning_task'
  );
END;
/
```

---

## Trainer Explanation

“This creates a SQL tuning task.

Replace `your_sql_id` with the SQL ID we found.

The scope is comprehensive, meaning the advisor can do deeper analysis.

The time limit is 60 seconds, so the advisor does not run forever.

The task name is our label for this tuning activity.”

---

# Slide 23: Execute Tuning Task

## Slide content

Run:

```sql id="day2s3_execute_task_001"
EXEC DBMS_SQLTUNE.EXECUTE_TUNING_TASK('loan_query_tuning_task');
```

Check task status:

```sql id="day2s3_task_status_001"
SELECT task_name, status
FROM dba_advisor_tasks
WHERE task_name = 'loan_query_tuning_task';
```

---

## Trainer Explanation

“After creating the task, we execute it.

Then we check task status.

If status is COMPLETED, we can view the report.

If it fails, check privileges, SQL ID, or whether the SQL is still available.”

---

# Slide 24: View Tuning Report

## Slide content

View report:

```sql id="day2s3_report_001"
SELECT DBMS_SQLTUNE.REPORT_TUNING_TASK('loan_query_tuning_task')
FROM dual;
```

For readable output:

```sql id="day2s3_report_output_001"
SET LONG 100000
SET LONGCHUNKSIZE 100000
SET LINESIZE 200
```

Then run report again.

---

## Trainer Explanation

“The report may be long, so we set LONG and LINESIZE to make it readable.

The report will show findings and recommendations.

Read it slowly.

Look for statistics recommendations, SQL Profile recommendations, index recommendations, or SQL restructuring suggestions.”

---

# Slide 25: Understanding the Report

## Slide content

In the report, look for:

* Findings
* Recommendation type
* Estimated benefit
* SQL Profile recommendation
* Index recommendation
* Statistics recommendation
* SQL restructure advice
* Commands suggested by Oracle

---

## Trainer Explanation

“Do not just scroll to the command and execute it.

Read the full report.

Understand what problem Oracle found.

Then understand what action it recommends.

Then ask whether that action is safe in your workload.”

---

# Slide 26: If Advisor Suggests SQL Profile

## Slide content

Advisor may show:

```text id="day2s3_profile_rec_001"
Recommendation: Accept SQL Profile
Estimated benefit: XX%
```

Possible command:

```sql id="day2s3_accept_profile_001"
EXEC DBMS_SQLTUNE.ACCEPT_SQL_PROFILE(
  task_name => 'loan_query_tuning_task',
  task_owner => USER,
  replace => TRUE
);
```

Important:

Do not accept blindly in production.

---

## Trainer Explanation

“If advisor suggests a SQL Profile, it may estimate a benefit.

But accepting a SQL Profile affects future executions of that SQL.

In lab, we can test it.

In production, we need approval, testing, and rollback plan.

Also check whether the SQL uses different bind values that may behave differently.”

---

# Slide 27: If Advisor Suggests Index

## Slide content

Advisor may suggest:

```sql id="day2s3_index_rec_001"
CREATE INDEX ...
```

Before creating, check:

* Existing indexes
* Table DML volume
* Index storage
* Similar SQL benefit
* Impact on inserts/updates/deletes
* Whether composite index can support more queries

---

## Trainer Explanation

“Index recommendation needs careful review.

For a loan eligibility query, an index may improve read performance.

But if the table is transaction-heavy, new indexes can slow down DML.

Also check whether a better composite index can support multiple workload queries.”

---

# Slide 28: If Advisor Suggests Statistics

## Slide content

Advisor may suggest:

```sql id="day2s3_stats_rec_001"
EXEC DBMS_STATS.GATHER_TABLE_STATS(...);
```

Before applying:

* Check when stats were last gathered
* Check stale stats
* Test plan changes
* Consider impact on other SQLs
* Use proper maintenance window

---

## Trainer Explanation

“Statistics recommendations are common.

If stats are stale, optimizer estimates may be wrong.

But gathering stats can change plans for many SQLs, not just one.

In production, use scheduled maintenance windows and test important SQLs after stats refresh.”

---

# Slide 29: If Advisor Suggests SQL Restructure

## Slide content

Advisor may suggest:

* Rewrite joins
* Remove unnecessary operations
* Use better predicates
* Avoid functions on columns
* Reduce selected columns
* Remove unnecessary sorting

Before applying:

* Confirm business logic
* Test result correctness
* Coordinate with application team

---

## Trainer Explanation

“SQL restructuring affects application logic.

So DBAs should not change it alone without confirming business correctness.

For example, removing a join may improve speed but change results.

Always validate results before performance.”

---

# Slide 30: Lab Task Worksheet

## Slide content

Participants must answer:

| Question                                  | Answer |
| ----------------------------------------- | ------ |
| SQL ID analyzed                           |        |
| Did advisor suggest index?                |        |
| Did advisor suggest SQL Profile?          |        |
| Did advisor suggest statistics gathering? |        |
| Did advisor suggest SQL restructuring?    |        |
| Estimated benefit                         |        |
| Is it safe to apply directly?             |        |
| What should be tested before production?  |        |

---

## Trainer Explanation

“This worksheet is the main lab output.

Each participant should read the advisor report and fill this table.

The important part is not only what advisor suggested.

The important part is whether they can judge the recommendation safely.”

---

# Slide 31: Testing Before Production

## Slide content

Before production:

* Capture current execution plan
* Capture current runtime metrics
* Apply recommendation in test
* Compare execution time
* Compare buffer gets
* Compare physical reads
* Compare result correctness
* Check DML impact
* Prepare rollback

---

## Trainer Explanation

“Testing must include both performance and correctness.

A query that runs faster but returns wrong result is a failure.

A new index that improves one report but slows fund transfers may also be a bad production change.

So test broadly.”

---

# Slide 32: Rollback Planning

## Slide content

Possible rollback actions:

* Drop newly created index
* Disable/drop SQL Profile
* Restore previous statistics
* Revert SQL change
* Remove hint
* Re-test previous execution plan

Example SQL Profile rollback:

```sql id="day2s3_drop_profile_001"
EXEC DBMS_SQLTUNE.DROP_SQL_PROFILE(name => 'profile_name');
```

---

## Trainer Explanation

“In production, every tuning change needs rollback.

If a SQL Profile causes unexpected behavior, drop it.

If an index hurts DML, drop it.

If statistics caused regression, restore previous stats if available.

Rollback planning is part of professional DBA work.”

---

# Slide 33: Common Tuning Problems Covered

## Slide content

This slot covers:

## Inefficient SQL

Advisor identifies expensive SQL improvement options.

## Regression After Environment Changes

Advisor may help after statistics refresh, upgrade, or plan change.

## Suboptimal Application Usage

Advisor may reveal poor predicates, unnecessary sorting, or inefficient SQL design.

---

## Trainer Explanation

“This slot connects to three common tuning problems.

SQL Tuning Advisor helps with inefficient SQL.

It can also help when a SQL regresses after a change.

And sometimes it reveals application-level SQL problems like poor filters or unnecessary operations.”

---

# Slide 34: What Not To Do

## Slide content

Do not:

* Accept SQL Profile blindly
* Create every suggested index
* Gather stats in production without plan
* Apply SQL rewrite without business validation
* Ignore DML impact
* Ignore bind value differences
* Skip before/after comparison
* Forget rollback

---

## Trainer Explanation

“This is the safety message.

Advisor recommendations can be useful, but production systems need discipline.

Never tune only for one execution.

Tune for workload, stability, and business safety.”

---

# Slide 35: Slot 3 Summary

## Slide content

In this slot, we learned:

* SQL Tuning Advisor analyzes one SQL
* It is useful after AWR/ADDM identifies expensive SQL
* It may recommend:

  * SQL Profile
  * Index
  * Statistics
  * SQL restructuring
* SQL Profile helps optimizer choose better plan
* Every recommendation must be validated
* Production changes need testing and rollback

---

## Trainer Explanation

“Let’s summarize.

SQL Tuning Advisor is powerful for targeted SQL tuning.

But it is not automatic magic.

It gives recommendations.

A DBA must review, test, compare, and safely apply only when the recommendation makes sense.”

---

# Slide 36: Transition to Slot 4

## Slide content

Next slot:

# SQL Access Advisor + Memory/I/O Diagnosis Lab

We will learn:

* Workload-level access recommendations
* Index and materialized view suggestions
* Difference between SQL Tuning Advisor and SQL Access Advisor
* Basic memory and I/O symptoms

---

## Trainer Explanation

“In this slot, we tuned one SQL.

In the next slot, we move to workload-level access design.

SQL Access Advisor helps analyze a group of SQL statements and recommend indexes, materialized views, or partitioning strategies.”

---

# Final Trainer Message for Slot 3

Use this line:

> “SQL Tuning Advisor can suggest the fix, but the DBA must prove the fix is safe.”
