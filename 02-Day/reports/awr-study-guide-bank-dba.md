# AWR Learning Guide for a Banking DBA

This folder contains one tiny sample AWR report and six mock production-style reports. The mock reports are not copied from a real bank; the values are generated for training, but the symptoms, section names, and troubleshooting flow are realistic.

## Suggested reading order

1. `awrrpt-sample.html` - see the original very small report.
2. `awrrpt-bank-00-baseline.html` - learn what healthy OLTP can look like.
3. `awrrpt-bank-01-cpu-sql.html` - CPU-bound SQL tuning case.
4. `awrrpt-bank-02-io-full-scan.html` - physical I/O and full scan case.
5. `awrrpt-bank-03-locking.html` - blocking and application row lock case.
6. `awrrpt-bank-04-hard-parse.html` - hard parse and library cache case.
7. `awrrpt-bank-05-commit-redo.html` - commit latency and redo case.

Open `awr-training-index.html` first if you want one page with links.

## Beginner level: what AWR is

AWR means Automatic Workload Repository. Oracle periodically takes snapshots of performance counters. An AWR report compares two snapshots and shows what changed during that interval.

The most important beginner idea is DB Time.

DB Time = time foreground database sessions spent working or waiting inside the database.

If 100 sessions each spend 1 minute in the database during a 1-minute report, DB Time is 100 minutes. This is why DB Time can be much larger than elapsed wall-clock time.

Average Active Sessions, or AAS, is:

DB Time in seconds / elapsed seconds

If a 60 minute report has 4,920 minutes of DB Time, AAS is 82. That means, on average, 82 sessions were active inside the database at any moment.

## Your first AWR reading checklist

1. Confirm scope: database, instance, PDB, begin snap, end snap, elapsed time, and whether it covers the user complaint window.
2. Read DB Time and AAS. Compare AAS to CPU count.
3. Read Top Foreground Events. Ask: CPU, I/O, locks, commit, cluster, parse, network, or something else?
4. Read Time Model. Ask whether time is SQL execution, parsing, PL/SQL, connection management, or hard parse.
5. Read SQL ordered by Elapsed Time, CPU Time, Gets, Reads, Executions, and Parse Calls.
6. Read Segment Statistics to connect SQL pressure to tables and indexes.
7. Read ASH sections to see which sessions, modules, SQL IDs, and time windows created the load.
8. Read ADDM findings, but verify them against the AWR sections.
9. Decide whether SQL Tuning Advisor is appropriate. It is best for bad SQL access paths, not for every bottleneck.

## Key terms

DB Time: Total foreground time spent in database calls. This is your main budget.

DB CPU: Part of DB Time spent running on CPU. High DB CPU usually means expensive SQL, parsing, PL/SQL, or simply more workload than CPU capacity.

Elapsed Time: Wall-clock duration between begin and end snapshot.

AAS: Average Active Sessions. AAS near or above CPU count with high DB CPU means CPU pressure.

Load Profile: Per-second and per-transaction workload rates. Look at executes, parses, hard parses, logical reads, physical reads, redo size, user commits, and transactions.

Logical Reads / Buffer Gets: Blocks read from Oracle buffer cache. High logical reads usually mean SQL is doing too much work, even if physical I/O is low.

Physical Reads: Blocks read from storage. High physical reads point to full scans, poor caching, missing partition pruning, or insufficient memory for the workload.

DB file sequential read: Usually single-block index/table lookup I/O. Not automatically bad; bad when it dominates DB Time or average wait is high.

DB file scattered read: Usually multiblock read from full scan or index fast full scan.

Direct path read: Reads that bypass buffer cache, common for large scans, parallel query, or serial direct path reads.

Log file sync: Foreground session waiting for commit to be durable. Often caused by too many commits or slow redo storage.

Log file parallel write: LGWR writing redo. If this is slow, log file sync often becomes slow too.

Enq: TX - row lock contention: A session waits because another transaction holds a row lock. Often application design, missing commit, or hot row.

Library cache: mutex X / cursor: pin S wait on X: Cursor/library cache contention. Often hard parse, many child cursors, invalidations, or literal SQL.

Parse Calls: SQL parse attempts. Some parsing is normal.

Hard Parses: Parses that require optimization and new cursor work. High hard parse rate is expensive and can cause shared pool contention.

Executions: Number of times a SQL ran. A SQL can be bad because it is slow once, or because it is cheap but runs millions of times.

Rows per Exec: Helps identify whether SQL processes too many rows or returns unexpected cardinality.

SQL ordered by Elapsed Time: Best first stop for user-visible slowness.

SQL ordered by CPU Time: Best for CPU-bound reports.

SQL ordered by Gets: Best for inefficient SQL doing too many logical reads.

SQL ordered by Reads: Best for I/O-bound reports.

SQL ordered by Executions: Best for chatty applications and small SQL called too often.

SQL ordered by Parse Calls: Best for hard parse/literal SQL problems.

Segments by Logical Reads / Physical Reads / Row Lock Waits: Connects workload to objects. This helps you say which table/index is hot.

ADDM: Automatic Database Diagnostic Monitor. It analyzes AWR data and points to likely findings and impact.

SQL Tuning Advisor: Tool that analyzes one or more SQL statements and may recommend statistics, indexes, SQL profiles, SQL plan baselines, or rewrites.

## Intermediate level: map symptom to section

CPU problem:

- Top event is DB CPU.
- Time Model shows DB CPU and sql execute elapsed time high.
- SQL ordered by CPU Time and Gets identifies SQL IDs.
- Fix: reduce logical reads, improve joins/access paths, update stats, create targeted indexes, rewrite SQL, or use summaries.

I/O problem:

- User I/O wait class dominates.
- Top events include db file scattered read, db file sequential read, or direct path read.
- SQL ordered by Reads and Segments by Physical Reads identify objects.
- Fix: partition pruning, selective indexes, SQL rewrite, cache strategy, reporting replica, storage investigation.

Locking problem:

- Application wait class dominates.
- Top event includes enq: TX - row lock contention.
- ASH shows blocking sessions or hot SQL.
- Segments by Row Lock Waits identifies object.
- Fix: transaction design, shorter transactions, avoid hot rows, queue design, SKIP LOCKED where appropriate.

Hard parse problem:

- Load Profile shows high hard parses per second.
- Time Model shows parse time and hard parse elapsed time.
- Top waits include library cache mutex or cursor pin waits.
- SQL ordered by Parse Calls and Version Count are important.
- Fix: bind variables, cursor reuse, reduce invalidations, review session cached cursors.

Commit/redo problem:

- Commit wait class dominates.
- Top event is log file sync.
- Background/System I/O may show log file parallel write.
- Load Profile shows high commits per second and redo size.
- Fix: commit batching, redo storage latency, Data Guard sync transport review, avoid row-by-row commits.

## Advanced level: do not stop at the first symptom

AWR gives system-level evidence, but SQL tuning needs a chain of proof:

1. Business symptom: which banking function was slow?
2. Time window: does the AWR snapshot cover that exact interval?
3. Dominant DB Time consumer: CPU, I/O, commit, lock, parse, cluster, or network?
4. Responsible module/service: internet banking, card auth, AML batch, settlement, fraud engine.
5. Responsible SQL ID or object.
6. Execution plan and row estimates from DBMS_XPLAN.DISPLAY_AWR or SQL Monitor.
7. Tuning action tested in non-production.
8. Before/after comparison using AWR, ASH, SQL stats, and business response time.

## ADDM and SQL Tuning Advisor workflow

Use ADDM first when you do not know the bottleneck. ADDM is good at saying where DB Time went.

Use SQL Tuning Advisor when a specific SQL ID consumes meaningful DB Time, CPU, I/O, or buffer gets.

Do not expect SQL Tuning Advisor to fix:

- Row lock contention caused by application transaction design.
- Commit latency caused by row-by-row commits or slow redo storage.
- Network waits caused by client fetch size or application behavior.
- CPU shortage caused by an intentional workload surge unless a SQL statement is inefficient.

Typical command flow in a real system:

```sql
-- Find report window.
SELECT snap_id, begin_interval_time, end_interval_time
FROM dba_hist_snapshot
WHERE begin_interval_time >= SYSDATE - 1
ORDER BY snap_id;

-- Generate AWR text or HTML from SQL*Plus.
@$ORACLE_HOME/rdbms/admin/awrrpt.sql

-- Display a historical execution plan for a SQL ID.
SELECT * FROM TABLE(
  dbms_xplan.display_awr(sql_id => '9m8v6q3k2b1fa', format => 'ALLSTATS LAST +PEEKED_BINDS')
);

-- Create SQL Tuning Advisor task for one SQL ID.
DECLARE
  l_task VARCHAR2(128);
BEGIN
  l_task := dbms_sqltune.create_tuning_task(
    sql_id      => '9m8v6q3k2b1fa',
    scope       => dbms_sqltune.scope_comprehensive,
    time_limit  => 120,
    task_name   => 'tune_9m8v6q3k2b1fa');
  dbms_sqltune.execute_tuning_task(task_name => 'tune_9m8v6q3k2b1fa');
END;
/

SELECT dbms_sqltune.report_tuning_task('tune_9m8v6q3k2b1fa') FROM dual;
```

## Bank DBA mental model

For a bank, never tune only for speed. Tune for correctness, recoverability, auditability, and predictable latency.

- A commit batching change must preserve restartability and no-duplicate-posting rules.
- An index on a hot payment table must be tested for DML overhead.
- A SQL profile must be tested against bind selectivity and plan stability.
- A reporting query should not steal capacity from card authorization or payment posting.
- Killing a blocker in settlement may be riskier than waiting unless the business owner approves.

## Practice exercise

For each mock report, write one page with:

1. Snapshot interval and AAS.
2. Top wait class and top event.
3. Top SQL ID and why it is suspicious.
4. Top object/segment.
5. What ADDM would say.
6. Whether SQL Tuning Advisor is useful.
7. Your production-safe action plan.
