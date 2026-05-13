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

* a blind AWR section-by-section reading marathon without diagnosis logic
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
| 10:10 - 10:45 | Read AWR using a DBA workflow, including ASH |
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
access to V$ACTIVE_SESSION_HISTORY / DBA_HIST_ACTIVE_SESS_HISTORY for ASH drills
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

# AWR VS ASH REPORT: WHEN TO GENERATE WHICH ONE

Use this distinction before starting any performance investigation.

| Question | Generate AWR Report | Generate ASH Report |
| -------- | ------------------- | ------------------- |
| What happened across a time window? | Yes | Sometimes |
| Which SQL consumed DB Time, CPU, gets, reads, parses? | Yes | Yes, as supporting evidence |
| Which wait class dominated over 30-60 minutes? | Yes | Yes, if you need session-level timeline |
| What was happening minute-by-minute inside the incident? | Limited | Yes |
| Which session/module/program was active at a specific moment? | Limited | Yes |
| Problem already finished and you need historical evidence | Yes | Yes, if historical ASH is available |
| Problem is happening right now and you need active session detail | Use later for summary | Yes, immediately |
| Need ADDM recommendations for the same interval | Yes | No |

Practical DBA rule:

```text
AWR = workload report between two snapshots.
ASH = sampled active-session evidence inside a time period.
ADDM = advisor interpretation of AWR evidence.
```

Use AWR when users say:

```text
The system was slow between 10:45 AM and 11:15 AM.
```

Use ASH when the DBA asks:

```text
During those minutes, which sessions, SQL IDs, modules, waits, blockers, or services were active?
```

Do not treat AWR and ASH as competing reports. In real troubleshooting, AWR usually gives the workload picture and ASH explains the active-session detail.

---

# WHERE AWR AND ASH REPORT SCRIPTS LIVE, AND WHERE REPORT FILES ARE CREATED

Oracle-supplied report scripts are normally located here:

```bash
$ORACLE_HOME/rdbms/admin/awrrpt.sql    # AWR report
$ORACLE_HOME/rdbms/admin/ashrpt.sql    # ASH report
$ORACLE_HOME/rdbms/admin/addmrpt.sql   # ADDM report
```

Important location rule:

```text
The SQL scripts live under $ORACLE_HOME/rdbms/admin.
The generated report file is created in the current operating-system directory from which SQL*Plus was started, unless you provide a path in the report name.
```

Check your current server directory before starting SQL*Plus:

```bash
pwd
```

Recommended training directory:

```bash
mkdir -p /tmp/day2_awr_reports
cd /tmp/day2_awr_reports
pwd
sqlplus / as sysdba
```

If you start SQL*Plus from `/tmp/day2_awr_reports` and provide this report name:

```text
awr_day2_morning.html
```

the file is created here:

```text
/tmp/day2_awr_reports/awr_day2_morning.html
```

If you provide a full path as the report name:

```text
/tmp/day2_awr_reports/awr_day2_morning.html
```

the report is created at that exact path.

Trainer warning:

Do not create training reports inside `$ORACLE_HOME/rdbms/admin`. That directory contains Oracle product scripts. Use a working directory such as `/tmp/day2_awr_reports` or a DBA-owned diagnostics directory.

---

# DAY 2 MORNING SCENARIO (9:00 - 9:10)

# Slide 1 - Production Complaint (9:00 - 9:10)

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

# SLOT 1 - AWR: AUTOMATIC WORKLOAD REPOSITORY (9:00 - 10:45)

## 9:00 AM - 10:45 AM core, including ASH bridge

# SECTION 1 - AWR MENTAL MODEL (9:10 - 9:25)

# Slide 2 - What AWR Answers (9:10 - 9:15)

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

# Slide 3 - Snapshot Window (9:15 - 9:20)

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

# Slide 4 - AWR Reading Workflow (9:20 - 9:25)

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

# Slide 5 - Lab Objective (9:25 - 9:30)

## Slide Content

# Lab Goal

We will:

1. interpret a production-style AWR incident report
2. identify top waits, top SQL, reads, gets, and hot segments
3. map AWR evidence to ADDM findings
4. use SQL Tuning Advisor output for the same SQL_ID
5. decide the tuning action using before/after evidence
6. explain the production risk and rollback plan

Primary low-memory hands-on runbook:

```text
02-Day/MOCK-REPORT-INTERPRETATION-LAB.md
```

Mock evidence files:

```text
02-Day/mock-reports/awr_day2_mock_incident.txt
02-Day/mock-reports/addm_day2_mock_incident.txt
02-Day/mock-reports/sql_tuning_advisor_day2_mock.txt
```

Full live workload runbook, only if the environment can handle it:

```text
02-Day/REAL-WORLD-INCIDENT-LAB.md
```

Trainer note:

If the VM cannot handle 200k+ rows or AWR privileges are unreliable, do not waste class time fighting the environment. Use the mock report lab as the main activity. It teaches the real skill: interpreting AWR, validating ADDM, reading SQL Tuning Advisor, and making a production-safe recommendation.

Use the smaller live workload below only as a quick demo or fallback.

---

# Step 1 - Confirm Day 1 Tables Exist (9:30 - 9:33)

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

# Step 2 - Confirm Data Volume (9:33 - 9:36)

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

# Step 3 - Confirm AWR Access (9:36 - 9:39)

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

# Step 4 - Get DBID And Instance Number (9:39 - 9:42)

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

# Step 5 - Create Workload Helper Table (9:42 - 9:45)

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

# Slide 6 - Workload Design (9:45 - 9:48)

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

# Step 1 - Create Start Snapshot (9:48 - 9:51)

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

# Step 2 - Run Tagged Workload (9:51 - 10:00)

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

# Optional Step - Generate Commit Wait Activity (9:58 - 10:00, only if machine allows)

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

# Step 3 - Verify Tagged SQL In V$SQL (10:00 - 10:03)

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

# Step 4 - Create End Snapshot (10:03 - 10:06)

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

# Step 5 - Generate AWR HTML Report (10:06 - 10:09)

Use HTML for class reading because the report has a clickable table of contents.

Before starting SQL*Plus, choose a server-side report directory:

```bash
mkdir -p /tmp/day2_awr_reports
cd /tmp/day2_awr_reports
pwd
sqlplus / as sysdba
```

Why:

```text
The report file is written to the current directory unless you give a full path.
Keeping reports under /tmp/day2_awr_reports makes them easy to find and download.
```

Confirm the database and snapshot IDs:

```sql
SELECT name, dbid
FROM v$database;

SELECT instance_name, instance_number
FROM v$instance;

SELECT &begin_snap AS begin_snapshot_id,
       &end_snap   AS end_snapshot_id
FROM dual;
```

Why:

```text
This prevents generating a report for the wrong database, instance, or time window.
```

Run the Oracle AWR report script:

```sql
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
```

When prompted, use:

```text
Specify the Report Type: html
Enter value for num_days: 1
Enter value for begin_snap: &begin_snap
Enter value for end_snap: &end_snap
Enter value for report_name: /tmp/day2_awr_reports/awr_day2_morning.html
```

Why:

```text
awrrpt.sql uses Oracle's supported report format.
HTML is easier to navigate than text during training.
The explicit report path avoids confusion about where the file was created.
```

Check that the report exists from the server shell:

```bash
ls -lh /tmp/day2_awr_reports/awr_day2_morning.html
```

Expected:

```text
The HTML file should exist and should not be zero bytes.
```

Optional text version for searching:

```sql
SPOOL /tmp/day2_awr_reports/awr_day2_morning.txt

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

Why:

```text
Text is convenient for grep/search.
HTML is better for classroom navigation.
Both should use the same begin and end snapshots.
```

Trainer note:

If `AWR_REPORT_TEXT` fails because of privileges, use `awrrpt.sql` as a privileged user.

---

# Step 6 - Generate ASH HTML Report For The Same Window (10:09 - 10:10, demo or trainer reference)

Use ASH after AWR when you need active-session detail inside the same incident period.

Run:

```sql
@$ORACLE_HOME/rdbms/admin/ashrpt.sql
```

When prompted, use the same problem window.

Typical choices:

```text
Report type: html
Begin time:  the begin interval time for &begin_snap
End time:    the end interval time for &end_snap
Report name: /tmp/day2_awr_reports/ash_day2_morning.html
```

Why:

```text
AWR tells what consumed DB Time across the interval.
ASH helps identify which sessions, SQL IDs, modules, programs, services, and wait events were active inside that interval.
```

If the prompt asks for database ID or instance number, use:

```sql
SELECT dbid FROM v$database;
SELECT instance_number FROM v$instance;
```

If the prompt asks for exact times, list snapshot times:

```sql
SELECT snap_id,
       TO_CHAR(begin_interval_time,'YYYY-MM-DD HH24:MI:SS') AS begin_time,
       TO_CHAR(end_interval_time,'YYYY-MM-DD HH24:MI:SS')   AS end_time
FROM dba_hist_snapshot
WHERE dbid = &dbid
AND instance_number = &inst_num
AND snap_id BETWEEN &begin_snap AND &end_snap
ORDER BY snap_id;
```

Check the ASH report file:

```bash
ls -lh /tmp/day2_awr_reports/ash_day2_morning.html
```

---

# Step 7 - Download AWR And ASH Reports With WinSCP CLI (10:09 - 10:10, demo or trainer reference)

From a Windows machine with WinSCP installed, open Command Prompt or PowerShell.

Create a local folder first:

```bat
mkdir "%USERPROFILE%\Downloads\day2_awr_reports"
```

Interactive WinSCP CLI method:

```bat
"C:\Program Files (x86)\WinSCP\WinSCP.com"
```

Connect to the database server:

```text
open sftp://oracle@DB_SERVER_HOSTNAME_OR_IP/
```

Go to the local download folder:

```text
lcd %USERPROFILE%\Downloads\day2_awr_reports
```

Go to the remote report folder:

```text
cd /tmp/day2_awr_reports
```

Download the reports:

```text
get awr_day2_morning.html
get ash_day2_morning.html
get awr_day2_morning.txt
exit
```

Why:

```text
The report is generated on the database server.
WinSCP copies the server-side HTML file to the trainee laptop so it can be opened in a browser.
```

One-command scripted method:

```bat
"C:\Program Files (x86)\WinSCP\WinSCP.com" ^
  /command ^
  "open sftp://oracle@DB_SERVER_HOSTNAME_OR_IP/" ^
  "lcd %USERPROFILE%\Downloads\day2_awr_reports" ^
  "cd /tmp/day2_awr_reports" ^
  "get awr_day2_morning.html" ^
  "get ash_day2_morning.html" ^
  "exit"
```

If the SSH port is not 22:

```text
open sftp://oracle@DB_SERVER_HOSTNAME_OR_IP:2222/
```

If passwordless login is not configured, WinSCP prompts for the password.

Production note:

Do not email AWR reports casually. They may contain SQL text, schema names, host names, service names, file paths, and business-sensitive workload information.

---

# SECTION 4 - READ AWR LIKE A DBA (10:10 - 10:45)

Goal of this section:

```text
HOW TO INTERPRET, READ, AND UNDERSTAND WHAT IS GOING ON
```

Trainees should keep these files open while reading:

| File | Use It For |
| ---- | ---------- |
| `02-Day/reports/awr-training-index.html` | one-page link index |
| `02-Day/reports/awrrpt-sample.html` | full Oracle-style AWR table of contents |
| `02-Day/reports/awrrpt-bank-00-baseline.html` | normal OLTP baseline |
| `02-Day/reports/awrrpt-bank-01-cpu-sql.html` | CPU-bound SQL example |
| `02-Day/reports/awrrpt-bank-02-io-full-scan.html` | User I/O and full-scan example |
| `02-Day/reports/awrrpt-bank-03-locking.html` | row lock and blocking example |
| `02-Day/reports/awrrpt-bank-04-hard-parse.html` | parse and library cache example |
| `02-Day/reports/awrrpt-bank-05-commit-redo.html` | commit and redo latency example |

Reading principle:

```text
Do not read AWR from top to bottom like a book.
Read it like an investigation.
Scope -> DB Time -> waits -> SQL -> objects -> supporting sections -> ASH/ADDM.
```

---

# Slide 7 - AWR Investigation Order (10:10 - 10:12)

## Slide Content

Use this order in every production review:

```text
1. Main Report
2. Report Summary
3. Wait Events Statistics
4. SQL Statistics
5. Instance Activity Statistics
6. IO Stats
7. Wait Statistics
8. Undo Statistics
9. Segment Statistics
10. Dictionary Cache Statistics
11. Library Cache Statistics
12. Initialization Parameters
13. Active Session History (ASH) Report
14. ADDM Reports
```

Why this order works:

```text
It starts with scope and DB Time.
It then identifies the dominant wait or CPU direction.
It then finds SQL and objects responsible for that time.
It uses lower sections to validate, not to guess.
```

---

# Slide 8 - Main Report (10:12 - 10:13)

## Slide Content

Open:

```text
02-Day/reports/awrrpt-sample.html
```

Look for the AWR table of contents:

```text
Main Report
Report Summary
Wait Events Statistics
SQL Statistics
Instance Activity Statistics
IO Stats
Wait Statistics
Undo Statistics
Segment Statistics
Dictionary Cache Statistics
Library Cache Statistics
Initialization Parameters
Active Session History (ASH) Report
ADDM Reports
```

Interpretation:

```text
Main Report is the navigation map.
It tells you which evidence exists in this report.
Use it to jump directly to the sections connected to the symptom.
```

Practical guidance:

* for "system slow", start with `Report Summary` and `Wait Events Statistics`
* for "one screen slow", go quickly to `SQL Statistics`
* for "storage slow", verify with `SQL Statistics`, `IO Stats`, and `Segment Statistics`
* for "blocking", verify with waits, ASH, and row-lock segments
* for "new release slow", check SQL, parse, version count, dictionary cache, and library cache

Real-life example:

```text
At 10:30 AM, branch users say the teller screen is slow, but internet banking looks normal.
Use Main Report as the map: start at Report Summary to confirm the exact window, then jump to Service Statistics and Wait Events instead of reading every AWR table from top to bottom.
```

Trainer delivery:

"The table of contents is not just navigation. It is the DBA checklist. Every section answers a different kind of question."

---

# Slide 9 - Report Summary (10:13 - 10:15)

## Slide Content

First check:

| Item | Why It Matters |
| ---- | -------------- |
| DB Name / Instance / Host | confirms the correct system |
| Startup Time | detects restart effects |
| Begin Snap / End Snap | confirms correct window |
| Elapsed Time | wall-clock duration |
| DB Time | total foreground database work |
| Sessions / Cursors | workload shape |
| Load Profile | per-second and per-transaction rates |
| Instance Efficiency | quick symptoms, not final proof |

Core formula:

```text
AAS = DB Time in seconds / elapsed seconds
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| DB Time near Elapsed Time | about one active session on average |
| DB Time much greater than Elapsed Time | many sessions active or waiting |
| AAS higher than CPU count with high DB CPU | possible CPU pressure |
| AAS high but DB CPU low | sessions are mostly waiting |

Use sample reports:

* `awrrpt-bank-00-baseline.html`: compare healthy OLTP shape
* `awrrpt-bank-01-cpu-sql.html`: DB Time rises because SQL burns CPU
* `awrrpt-bank-05-commit-redo.html`: DB Time rises because sessions wait on commit

Real-life example:

```text
Users complain about slowness from 11:00 AM to 11:15 AM, but the DBA accidentally generates an AWR from 9:00 AM to 10:00 AM.
Report Summary immediately exposes the wrong begin and end snapshots before anyone wastes time tuning the wrong workload.
```

Trainer delivery:

"Report Summary prevents wrong diagnosis. If this is the wrong instance, wrong PDB, or wrong time window, every conclusion after this is noise."

---

# Slide 10 - Wait Events Statistics (10:15 - 10:16)

## Slide Content

This section answers:

```text
Where did foreground DB Time go?
```

Read in this order:

```text
1. Time Model Statistics
2. Foreground Wait Class
3. Foreground Wait Events
4. Service Statistics
5. Service Wait Class Stats
6. Top Process Types by Wait Class
7. Top Process Types by CPU Used
```

First interpretation table:

| Dominant Signal | Meaning | Next Section |
| --------------- | ------- | ------------ |
| DB CPU | CPU was the bottleneck or SQL used too much CPU | SQL ordered by CPU Time, Gets |
| User I/O | sessions waited for data blocks | SQL ordered by Reads, IO Stats, Segment Statistics |
| Commit | sessions waited for commit completion | Load Profile, log file sync, redo stats |
| Application | often locks or application-level waits | ASH, blockers, row-lock segments |
| Concurrency | shared resource contention | ASH, segment waits, library cache |
| Network | client fetch or round-trip behavior | service/module and application review |

Real-life example:

```text
After salary processing starts, DB Time jumps and User I/O dominates.
This can happen when a payroll report full-scans a large transaction table during online banking peak time.
The wait class points the DBA toward SQL by Reads, not directly toward a storage ticket.
```

Trainer delivery:

"Waits tell direction. They do not prove root cause. A User I/O report may be bad storage, but very often it is bad SQL reading too many blocks."

---

# Slide 11 - Time Model Statistics (10:16 - 10:17)

## Slide Content

Time Model answers:

```text
What type of database work consumed time?
```

Read these rows carefully:

| Row | Meaning |
| --- | ------- |
| DB time | total foreground database time |
| DB CPU | foreground CPU time |
| sql execute elapsed time | SQL execution work |
| parse time elapsed | parsing overhead |
| hard parse elapsed time | optimizer and library cache work |
| PL/SQL execution elapsed time | time in PL/SQL |
| connection management call elapsed time | logon/logoff or connection churn |

Interpretation:

| Pattern | Likely Direction |
| ------- | ---------------- |
| `DB CPU` close to `DB time` | CPU-bound workload |
| `sql execute elapsed time` dominates | SQL execution is the main area |
| `parse time elapsed` high | parsing overhead |
| `hard parse elapsed time` high | literal SQL, invalidations, shared pool pressure |
| PL/SQL time high | inspect PL/SQL code and SQL inside it |

Use sample reports:

* `awrrpt-bank-01-cpu-sql.html`: SQL execution and CPU dominate
* `awrrpt-bank-04-hard-parse.html`: parse time and library cache symptoms matter

Real-life example:

```text
A new mobile banking release sends SQL with literal customer IDs instead of bind variables.
Time Model shows parse and hard parse time rising, even though the individual SQL executions are small.
That tells the DBA to investigate cursor reuse and application SQL generation.
```

Trainer delivery:

"Time Model is the bridge between high-level DB Time and specific SQL sections. It tells whether to chase execution, parsing, PL/SQL, or connection behavior."

---

# Slide 12 - Foreground Wait Class (10:17 - 10:18)

## Slide Content

Foreground Wait Class groups detailed waits into categories:

| Wait Class | DBA Interpretation |
| ---------- | ------------------ |
| User I/O | foreground sessions waited for datafile I/O |
| Commit | foreground sessions waited for commit durability |
| Application | often row locks or application coordination |
| Concurrency | shared Oracle structure contention |
| Configuration | setup or sizing related waits |
| Network | client/server communication |
| System I/O | background or system I/O influence |

How to read:

```text
Sort mentally by % DB Time.
Ignore tiny percentages at first.
Focus on the class that explains the user complaint.
```

Practical examples:

* if `User I/O` dominates, read SQL by Reads before blaming disks
* if `Commit` dominates, check `log file sync` and commits per second
* if `Application` dominates, look for `enq: TX - row lock contention`
* if `Concurrency` dominates, inspect detailed events and ASH

Use sample reports:

* `awrrpt-bank-02-io-full-scan.html`: User I/O pattern
* `awrrpt-bank-03-locking.html`: Application wait pattern
* `awrrpt-bank-05-commit-redo.html`: Commit wait pattern

Real-life example:

```text
The payment posting service is slow only during end-of-day upload.
Foreground Wait Class shows Commit dominating because the loader commits every row instead of batching transactions.
```

---

# Slide 13 - Foreground Wait Events (10:18 - 10:19)

## Slide Content

Foreground Wait Events gives the detailed wait names.

Common production readings:

| Event | What It Usually Means | First Validation |
| ----- | --------------------- | ---------------- |
| `db file sequential read` | single-block reads, often index access | SQL by Reads, plan access path |
| `db file scattered read` | multiblock reads, often full scans | SQL by Reads, segment physical reads |
| `direct path read` | large/direct reads | SQL by Reads, parallel/direct scan behavior |
| `log file sync` | foreground waiting for commit | commits/sec, redo latency, app commit pattern |
| `enq: TX - row lock contention` | row lock blocking | ASH blockers, row-lock segments |
| `library cache: mutex X` | library cache contention | parse calls, version count, hard parse time |
| `cursor: pin S wait on X` | cursor contention | version count, parse behavior |

Do not conclude:

```text
db file sequential read = index problem
db file scattered read = storage problem
log file sync = redo disk problem
```

Better conclusion:

```text
This wait tells me where to investigate next.
I need SQL, object, module, and timing evidence.
```

Real-life example:

```text
`enq: TX - row lock contention` appears as a top event during loan approval.
This can happen when one clerk opens a customer loan record and leaves the transaction uncommitted while other branches try to update the same account.
The next check is ASH blocker evidence and the locked object, not an index rebuild.
```

---

# Slide 14 - Service Statistics (10:19 - 10:20)

## Slide Content

Service Statistics answers:

```text
Which service consumed DB Time, DB CPU, physical reads, or logical reads?
```

Why this matters in banking:

```text
One database may serve internet banking, branch teller, card authorization,
AML batch, statement generation, settlement, and reporting.
The database can be slow for one service while another service is normal.
```

How to read:

| Column | DBA Question |
| ------ | ------------ |
| Service Name | which application path is involved? |
| DB Time | where users spent database time |
| DB CPU | which service burned CPU |
| Physical Reads | which service drove storage reads |
| Logical Reads | which service did the most buffer work |

Practical guidance:

* if `IBANK_WEB` dominates, focus on customer-facing SQL first
* if `AML_BATCH` dominates during business hours, check scheduling and resource manager
* if `CARD_AUTH` dominates but response time is normal, do not tune only because it is busy
* if service names are generic, ask application teams to set service/module/action properly

Use sample reports:

* `awrrpt-bank-01-cpu-sql.html`: internet banking SQL dominates CPU
* `awrrpt-bank-02-io-full-scan.html`: AML-style workload drives reads

Real-life example:

```text
The database hosts both card authorization and fraud analytics.
Service Statistics shows `FRAUD_BATCH` consumed most physical reads, while `CARD_AUTH` used little DB Time.
That means the incident may be a batch scheduling conflict, not a card application defect.
```

---

# Slide 15 - Service Wait Class Stats (10:20 - 10:21)

## Slide Content

Service Wait Class Stats connects services to wait classes.

This answers:

```text
Which application service is waiting on what?
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| one service high in User I/O | that service likely drove read workload |
| one service high in Commit | that service may commit too often |
| one service high in Application | that service may be blocked or locking |
| all services high in same wait | shared system-wide bottleneck possible |

Practical example:

```text
CARD_SETTLE has most Commit waits.
Do not blame all banking users.
Focus on settlement import commit behavior.
```

Real-life example:

```text
Only the statement-generation service has high User I/O waits.
This can happen when monthly PDF statement creation scans account history while teller and ATM services remain healthy.
```

Use sample report:

```text
02-Day/reports/awrrpt-bank-05-commit-redo.html
```

Trainer delivery:

"Service Wait Class Stats helps avoid vague statements like 'the database was slow'. It lets a DBA say which application service was slow and why."

---

# Slide 16 - Top Process Types By Wait Class (10:21 - 10:22)

## Slide Content

This section separates foreground and background process behavior.

Read it to answer:

```text
Are user sessions waiting, or are background processes showing the pressure?
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| foreground processes dominate User I/O | user SQL is waiting for reads |
| foreground processes dominate Commit | users wait for commits |
| LGWR/system process waits are high | redo write path may need investigation |
| DBWR/system I/O pressure appears | checkpoint/write pressure possible |

Practical guidance:

* foreground waits explain user response time directly
* background waits explain system support work
* connect background pressure back to foreground impact before escalating

Example:

```text
If users wait on log file sync, check whether LGWR/log file parallel write is also slow.
If LGWR writes are slow, storage/Data Guard/synchronous commit path may be involved.
If commits per second are extreme, application commit design may be the cause.
```

Real-life example:

```text
Foreground sessions show Commit waits and LGWR also shows write latency.
This can happen when synchronous Data Guard transport slows down or redo logs sit on a busy storage volume.
```

---

# Slide 17 - Top Process Types By CPU Used (10:21 - 10:22)

## Slide Content

This section answers:

```text
Who used CPU: foreground sessions or background processes?
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| foreground CPU dominates | application SQL is likely the CPU consumer |
| background CPU unusually high | background activity needs review |
| CPU high but SQL sections weak | check PL/SQL, parsing, recursive SQL, or report window |

Practical guidance:

* if foreground CPU dominates, go to `SQL ordered by CPU Time`
* if parse-related CPU is suspected, go to `Parse Calls`, `Version Count`, and `Library Cache`
* if CPU is high but no SQL stands out, check whether many small SQL statements spread the load

Use sample reports:

* `awrrpt-bank-01-cpu-sql.html`: foreground SQL CPU
* `awrrpt-bank-04-hard-parse.html`: parse/library cache pressure

Real-life example:

```text
Foreground CPU dominates after a marketing campaign starts.
This can happen when thousands of customers repeatedly refresh balance and mini-statement screens that execute inefficient SQL.
```

---

# Slide 18 - SQL Statistics (10:22 - 10:23)

## Slide Content

SQL Statistics is where AWR usually becomes actionable.

Use this order:

```text
1. SQL ordered by Elapsed Time
2. SQL ordered by CPU Time
3. SQL ordered by User I/O Wait Time
4. SQL ordered by Gets
5. SQL ordered by Reads
6. SQL ordered by Physical Reads (UnOptimized)
7. SQL ordered by Executions
8. SQL ordered by Parse Calls
9. SQL ordered by Sharable Memory
10. SQL ordered by Version Count
11. Complete List of SQL Text
```

Rule:

```text
A SQL_ID appearing in multiple top SQL sections is a stronger suspect than a SQL_ID appearing in only one section.
```

Evidence chain:

```text
SQL_ID -> module/service -> elapsed/CPU/IO/gets/executions -> SQL text -> plan -> predicates -> fix
```

Real-life example:

```text
The complaint is "fund transfer is slow", but AWR shows one SQL_ID near the top of Elapsed Time, CPU Time, and Gets.
This can happen when a transfer validation query scans transaction history too broadly for every transfer request.
```

---

# Slide 19 - SQL Ordered By Elapsed Time (10:23 - 10:24)

## Slide Content

This is usually the first SQL section to read.

It answers:

```text
Which SQL consumed the most wall-clock database time?
```

Read these columns:

| Column | Meaning |
| ------ | ------- |
| Elapsed Time | total time spent by this SQL |
| Executions | how many times it ran |
| Elapsed per Exec | average time per execution |
| % Total | share of total DB Time |
| % CPU / % IO | whether time was CPU or I/O heavy |
| SQL ID | key for deeper plan analysis |
| Module | application source |
| SQL Text | first clue about business function |

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high elapsed, low executions | each run is expensive |
| moderate elapsed, huge executions | application loop or chatty SQL |
| high elapsed and high CPU | CPU-heavy SQL |
| high elapsed and high I/O | read-heavy SQL |

Use sample report:

```text
02-Day/reports/awrrpt-bank-01-cpu-sql.html
```

Practice:

```text
Find SQL_ID 9m8v6q3k2b1fa.
Notice it is high in elapsed time, CPU time, and buffer gets.
Conclusion: this is not just a slow screen; it is a workload-level SQL consumer.
```

Real-life example:

```text
A customer statement query runs only 300 times in 30 minutes, but each execution takes several seconds.
SQL ordered by Elapsed Time makes it visible because the total user-facing time is high even though execution count is not huge.
```

---

# Slide 20 - SQL Ordered By CPU Time (10:24 - 10:25)

## Slide Content

This section answers:

```text
Which SQL burned database CPU?
```

Read it when:

* `DB CPU` is a top timed event
* AAS is near or above CPU count
* OS CPU was saturated during the incident
* user response time increased without obvious I/O or lock waits

Interpretation:

| Pattern | Likely Cause |
| ------- | ------------ |
| high CPU and high gets | too many logical reads |
| high CPU and many executions | repeated small SQL |
| high CPU and high parse calls | parsing overhead |
| high CPU but low rows returned | inefficient access path or join |

Next check:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

Trainer delivery:

"CPU tuning usually means reducing work, not just adding CPU. The plan must explain why the SQL used so many buffers or executions."

Real-life example:

```text
CPU reaches 95 percent during login peak.
SQL ordered by CPU Time shows an account entitlement query doing millions of logical reads because it misses a selective index.
The practical fix is to reduce logical work, not immediately request more CPU cores.
```

---

# Slide 21 - SQL Ordered By User I/O Wait Time (10:25 - 10:26)

## Slide Content

This section answers:

```text
Which SQL spent the most time waiting for foreground I/O?
```

Use it when top waits include:

```text
db file sequential read
db file scattered read
direct path read
cell single block physical read
cell smart table scan
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high User I/O time and high Reads | SQL is driving physical reads |
| high User I/O time but low Reads | average I/O latency may be high |
| high Reads per Exec | each execution reads too much |
| high executions with small reads | repeated lookup pattern |

Use sample report:

```text
02-Day/reports/awrrpt-bank-02-io-full-scan.html
```

Trainer warning:

"Do not say storage is slow until you know which SQL caused the reads and whether those reads were necessary."

Real-life example:

```text
User I/O wait time jumps during AML screening.
SQL ordered by User I/O Wait Time shows one scan of `TRANSACTIONS` reading years of data because the date predicate does not prune partitions.
```

---

# Slide 22 - SQL Ordered By Gets (10:26 - 10:27)

## Slide Content

Buffer Gets are logical reads.

This section answers:

```text
Which SQL touched the most database blocks in memory?
```

Why it matters:

```text
Logical reads consume CPU and latch/cache resources even when physical I/O is low.
A SQL can be CPU-heavy because it repeatedly scans too many cached blocks.
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high Gets per Exec | inefficient access path per run |
| high Gets and high Executions | repeated inefficient SQL |
| high Gets but low Reads | data is cached, but SQL still wastes CPU |
| same SQL in CPU and Gets | strong CPU tuning candidate |

Use sample report:

```text
02-Day/reports/awrrpt-bank-01-cpu-sql.html
```

Practice:

```text
Find the SQL with very high Buffer Gets.
Ask: is it scanning account history too broadly?
Next: inspect predicates and indexes.
```

Real-life example:

```text
The same balance-check SQL runs thousands of times per minute and data is mostly cached.
Physical reads are low, but SQL ordered by Gets is high because each execution touches too many index and table blocks in memory.
```

---

# Slide 23 - SQL Ordered By Reads (10:27 - 10:28)

## Slide Content

Physical Reads are blocks read from storage or Exadata cells.

This section answers:

```text
Which SQL caused the most physical read volume?
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high Reads per Exec | large scan or poor pruning |
| high Reads and high Elapsed | likely user-visible read pressure |
| high Reads but low Elapsed | efficient large scan, maybe normal batch |
| same object hot in Segment Stats | SQL-to-object evidence is stronger |

Use sample report:

```text
02-Day/reports/awrrpt-bank-02-io-full-scan.html
```

Next checks:

* `Segment Statistics` for the table/index being read
* execution plan for full scan, partition pruning, or index access
* business timing: should this report or batch run during peak OLTP?

Real-life example:

```text
End-of-month statement generation starts at 10:00 AM and the `ACCOUNT_TXN_HISTORY` table becomes the top physical-read object.
SQL ordered by Reads identifies the report SQL that is pulling too much historical data during business hours.
```

---

# Slide 24 - SQL Ordered By Physical Reads (UnOptimized) (10:28 - 10:29)

## Slide Content

This section separates reads that did not benefit from optimization such as cache/offload behavior.

It answers:

```text
Which SQL generated physical reads that were not optimized?
```

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high unoptimized read requests | SQL may be causing avoidable storage work |
| low % optimized | cache/offload/storage optimization is not helping enough |
| high unoptimized per exec | each execution is expensive at the storage layer |

Practical guidance:

* compare with `SQL ordered by Reads`
* check whether the SQL is scanning too much data
* check partition pruning and predicates
* on Exadata, check whether predicates are offloadable
* do not tune this section without reading the execution plan

Use sample report:

```text
02-Day/reports/awrrpt-sample.html
```

Trainer delivery:

"Unoptimized reads point to avoidable physical read pressure. The fix is often SQL shape, pruning, indexes, or workload placement, not only storage."

Real-life example:

```text
On Exadata, a large fraud query reads many blocks but gets little smart-scan benefit.
This can happen when predicates use functions or expressions that cannot be offloaded efficiently.
```

---

# Slide 25 - SQL Ordered By Executions (10:29 - 10:30)

## Slide Content

This section answers:

```text
Which SQL ran the most times?
```

High execution count is not automatically bad. It is bad when:

* total elapsed time is meaningful
* total CPU is meaningful
* total gets are meaningful
* parse calls are close to executions
* the SQL is called row-by-row from application code

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| many executions, tiny per exec, large total | death by repetition |
| executions close to parse calls | cursor reuse problem |
| many executions from one module | application loop |
| many executions and commit waits | row-by-row transaction design |

Use sample reports:

* `awrrpt-bank-05-commit-redo.html`: many settlement operations and commits
* `awrrpt-bank-01-cpu-sql.html`: repeated customer-facing SQL

Production question:

```text
Can the application batch, cache, bind, array fetch, or reduce calls without changing business correctness?
```

Real-life example:

```text
A mobile app calls the same customer-preference lookup once for every account card displayed on the screen.
Each call is fast, but SQL ordered by Executions shows millions of executions and a large total cost.
```

---

# Slide 26 - SQL Ordered By Parse Calls (10:30 - 10:31)

## Slide Content

This section answers:

```text
Which SQL caused the most parse activity?
```

Read it when:

* Time Model shows parse time
* hard parse elapsed time is high
* library cache waits appear
* CPU is high after a release
* SQL text contains literals instead of bind variables

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| Parse Calls close to Executions | poor cursor reuse |
| many similar SQL texts | literals instead of binds |
| high parse calls and high CPU | parsing contributes to CPU pressure |
| high parse calls and library cache waits | shared pool/cursor contention possible |

Use sample report:

```text
02-Day/reports/awrrpt-bank-04-hard-parse.html
```

Next checks:

```sql
SELECT sql_id,
       executions,
       parse_calls,
       version_count,
       substr(sql_text,1,120) sql_text
FROM v$sqlarea
WHERE parse_calls > 1000
ORDER BY parse_calls DESC
FETCH FIRST 20 ROWS ONLY;
```

Trainer delivery:

"High parse calls are often an application coding problem. Adding memory may hide the symptom briefly, but bind variables and cursor reuse fix the cause."

Real-life example:

```text
After a release, the application sends `WHERE CUSTOMER_ID = 101`, `102`, `103` as different literal SQL texts.
SQL ordered by Parse Calls becomes hot because Oracle repeatedly parses similar statements instead of reusing one bind-aware cursor.
```

---

# Slide 27 - SQL Ordered By Sharable Memory (10:31 - 10:32)

## Slide Content

This section answers:

```text
Which SQL consumes the most shared pool memory?
```

Read it when:

* shared pool pressure is suspected
* hard parsing increased
* library cache waits appear
* large generated SQL or many child cursors exist

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| one SQL uses very high sharable memory | complex SQL, many objects, large plan |
| many similar SQL consume memory | literal SQL or generated SQL problem |
| high memory and high version count | child cursor explosion |
| high memory but low executions | expensive cursor footprint with little value |

Next checks:

* `SQL ordered by Version Count`
* `Library Cache Statistics`
* `V$SQL_SHARED_CURSOR`
* application SQL generation logic

Production caution:

```text
Do not increase shared pool first.
Find why sharable memory grew.
```

Real-life example:

```text
A reporting tool generates very large SQL with hundreds of selected columns and dynamic filters.
SQL ordered by Sharable Memory shows a few generated statements occupying disproportionate shared pool memory.
```

---

# Slide 28 - SQL Ordered By Version Count (10:32 - 10:33)

## Slide Content

Version Count means one SQL_ID has multiple child cursors.

This section answers:

```text
Which SQL has many child cursors and may be stressing library cache?
```

Possible reasons:

* bind mismatch
* optimizer environment mismatch
* different NLS settings
* adaptive cursor sharing
* invalidations
* different object privileges
* literal or generated SQL patterns

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| high version count and high parse | cursor sharing problem likely |
| high version count and library cache waits | contention risk |
| high version count after deployment | application or environment changed |
| version count high but no DB Time impact | note it, but prioritize bigger DB Time consumers |

Use sample report:

```text
02-Day/reports/awrrpt-bank-04-hard-parse.html
```

Next query:

```sql
SELECT sql_id,
       child_number,
       executions,
       plan_hash_value,
       is_bind_sensitive,
       is_bind_aware,
       is_shareable
FROM v$sql
WHERE sql_id = '&&sql_id_from_awr'
ORDER BY child_number;
```

Real-life example:

```text
Different application servers connect with different NLS settings after a deployment.
The same SQL_ID gets many child cursors, so SQL ordered by Version Count rises and library cache contention may follow.
```

---

# Slide 29 - Complete List Of SQL Text (10:33 - 10:34)

## Slide Content

This section answers:

```text
What is the fuller SQL text for a SQL_ID shown earlier?
```

Use it when:

* top SQL text is truncated in earlier sections
* you need to map SQL_ID to business logic
* the same SQL_ID appears in multiple sections
* you need the exact text before getting the plan

Practical guidance:

```text
Do not tune from the SQL text alone.
Use SQL text to identify business function and predicates.
Then inspect the execution plan.
```

Use sample report:

```text
02-Day/reports/awrrpt-sample.html
```

Follow-up command:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

If the SQL is still in memory:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    sql_id => '&&sql_id_from_awr',
    cursor_child_no => NULL,
    format => 'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

Real-life example:

```text
The top SQL text in the elapsed-time section is truncated and only shows `SELECT ... FROM TRANSACTIONS`.
Complete SQL Text reveals the business predicate, such as a missing branch/date filter, before the DBA retrieves the plan.
```

---

# Slide 30 - Instance Activity Statistics (10:34 - 10:35)

## Slide Content

This section answers:

```text
What changed at the instance counter level during the interval?
```

Useful counters:

| Counter | Meaning |
| ------- | ------- |
| logical reads | buffer work volume |
| physical reads | storage read volume |
| physical writes | write pressure |
| execute count | SQL execution rate |
| parse count total | parse rate |
| parse count hard | hard parse rate |
| user commits | commit rate |
| redo size | redo generation |
| sorts disk | temp spill risk |

How to use:

```text
Use instance activity to validate what the top sections suggested.
Do not start here unless you already know what symptom you are validating.
```

Examples:

* high `user commits` supports a `log file sync` diagnosis
* high `parse count hard` supports a hard parse diagnosis
* high `physical reads` supports I/O pressure, but SQL must explain the reads
* high `redo size` supports heavy DML or commit workload

Real-life example:

```text
The top wait is `log file sync`, and Instance Activity shows a very high `user commits` rate.
This can happen when a settlement loader commits every inserted row instead of every business batch.
```

---

# Slide 31 - IO Stats (10:35 - 10:36)

## Slide Content

IO Stats answers:

```text
Which tablespaces or datafiles experienced read/write volume and latency?
```

Read:

| Section | Use |
| ------- | --- |
| Tablespace IO Stats | broad storage pressure by tablespace |
| File IO Stats | specific datafile hotspots |

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| one tablespace has most reads | likely object concentration |
| one datafile latency is high | possible storage or placement issue |
| reads high but latency normal | SQL volume may be the issue |
| latency high across many files | storage layer investigation may be valid |

How to connect:

```text
SQL ordered by Reads -> Segment Statistics -> tablespace/datafile
```

Real-life example:

```text
File IO Stats shows one datafile in the `TXN_DATA` tablespace has much higher read latency than others.
This can happen when a hot transaction partition or datafile is placed on a slower storage tier.
```

Trainer delivery:

"IO Stats tells where I/O happened. SQL and Segment sections tell why it happened."

---

# Slide 32 - Wait Statistics (10:36 - 10:37)

## Slide Content

Wait Statistics often contains lower-level buffer and instance wait details.

Use it to validate:

* buffer busy waits
* read/write pressure
* concurrency symptoms
* RAC or cluster-related symptoms, if present
* latch or cache contention direction

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| buffer busy style waits | hot block or segment contention possible |
| many concurrency waits | inspect ASH and object waits |
| wait stats align with top events | stronger evidence |
| wait stats do not align | lower priority until tied to DB Time |

Practical rule:

```text
If a wait does not consume meaningful DB Time and does not match the complaint, do not lead with it.
```

Real-life example:

```text
Buffer busy waits rise during branch cash posting.
This can happen when many sessions insert into or update rows concentrated in the same few blocks, such as a poorly distributed sequence/index hotspot.
```

---

# Slide 33 - Undo Statistics (10:37 - 10:38)

## Slide Content

Undo Statistics answers:

```text
Was undo pressure, long transaction behavior, or read consistency risk part of the incident?
```

Read when:

* long-running reports fail or slow down
* ORA-01555 appears
* large DML or batch ran
* blocking and long transactions are suspected

Interpretation:

| Signal | Meaning |
| ------ | ------- |
| high undo generation | heavy DML workload |
| long query length | read consistency pressure |
| tuned undo retention pressure | possible snapshot-too-old risk |
| high transaction table activity | concurrent DML pressure |

Use with:

* `Segment Statistics` for changed objects
* ASH for long-running DML sessions
* application transaction design

Banking note:

```text
Undo is not only performance.
It protects read consistency and rollback safety during financial transactions.
```

Real-life example:

```text
A long-running regulatory report fails with snapshot-too-old while a batch job updates millions of transaction rows.
Undo Statistics helps show whether undo pressure and long query duration were part of the incident.
```

---

# Slide 34 - Segment Statistics (10:38 - 10:39)

## Slide Content

Segment Statistics answers:

```text
Which table, index, partition, or segment was hot?
```

Read these subsections:

| Subsection | Use |
| ---------- | --- |
| Segments by Logical Reads | objects causing buffer work |
| Segments by Physical Reads | objects causing storage reads |
| Segments by Table Scans | scan-heavy objects |
| Segments by DB Block Changes | DML-heavy objects |
| Segments by Row Lock Waits | lock-hot objects |
| Segments by Buffer Busy Waits | block contention candidates |

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| SQL by Reads and same table in physical reads | strong I/O evidence |
| SQL by Gets and same index/table in logical reads | strong CPU/logical read evidence |
| row lock waits on one table | application transaction hotspot |
| DB block changes high | DML/redo/undo impact |

Use sample reports:

* `awrrpt-bank-02-io-full-scan.html`: object read pressure
* `awrrpt-bank-03-locking.html`: row lock object evidence
* `awrrpt-bank-05-commit-redo.html`: DML and redo-related objects

Trainer delivery:

"Segment Statistics connects SQL symptoms to physical database objects. This is where vague SQL evidence becomes table/index evidence."

Real-life example:

```text
SQL by Reads points to a statement, and Segment Statistics shows `TRANSACTIONS_2026_Q2` as the top physical-read segment.
This can happen when a report misses partition pruning and scans the current quarter transaction partition repeatedly.
```

---

# Slide 35 - Dictionary Cache Statistics (10:39 - 10:40)

## Slide Content

Dictionary Cache Statistics answers:

```text
Was Oracle repeatedly looking up object metadata?
```

Read when:

* hard parse is high
* recursive SQL is high
* object invalidation is suspected
* many DDL or stats operations occurred
* library cache symptoms appear

Interpretation:

| Pattern | Meaning |
| ------- | ------- |
| low get hit ratio for key dictionary areas | metadata lookup pressure |
| many dictionary gets with hard parse | parse-related symptom |
| dictionary pressure after deployment | object churn or invalidation possible |

Practical guidance:

```text
Dictionary cache symptoms usually support a parse/library-cache diagnosis.
They are rarely the first section to read.
```

Use sample report:

```text
02-Day/reports/awrrpt-bank-04-hard-parse.html
```

Real-life example:

```text
During a deployment window, many packages are recompiled and application sessions reconnect.
Dictionary Cache Statistics can show extra metadata lookup pressure caused by object invalidation and reparsing.
```

---

# Slide 36 - Library Cache Statistics (10:40 - 10:41)

## Slide Content

Library Cache Statistics answers:

```text
Did SQL and PL/SQL cursor sharing become inefficient?
```

Read when:

* parse time is high
* hard parse is high
* SQL by Parse Calls is high
* SQL by Version Count is high
* library cache waits appear

Interpretation:

| Signal | Meaning |
| ------ | ------- |
| low library cache hit percentage | cursor reuse problem possible |
| high reloads | aged out or invalidated objects |
| high invalidations | object/stats/DDL churn |
| mutex/cursor waits | concurrency around shared cursors |

Use sample report:

```text
02-Day/reports/awrrpt-bank-04-hard-parse.html
```

Production fixes to consider only after validation:

* bind variables
* reduce literal SQL
* avoid unnecessary DDL during peak
* stabilize object invalidations
* review session cursor caching
* fix application connection/session behavior

Real-life example:

```text
A release process gathers stats and recompiles objects during online peak.
Library Cache Statistics shows reloads and invalidations because shared SQL and PL/SQL objects keep being invalidated while users are active.
```

---

# Slide 37 - Initialization Parameters (10:41 - 10:42)

## Slide Content

Initialization Parameters answers:

```text
What database settings were active during the report?
```

Use it to verify context, not to guess first fixes.

Read when:

* optimizer behavior changed
* memory sizing is suspected
* parallel query appears unexpectedly
* cursor sharing or adaptive settings matter
* undo or redo behavior needs context

Useful parameters:

| Parameter | Why It Matters |
| --------- | -------------- |
| `optimizer_features_enable` | optimizer behavior baseline |
| `cursor_sharing` | literal SQL handling |
| `pga_aggregate_target` | workarea/sort/hash memory |
| `sga_target` / `memory_target` | cache/shared memory context |
| `db_file_multiblock_read_count` | scan behavior context |
| `parallel_degree_policy` | unexpected parallelism |
| `undo_retention` | undo/read consistency context |

Real-life example:

```text
After migration, reports suddenly run in parallel and consume CPU during OLTP hours.
Initialization Parameters helps confirm whether parallel policy or optimizer-related settings changed between the baseline and incident window.
```

Trainer warning:

"Parameter changes are high-risk production changes. AWR can justify investigation, but it rarely justifies an immediate parameter change by itself."

---

# Slide 38 - Active Session History (ASH) Report (10:42 - 10:43)

## Slide Content

ASH answers:

```text
Which active sessions were doing what during the problem time?
```

Use ASH after AWR when you need:

* SQL_ID by sample count
* wait class by time slot
* blocking session evidence
* service/module/action evidence
* program or machine evidence
* minute-by-minute incident shape

Simple live ASH summary:

```sql
SELECT NVL(wait_class,'CPU') AS wait_class,
       COUNT(*) AS ash_samples
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (30/1440)
GROUP BY NVL(wait_class,'CPU')
ORDER BY ash_samples DESC;
```

ASH by SQL and event:

```sql
SELECT sql_id,
       NVL(wait_class,'CPU') AS wait_class,
       NVL(event,'ON CPU') AS event,
       COUNT(*) AS ash_samples
FROM v$active_session_history
WHERE sample_time >= SYSDATE - (30/1440)
AND sql_id IS NOT NULL
GROUP BY sql_id,
         NVL(wait_class,'CPU'),
         NVL(event,'ON CPU')
ORDER BY ash_samples DESC
FETCH FIRST 10 ROWS ONLY;
```

Historical ASH for the AWR snapshot window:

```sql
SELECT h.sql_id,
       NVL(h.wait_class,'CPU') AS wait_class,
       NVL(h.event,'ON CPU') AS event,
       COUNT(*) AS ash_samples
FROM dba_hist_active_sess_history h
WHERE h.dbid = &dbid
AND h.instance_number = &inst_num
AND h.snap_id BETWEEN &begin_snap AND &end_snap
AND h.sql_id IS NOT NULL
GROUP BY h.sql_id,
         NVL(h.wait_class,'CPU'),
         NVL(h.event,'ON CPU')
ORDER BY ash_samples DESC
FETCH FIRST 10 ROWS ONLY;
```

Real-life example:

```text
AWR shows Application waits but not the exact blocker story.
ASH shows session 321 from the loan module blocking many teller sessions for 12 minutes on the same SQL_ID and object.
```

Trainer delivery:

"AWR says what consumed time in the interval. ASH says who was active, when, and on what."

---

# Slide 39 - ADDM Reports (10:43 - 10:44)

## Slide Content

ADDM answers:

```text
What does Oracle think were the biggest findings in this AWR window?
```

Read ADDM after your own AWR review.

For each finding, capture:

| Item | Question |
| ---- | -------- |
| Finding | what problem did ADDM identify? |
| Impact | how much DB Time is involved? |
| Recommendation | what does Oracle suggest? |
| Rationale | why does it suggest that? |
| SQL/Object | what exact evidence is referenced? |
| Validation | where is the same evidence in AWR? |

Interpretation:

```text
ADDM is prioritization, not permission.
The DBA still validates before changing SQL, indexes, memory, storage, or application behavior.
```

Use sample reports:

* `awrrpt-bank-01-cpu-sql.html`: high-load SQL direction
* `awrrpt-bank-02-io-full-scan.html`: I/O and full-scan direction
* `awrrpt-bank-03-locking.html`: blocking direction
* `awrrpt-bank-05-commit-redo.html`: commit latency direction

Real-life example:

```text
ADDM recommends SQL tuning for one high-load SQL_ID.
Before accepting it, the DBA confirms the same SQL_ID appears in AWR SQL by Elapsed Time, CPU Time, and Gets, then checks the execution plan.
```

---

# Slide 40 - Cross-Section Diagnosis Patterns (10:44 - 10:45)

## Slide Content

CPU-bound SQL pattern:

```text
Report Summary: high DB Time and high DB CPU
Wait Events: DB CPU dominates
SQL Statistics: same SQL high in CPU Time and Gets
Segment Statistics: related table/index high in logical reads
Next: DBMS_XPLAN and SQL tuning
```

I/O-bound scan pattern:

```text
Wait Events: User I/O dominates
SQL Statistics: SQL high in Reads and User I/O Wait Time
IO Stats: tablespace/file read volume visible
Segment Statistics: table high in physical reads/table scans
Next: plan, predicates, partition pruning, batch scheduling
```

Locking pattern:

```text
Wait Events: enq: TX - row lock contention
Foreground Wait Class: Application dominates
ASH: blocker/waiter sessions visible
Segment Statistics: row lock waits on hot object
Next: transaction design and blocker handling
```

Commit latency pattern:

```text
Wait Events: log file sync
Instance Activity: high user commits and redo size
Service Wait Class: one service high in Commit
SQL Statistics: DML SQL high by executions
Next: commit batching, redo latency, Data Guard path
```

Hard parse pattern:

```text
Time Model: parse and hard parse time
Wait Events: library cache or cursor waits
SQL Statistics: Parse Calls and Version Count high
Library Cache: low hit/reloads/invalidations
Next: bind variables, cursor reuse, invalidation review
```

---

# Lab Task - AWR Evidence Table (10:43 - 10:45)

Participants fill this from the generated `awr_day2_morning.html` and the sample reports.

| AWR Section | What You Found | Likely Meaning | Next Check |
| ----------- | -------------- | -------------- | ---------- |
| Main Report | | section map | choose evidence path |
| Report Summary | | window and DB Time | compare baseline |
| Time Model | | execution vs parse vs PL/SQL | SQL or parse sections |
| Foreground Wait Class | | CPU/I/O/commit/lock direction | detailed wait events |
| Foreground Wait Events | | top event names | SQL, ASH, object evidence |
| Service Statistics | | affected application service | service wait class |
| SQL by Elapsed | | user-impact SQL | plan and predicates |
| SQL by CPU | | CPU-heavy SQL | gets, executions, plan |
| SQL by User I/O | | I/O-waiting SQL | reads, IO stats, segments |
| SQL by Gets | | logical read pressure | access path |
| SQL by Reads | | physical I/O driver | full scans, large objects |
| SQL by Executions | | application loop | parse calls, app logic |
| SQL by Parse Calls | | parse pressure | bind/cursor reuse |
| SQL by Version Count | | child cursor pressure | `V$SQL_SHARED_CURSOR` |
| Instance Activity | | commits/parses/reads/redo rates | validate symptom |
| IO Stats | | file/tablespace I/O | map to object and SQL |
| Segment Stats | | hot object | table/index/partition design |
| Library Cache | | cursor/shared pool health | parse sections |
| ASH Report | | active sessions and timing | blockers/modules/SQL IDs |
| ADDM Reports | | Oracle findings | verify in AWR |

---

# Guided Answer Key - AWR Interpretation (10:43 - 10:45)

The exact numbers will vary by machine. The correct learning outcome is the reasoning pattern.

| Scenario | Correct Reading Pattern |
| -------- | ----------------------- |
| CPU SQL | DB CPU high, SQL by CPU and Gets identify SQL_ID, plan shows expensive access path |
| I/O full scan | User I/O high, SQL by Reads and Segment Physical Reads point to scanned object |
| Locking | Application wait high, `enq: TX` event, ASH blocker evidence, row-lock segment |
| Hard parse | parse time, library cache waits, SQL by Parse Calls, Version Count |
| Commit redo | `log file sync`, high commits, redo pressure, service commit waits |

Strong trainee answer:

```text
The report shows the direction first.
Then I connect wait class, SQL_ID, service/module, object, and plan evidence.
Only after that do I recommend a fix.
```

Weak trainee answer to correct:

```text
AWR shows I/O, so storage is slow.
```

Trainer correction:

```text
I/O waits may be caused by bad SQL reading too much.
First identify the SQL, plan, and segment before blaming storage.
```

---

# Slide 41 - Connect AWR To Day 1 (10:44 - 10:45)

## Slide Content

Once AWR identifies SQL:

```text
AWR SQL_ID
  -> DBMS_XPLAN.DISPLAY_AWR or DISPLAY_CURSOR
  -> predicates
  -> E-Rows vs A-Rows
  -> access path
  -> fix
  -> validate
```

Useful follow-up query:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_AWR(
    sql_id => '&&sql_id_from_awr',
    format => 'ALL +PREDICATE +PEEKED_BINDS'
  )
);
```

If the cursor is still in memory and you reran the SQL:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    '&&sql_id_from_awr',
    NULL,
    'ALLSTATS LAST +PREDICATE +PEEKED_BINDS'
  )
);
```

Trainer note:

If the cursor aged out, use the plan shown in AWR as evidence and rerun the SQL with a controlled comment to capture a fresh runtime plan.

---

# SLOT 2 - ADDM: AUTOMATIC DATABASE DIAGNOSTIC MONITOR (10:45 - 12:00)

## 10:45 AM - 12:00 PM

# SECTION 5 - ADDM MENTAL MODEL (10:45 - 11:00)

# Slide 42 - AWR vs ADDM (10:45 - 10:52)

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

# Slide 43 - ADDM Finding Structure (10:52 - 11:00)

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

# Slide 44 - Use Same Snapshot Window (11:00 - 11:03)

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

# Step 1 - Confirm Snapshot IDs (11:03 - 11:06)

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

# Step 2 - Generate ADDM Report (11:06 - 11:18)

Recommended reliable method:

```sql
@$ORACLE_HOME/rdbms/admin/addmrpt.sql
```

When prompted, use:

```text
Begin snapshot: &begin_snap
End snapshot:   &end_snap
Report name:    /tmp/day2_awr_reports/addm_day2_morning.txt
```

Trainer note:

The Oracle-supplied script is the safest cross-environment approach for 19c training because it handles the internal ADDM task creation.

---

# Step 3 - If ADDM Has No Major Finding (11:18 - 11:25)

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

# Slide 45 - ADDM Reading Workflow (11:25 - 11:30)

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

# Slide 46 - Impact Percentage (11:30 - 11:34)

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

# Slide 47 - Example Interpretation: High SQL Load (11:34 - 11:38)

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

# Slide 48 - Example Interpretation: I/O (11:38 - 11:42)

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

# Slide 49 - Example Interpretation: Commit Latency (11:42 - 11:46)

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

# Slide 50 - Example Interpretation: Memory (11:46 - 11:48)

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

# Lab Task - ADDM Evidence Table (11:48 - 11:50)

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

# Guided Answer Key - ADDM Interpretation (11:48 - 11:50)

Use this after participants complete the ADDM evidence table.

| ADDM Finding Type | What Trainees Should Say | Validation Evidence |
| ----------------- | ------------------------ | ------------------- |
| High-load SQL | one or more SQL statements consumed significant DB time | AWR SQL by Elapsed/CPU/Gets and DBMS_XPLAN |
| I/O throughput or reads | the database spent time reading blocks | SQL by Reads, Segment Statistics, execution plan |
| Commit latency | sessions waited for commit acknowledgement | `log file sync`, commit workload, application transaction design |
| Memory pressure | sorts/hash joins/parsing may be causing pressure | PGA stats, temp usage, SQL plans, ADDM memory advice |
| No significant finding | workload was too short or not intense enough | rerun with larger loop count or explain that no-finding is valid evidence |

Strong trainee answer:

```text
ADDM recommends an investigation direction.
Before applying the recommendation, I need to confirm the same SQL/wait/object in AWR and inspect the execution plan or system evidence.
```

Trainer reminder:

```text
ADDM impact percentage helps prioritize.
It does not approve the change.
```

---

# SECTION 8 - VALIDATION DECISION TREE (11:50 - 12:00)

# Slide 51 - Do Not Apply Blindly (11:50 - 11:54)

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

# Slide 52 - Professional Validation Workflow (11:54 - 11:58)

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

# FINAL MORNING SUMMARY (11:58 - 12:00)

## What Trainees Should Now Be Able To Do

* create an AWR snapshot window around a test workload
* generate AWR HTML/text report
* identify top waits and top SQL
* connect AWR SQL back to execution-plan analysis
* generate ADDM for the same window
* interpret findings, impact, and recommendations
* explain why advisor recommendations require validation

---

# TRANSITION TO DAY 2 SECOND HALF (11:58 - 12:00)

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
