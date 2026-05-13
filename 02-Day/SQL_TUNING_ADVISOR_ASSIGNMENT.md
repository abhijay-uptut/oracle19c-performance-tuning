# SQL Tuning Advisor Assignment - Multiple Bad SQLs

# Problem Statement

You are the DBA for a training database.

The application team says several transaction screens are slow. Your task is to create a dummy workload, run bad SQL statements without supporting indexes, record the SQL IDs, use SQL Tuning Advisor for each SQL ID, apply safe recommendations in the training schema, and compare before and after performance.

This assignment is designed for trainees who use:

* SQL Developer for table setup and SQL testing
* SQL*Plus or SQL Developer worksheet for advisor commands
* their own Oracle training user account

You do not need the `SOE` sample schema.

---

# Learning Goals

By the end of this assignment, you should be able to:

* create a dummy table with enough data for tuning practice
* run intentionally inefficient SQL without indexes
* find the `SQL_ID` for each bad SQL
* create and execute SQL Tuning Advisor tasks
* read the advisor report
* apply index recommendations in a controlled training environment
* compare before and after plan, elapsed time, buffer gets, and disk reads

Simple mental model:

```text
Bad SQL without index
  -> find SQL_ID
  -> run SQL Tuning Advisor
  -> review recommendation
  -> apply recommendation in training
  -> rerun SQL and compare evidence
```

---

# Safety And Licensing Note

SQL Tuning Advisor is an Oracle Tuning Pack feature.

Use this assignment only in a licensed training environment.

In production, never apply advisor recommendations blindly. Always check duplicate indexes, DML overhead, storage impact, rollback plan, and change approval.

---

# Assignment Deliverables

Submit one completed worksheet containing:

| Deliverable | Required |
| ----------- | -------- |
| Row count of the dummy table | Yes |
| Four bad SQL statements used | Yes |
| Four SQL IDs captured from `V$SQL` | Yes |
| Four SQL Tuning Advisor task names | Yes |
| Recommendation summary for each SQL | Yes |
| Before and after comparison table | Yes |
| Final DBA recommendation | Yes |

---

# Trainee Tasks

## Task 1 - Create The Dummy Transaction Table

Create a table named:

```text
STA_ASSIGN_TXN
```

The table should contain dummy transaction data with these columns:

* transaction ID
* customer ID
* branch ID
* transaction date
* amount
* status
* channel
* merchant category

Load at least:

```text
300,000 rows
```

Gather table statistics after loading the data.

Record:

| Item | Value |
| ---- | ----- |
| Table name | |
| Row count | |
| Statistics gathered? | |

Important:

```text
Do not create tuning indexes yet.
The first test must run without supporting indexes.
```

---

## Task 2 - Run Four Bad SQL Statements

Run four different SQL statements against `STA_ASSIGN_TXN`.

Each SQL must have a unique comment tag so you can find it later in `V$SQL`.

Required query patterns:

| SQL | Required Problem Pattern |
| --- | ------------------------ |
| SQL 1 | Customer/date lookup without a customer/date index |
| SQL 2 | Function on a column, such as `LOWER(status)` |
| SQL 3 | Branch/channel/date report without a composite index |
| SQL 4 | Amount range query without an amount index |

Use tags like:

```text
sta_assign_q1_customer
sta_assign_q2_status_function
sta_assign_q3_branch_channel
sta_assign_q4_amount_range
```

Record the SQL text you used:

| SQL | Comment Tag | SQL Text |
| --- | ----------- | -------- |
| SQL 1 | | |
| SQL 2 | | |
| SQL 3 | | |
| SQL 4 | | |

---

## Task 3 - Capture Before Evidence

For each SQL, capture the runtime plan and basic metrics before creating indexes.

Record:

| SQL | SQL ID | Main Plan Operation | Executions | Buffer Gets | Disk Reads | Elapsed Seconds |
| --- | ------ | ------------------- | ---------- | ----------- | ---------- | --------------- |
| SQL 1 | | | | | | |
| SQL 2 | | | | | | |
| SQL 3 | | | | | | |
| SQL 4 | | | | | | |

Expected direction:

```text
Most queries should show TABLE ACCESS FULL before indexes exist.
```

---

## Task 4 - Create SQL Tuning Advisor Tasks

For each SQL ID from Task 3, create one SQL Tuning Advisor task.

Use task names like:

```text
STA_ASSIGN_Q1_TASK
STA_ASSIGN_Q2_TASK
STA_ASSIGN_Q3_TASK
STA_ASSIGN_Q4_TASK
```

Record:

| SQL | SQL ID | Task Name | Task Status |
| --- | ------ | --------- | ----------- |
| SQL 1 | | | |
| SQL 2 | | | |
| SQL 3 | | | |
| SQL 4 | | | |

---

## Task 5 - Read Advisor Reports

Read the SQL Tuning Advisor report for each task.

For each SQL, identify:

* recommendation type
* estimated benefit
* suggested SQL command
* whether the recommendation is safe to test in training

Record:

| SQL | Recommendation Type | Estimated Benefit | Suggested Command | Test It? |
| --- | ------------------- | ----------------- | ----------------- | -------- |
| SQL 1 | | | | |
| SQL 2 | | | | |
| SQL 3 | | | | |
| SQL 4 | | | | |

---

## Task 6 - Apply Recommendations In Training

Apply the recommendations that are safe in your training schema.

Most expected recommendations should be indexes.

Record the objects you created:

| SQL | Object Created | Columns / Expression | Reason |
| --- | -------------- | -------------------- | ------ |
| SQL 1 | | | |
| SQL 2 | | | |
| SQL 3 | | | |
| SQL 4 | | | |

After creating indexes, gather table statistics again.

---

## Task 7 - Rerun The Same SQL Statements

Rerun the exact same four SQL statements.

The SQL text should remain the same, including the comment tag.

Capture the after plan and metrics.

Record:

| SQL | SQL ID | Main Plan Operation After | Executions | Buffer Gets | Disk Reads | Elapsed Seconds |
| --- | ------ | ------------------------- | ---------- | ----------- | ---------- | --------------- |
| SQL 1 | | | | | | |
| SQL 2 | | | | | | |
| SQL 3 | | | | | | |
| SQL 4 | | | | | | |

---

## Task 8 - Compare Before And After

Complete this comparison table:

| SQL | Before Plan | After Plan | Buffer Gets Improved? | Disk Reads Improved? | Elapsed Time Improved? |
| --- | ----------- | ---------- | --------------------- | -------------------- | ---------------------- |
| SQL 1 | | | | | |
| SQL 2 | | | | | |
| SQL 3 | | | | | |
| SQL 4 | | | | | |

Answer:

```text
Which SQL improved the most?

Which SQL improved the least?

Did SQL Tuning Advisor recommend the same type of fix for all SQLs?

Would you apply all of these indexes in production? Why or why not?
```

---

# Final DBA Recommendation

Write a short final recommendation:

```text
The bad SQL IDs tested were:
1. __________
2. __________
3. __________
4. __________

The main problem before tuning was __________.

SQL Tuning Advisor recommended __________.

After applying recommendations in training, the main improvement was __________.

The recommendation I would take to production is __________.

Production cautions:
1. __________
2. __________
3. __________
```

