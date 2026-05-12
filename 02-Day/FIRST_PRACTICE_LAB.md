# Day 2 First Practice Lab - Using AWR SQL Reports

# Problem Statement

You are the DBA for a training database.

The application team reports that one order lookup SQL statement changed performance after an index was added. Your task is to prove this using an AWR SQL report.

This lab is designed for trainees who use:

* SQL Developer GUI for normal SQL work
* PuTTY CLI for Linux shell commands and SQL*Plus scripts
* their own Oracle training user account, not the `SOE` sample schema

In this lab, you will:

* create a test table called `ORDERS2` in your own schema
* run the same SQL many times without an index
* take an AWR snapshot
* create an index
* run the same SQL many times again
* take another AWR snapshot
* generate an AWR SQL report for the SQL ID
* compare the two execution plans shown in the report

The main learning point is:

```text
An AWR SQL report shows historical performance for one SQL statement.
It can show whether the same SQL used more than one execution plan.
```

---

# Safety Note

AWR is part of Oracle Diagnostic Pack.

Use this only in a licensed training environment, not on production unless your organization has approved Diagnostic Pack usage.

---

# Connection Information

Use your own training account.

Example placeholders:

```text
Username      = your_training_user
Password      = your_password
Service name  = pdb1.localdomain
```

In SQL Developer, connect using the VM IP address:

```text
Hostname      = <linux_vm_ip>
Port          = 1521
Service name  = pdb1.localdomain
```

In PuTTY on the Linux VM, SQL*Plus can usually connect using localhost:

```bash
sqlplus your_training_user/your_password@//localhost:1521/pdb1.localdomain
```

Replace `your_training_user` and `your_password` everywhere in this lab with your actual account.

---

# Lab Files To Create In PuTTY

Create a working folder on the database server:

```bash
mkdir -p /tmp/day2_first_practice_lab
cd /tmp/day2_first_practice_lab
```

You will create two small files:

| File | Purpose |
| ---- | ------- |
| `run_query.sql` | contains the SQL statement to execute |
| `run_query.sh` | starts many SQL*Plus sessions to create workload |

The SQL statement used in this lab is:

```sql
SELECT ORDER_ID, ORDER_TOTAL FROM ORDERS2 WHERE ORDER_ID <= 15000;
```

---

# Trainee Tasks

## Task 1 - Prepare The Test Table In SQL Developer

Connect to your own training user in SQL Developer.

Create `ORDERS2` in your own schema.

`ORDERS2` should contain generated test rows with:

* `ORDER_ID`
* `ORDER_TOTAL`
* 150,000 rows

Gather statistics on `ORDERS2`.

---

## Task 2 - Take The First Snapshot In PuTTY

Connect as SYSDBA in SQL*Plus from PuTTY and create an AWR snapshot before running the workload.

Record the snapshot ID:

| Item | Value |
| ---- | ----- |
| First snapshot ID | |

---

## Task 3 - Run The SQL Without An Index From PuTTY

Run the workload script twice.

Each run should start 30 SQL*Plus sessions using your own training user account.

Expected result:

```text
The SQL should run without a supporting index on ORDERS2.ORDER_ID.
Oracle may use a full table scan.
```

---

## Task 4 - Take The Second Snapshot In PuTTY

Create another AWR snapshot after the no-index workload.

Record the snapshot ID:

| Item | Value |
| ---- | ----- |
| Second snapshot ID | |

---

## Task 5 - Create The Index In SQL Developer

Create an index on:

```sql
ORDERS2(ORDER_ID)
```

Gather statistics again.

---

## Task 6 - Run The Same SQL Again From PuTTY

Run the workload script twice again.

Expected result:

```text
The SQL should now have a better access path available.
Oracle may use an index range scan.
```

---

## Task 7 - Take The Third Snapshot In PuTTY

Create one more AWR snapshot after the indexed workload.

Record the snapshot ID:

| Item | Value |
| ---- | ----- |
| Third snapshot ID | |

---

## Task 8 - Find The SQL ID

Find the SQL ID for this statement:

```sql
SELECT ORDER_ID, ORDER_TOTAL FROM ORDERS2 WHERE ORDER_ID <= 15000;
```

Record it:

| Item | Value |
| ---- | ----- |
| SQL ID | |

---

## Task 9 - Generate The AWR SQL Report From PuTTY

Generate an AWR SQL report using:

```sql
@?/rdbms/admin/awrsqrpt.sql
```

Use:

| Prompt | What To Enter |
| ------ | ------------- |
| Report type | `html` |
| Number of days | `1` |
| Begin snapshot | first snapshot from this lab |
| End snapshot | third snapshot from this lab |
| SQL ID | SQL ID from Task 8 |
| Report name | `first_practice_awr_sql.html` |

If the script asks for database ID or instance number, choose the current training database and instance from the prompt list.

---

# Questions To Answer

## Question 1 - SQL Identity

| Question | Answer |
| -------- | ------ |
| What SQL ID did you report on? | |
| What SQL text does it represent? | |

---

## Question 2 - Execution Plans

From the AWR SQL report, fill this:

| Plan Hash Value | Access Path Seen | When It Was Used |
| --------------- | ---------------- | ---------------- |
| | | Before index / After index |
| | | Before index / After index |

---

## Question 3 - Plan Comparison

Compare the full scan plan and the index plan:

| Metric | Full Scan Plan | Index Plan | Which Is Better? |
| ------ | -------------- | ---------- | ---------------- |
| Executions | | | |
| Elapsed time | | | |
| Buffer gets | | | |
| Physical reads | | | |

---

## Question 4 - DBA Conclusion

Write a short conclusion:

```text
The AWR SQL report shows that SQL ID __________ used ______ execution plans.

Before the index, the SQL used ____________________.

After the index, the SQL used ____________________.

The better plan is ____________________ because ____________________.
```

---

# Cleanup Required

At the end of the lab:

* drop `ORDERS2` from your own schema
* remove the temporary script files from `/tmp/day2_first_practice_lab`

