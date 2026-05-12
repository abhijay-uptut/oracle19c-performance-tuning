# Day 2 Second Practice Lab - SQL Tuning Advisor And Access Design

# Problem Statement

You are the DBA for a training database.

The application team reports that a customer transaction lookup and a branch reporting screen are slow. Your task is to use SQL Tuning Advisor thinking for one SQL, then use workload access-design thinking for several reporting SQLs.

This lab is designed for trainees who use:

* SQL Developer GUI for normal SQL work
* PuTTY CLI / SQL*Plus for DBA scripts and advisor reports
* their own Oracle training user account

You do not need the `SOE` sample schema.

---

# What You Will Practice

By the end of this lab, you should be able to:

* create a simple training workload table
* run one slow SQL and find its `SQL_ID`
* create and execute a SQL Tuning Advisor task
* read the advisor report safely
* validate an index recommendation with before/after evidence
* compare one-SQL tuning with workload-level access design
* inspect basic memory and I/O evidence

Simple mental model:

```text
AWR tells you which SQL is slow.
SQL Tuning Advisor suggests how one SQL may improve.
SQL Access Advisor thinking asks what helps the workload.
The DBA proves every recommendation before applying it.
```

---

# Safety And Licensing Note

SQL Tuning Advisor and SQL Access Advisor are Oracle Tuning Pack features.

Use them only in a licensed training environment.

If your user does not have advisor privileges, complete the manual before/after validation sections. The learning goal is still valid.

---

# Trainee Tasks

## Task 1 - Create The Practice Table In SQL Developer

Create a table called:

```text
DAY2_PRACTICE_TXN
```

It should contain generated transaction data with:

* transaction ID
* customer ID
* branch ID
* transaction date
* amount
* status
* channel

Gather statistics after loading the data.

---

## Task 2 - Run One Tagged SQL

Run this type of query once:

```sql
SELECT /* day2_second_sta_customer */
       transaction_id,
       customer_id,
       txn_date,
       amount,
       status
FROM day2_practice_txn
WHERE customer_id = 1001
AND txn_date >= ADD_MONTHS(SYSDATE, -12)
ORDER BY txn_date DESC;
```

The comment tag helps you find the SQL in `V$SQL`.

---

## Task 3 - Capture The Before Plan

Capture the runtime plan and metrics for the SQL.

Record:

| Item | Before Value |
| ---- | ------------ |
| SQL ID | |
| Plan operation | |
| Buffer gets | |
| Disk reads | |
| Elapsed time | |

Expected before direction:

```text
Oracle may scan more data than needed because there is no customer/date index yet.
```

---

## Task 4 - Run SQL Tuning Advisor

Use the SQL ID from Task 3 and create a SQL Tuning Advisor task.

Record:

| Item | Answer |
| ---- | ------ |
| Task name | |
| Task status | |
| Recommendation type | |
| Estimated benefit | |
| Suggested command | |

---

## Task 5 - Validate The Recommendation Safely

If the advisor recommends an index, do not blindly create it as a normal visible index.

Test a candidate invisible index first:

```text
DAY2_PRACTICE_TXN(customer_id, txn_date DESC)
```

Then rerun the SQL in the same session with invisible indexes enabled.

Record:

| Metric | Before | After |
| ------ | ------ | ----- |
| Plan operation | | |
| Buffer gets | | |
| Disk reads | | |
| Elapsed time | | |

---

## Task 6 - Workload Access Design

Run these three workload-style queries:

* customer transaction lookup
* branch monthly dashboard
* status/date exception report

Fill this table:

| Query | Main Filter | Sort/Group By | Candidate Access Structure | Risk |
| ----- | ----------- | ------------- | -------------------------- | ---- |
| Customer lookup | | | | |
| Branch dashboard | | | | |
| Exception report | | | | |

Question:

```text
Does one index help all three queries, or do they need different access designs?
```

---

## Task 7 - Optional SQL Access Advisor Demo

If privileges allow, run a simple SQL Access Advisor quick tune for the branch dashboard SQL.

Record:

| Item | Answer |
| ---- | ------ |
| Task status | |
| Recommendation type | |
| Benefit | |
| Suggested action | |

If the advisor is not available, use the manual access-design worksheet from Task 6.

---

## Task 8 - Memory And I/O Evidence Check

Use dynamic performance views to answer:

| Question | Answer |
| -------- | ------ |
| Which non-idle wait events are high? | |
| Which SQL has high disk reads? | |
| Is there active TEMP usage? | |
| Is this a SQL access-path problem or a memory/I/O parameter problem? | |

---

# Final DBA Recommendation

Write a short final recommendation:

```text
The slow SQL ID is __________.

The main plan problem is __________.

SQL Tuning Advisor recommended __________.

Before/after testing showed __________.

For the wider workload, the access-design recommendation is __________.

Production caution: before applying this in production, we must check __________.
```

---
