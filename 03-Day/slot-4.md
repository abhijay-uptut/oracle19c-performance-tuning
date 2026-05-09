# Day 3 — Slot 4

## 2:45 PM to 5:00 PM

# Final Capstone: End-to-End Banking Performance Tuning Case

## Slot Objective

By the end of this final slot, trainees should be able to diagnose a banking performance issue end-to-end using:

* AWR
* ADDM
* Execution plans
* SQL tuning techniques
* Indexing decisions
* SQL Profiles / baselines where needed
* Locking diagnosis
* Before/after validation

---

# Suggested Slot Flow

| Time        | Section                                     |
| ----------- | ------------------------------------------- |
| 2:45 - 3:00 | Capstone scenario briefing                  |
| 3:00 - 3:25 | Part 1: Identify workload problem using AWR |
| 3:25 - 3:50 | Part 2: Analyze SQL plan                    |
| 3:50 - 4:20 | Part 3: Tune SQL                            |
| 4:20 - 4:40 | Part 4: Diagnose locking                    |
| 4:40 - 4:55 | Part 5: Validate improvement                |
| 4:55 - 5:00 | Final training closure                      |

---

# Slide 1: Slot Title

## Final Capstone: End-to-End Banking Performance Tuning Case

**Slide content:**

In this final lab, we will diagnose a real-world style banking performance issue.

We will combine:

* AWR
* ADDM
* Execution plans
* Indexing
* SQL tuning
* SQL Profiles
* SQL Plan Baselines
* Locking diagnosis
* Before/after validation

---

## Trainer Explanation

“This is the final slot of the training.

Now we combine everything we learned in the last three days.

The goal is to think like a production DBA.

You will not receive one clean problem. You will receive many symptoms, like in real production.

Your job is to collect evidence, identify root causes, apply safe fixes, and validate improvement.”

---

# Slide 2: Capstone Scenario

## Slide content:

## Business Problem

The bank’s core transaction dashboard is slow.

Symptoms:

* Users complain between 10 AM and 12 PM
* Fund transfer report takes 45 seconds
* Login audit table is growing fast
* AWR shows high DB time
* ADDM recommends SQL tuning
* Some sessions are blocked
* Query plan changed after statistics refresh
* I/O wait increased
* One report query does full table scan on 1M+ transactions

---

## Trainer Explanation

“This is realistic.

In production, we rarely get one simple symptom.

Users say the dashboard is slow.

AWR shows high DB time.

ADDM recommends SQL tuning.

Some sessions are blocked.

I/O waits increased.

One report is scanning a huge table.

So the question is: where do we start, and how do we prove the real issue?”

---

# Slide 3: DBA Investigation Mindset

## Slide content:

Do not guess.

Follow the evidence:

```text
1. Confirm time window
2. Check workload impact
3. Identify top SQL and waits
4. Analyze execution plans
5. Check locking
6. Apply controlled fixes
7. Validate before and after
8. Document findings
```

---

## Trainer Explanation

“This is the mindset I want everyone to take from this training.

Do not immediately create indexes.

Do not immediately kill sessions.

Do not restart the database.

Start with evidence.

Confirm when the issue happened, what changed, which SQL consumed time, and whether sessions were waiting.”

---

# Slide 4: Capstone Lab Structure

## Slide content:

The capstone has 5 parts:

1. Identify workload problem using AWR
2. Analyze SQL plan using DBMS_XPLAN
3. Tune SQL safely
4. Diagnose locking
5. Validate improvement

---

## Trainer Explanation

“We will go step by step.

First, we identify the workload problem.

Then we analyze the specific SQL.

Then we tune.

Then we check locking.

Finally, we prove whether performance improved.”

---

# Slide 5: Part 1 — Identify Workload Problem

## Slide content:

Use AWR to check:

* Top Timed Events
* SQL ordered by Elapsed Time
* SQL ordered by Buffer Gets
* SQL ordered by Physical Reads
* DB Time
* Load Profile
* Segment Statistics

Goal:

```text
Find the biggest contributor to database time.
```

---

## Trainer Explanation

“First, we start with AWR.

AWR helps us answer: what happened between 10 AM and 12 PM?

We are looking for the biggest database time consumers.

Was the issue CPU?

Was it I/O?

Was it SQL?

Was it locking?

AWR gives us the first direction.”

---

# Slide 6: AWR Time Window

## Slide content:

Problem window:

```text
10:00 AM to 12:00 PM
```

Select snapshots around this window.

Example:

```text
Begin Snapshot: 10:00 AM
End Snapshot: 12:00 PM
```

Important:

Wrong snapshot window = wrong diagnosis.

---

## Trainer Explanation

“Snapshot selection is critical.

If users complained between 10 and 12, we should not generate a report from 2 to 3 PM.

The report must match the problem window.

Otherwise, we may diagnose the wrong workload.”

---

# Slide 7: Generate AWR Report

## Slide content:

Run:

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

Choose:

* Report type: HTML
* Begin snapshot
* End snapshot
* Report name

Example:

```text
awr_dashboard_slow_10am_12pm.html
```

---

## Trainer Explanation

“Generate an AWR report for the complaint window.

HTML is easier to read.

Once the report is generated, do not read randomly.

Use a structured flow.”

---

# Slide 8: AWR First Checks

## Slide content:

First check:

| Section             | Question                          |
| ------------------- | --------------------------------- |
| DB Time             | Was database load high?           |
| Top Timed Events    | Where did time go?                |
| SQL by Elapsed Time | Which SQL delayed users?          |
| SQL by Gets         | Which SQL did most logical reads? |
| SQL by Reads        | Which SQL caused physical I/O?    |
| Segment Stats       | Which objects were hot?           |

---

## Trainer Explanation

“This table is your AWR reading checklist.

DB Time tells us workload size.

Top Timed Events tell us wait category.

SQL sections identify the statements causing load.

Segment stats show which tables or indexes were heavily accessed.”

---

# Slide 9: Expected AWR Finding

## Slide content:

Possible findings:

* High DB Time
* High `db file scattered read`
* High `db file sequential read`
* One transaction report SQL high in elapsed time
* Same SQL high in buffer gets
* Same SQL high in physical reads
* `TRANSACTIONS` table appears in segment statistics

---

## Trainer Explanation

“In this scenario, we expect one report query to appear as a major contributor.

If the same SQL appears in elapsed time, buffer gets, and reads, it becomes a strong suspect.

If the transactions table also appears in segment statistics, the evidence becomes stronger.”

---

# Slide 10: Part 1 Lab Task

## Slide content:

Participants must identify:

| AWR Item                        | Observation                  |
| ------------------------------- | ---------------------------- |
| DB Time                         |                              |
| Top 3 wait events               |                              |
| Top SQL by elapsed time         |                              |
| SQL with highest buffer gets    |                              |
| SQL with highest physical reads |                              |
| Hot segment/table               |                              |
| Likely problem type             | SQL / I/O / Locking / Memory |

---

## Trainer Explanation

“This is the first lab worksheet.

Participants should not only copy values.

They should interpret them.

For example, if one SQL has high reads and the transactions table has high physical reads, the likely issue may be SQL access path causing I/O.”

---

# Slide 11: Part 2 — Analyze SQL Plan

## Slide content:

Use:

```sql
SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(
  'your_sql_id',
  NULL,
  'ALLSTATS LAST +PREDICATE +NOTE'
));
```

Participants identify:

* Full table scan
* Wrong join method
* Missing index
* Bad cardinality
* Expensive sort
* Predicate issues

---

## Trainer Explanation

“Once AWR identifies the SQL ID, we go deeper into the SQL plan.

This is where Day 1 skills come back.

AWR tells us which SQL is expensive.

DBMS_XPLAN tells us why it may be expensive.”

---

# Slide 12: Problem SQL Example

## Slide content:

Example slow dashboard query:

```sql
SELECT *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;
```

Possible issues:

* `SELECT *`
* No date range
* Large sort
* Full table scan
* Too many rows returned

---

## Trainer Explanation

“This query looks simple, but it can be expensive.

It fetches all columns.

It filters only by branch.

It has no date range.

It sorts by transaction date.

If the transactions table has millions of rows, this can become very expensive.”

---

# Slide 13: Better Business Query

## Slide content:

Better version:

```sql
SELECT transaction_id,
       account_id,
       customer_id,
       transaction_date,
       amount,
       status
FROM transactions
WHERE branch_id = 10
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

Benefits:

* Avoids `SELECT *`
* Adds date filter
* Limits rows
* Reduces sort volume
* Better dashboard behavior

---

## Trainer Explanation

“Before thinking about indexes, ask what the screen really needs.

Does it need all columns? Usually no.

Does it need all historical transactions? Usually no.

Does it need unlimited rows? Usually no.

This rewrite is more business-friendly and performance-friendly.”

---

# Slide 14: Plan Issue — Full Table Scan

## Slide content:

Possible plan:

```text
TABLE ACCESS FULL TRANSACTIONS
SORT ORDER BY
```

Ask:

* Is full scan expected?
* How many rows are returned?
* Is the table large?
* Is there a selective predicate?
* Is this report run frequently?

---

## Trainer Explanation

“Full table scan is not always bad.

But in this case, if the dashboard needs recent rows for one branch, scanning 1M+ rows may be wasteful.

We need to check row count, predicate, and frequency.”

---

# Slide 15: Plan Issue — Bad Cardinality

## Slide content:

Check:

```text
E-Rows vs A-Rows
```

Example:

```text
E-Rows = 100
A-Rows = 200000
```

Meaning:

* Optimizer underestimated rows
* May choose wrong access path
* May choose wrong join method
* Statistics or data skew may be issue

---

## Trainer Explanation

“Estimated rows versus actual rows is very important.

If Oracle expected 100 rows but got 200,000, the plan may be wrong.

This could be due to stale statistics, skewed data, or missing histogram.”

---

# Slide 16: Plan Issue — Expensive Sort

## Slide content:

Sort operation:

```text
SORT ORDER BY
```

Expensive when:

* Many rows sorted
* `SELECT *` increases row size
* No limit/pagination
* Sort spills to TEMP
* Memory is insufficient

---

## Trainer Explanation

“Sorting is common in dashboards.

But sorting too many rows is expensive.

If the dashboard only shows top 100 rows, then sorting millions of rows is bad design.

Reduce rows before sorting whenever possible.”

---

# Slide 17: Plan Issue — Wrong Join Method

## Slide content:

Possible join issues:

* Nested loops used for large row set
* Hash join used when lookup is small
* Wrong table selected first
* Bad cardinality drives wrong join order

Check:

* Join method
* Join order
* E-Rows vs A-Rows
* Predicate section

---

## Trainer Explanation

“If the dashboard query joins multiple tables, join method matters.

Nested loops can be good for small row sets.

Hash joins can be good for large row sets.

Wrong cardinality can cause wrong join method.

So always connect join method with actual rows.”

---

# Slide 18: Part 2 Lab Task

## Slide content:

Participants must record:

| Plan Item                   | Observation     |
| --------------------------- | --------------- |
| Main operation              |                 |
| Full scan present?          |                 |
| Index scan present?         |                 |
| Sort operation present?     |                 |
| Join method                 |                 |
| E-Rows vs A-Rows difference |                 |
| Predicate type              | Access / Filter |
| Likely plan issue           |                 |

---

## Trainer Explanation

“This worksheet forces plan reading.

Participants should identify whether the problem is full scan, sort, join method, bad estimate, or predicate issue.

Do not allow vague answers like ‘query is slow’.

Ask: what exactly in the plan shows the problem?”

---

# Slide 19: Part 3 — Tune SQL

## Slide content:

Possible fixes:

* Add composite index
* Add function-based index
* Rewrite query
* Avoid `SELECT *`
* Add date filter
* Gather statistics
* Use SQL Profile
* Create baseline if plan regression happened

---

## Trainer Explanation

“Now we move to tuning.

There is no single fix.

The correct fix depends on evidence.

If missing access path, index may help.

If SQL returns too much data, rewrite.

If stats are stale, gather stats.

If plan regressed, baseline may help.

If optimizer estimate is wrong, SQL Profile may help.”

---

# Slide 20: Fix Option — Composite Index

## Slide content:

For dashboard query:

```sql
WHERE branch_id = 10
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC
```

Possible index:

```sql
CREATE INDEX idx_txn_branch_date
ON transactions(branch_id, transaction_date DESC);
```

---

## Trainer Explanation

“This index matches the query pattern.

The query filters by branch and date, and sorts by transaction date descending.

A composite index may reduce scanning and sorting.

But before creating it in production, check DML impact and existing indexes.”

---

# Slide 21: Fix Option — Function-Based Index

## Slide content:

If query uses:

```sql
WHERE LOWER(email) = 'user100@mail.com'
```

Possible index:

```sql
CREATE INDEX idx_customers_lower_email
ON customers(LOWER(email));
```

Use when:

* Function is required
* Query is frequent
* Table is large
* Normal index is not helping

---

## Trainer Explanation

“This fix comes from Day 1.

If the query applies a function to the column, a normal index may not help.

A function-based index supports that exact expression.”

---

# Slide 22: Fix Option — Rewrite Query

## Slide content:

Bad pattern:

```sql
SELECT *
FROM transactions
WHERE branch_id = 10
ORDER BY transaction_date DESC;
```

Better:

```sql
SELECT transaction_id, account_id, amount, status, transaction_date
FROM transactions
WHERE branch_id = 10
AND transaction_date >= ADD_MONTHS(SYSDATE, -3)
ORDER BY transaction_date DESC
FETCH FIRST 100 ROWS ONLY;
```

---

## Trainer Explanation

“Query rewrite is often the best fix.

Indexes help access data faster.

But if the SQL asks for too much data, the better fix is to ask for less data.

This is especially important for dashboards.”

---

# Slide 23: Fix Option — Gather Statistics

## Slide content:

If statistics are stale:

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

Use when:

* Data changed significantly
* A-Rows and E-Rows differ heavily
* Plan changed after bad estimates
* Stats are missing/stale

---

## Trainer Explanation

“If cardinality estimates are wrong, statistics may be part of the problem.

Gathering stats can help optimizer choose better plan.

But in production, stats gathering can change many plans, so use maintenance window and test critical SQL.”

---

# Slide 24: Fix Option — SQL Profile

## Slide content:

Use SQL Profile when:

* SQL Tuning Advisor recommends it
* Cardinality estimates are wrong
* SQL text cannot be changed
* Need optimizer correction without app change

Caution:

```text
Do not accept blindly.
Test before production.
```

---

## Trainer Explanation

“A SQL Profile can help when optimizer needs better information.

It does not change SQL text.

But it affects future executions of that SQL, so test carefully.

Use it when advisor recommendation is validated.”

---

# Slide 25: Fix Option — Plan Baseline

## Slide content:

Use SQL Plan Baseline when:

* Query was fast earlier
* Plan changed after stats refresh
* Good plan is known
* SQL is business-critical
* Need stable performance

Example:

```sql
DECLARE
  l_plans_loaded PLS_INTEGER;
BEGIN
  l_plans_loaded := DBMS_SPM.LOAD_PLANS_FROM_CURSOR_CACHE(
    sql_id => 'your_sql_id'
  );
END;
/
```

---

## Trainer Explanation

“In this scenario, one symptom says the plan changed after statistics refresh.

That is a strong case for checking SQL Plan Management.

If we know yesterday’s good plan, baseline can help stabilize the query.

But also investigate why the plan changed.”

---

# Slide 26: Part 3 Lab Task

## Slide content:

Participants must choose the fix:

| Issue Found                  | Possible Fix                       |
| ---------------------------- | ---------------------------------- |
| Full scan on selective query | Composite index                    |
| Function on column           | Function-based index               |
| Too many rows                | Add date filter / pagination       |
| `SELECT *`                   | Select required columns            |
| Bad cardinality              | Gather stats / histogram / profile |
| Plan regression              | SQL Plan Baseline                  |
| Expensive sort               | Reduce rows / index support        |

---

## Trainer Explanation

“This table helps participants choose fixes based on evidence.

Do not let them use one fix for all problems.

The correct fix depends on the issue found in the plan and workload.”

---

# Slide 27: Part 4 — Diagnose Locking

## Slide content:

Use:

* `v$session`
* `dba_blockers`
* `dba_waiters`
* `v$locked_object`

Goal:

```text
Find blocker, waiter, locked object, and SQL involved.
```

---

## Trainer Explanation

“The scenario says some sessions are blocked.

So even if we tune SQL, locking may still affect users.

We must diagnose blockers and waiters separately.

A query may look slow because it is waiting, not because its execution plan is bad.”

---

# Slide 28: Find Blocking Sessions

## Slide content:

```sql
SELECT sid,
       serial#,
       username,
       blocking_session,
       wait_class,
       event
FROM v$session
WHERE blocking_session IS NOT NULL;
```

---

## Trainer Explanation

“This query shows sessions that are waiting because another session is blocking them.

The blocking_session column tells us who is blocking.

The event tells us what type of wait it is.”

---

# Slide 29: Find Blockers and Waiters

## Slide content:

```sql
SELECT *
FROM dba_blockers;
```

```sql
SELECT *
FROM dba_waiters;
```

Use these to identify:

* Blocking session
* Waiting session
* Lock relationship

---

## Trainer Explanation

“These views are very useful during lock diagnosis.

dba_blockers shows who is blocking.

dba_waiters shows who is waiting.

Together they show the lock chain.”

---

# Slide 30: Find Locked Object

## Slide content:

```sql
SELECT lo.session_id,
       o.object_name,
       o.object_type,
       lo.locked_mode
FROM v$locked_object lo
JOIN dba_objects o
  ON lo.object_id = o.object_id;
```

---

## Trainer Explanation

“This query shows which object is involved in the lock.

For example, ACCOUNTS, PAYMENTS, or TRANSACTIONS.

This helps connect the locking issue to a business module.”

---

# Slide 31: Locking Lab Task

## Slide content:

Participants must identify:

| Lock Item        | Observation |
| ---------------- | ----------- |
| Blocking session |             |
| Waiting session  |             |
| Locked object    |             |
| Wait event       |             |
| SQL involved     |             |
| Safe action      |             |

Safe actions:

* Ask application/user to commit
* Ask application/user to rollback
* Wait if transaction is valid
* Kill session only with approval

---

## Trainer Explanation

“Locking diagnosis must be careful.

Do not kill sessions casually.

In banking, the blocked transaction may be a payment or settlement process.

Always follow safe resolution steps.”

---

# Slide 32: Part 5 — Validate Improvement

## Slide content:

Compare before and after:

* Execution time
* Logical reads
* Physical reads
* Cost
* Plan operation
* Predicate usage
* Rows returned
* AWR snapshot difference

---

## Trainer Explanation

“No tuning is complete without validation.

After applying a fix, we must prove improvement.

Compare runtime, logical reads, physical reads, and plan shape.

If possible, generate another AWR report for the improved workload.”

---

# Slide 33: Before/After Plan Comparison

## Slide content:

Before:

```text
TABLE ACCESS FULL TRANSACTIONS
SORT ORDER BY
High buffer gets
High physical reads
```

After:

```text
INDEX RANGE SCAN IDX_TXN_BRANCH_DATE
Lower buffer gets
Lower physical reads
Reduced sort
```

---

## Trainer Explanation

“This is the kind of comparison we want.

Do not just say ‘it is faster’.

Show that access path improved.

Show reads reduced.

Show sort reduced.

Show execution time improved.”

---

# Slide 34: AWR Before/After Comparison

## Slide content:

Compare two AWR reports:

| Metric            | Before | After |
| ----------------- | -----: | ----: |
| DB Time           |        |       |
| Top wait event    |        |       |
| SQL elapsed time  |        |       |
| Buffer gets       |        |       |
| Physical reads    |        |       |
| Hot segment reads |        |       |

---

## Trainer Explanation

“If we want strong evidence, compare AWR before and after.

This is useful for production reporting.

It shows whether the database workload improved, not just one manual execution.”

---

# Slide 35: Final Capstone Worksheet

## Slide content:

Participants submit:

| Section              | Finding |
| -------------------- | ------- |
| Main user complaint  |         |
| AWR top wait         |         |
| Top SQL ID           |         |
| Plan issue           |         |
| Locking issue found? |         |
| Root cause           |         |
| Fix applied          |         |
| Before metrics       |         |
| After metrics        |         |
| Production caution   |         |

---

## Trainer Explanation

“This is the final capstone output.

Each participant or group should present findings like a real DBA incident report.

The answer should be evidence-based.

What was the symptom?

What did AWR show?

What did the plan show?

What fix was applied?

What improved?”

---

# Slide 36: Expected Root Cause Possibilities

## Slide content:

The issue may be a combination of:

* Bad dashboard SQL
* No date filter
* Full scan on large transaction table
* Expensive sort
* Stale statistics
* Plan regression after stats refresh
* Increased physical I/O
* Blocking sessions from uncommitted transactions
* Fast-growing audit table affecting reports

---

## Trainer Explanation

“In real production, there may be more than one root cause.

The dashboard query may be bad.

Stats may be stale.

Plan may have changed.

Some sessions may be blocked.

A good DBA separates primary cause from secondary symptoms.”

---

# Slide 37: Production Recommendation Format

## Slide content:

Final recommendation should include:

1. Problem summary
2. Evidence from AWR/ADDM
3. SQL ID and plan issue
4. Locking finding, if any
5. Recommended fix
6. Risk and impact
7. Test result
8. Rollback plan
9. Monitoring plan

---

## Trainer Explanation

“In a bank, we should not simply say ‘create index’.

We should prepare a professional recommendation.

What is the evidence?

What fix are we proposing?

What is the risk?

How will we rollback?

How will we monitor after the change?”

---

# Slide 38: Example Final Finding

## Slide content:

Example:

```text
Root cause:
Dashboard query scanned 1M+ TRANSACTIONS rows and sorted large result set.

Evidence:
AWR showed SQL as top elapsed time and top physical reads.
DBMS_XPLAN showed TABLE ACCESS FULL and SORT ORDER BY.
Query had no date filter and used SELECT *.

Fix:
Added date filter, selected required columns, created composite index on branch_id and transaction_date.

Validation:
Execution time reduced from 45s to 3s.
Logical reads and physical reads reduced significantly.
```

---

## Trainer Explanation

“This is how a final finding should sound.

It is clear, evidence-based, and action-oriented.

It explains root cause, evidence, fix, and validation.”

---

# Slide 39: What Not To Do in Production

## Slide content:

Avoid:

* Restarting database without diagnosis
* Creating indexes blindly
* Killing sessions without approval
* Accepting SQL Profiles without testing
* Gathering stats randomly during peak hours
* Ignoring application query design
* Looking only at cost
* Ignoring before/after validation

---

## Trainer Explanation

“These are common mistakes.

A production DBA must be careful.

Performance tuning is not just technical skill.

It also needs discipline, communication, and change control.”

---

# Slide 40: 3-Day Training Final Recap

## Slide content:

## Day 1

SQL tuning foundation, execution plans, indexing

## Day 2

AWR, ADDM, SQL Tuning Advisor, SQL Access Advisor, memory/I/O diagnosis

## Day 3

SQL Plan Management, bind peeking, adaptive cursor sharing, locking, capstone case

---

## Trainer Explanation

“Let’s recap the full journey.

Day 1 gave us SQL-level understanding.

Day 2 gave us workload-level diagnosis.

Day 3 gave us advanced production handling.

Together, these skills help DBAs investigate real banking performance problems.”

---

# Slide 41: Final DBA Tuning Framework

## Slide content:

Use this framework:

```text
1. Understand complaint
2. Confirm time window
3. Check AWR/ADDM
4. Identify top SQL/waits
5. Read execution plan
6. Check locking/concurrency
7. Choose safe fix
8. Test and validate
9. Apply with approval
10. Monitor after change
```

---

## Trainer Explanation

“This is the complete framework.

Whenever someone says ‘database is slow’, follow this process.

It will prevent guessing and help you reach root cause faster.”

---

# Slide 42: Final Outcome

## Slide content:

After this training, participants should be able to:

* Diagnose slow SQL
* Read execution plans
* Use AWR and ADDM
* Use SQL advisors safely
* Identify indexing issues
* Handle plan regression
* Understand bind-related plan problems
* Diagnose locks and blockers
* Validate tuning changes professionally

---

## Trainer Explanation

“This is what participants should now be able to do.

They may not remember every command immediately.

That is okay.

The important thing is they now understand the process, the tools, and the thinking required for performance diagnosis.”

---

# Slide 43: Closing Message

## Slide content:

Performance tuning is investigation.

A good DBA does not guess.

A good DBA:

* Collects evidence
* Understands the workload
* Finds root cause
* Applies safe fixes
* Validates improvement
* Documents the result

---

## Trainer Explanation

“Performance tuning is not magic.

It is investigation.

The best DBAs are not the ones who know one command.

The best DBAs are the ones who ask the right questions, collect the right evidence, and apply safe changes.”

---

# Slide 44: Final Q&A

## Slide content:

## Questions and Discussion

Possible discussion topics:

* Which tool felt most useful?
* Which lab was most realistic?
* Where do you see these issues in your environment?
* What will you check first during your next performance incident?

---

## Trainer Explanation

“Use this time for final discussion.

Ask participants to connect the training with their real banking environment.

This makes the training more practical and memorable.”

---

# Final Trainer Closing Line

> “When the database is slow, do not guess. Follow the evidence from workload, SQL plan, waits, locks, and before/after validation.”
