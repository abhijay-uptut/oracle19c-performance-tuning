# Day 2 - FIRST HALF (FINAL ENTERPRISE VERSION)

## 9:00 AM - 12:00 PM

# AWR, ADDM & Workload-Level Diagnosis

---

# PRIMARY OBJECTIVE OF THIS HALF DAY

By the end of this half day, trainees should be able to:

* move from single-SQL diagnosis to database workload diagnosis
* generate controlled AWR snapshots around a problem window
* create enough workload for AWR to show meaningful evidence
* identify top SQL, top waits, logical reads, physical reads, and DB time
* read AWR with a repeatable investigation workflow
* generate ADDM for the same snapshot window
* interpret ADDM findings, impact, and recommendations
* validate ADDM recommendations using AWR and execution-plan evidence
* avoid applying advisor recommendations blindly

---

# HALF-DAY DESIGN PHILOSOPHY

This half day is intentionally:

* diagnosis-first
* report-driven
* evidence-based
* practical for production DBAs
* connected to Day 1 execution-plan skills

NOT:

* an AWR section-by-section reading marathon
* a list of wait-event definitions
* "run ADDM and accept everything"
* theory without workload

---

# FINAL TIME STRUCTURE

| Time          | Section                                      |
| ------------- | -------------------------------------------- |
| 9:00 - 9:10   | Day 2 opening and production scenario        |
| 9:10 - 9:25   | AWR mental model and snapshot window         |
| 9:25 - 9:45   | Lab setup and workload tagging               |
| 9:45 - 10:10  | Live lab: create AWR workload window         |
| 10:10 - 10:30 | Read AWR using a DBA workflow                |
| 10:45 - 11:00 | ADDM mental model                            |
| 11:00 - 11:25 | Live lab: generate ADDM for same window      |
| 11:25 - 11:50 | Interpret ADDM findings and validate them    |
| 11:50 - 12:00 | Morning summary and transition to Slot 3     |

---

# LICENSING AND PRIVILEGE NOTE

AWR and ADDM are Oracle Diagnostic Pack features.

Before using them in a real bank environment, confirm:

* Diagnostic Pack license is approved
* the training database permits AWR/ADDM use
* the training user has required privileges
* the report window is from the intended database and instance

Typical privileges or access needed:

```text
SELECT_CATALOG_ROLE or access to DBA_HIST_* views
EXECUTE on DBMS_WORKLOAD_REPOSITORY
permission to run $ORACLE_HOME/rdbms/admin/awrrpt.sql
permission to run $ORACLE_HOME/rdbms/admin/addmrpt.sql
```

Trainer note:

Do not skip this point. These trainees work in banking, so licensing and production governance matter.

---

# COMMON SESSION SETTINGS

Run these in SQL*Plus or SQLcl:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET LONG 1000000
SET LONGCHUNKSIZE 1000000
SET TRIMSPOOL ON
SET TIMING ON
SET AUTOTRACE OFF
```

---

# DAY 2 MORNING SCENARIO

# Slide 1 - Production Complaint

## Slide Content

# Banking Complaint

At 11:00 AM:

```text
Fund transfer and customer statement screens are slow.
```

The DBA must answer:

* Is the whole database slow or only one SQL?
* Is the problem CPU, I/O, locking, commits, or bad SQL?
* Which SQL consumed the most DB time?
* Which wait events dominated?
* Is this normal workload or abnormal workload?
* What should we investigate first?

---

## Trainer Delivery

"On Day 1 we diagnosed individual SQL.

Today we diagnose the database workload during a problem window.

In production, users usually do not provide SQL IDs.

They say the system is slow.

AWR helps us identify what happened during that time window.

ADDM helps summarize likely causes and recommendations.

But the DBA still validates everything."

---

# SLOT 1 - AWR: AUTOMATIC WORKLOAD REPOSITORY

## 9:00 AM - 10:30 AM

# SECTION 1 - AWR MENTAL MODEL (9:10 - 9:25)

# Slide 2 - What AWR Answers

## Slide Content

# AWR Answers

```text
What happened between two snapshots?
```

AWR helps identify:

* DB time
* top wait events
* top SQL by elapsed time
* top SQL by CPU time
* top SQL by logical reads
* top SQL by physical reads
* load profile
* instance efficiency signals
* hot segments

---

## Trainer Delivery

"AWR does not fix performance.

AWR tells us where to investigate.

The key skill is not generating the report.

The key skill is choosing the right snapshot window and reading the report in the right order."

---

# Slide 3 - Snapshot Window

## Slide Content

Wrong window:

```text
Problem happened: 11:00 AM
Report window:   2:00 PM - 3:00 PM
```

Correct window:

```text
Problem happened: 11:00 AM
Report window:   10:45 AM - 11:15 AM
```

---

## Trainer Delivery

"AWR is only as useful as the snapshot interval.

If the issue was short-lived, a wide report may dilute the signal.

If the issue happened at 11 AM, do not analyze a quiet period at 2 PM."

---

# Slide 4 - AWR Reading Workflow

## Slide Content

Use this order:

```text
1. Confirm database, instance, and snapshot window
2. Compare DB Time with elapsed time
3. Read Top Timed Events
4. Check SQL ordered by Elapsed Time
5. Check SQL ordered by CPU Time
6. Check SQL ordered by Gets
7. Check SQL ordered by Reads
8. Check Segment Statistics
9. Decide likely next investigation
```

---

## Trainer Delivery

"Do not jump randomly inside AWR.

Start with the window.

Then DB time.

Then waits.

Then SQL.

Then segments.

That sequence prevents shallow conclusions."

---

# SECTION 2 - LAB PREREQUISITES (9:25 - 9:45)

# Slide 5 - Lab Objective

## Slide Content

# Lab Goal

We will:

1. create a start AWR snapshot
2. run tagged workload
3. create an end AWR snapshot
4. generate an AWR report
5. identify top SQL and waits
6. connect AWR evidence to Day 1 plan skills

---

# Step 1 - Confirm Day 1 Tables Exist

```sql
SELECT table_name
FROM user_tables
WHERE table_name IN ('TRANSACTIONS','CUSTOMERS','ACCOUNTS')
ORDER BY table_name;
```

Expected:

```text
ACCOUNTS
CUSTOMERS
TRANSACTIONS
```

If `CUSTOMERS` or `ACCOUNTS` does not exist, run `01-Day/SECOND.md` setup before this lab.

---

# Step 2 - Confirm Data Volume

```sql
SELECT 'TRANSACTIONS' table_name, COUNT(*) row_count FROM transactions
UNION ALL
SELECT 'CUSTOMERS', COUNT(*) FROM customers
UNION ALL
SELECT 'ACCOUNTS', COUNT(*) FROM accounts;
```

Recommended minimum:

```text
TRANSACTIONS >= 300000
CUSTOMERS    >= 100000
ACCOUNTS     >= 100000
```

Trainer note:

If the tables are smaller, the lab still works, but AWR evidence may be weaker.

---

# Step 3 - Confirm AWR Access

```sql
SELECT COUNT(*) AS awr_snapshot_count
FROM dba_hist_snapshot;
```

If this fails:

```text
The user does not have AWR catalog access.
Use a privileged training account or ask the DBA to grant access for the lab.
```

---

# Step 4 - Get DBID And Instance Number

```sql
COLUMN dbid NEW_VALUE dbid
COLUMN inst_num NEW_VALUE inst_num

SELECT dbid
FROM v$database;

SELECT instance_number AS inst_num
FROM v$instance;
```

These SQL*Plus variables are used later:

```text
&dbid
&inst_num
```

---

# Step 5 - Create Workload Helper Table

This table is used only to generate controlled commit activity.

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE awr_commit_test PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE awr_commit_test (
    id          NUMBER,
    payload     VARCHAR2(100),
    created_at  DATE
);
```

Trainer note:

This lets us optionally create `log file sync` activity. Keep the loop modest on small lab machines.

---

# SECTION 3 - LIVE LAB: CREATE AWR WORKLOAD WINDOW (9:45 - 10:10)

# Slide 6 - Workload Design

## Slide Content

The workload is intentionally imperfect:

* broad transaction scan
* large sort
* function search
* repeated execution
* optional frequent commits

We tag SQL using comments:

```sql
/* awr_day2_... */
```

---

## Trainer Delivery

"The SQL comments are important.

They make the workload easy to find in `V$SQL` and in AWR top SQL sections.

In production, module/action names from the application are even better.

Today we use both SQL comments and `DBMS_APPLICATION_INFO`."

---

# Step 1 - Create Start Snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Capture the latest snapshot as the beginning of the lab window:

```sql
COLUMN begin_snap NEW_VALUE begin_snap

SELECT MAX(s.snap_id) AS begin_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;
```

Confirm:

```sql
SELECT &begin_snap AS begin_snapshot_id
FROM dual;
```

---

# Step 2 - Run Tagged Workload

Run this workload for a few minutes.

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_MODULE(
    module_name => 'ORACLE19C_DAY2_AWR_LAB',
    action_name => 'CONTROLLED_WORKLOAD'
  );
END;
/
```

```sql
DECLARE
  v_number NUMBER;
BEGIN
  FOR i IN 1..12 LOOP

    SELECT /*+ FULL(t) */ /* awr_day2_full_scan_txn */
           SUM(amount)
    INTO v_number
    FROM transactions t
    WHERE status = 'SUCCESS';

    SELECT /* awr_day2_date_sort_txn */
           COUNT(*)
    INTO v_number
    FROM (
      SELECT /*+ FULL(t) */ transaction_id, amount, transaction_date
      FROM transactions t
      WHERE transaction_date >= ADD_MONTHS(SYSDATE,-24)
      ORDER BY amount DESC, transaction_date DESC
      FETCH FIRST 5000 ROWS ONLY
    );

    SELECT /*+ FULL(c) */ /* awr_day2_function_customer */
           COUNT(*)
    INTO v_number
    FROM customers c
    WHERE LOWER(email) LIKE '%user%';

    SELECT /*+ FULL(a) */ /* awr_day2_account_lookup */
           COUNT(*)
    INTO v_number
    FROM accounts a
    WHERE TO_NUMBER(account_number) BETWEEN 1000000001 AND 1000010000;

  END LOOP;
END;
/
```

Expected:

```text
These SQL statements should appear in V$SQL and may appear in AWR top SQL sections.
```

Trainer note:

The `TO_NUMBER(account_number)` query intentionally applies a function to the column. It is a controlled anti-pattern for AWR visibility and discussion.

---

# Optional Step - Generate Commit Wait Activity

Only run this if the class machine can handle extra workload.

```sql
BEGIN
  DBMS_APPLICATION_INFO.SET_ACTION('COMMIT_WORKLOAD');

  FOR i IN 1..500 LOOP
    INSERT /* awr_day2_commit_test */
    INTO awr_commit_test
    VALUES (
      i,
      'commit workload',
      SYSDATE
    );

    COMMIT;
  END LOOP;
END;
/
```

Expected possible wait:

```text
log file sync
```

Trainer note:

If `log file sync` does not appear prominently, do not force it. Explain that wait visibility depends on storage speed, redo configuration, and workload volume.

---

# Step 3 - Verify Tagged SQL In V$SQL

```sql
SELECT sql_id,
       child_number,
       executions,
       ROUND(elapsed_time/1000000,2) elapsed_sec,
       buffer_gets,
       disk_reads,
       rows_processed,
       SUBSTR(sql_text,1,80) sql_text
FROM v$sql
WHERE sql_text LIKE '%awr_day2_%'
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;
```

If no rows appear:

* run the workload again
* confirm you are connected to the same instance
* reduce filters in the `V$SQL` query

---

# Step 4 - Create End Snapshot

```sql
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT;
```

Capture latest snapshot as the end of the lab window:

```sql
COLUMN end_snap NEW_VALUE end_snap

SELECT MAX(s.snap_id) AS end_snap
FROM dba_hist_snapshot s
WHERE s.dbid = &dbid
AND s.instance_number = &inst_num;
```

Confirm:

```sql
SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

Expected:

```text
END_SNAPSHOT_ID should be greater than BEGIN_SNAPSHOT_ID
```

---

# Step 5 - Generate AWR Report Non-Interactively

Use text report first because it is simple to spool and search.

```sql
SPOOL awr_day2_morning.txt

SELECT output
FROM TABLE(
  DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_TEXT(
    &dbid,
    &inst_num,
    &begin_snap,
    &end_snap
  )
);

SPOOL OFF
```

Alternative interactive script:

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

Use:

```text
Report type: text or html
Begin snapshot: &begin_snap
End snapshot:   &end_snap
```

Trainer note:

If `AWR_REPORT_TEXT` fails because of privileges, use `awrrpt.sql` as a privileged user.

---

# SECTION 4 - READ AWR LIKE A DBA (10:10 - 10:30)

# Slide 7 - First Check: Report Window

## Slide Content

Before interpreting anything, confirm:

* database name
* instance name
* host
* begin snapshot
* end snapshot
* elapsed time
* DB time

---

## Trainer Delivery

"Wrong report window means wrong diagnosis.

Before discussing waits or SQL, confirm the report is for the workload we just generated."

---

# Slide 8 - DB Time vs Elapsed Time

## Slide Content

Interpretation:

```text
Elapsed Time = wall clock report duration
DB Time      = total active database session time
```

If DB Time is much larger than elapsed time:

```text
Many sessions were active or waiting.
```

---

## Trainer Delivery

"DB Time tells us the size of database work.

For a short lab, DB Time may not be huge.

In production, sudden DB Time increase compared to baseline is a strong signal."

---

# Slide 9 - Top Timed Events

## Slide Content

Read wait events as direction, not final proof.

Common examples:

| Event | First Investigation |
| ----- | ------------------- |
| DB CPU | SQL by CPU, high executions |
| db file sequential read | index lookups, single-block reads |
| db file scattered read | full scans, multiblock reads |
| direct path read | large scans, parallel/direct reads |
| log file sync | commit frequency, redo latency |
| enq: TX - row lock contention | blocking transactions |

---

## Trainer Delivery

"A wait event is a clue.

It is not automatically the root cause.

If you see I/O waits, first ask:

Which SQL caused the reads?

If you see log file sync, ask:

Who is committing too frequently?"

---

# Slide 10 - Top SQL Sections

## Slide Content

Use SQL sections this way:

| AWR Section | Use It To Find |
| ----------- | -------------- |
| SQL ordered by Elapsed Time | highest user-impact SQL |
| SQL ordered by CPU Time | CPU-heavy SQL |
| SQL ordered by Gets | high logical reads |
| SQL ordered by Reads | physical I/O drivers |
| SQL ordered by Executions | application loops |
| SQL ordered by Parse Calls | hard-parse / bind issues |

---

## Trainer Delivery

"The same SQL appearing in multiple sections is a strong suspect.

For example:

* high elapsed time
* high gets
* high reads

That usually means the SQL deserves execution-plan analysis."

---

# Lab Task - AWR Evidence Table

Participants fill this from `awr_day2_morning.txt`:

| AWR Section | What You Found | Likely Meaning | Next Check |
| ----------- | -------------- | -------------- | ---------- |
| DB Time | | workload intensity | compare baseline |
| Top Timed Events | | CPU/I/O/commit/lock direction | top SQL |
| SQL by Elapsed | | user-impact SQL | plan and predicates |
| SQL by CPU | | CPU-heavy SQL | functions, joins, executions |
| SQL by Gets | | logical read pressure | access path |
| SQL by Reads | | physical I/O driver | full scans, large objects |
| Segment Stats | | hot object | table/index/partition design |

---

# Slide 11 - Connect AWR To Day 1

## Slide Content

Once AWR identifies SQL:

```text
AWR SQL_ID
  -> DBMS_XPLAN.DISPLAY_CURSOR
  -> predicates
  -> E-Rows vs A-Rows
  -> access path
  -> fix
  -> validate
```

---

# Useful Follow-Up Query

Use a SQL ID from AWR or `V$SQL`:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&sql_id_from_awr',
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Trainer note:

If the cursor aged out, use the plan shown in AWR as evidence and rerun the SQL with a controlled comment to capture a fresh runtime plan.

---

# SLOT 2 - ADDM: AUTOMATIC DATABASE DIAGNOSTIC MONITOR

## 10:45 AM - 12:00 PM

# SECTION 5 - ADDM MENTAL MODEL (10:45 - 11:00)

# Slide 12 - AWR vs ADDM

## Slide Content

| Item | AWR | ADDM |
| ---- | --- | ---- |
| Type | performance report | diagnostic advisor |
| Input | snapshots | AWR snapshots |
| Output | metrics and SQL sections | findings and recommendations |
| Strength | evidence | prioritization |
| Risk | can overwhelm | can oversimplify |
| Final decision? | no | no |

---

## Trainer Delivery

"AWR shows evidence.

ADDM interprets evidence.

But neither replaces DBA judgment.

ADDM can guide us, but we still validate the finding before changing SQL, indexes, memory, or parameters."

---

# Slide 13 - ADDM Finding Structure

## Slide Content

Read each finding as:

* finding name
* impact
* description
* recommendation
* rationale
* related SQL or object
* validation needed

---

## Trainer Delivery

"The most important ADDM mistake is copying the recommendation without understanding the finding.

Impact tells us priority.

Recommendation tells us what to consider.

Validation tells us whether it is safe."

---

# SECTION 6 - LIVE LAB: GENERATE ADDM REPORT (11:00 - 11:25)

# Slide 14 - Use Same Snapshot Window

## Slide Content

Use the same snapshots from the AWR lab:

```text
Begin snapshot: &begin_snap
End snapshot:   &end_snap
```

This lets us compare:

```text
AWR raw evidence
ADDM diagnosis
```

---

# Step 1 - Confirm Snapshot IDs

```sql
SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

If variables are lost, list recent snapshots:

```sql
SELECT snap_id,
       begin_interval_time,
       end_interval_time
FROM dba_hist_snapshot
WHERE dbid = &dbid
AND instance_number = &inst_num
ORDER BY snap_id DESC
FETCH FIRST 10 ROWS ONLY;
```

---

# Step 2 - Generate ADDM Report

Recommended reliable method:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

When prompted, use:

```text
Begin snapshot: &begin_snap
End snapshot:   &end_snap
Report name:    addm_day2_morning.txt
```

Trainer note:

The Oracle-supplied script is the safest cross-environment approach for 19c training because it handles the internal ADDM task creation.

---

# Step 3 - If ADDM Has No Major Finding

This can happen in a short lab.

If ADDM says there are no significant findings:

* explain that the workload may be too small or too short
* increase workload loop count from 12 to 30
* include the optional commit workload
* create a fresh start snapshot
* rerun workload
* create a fresh end snapshot
* regenerate AWR and ADDM

Trainer note:

Do not fake findings. Use this as a production lesson: not every report interval has a meaningful bottleneck.

---

# SECTION 7 - INTERPRET ADDM FINDINGS (11:25 - 11:50)

# Slide 15 - ADDM Reading Workflow

## Slide Content

Use this order:

```text
1. Confirm report window
2. Read Finding 1
3. Check impact percentage
4. Identify related SQL/object/wait
5. Read recommendation
6. Verify same issue in AWR
7. Decide next validation step
```

---

## Trainer Delivery

"The important phrase is:

verify same issue in AWR.

If ADDM says high-load SQL, find that SQL in AWR SQL sections.

If ADDM says I/O, check SQL by Reads and Segment Statistics.

If ADDM says commits, check log file sync and commit behavior."

---

# Slide 16 - Impact Percentage

## Slide Content

Example:

```text
Finding impact: 45% of DB time
```

Means:

* this finding affected a large portion of database time
* it should be investigated early
* it is not automatic approval to apply the recommendation

---

## Trainer Delivery

"Impact helps prioritize.

It does not prove the fix is safe.

For example, ADDM may recommend SQL tuning or an index.

That index may improve one query but hurt transaction-heavy DML.

So we validate."

---

# Slide 17 - Example Interpretation: High SQL Load

## Slide Content

If ADDM says:

```text
SQL statements were consuming significant database time.
```

Validation:

* identify SQL ID
* check AWR SQL by Elapsed / CPU / Gets / Reads
* get execution plan
* inspect predicates
* compare E-Rows vs A-Rows
* test the smallest safe fix

---

# Slide 18 - Example Interpretation: I/O

## Slide Content

If ADDM says:

```text
Database file reads consumed significant database time.
```

Validation:

* check SQL ordered by Reads
* check Segment Statistics
* inspect full scans or large index lookups
* separate bad SQL from storage latency
* avoid blaming storage too early

---

# Slide 19 - Example Interpretation: Commit Latency

## Slide Content

If ADDM says:

```text
Commit processing or log file sync consumed database time.
```

Validation:

* check commit frequency
* check application transaction design
* identify sessions/modules with frequent commits
* review redo/log performance
* avoid commit inside tight loops where business allows batching

---

# Slide 20 - Example Interpretation: Memory

## Slide Content

If ADDM says memory pressure:

Validate:

* parsing behavior
* SQL executions
* shared pool pressure
* large sorts
* PGA/temp usage
* whether SQL design caused the memory symptom

Do not immediately increase memory.

---

# Lab Task - ADDM Evidence Table

Participants fill this from `addm_day2_morning.txt`:

| Item | Answer |
| ---- | ------ |
| Top ADDM finding | |
| Finding impact | |
| Related SQL/object/wait | |
| Recommendation | |
| Supporting AWR evidence | |
| Is the recommendation safe directly? | |
| What validation is needed? | |
| What Day 1 skill applies next? | |

---

# SECTION 8 - VALIDATION DECISION TREE (11:50 - 12:00)

# Slide 21 - Do Not Apply Blindly

## Slide Content

Do not:

* apply ADDM recommendations blindly
* create indexes without DML impact check
* change memory parameters during business hours
* blame storage without SQL evidence
* ignore business workload
* tune only by percentage impact
* skip before/after measurement

---

# Slide 22 - Professional Validation Workflow

## Slide Content

```text
ADDM finding
  -> confirm in AWR
  -> identify SQL/object/wait
  -> get execution plan or system evidence
  -> propose smallest safe fix
  -> test in controlled environment
  -> compare before/after
  -> apply through change control
```

---

## Trainer Delivery

"This is the senior DBA mindset.

ADDM helps you prioritize.

AWR gives supporting evidence.

Execution plans and system views help validate.

Only then do we decide the fix."

---

# FINAL MORNING SUMMARY

## What Trainees Should Now Be Able To Do

* create an AWR snapshot window around a test workload
* generate AWR text report
* identify top waits and top SQL
* connect AWR SQL back to execution-plan analysis
* generate ADDM for the same window
* interpret findings, impact, and recommendations
* explain why advisor recommendations require validation

---

# TRANSITION TO DAY 2 SECOND HALF

## Next Topics

* SQL Tuning Advisor
* SQL Access Advisor
* SQL Profiles
* advisor recommendation review
* memory and I/O symptom diagnosis

Trainer closing line:

```text
AWR tells us where time went.
ADDM tells us what Oracle thinks matters.
The DBA decides what is true, safe, and worth changing.
```
