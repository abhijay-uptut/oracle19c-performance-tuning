# Day 2 First Practice Lab Solution - Using AWR SQL Reports

# Objective

This solution uses each trainee's own Oracle account. It does not require the `SOE` sample schema or an existing `ORDERS` table.

The lab creates a generated table called `ORDERS2`, runs one SQL statement before and after an index, captures AWR snapshots, and generates an AWR SQL report.

The evidence chain is:

```text
same SQL text
  -> same SQL ID
  -> multiple AWR snapshots
  -> two execution plans
  -> compare elapsed time, buffer gets, reads, and plan operations
```

---

# Replace These Values

Use your own values:

```text
TRAINING_USER = your_training_user
TRAINING_PASS = your_password
SERVICE_NAME  = pdb1.localdomain
```

For SQL Developer:

```text
Hostname      = <linux_vm_ip>
Port          = 1521
Service name  = pdb1.localdomain
Username      = your_training_user
Password      = your_password
```

For SQL*Plus from PuTTY on the Linux VM:

```bash
sqlplus your_training_user/your_password@//localhost:1521/pdb1.localdomain
```

---

# Step 1 - Create The Test Table In SQL Developer

Connect to your training user in SQL Developer and run:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE orders2 PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE orders2 NOLOGGING AS
SELECT level AS order_id,
       ROUND(DBMS_RANDOM.VALUE(10, 5000), 2) AS order_total,
       TRUNC(SYSDATE) - MOD(level, 365) AS order_date,
       CASE MOD(level, 4)
         WHEN 0 THEN 'ONLINE'
         WHEN 1 THEN 'BRANCH'
         WHEN 2 THEN 'MOBILE'
         ELSE 'ATM'
       END AS channel
FROM dual
CONNECT BY level <= 150000;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ORDERS2',
    cascade => TRUE
  );
END;
/

SELECT COUNT(*) AS orders2_rows
FROM orders2;
```

Expected result:

```text
ORDERS2_ROWS = 150000
```

Important:

```text
Do not create the index yet.
The first workload must run without an index on ORDER_ID.
```

---

# Step 2 - Create The Workload Files In PuTTY

Log in to the Linux VM using PuTTY.

Create the working folder:

```bash
mkdir -p /tmp/day2_first_practice_lab
cd /tmp/day2_first_practice_lab
```

Create `run_query.sql`:

```bash
cat > run_query.sql <<'EOF'
SET HEADING OFF
SET FEEDBACK OFF
SET PAGESIZE 0
SET LINESIZE 200

SELECT ORDER_ID, ORDER_TOTAL FROM ORDERS2 WHERE ORDER_ID <= 15000;

EXIT
EOF
```

Create `run_query.sh`.

Replace `your_training_user` and `your_password` before running it:

```bash
cat > run_query.sh <<'EOF'
#!/bin/bash

CONNECT_STRING="your_training_user/your_password@//localhost:1521/pdb1.localdomain"

counter=1
while [ "$counter" -le "$1" ]
do
  sqlplus -L -S "$CONNECT_STRING" @run_query.sql >/dev/null 2>&1 &
  counter=$((counter + 1))
done

wait
EOF

chmod +x run_query.sh
```

Quick connection test:

```bash
sqlplus -L your_training_user/your_password@//localhost:1521/pdb1.localdomain
```

Inside SQL*Plus:

```sql
SHOW USER
SELECT COUNT(*) FROM orders2;
EXIT
```

Expected:

```text
The user should be your training user.
The ORDERS2 count should be 150000.
```

---

# Step 3 - Take Snapshot 1 In PuTTY

Connect as SYSDBA:

```bash
sqlplus / as sysdba
```

If this is a multitenant database, switch to the training PDB:

```sql
ALTER SESSION SET CONTAINER = PDB1;
```

Create the first AWR snapshot:

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT(FLUSH_LEVEL => 'ALL');

SELECT MAX(snap_id) AS snapshot_1
FROM dba_hist_snapshot;
```

Record the snapshot ID.

Example:

```text
Snapshot 1 = 201
```

Exit:

```sql
EXIT
```

---

# Step 4 - Run The Workload Without The Index

From PuTTY:

```bash
cd /tmp/day2_first_practice_lab
./run_query.sh 30
./run_query.sh 30
```

This should execute the target SQL about 60 times before the index exists.

Expected plan direction:

```text
TABLE ACCESS FULL ORDERS2
```

---

# Step 5 - Take Snapshot 2 In PuTTY

```bash
sqlplus / as sysdba
```

```sql
ALTER SESSION SET CONTAINER = PDB1;

EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT(FLUSH_LEVEL => 'ALL');

SELECT MAX(snap_id) AS snapshot_2
FROM dba_hist_snapshot;

EXIT
```

Record the snapshot ID.

Example:

```text
Snapshot 2 = 202
```

---

# Step 6 - Create The Index In SQL Developer

Connect as your own training user in SQL Developer and run:

```sql
CREATE INDEX i_orders2_order_id
ON orders2(order_id)
NOLOGGING;

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'ORDERS2',
    cascade => TRUE
  );
END;
/
```

Explanation:

```text
The predicate is ORDER_ID <= 15000.
An index on ORDER_ID gives Oracle an index range scan option.
```

---

# Step 7 - Run The Same Workload After The Index

From PuTTY:

```bash
cd /tmp/day2_first_practice_lab
./run_query.sh 30
./run_query.sh 30
```

This should execute the same SQL about 60 more times after the index exists.

Expected plan direction:

```text
INDEX RANGE SCAN I_ORDERS2_ORDER_ID
TABLE ACCESS BY INDEX ROWID ORDERS2
```

---

# Step 8 - Take Snapshot 3 In PuTTY

```bash
sqlplus / as sysdba
```

```sql
ALTER SESSION SET CONTAINER = PDB1;

EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT(FLUSH_LEVEL => 'ALL');

SELECT MAX(snap_id) AS snapshot_3
FROM dba_hist_snapshot;

EXIT
```

Record the snapshot ID.

Example:

```text
Snapshot 3 = 203
```

---

# Step 9 - Find The SQL ID

You can run this from SQL Developer as your training user, or from PuTTY as SYSDBA.

```sql
COLUMN sql_text FORMAT A80
COLUMN sql_id FORMAT A15

SELECT sql_id,
       plan_hash_value,
       executions,
       buffer_gets,
       disk_reads,
       ROUND(elapsed_time / 1000000, 2) AS elapsed_seconds,
       sql_text
FROM v$sql
WHERE sql_text LIKE 'SELECT ORDER_ID, ORDER_TOTAL FROM ORDERS2%'
ORDER BY last_active_time DESC;
```

If the statement is not found, use this broader search:

```sql
SELECT sql_id,
       plan_hash_value,
       executions,
       sql_text
FROM v$sql
WHERE UPPER(sql_text) LIKE '%FROM ORDERS2%'
AND UPPER(sql_text) LIKE '%ORDER_ID <= 15000%'
ORDER BY last_active_time DESC;
```

Expected result:

```text
One SQL ID should represent the target query.
There may be more than one PLAN_HASH_VALUE for that SQL ID.
```

Record the SQL ID returned by your database.

---

# Step 10 - Generate The AWR SQL Report In PuTTY

Start SQL*Plus from the report folder so the HTML file is created there:

```bash
cd /tmp/day2_first_practice_lab
sqlplus / as sysdba
```

In SQL*Plus:

```sql
ALTER SESSION SET CONTAINER = PDB1;

@?/rdbms/admin/awrsqrpt.sql
```

Use these prompt values:

| Prompt | Example Value |
| ------ | ------------- |
| Report type | `html` |
| Number of days | `1` |
| Begin snapshot | snapshot 1 from this lab |
| End snapshot | snapshot 3 from this lab |
| SQL ID | SQL ID found in Step 9 |
| Report name | `first_practice_awr_sql.html` |

If the script prompts for database ID or instance number, choose the current training database and instance shown in the prompt list.

Important:

```text
Use the first snapshot as the begin snapshot and the third snapshot as the end snapshot.
That allows the report to include both the no-index and indexed executions.
```

The report should be created here:

```text
/tmp/day2_first_practice_lab/first_practice_awr_sql.html
```

---

# Step 11 - What To Look For In The AWR SQL Report

Open the HTML report and find:

* SQL ID and SQL text
* plan hash values
* elapsed time
* executions
* buffer gets
* disk reads
* execution plan sections

Expected observation:

```text
The same SQL should show two execution plans.
One plan should show a full table scan of ORDERS2.
The other plan should show access through I_ORDERS2_ORDER_ID.
```

Typical plan before the index:

```text
TABLE ACCESS FULL ORDERS2
```

Typical plan after the index:

```text
INDEX RANGE SCAN I_ORDERS2_ORDER_ID
TABLE ACCESS BY INDEX ROWID ORDERS2
```

---

# Answer Key

## Question 1 - SQL Identity

| Question | Expected Answer |
| -------- | --------------- |
| What SQL ID did you report on? | The SQL ID returned from `V$SQL` for the `ORDERS2` query |
| What SQL text does it represent? | `SELECT ORDER_ID, ORDER_TOTAL FROM ORDERS2 WHERE ORDER_ID <= 15000` |

---

## Question 2 - Execution Plans

| Plan Hash Value | Access Path Seen | When It Was Used |
| --------------- | ---------------- | ---------------- |
| environment-specific | `TABLE ACCESS FULL ORDERS2` | before index |
| environment-specific | `INDEX RANGE SCAN I_ORDERS2_ORDER_ID` plus table rowid access | after index |

Correct interpretation:

```text
The same SQL ID had more than one plan in AWR history.
The plan changed after the index was created.
```

---

## Question 3 - Plan Comparison

Expected comparison:

| Metric | Full Scan Plan | Index Plan | Which Is Better? |
| ------ | -------------- | ---------- | ---------------- |
| Executions | about 60 | about 60 | neither; execution count should be similar |
| Elapsed time | higher | lower | index plan |
| Buffer gets | higher | lower | index plan |
| Physical reads | usually higher | usually lower | index plan |

The exact values depend on cache state, table size, server speed, and Oracle version.

---

# Final DBA Conclusion

A good trainee answer should look like this:

```text
The AWR SQL report shows that SQL ID <your_sql_id> used two execution plans.

Before the index, the SQL used a full table scan on ORDERS2.

After the index, the SQL used an index range scan on I_ORDERS2_ORDER_ID.

The index plan is better because it performs less work for this ORDER_ID range query.
The evidence should be lower elapsed time, buffer gets, and reads in the AWR SQL report.
```

Production caution:

```text
Do not create indexes blindly in production.
Check duplicate indexes, DML overhead, storage impact, statistics, and change approval.
Use AWR SQL report evidence together with execution plans and application response time.
```

---

# Optional Direct DBA_HIST Check

The AWR SQL report reads historical SQL statistics from views such as `DBA_HIST_SQLSTAT`.

After finding the SQL ID, you can inspect the same history with:

```sql
SELECT s.snap_id,
       s.sql_id,
       s.plan_hash_value,
       s.executions_delta,
       s.buffer_gets_delta,
       s.disk_reads_delta,
       ROUND(s.elapsed_time_delta / 1000000, 2) AS elapsed_seconds_delta
FROM dba_hist_sqlstat s
WHERE s.sql_id = '<your_sql_id>'
ORDER BY s.snap_id, s.plan_hash_value;
```

Expected teaching point:

```text
The report is easier to read, but the historical data also exists in DBA_HIST_SQLSTAT.
```

---

# Cleanup

In SQL Developer, connect as your training user and run:

```sql
DROP TABLE orders2 PURGE;
```

In PuTTY, remove temporary files:

```bash
cd /tmp/day2_first_practice_lab
rm -f run_query.sql run_query.sh first_practice_awr_sql.html
```

