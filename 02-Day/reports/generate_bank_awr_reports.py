from __future__ import annotations

from html import escape
from pathlib import Path
from textwrap import dedent


OUT = Path(__file__).resolve().parent


CSS = """
body.awr {font: 10pt Arial,Helvetica,Geneva,sans-serif;color:black;background:white;margin:16px;}
pre.awr {font:8pt Courier;color:black;background:white;white-space:pre-wrap;}
h1.awr {font:bold 20pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:white;border-bottom:1px solid #cccc99;margin:0 0 8px 0;padding:0;}
h2.awr {font:bold 18pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:white;margin:18px 0 4px 0;}
h3.awr {font:bold 15pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:white;margin:14px 0 4px 0;}
h4.awr {font:bold 11pt Arial,Helvetica,Geneva,sans-serif;color:#333;margin:10px 0 3px 0;}
li.awr {font: 8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:white;margin-bottom:2px;}
th.awrnobg {font:bold 8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:white;padding:3px 6px;}
th.awrbg {font:bold 8pt Arial,Helvetica,Geneva,sans-serif;color:white;background:#0066CC;padding:3px 6px;text-align:left;}
td.awrnc {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:white;vertical-align:top;padding:3px 6px;}
td.awrc {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:#FFFFCC;vertical-align:top;padding:3px 6px;}
td.num {text-align:right;}
table.tdiff {border-collapse:collapse;margin:4px 0 10px 0;}
table.tdiff td, table.tdiff th {border:1px solid #d0d0b8;}
a.awr {font:bold 8pt Arial,Helvetica,sans-serif;color:#663300;vertical-align:top;}
.note {max-width:980px;border-left:4px solid #0066CC;background:#f5f9ff;padding:8px 10px;margin:8px 0 12px 0;font-size:9pt;line-height:1.35;}
.warning {max-width:980px;border-left:4px solid #b45309;background:#fff7ed;padding:8px 10px;margin:8px 0 12px 0;font-size:9pt;line-height:1.35;}
.finding {max-width:980px;border-left:4px solid #7c3aed;background:#f7f3ff;padding:8px 10px;margin:8px 0 12px 0;font-size:9pt;line-height:1.35;}
.small {font-size:8pt;color:#444;}
.toc li {margin-bottom:4px;}
"""


SCENARIOS = [
    {
        "file": "awrrpt-bank-00-baseline.html",
        "snap": (4102, 4103),
        "title": "Healthy OLTP Baseline",
        "summary": "Normal weekday payment, account inquiry, card authorization, and digital banking traffic. Use this report to learn what a balanced banking OLTP AWR looks like before diagnosing a problem.",
        "db_time_min": 1260,
        "elapsed_min": 60,
        "sessions": (1180, 1245),
        "cursors": (9.6, 10.1),
        "host": ("bkdb-prd1-rac1", 48, 24, 384),
        "load": [
            ("DB Time(s)", "21.0", "0.084", "0.012", "0.018"),
            ("DB CPU(s)", "15.9", "0.064", "0.009", "0.014"),
            ("Redo size (bytes)", "26,420,000", "105,680", "", ""),
            ("Logical read (blocks)", "1,850,000", "7,400", "", ""),
            ("Physical read (blocks)", "16,800", "67", "", ""),
            ("Physical write (blocks)", "9,900", "40", "", ""),
            ("User calls", "1,180", "4.7", "", ""),
            ("Parses (SQL)", "3,900", "15.6", "", ""),
            ("Hard parses (SQL)", "42", "0.17", "", ""),
            ("Executes (SQL)", "104,000", "416", "", ""),
            ("Transactions", "250", "", "", ""),
        ],
        "wait_events": [
            ("DB CPU", "", "57,240", "", "75.7", ""),
            ("db file sequential read", "18,700,000", "5,610", "0.30 ms", "7.4", "User I/O"),
            ("log file sync", "896,000", "3,852", "4.30 ms", "5.1", "Commit"),
            ("gc cr block 2-way", "2,560,000", "2,816", "1.10 ms", "3.7", "Cluster"),
            ("db file scattered read", "480,000", "1,440", "3.00 ms", "1.9", "User I/O"),
            ("SQL*Net more data to client", "3,600,000", "1,080", "0.30 ms", "1.4", "Network"),
            ("enq: TX - row lock contention", "6,100", "915", "150 ms", "1.2", "Application"),
        ],
        "wait_classes": [
            ("DB CPU", "", "57,240", "", "75.7", "15.9"),
            ("User I/O", "19,180,000", "7,050", "0.37 ms", "9.3", "2.0"),
            ("Commit", "896,000", "3,852", "4.30 ms", "5.1", "1.1"),
            ("Cluster", "2,560,000", "2,816", "1.10 ms", "3.7", "0.8"),
            ("Application", "6,100", "915", "150 ms", "1.2", "0.3"),
            ("Network", "3,900,000", "1,170", "0.30 ms", "1.5", "0.3"),
        ],
        "time_model": [
            ("DB CPU", "57,240", "75.7"),
            ("sql execute elapsed time", "66,840", "88.4"),
            ("PL/SQL execution elapsed time", "9,870", "13.1"),
            ("parse time elapsed", "1,560", "2.1"),
            ("hard parse elapsed time", "240", "0.3"),
            ("connection management call elapsed time", "120", "0.2"),
            ("DB time", "75,600", ""),
        ],
        "sql": [
            ("8h3kczwq0n2ua", "Account balance lookup by account number", "ACCT_SVC", "BANKPDB", "4,320", "18,200,000", "1,200", "980", "9,600,000", "SELECT current_balance FROM core_accounts WHERE account_no = :B1"),
            ("cz7mrb1f0a21q", "Card authorization limit check", "CARD_AUTH", "BANKPDB", "3,780", "25,600,000", "2,040", "420", "14,080,000", "SELECT available_limit FROM card_limits WHERE card_no = :B1 AND status = 'A'"),
            ("5w4h9fg0u9sp2", "Recent payment list for mobile app", "MOBILE_API", "BANKPDB", "2,760", "1,920,000", "2,210", "1,300", "5,300,000", "SELECT * FROM payments WHERE customer_id = :B1 ORDER BY payment_ts DESC FETCH FIRST 20 ROWS ONLY"),
            ("b1x7qpt53mnd8", "Fraud rules package", "FRAUD_ENGINE", "BANKPDB", "2,240", "640,000", "1,780", "220", "3,100,000", "BEGIN fraud_pkg.score_txn(:B1,:B2,:B3); END;"),
        ],
        "segments": [
            ("CORE", "CORE_ACCOUNTS_PK", "INDEX", "18,900,000", "120,000", "0", "0"),
            ("CARDS", "CARD_LIMITS_IX1", "INDEX", "14,200,000", "80,000", "0", "0"),
            ("PAYMENTS", "PAYMENTS_CUST_TS_IX", "INDEX", "5,900,000", "460,000", "0", "0"),
            ("PAYMENTS", "PAYMENTS", "TABLE", "4,800,000", "950,000", "12,000", "180"),
        ],
        "ash": [
            ("15:00-15:10", "DB CPU", "CARD_AUTH", "cz7mrb1f0a21q", "Normal card authorization peak"),
            ("15:10-15:20", "db file sequential read", "ACCT_SVC", "8h3kczwq0n2ua", "Index lookups, acceptable latency"),
            ("15:20-15:30", "log file sync", "PAYMENT_API", "5w4h9fg0u9sp2", "Commit cost visible but not dominant"),
        ],
        "addm": [
            ("No critical findings", "Database time is spread across CPU, commit, and normal index I/O. No single bottleneck dominates.", "Keep this report as your baseline. Compare bad reports against its DB Time per second, top waits, hard parse rate, and top SQL shape.", "Low"),
        ],
        "advisor": [
            ("Review top SQL plans", "No emergency action. Capture SQL plan baselines for the four critical OLTP SQL statements before release windows.", "Prevent plan instability during stats refresh or application deployment."),
        ],
        "lesson": "Healthy does not mean zero waits. In a bank OLTP system, some sequential reads, log file sync, RAC block traffic, and network waits are normal. The question is whether one class consumes DB Time abnormally or whether one SQL ID explains a large share of load.",
    },
    {
        "file": "awrrpt-bank-01-cpu-sql.html",
        "snap": (4210, 4211),
        "title": "CPU Bound Due to Expensive SQL",
        "summary": "Month-end statement preview caused one SQL to repeatedly scan and aggregate account history. Users report slow internet banking and CPU saturation.",
        "db_time_min": 4920,
        "elapsed_min": 60,
        "sessions": (1520, 1685),
        "cursors": (13.2, 14.9),
        "host": ("bkdb-prd1-rac1", 48, 24, 384),
        "load": [
            ("DB Time(s)", "82.0", "0.246", "0.054", "0.072"),
            ("DB CPU(s)", "73.5", "0.221", "0.049", "0.065"),
            ("Redo size (bytes)", "18,200,000", "54,600", "", ""),
            ("Logical read (blocks)", "9,850,000", "29,550", "", ""),
            ("Physical read (blocks)", "42,000", "126", "", ""),
            ("Physical write (blocks)", "8,100", "24", "", ""),
            ("User calls", "1,140", "3.4", "", ""),
            ("Parses (SQL)", "4,400", "13.2", "", ""),
            ("Hard parses (SQL)", "55", "0.16", "", ""),
            ("Executes (SQL)", "91,000", "273", "", ""),
            ("Transactions", "333", "", "", ""),
        ],
        "wait_events": [
            ("DB CPU", "", "264,600", "", "89.6", ""),
            ("resmgr:cpu quantum", "1,780,000", "12,460", "7.00 ms", "4.2", "Scheduler"),
            ("db file sequential read", "21,200,000", "7,420", "0.35 ms", "2.5", "User I/O"),
            ("log file sync", "650,000", "2,860", "4.40 ms", "1.0", "Commit"),
            ("latch: cache buffers chains", "92,000", "1,840", "20.0 ms", "0.6", "Concurrency"),
            ("gc current block 2-way", "980,000", "1,470", "1.50 ms", "0.5", "Cluster"),
        ],
        "wait_classes": [
            ("DB CPU", "", "264,600", "", "89.6", "73.5"),
            ("Scheduler", "1,780,000", "12,460", "7.00 ms", "4.2", "3.5"),
            ("User I/O", "21,300,000", "7,560", "0.36 ms", "2.6", "2.1"),
            ("Commit", "650,000", "2,860", "4.40 ms", "1.0", "0.8"),
            ("Concurrency", "92,000", "1,840", "20.0 ms", "0.6", "0.5"),
            ("Cluster", "980,000", "1,470", "1.50 ms", "0.5", "0.4"),
        ],
        "time_model": [
            ("DB CPU", "264,600", "89.6"),
            ("sql execute elapsed time", "286,900", "97.1"),
            ("PL/SQL execution elapsed time", "18,400", "6.2"),
            ("parse time elapsed", "2,100", "0.7"),
            ("hard parse elapsed time", "310", "0.1"),
            ("DB time", "295,200", ""),
        ],
        "sql": [
            ("9m8v6q3k2b1fa", "Month-end statement preview aggregation", "IBANK_WEB", "BANKPDB", "142,800", "19,200", "137,400", "2,100", "21,800,000,000", "SELECT txn_type, SUM(amount) FROM acct_txn_history WHERE customer_id = :B1 AND txn_date BETWEEN :B2 AND :B3 GROUP BY txn_type"),
            ("47k1rj6g8z2px", "Dashboard portfolio summary", "RM_PORTAL", "BANKPDB", "38,400", "86,000", "34,200", "1,600", "5,400,000,000", "SELECT product_code, SUM(balance) FROM customer_positions WHERE rm_id = :B1 GROUP BY product_code"),
            ("cz7mrb1f0a21q", "Card authorization limit check", "CARD_AUTH", "BANKPDB", "7,900", "26,100,000", "5,000", "880", "15,300,000", "SELECT available_limit FROM card_limits WHERE card_no = :B1 AND status = 'A'"),
            ("8h3kczwq0n2ua", "Account balance lookup", "ACCT_SVC", "BANKPDB", "6,400", "19,400,000", "2,200", "1,100", "10,100,000", "SELECT current_balance FROM core_accounts WHERE account_no = :B1"),
        ],
        "segments": [
            ("ACCT", "ACCT_TXN_HISTORY", "TABLE", "20,800,000,000", "28,600,000", "0", "0"),
            ("ACCT", "ACCT_TXN_HIST_CUST_DT_IX", "INDEX", "9,200,000,000", "6,100,000", "0", "0"),
            ("CRM", "CUSTOMER_POSITIONS", "TABLE", "5,800,000,000", "8,400,000", "0", "0"),
            ("CORE", "CORE_ACCOUNTS_PK", "INDEX", "10,100,000", "110,000", "0", "0"),
        ],
        "ash": [
            ("20:00-20:10", "DB CPU", "IBANK_WEB", "9m8v6q3k2b1fa", "Statement preview release begins"),
            ("20:10-20:20", "DB CPU", "IBANK_WEB", "9m8v6q3k2b1fa", "AAS exceeds CPU cores; user response time degrades"),
            ("20:20-20:30", "resmgr:cpu quantum", "IBANK_WEB", "9m8v6q3k2b1fa", "Sessions waiting to be scheduled on CPU"),
            ("20:30-20:40", "latch: cache buffers chains", "IBANK_WEB", "9m8v6q3k2b1fa", "Hot buffer access from repeated logical reads"),
        ],
        "addm": [
            ("SQL statements consuming significant database time", "SQL ID 9m8v6q3k2b1fa is responsible for 48.4% of DB Time and 52.0% of DB CPU.", "Run SQL Tuning Advisor for SQL ID 9m8v6q3k2b1fa. Review access path, grouping strategy, and whether a summary table or covering index is appropriate.", "Very high"),
            ("CPU bottleneck", "Average Active Sessions on CPU is 73.5 on a 48 CPU host, so sessions queue for CPU.", "Fix the high logical-read SQL before adding CPU. Extra CPU would hide the problem temporarily.", "High"),
        ],
        "advisor": [
            ("Create or validate composite index", "Consider an index on ACCT_TXN_HISTORY(customer_id, txn_date, txn_type) if the predicate is selective and DML overhead is acceptable.", "Lower buffer gets by accessing only the customer's date range."),
            ("SQL profile or plan baseline", "If optimizer estimates are wrong after stats refresh, test an accepted SQL profile or baseline for the known good plan.", "Stabilize execution plan during month-end."),
            ("Rewrite/reporting design", "For repeated statement previews, pre-aggregate by customer/month into a statement summary table.", "Avoid scanning raw transaction history for every screen refresh."),
        ],
        "lesson": "CPU-bound AWRs usually show DB CPU dominating Top Events and sql execute elapsed time dominating Time Model. The next step is not to tune every SQL, but to find the few SQL IDs responsible for the most elapsed time, CPU time, and buffer gets.",
    },
    {
        "file": "awrrpt-bank-02-io-full-scan.html",
        "snap": (4318, 4319),
        "title": "User I/O Bound Full Table Scan",
        "summary": "A compliance AML extract ran during business hours and scanned payments history. Online payment screens slowed because storage latency and cache churn increased.",
        "db_time_min": 3780,
        "elapsed_min": 60,
        "sessions": (1320, 1410),
        "cursors": (10.5, 11.0),
        "host": ("bkdb-prd2-rac2", 40, 20, 512),
        "load": [
            ("DB Time(s)", "63.0", "0.420", "0.210", "0.190"),
            ("DB CPU(s)", "19.4", "0.129", "0.065", "0.058"),
            ("Redo size (bytes)", "9,800,000", "65,333", "", ""),
            ("Logical read (blocks)", "3,200,000", "21,333", "", ""),
            ("Physical read (blocks)", "1,180,000", "7,867", "", ""),
            ("Physical write (blocks)", "7,800", "52", "", ""),
            ("Read IO requests", "62,000", "413", "", ""),
            ("Read IO (MB)", "9,216", "61.4", "", ""),
            ("User calls", "330", "2.2", "", ""),
            ("Executes (SQL)", "18,000", "120", "", ""),
            ("Transactions", "150", "", "", ""),
        ],
        "wait_events": [
            ("db file scattered read", "4,240,000", "91,160", "21.5 ms", "40.2", "User I/O"),
            ("direct path read", "1,780,000", "53,400", "30.0 ms", "23.5", "User I/O"),
            ("DB CPU", "", "69,840", "", "30.8", ""),
            ("db file sequential read", "2,100,000", "8,400", "4.0 ms", "3.7", "User I/O"),
            ("log file sync", "320,000", "1,600", "5.0 ms", "0.7", "Commit"),
            ("SQL*Net more data to client", "900,000", "1,080", "1.2 ms", "0.5", "Network"),
        ],
        "wait_classes": [
            ("User I/O", "8,120,000", "153,200", "18.9 ms", "67.5", "42.6"),
            ("DB CPU", "", "69,840", "", "30.8", "19.4"),
            ("Commit", "320,000", "1,600", "5.0 ms", "0.7", "0.4"),
            ("Network", "900,000", "1,080", "1.2 ms", "0.5", "0.3"),
        ],
        "time_model": [
            ("sql execute elapsed time", "221,300", "97.6"),
            ("DB CPU", "69,840", "30.8"),
            ("PL/SQL execution elapsed time", "4,800", "2.1"),
            ("parse time elapsed", "900", "0.4"),
            ("DB time", "226,800", ""),
        ],
        "sql": [
            ("7p9k2xq4v1dms", "AML same-day payment scan", "AML_BATCH", "BANKPDB", "118,600", "12", "36,200", "74,800", "8,900,000,000", "SELECT /* aml extract */ * FROM payments_history WHERE beneficiary_country <> :B1 AND amount > :B2"),
            ("51hbr71msv2aa", "Branch cash transaction report", "BRANCH_RPT", "BANKPDB", "22,400", "120", "6,900", "15,100", "1,600,000,000", "SELECT branch_id, SUM(amount) FROM cash_txn WHERE txn_date = :B1 GROUP BY branch_id"),
            ("5w4h9fg0u9sp2", "Recent payment list", "MOBILE_API", "BANKPDB", "4,500", "2,100,000", "2,900", "980", "6,100,000", "SELECT * FROM payments WHERE customer_id = :B1 ORDER BY payment_ts DESC FETCH FIRST 20 ROWS ONLY"),
        ],
        "segments": [
            ("PAYMENTS", "PAYMENTS_HISTORY", "TABLE", "8,900,000,000", "9,100,000,000", "0", "0"),
            ("CASH", "CASH_TXN", "TABLE", "1,600,000,000", "1,180,000,000", "0", "0"),
            ("PAYMENTS", "PAYMENTS_CUST_TS_IX", "INDEX", "6,100,000", "820,000", "0", "0"),
            ("TEMP", "SYS_TEMP_0FD9D", "TEMP", "0", "480,000,000", "420,000,000", "0"),
        ],
        "ash": [
            ("11:00-11:10", "db file scattered read", "AML_BATCH", "7p9k2xq4v1dms", "Large multiblock reads begin"),
            ("11:10-11:20", "direct path read", "AML_BATCH", "7p9k2xq4v1dms", "Serial direct path scans bypass buffer cache"),
            ("11:20-11:30", "db file scattered read", "BRANCH_RPT", "51hbr71msv2aa", "Second report increases storage pressure"),
            ("11:30-11:40", "db file sequential read", "MOBILE_API", "5w4h9fg0u9sp2", "OLTP index reads also slow because storage is saturated"),
        ],
        "addm": [
            ("I/O throughput bottleneck", "User I/O accounts for 67.5% of DB Time. Average read latency is far above the healthy baseline.", "Move AML extract outside online hours, add a selective predicate/index if possible, or run against a reporting replica.", "Very high"),
            ("High-load SQL by physical reads", "SQL ID 7p9k2xq4v1dms accounts for most physical reads and should be tuned first.", "Run SQL Tuning Advisor. Check predicate selectivity, partition pruning, and required indexes.", "Very high"),
        ],
        "advisor": [
            ("Partition pruning", "If PAYMENTS_HISTORY is range partitioned by txn_date, add a date predicate and verify PSTART/PSTOP in the execution plan.", "Avoid scanning old partitions for same-day AML work."),
            ("Index strategy", "Consider local indexes on amount, beneficiary_country, and txn_date only after testing selectivity and DML cost.", "Reduce full-scan pressure where predicate is selective."),
            ("Workload isolation", "Run regulatory extracts on Active Data Guard, a reporting PDB, or a scheduled batch window.", "Protect customer-facing OLTP response time."),
        ],
        "lesson": "When User I/O dominates DB Time, read SQL ordered by Reads, Segments by Physical Reads, and the IO profile together. One bad report or batch can make normal OLTP index lookups appear slow because the storage system is already busy.",
    },
    {
        "file": "awrrpt-bank-03-locking.html",
        "snap": (4401, 4402),
        "title": "Application Locking and Blocking Sessions",
        "summary": "End-of-day payment posting created a hot row in settlement control. Many sessions waited on enq: TX - row lock contention.",
        "db_time_min": 2550,
        "elapsed_min": 60,
        "sessions": (980, 1560),
        "cursors": (8.4, 8.8),
        "host": ("bkdb-prd1-rac2", 48, 24, 384),
        "load": [
            ("DB Time(s)", "42.5", "0.900", "0.180", "0.280"),
            ("DB CPU(s)", "8.6", "0.182", "0.036", "0.057"),
            ("Redo size (bytes)", "38,700,000", "819,000", "", ""),
            ("Logical read (blocks)", "980,000", "20,762", "", ""),
            ("Physical read (blocks)", "8,100", "172", "", ""),
            ("Block changes", "148,000", "3,136", "", ""),
            ("User calls", "152", "3.2", "", ""),
            ("Executes (SQL)", "14,200", "301", "", ""),
            ("Rollbacks", "12", "0.25", "", ""),
            ("Transactions", "47", "", "", ""),
        ],
        "wait_events": [
            ("enq: TX - row lock contention", "18,200", "97,370", "5.35 s", "63.6", "Application"),
            ("DB CPU", "", "30,960", "", "20.2", ""),
            ("buffer busy waits", "240,000", "8,400", "35.0 ms", "5.5", "Concurrency"),
            ("log file sync", "169,000", "5,070", "30.0 ms", "3.3", "Commit"),
            ("gc buffer busy acquire", "36,000", "3,960", "110 ms", "2.6", "Cluster"),
            ("db file sequential read", "820,000", "2,460", "3.0 ms", "1.6", "User I/O"),
        ],
        "wait_classes": [
            ("Application", "18,200", "97,370", "5.35 s", "63.6", "27.0"),
            ("DB CPU", "", "30,960", "", "20.2", "8.6"),
            ("Concurrency", "240,000", "8,400", "35.0 ms", "5.5", "2.3"),
            ("Commit", "169,000", "5,070", "30.0 ms", "3.3", "1.4"),
            ("Cluster", "36,000", "3,960", "110 ms", "2.6", "1.1"),
            ("User I/O", "820,000", "2,460", "3.0 ms", "1.6", "0.7"),
        ],
        "time_model": [
            ("sql execute elapsed time", "148,900", "97.3"),
            ("DB CPU", "30,960", "20.2"),
            ("PL/SQL execution elapsed time", "18,100", "11.8"),
            ("parse time elapsed", "620", "0.4"),
            ("DB time", "153,000", ""),
        ],
        "sql": [
            ("2gk0s8h4b91qx", "Update settlement control row", "PAYMENT_POST", "BANKPDB", "88,600", "18,200", "5,200", "410", "1,120,000", "UPDATE settlement_control SET last_batch_no = :B1, status = :B2 WHERE settlement_date = :B3"),
            ("2qv5mmu1rrp0z", "Post individual payment ledger entries", "PAYMENT_POST", "BANKPDB", "18,400", "420,000", "10,900", "1,200", "6,800,000", "INSERT INTO payment_ledger(...) VALUES (...)"),
            ("6cm9sgg9qtb34", "Reverse failed payment", "PAYMENT_POST", "BANKPDB", "8,100", "19,000", "2,200", "380", "980,000", "UPDATE payments SET status = :B1 WHERE payment_id = :B2"),
        ],
        "segments": [
            ("PAYMENTS", "SETTLEMENT_CONTROL", "TABLE", "1,120,000", "8,000", "148,000", "18,200"),
            ("PAYMENTS", "SETTLEMENT_CONTROL_PK", "INDEX", "1,080,000", "4,000", "0", "2,100"),
            ("PAYMENTS", "PAYMENT_LEDGER", "TABLE", "6,800,000", "120,000", "136,000", "0"),
            ("PAYMENTS", "PAYMENTS", "TABLE", "980,000", "40,000", "12,000", "400"),
        ],
        "ash": [
            ("23:00-23:10", "enq: TX - row lock contention", "PAYMENT_POST", "2gk0s8h4b91qx", "One blocker holds settlement control row"),
            ("23:10-23:20", "enq: TX - row lock contention", "PAYMENT_POST", "2gk0s8h4b91qx", "Wait chain grows across posting workers"),
            ("23:20-23:30", "buffer busy waits", "PAYMENT_POST", "2gk0s8h4b91qx", "Hot block symptoms after lock queue forms"),
            ("23:30-23:40", "log file sync", "PAYMENT_POST", "2qv5mmu1rrp0z", "Commit waits rise as workers catch up"),
        ],
        "addm": [
            ("Application waits caused by row locking", "enq: TX - row lock contention is 63.6% of DB Time. SQL ID 2gk0s8h4b91qx updates one settlement control row from many sessions.", "Fix application design. Avoid a single mutable control row or serialize this step intentionally.", "Very high"),
            ("Hot database object", "SETTLEMENT_CONTROL shows row lock waits and high block changes.", "Investigate blocking session history and application transaction boundaries.", "High"),
        ],
        "advisor": [
            ("SQL Tuning Advisor limitation", "SQL Tuning Advisor can verify the update uses the primary key, but it cannot fix long transaction holding a row lock.", "Use ADDM and ASH to prove the issue is application concurrency, not access path."),
            ("Application redesign", "Use sequence-generated batch ids, per-worker rows, SKIP LOCKED queueing, or an explicit single posting coordinator.", "Remove the hot row from the critical path."),
            ("Operational triage", "Find blocker with ASH/V$SESSION, confirm uncommitted transaction, then work with application owner before killing sessions.", "Avoid data corruption or duplicate posting in a banking flow."),
        ],
        "lesson": "AWR tells you the wait class, not only the SQL text. If Application waits dominate, an index may already be perfect. The cure can be transaction design, commit timing, or reducing hot rows.",
    },
    {
        "file": "awrrpt-bank-04-hard-parse.html",
        "snap": (4505, 4506),
        "title": "Hard Parse and Library Cache Pressure",
        "summary": "A fraud rules deployment generated literal SQL instead of bind variables. CPU rose, library cache mutex waits appeared, and SQL version counts exploded.",
        "db_time_min": 3180,
        "elapsed_min": 60,
        "sessions": (1220, 1305),
        "cursors": (28.4, 46.9),
        "host": ("bkdb-prd1-rac1", 48, 24, 384),
        "load": [
            ("DB Time(s)", "53.0", "0.128", "0.021", "0.044"),
            ("DB CPU(s)", "31.8", "0.077", "0.013", "0.026"),
            ("Redo size (bytes)", "16,900,000", "40,819", "", ""),
            ("Logical read (blocks)", "2,800,000", "6,763", "", ""),
            ("Physical read (blocks)", "18,000", "43", "", ""),
            ("User calls", "1,210", "2.9", "", ""),
            ("Parses (SQL)", "42,000", "101.4", "", ""),
            ("Hard parses (SQL)", "18,500", "44.7", "", ""),
            ("Executes (SQL)", "119,000", "287", "", ""),
            ("Transactions", "414", "", "", ""),
        ],
        "wait_events": [
            ("DB CPU", "", "114,480", "", "60.0", ""),
            ("library cache: mutex X", "1,260,000", "39,690", "31.5 ms", "20.8", "Concurrency"),
            ("cursor: pin S wait on X", "560,000", "14,560", "26.0 ms", "7.6", "Concurrency"),
            ("latch: shared pool", "180,000", "5,400", "30.0 ms", "2.8", "Concurrency"),
            ("db file sequential read", "2,100,000", "4,200", "2.0 ms", "2.2", "User I/O"),
            ("log file sync", "520,000", "2,600", "5.0 ms", "1.4", "Commit"),
        ],
        "wait_classes": [
            ("DB CPU", "", "114,480", "", "60.0", "31.8"),
            ("Concurrency", "2,000,000", "59,650", "29.8 ms", "31.3", "16.6"),
            ("User I/O", "2,100,000", "4,200", "2.0 ms", "2.2", "1.2"),
            ("Commit", "520,000", "2,600", "5.0 ms", "1.4", "0.7"),
        ],
        "time_model": [
            ("DB CPU", "114,480", "60.0"),
            ("sql execute elapsed time", "103,400", "54.2"),
            ("parse time elapsed", "70,800", "37.1"),
            ("hard parse elapsed time", "62,600", "32.8"),
            ("hard parse (sharing criteria) elapsed time", "39,200", "20.5"),
            ("PL/SQL execution elapsed time", "8,900", "4.7"),
            ("DB time", "190,800", ""),
        ],
        "sql": [
            ("1n0literal001", "Fraud rule literal SQL family", "FRAUD_ENGINE", "BANKPDB", "54,200", "18,900", "31,200", "1,120", "880,000,000", "SELECT rule_score FROM fraud_rules WHERE merchant_id = 348923 AND amount BETWEEN 100 AND 500"),
            ("1n0literal002", "Similar fraud rule literal SQL", "FRAUD_ENGINE", "BANKPDB", "31,600", "17,800", "18,400", "720", "620,000,000", "SELECT rule_score FROM fraud_rules WHERE merchant_id = 881277 AND amount BETWEEN 500 AND 1000"),
            ("a91c7b0npx3vv", "Customer risk profile", "FRAUD_ENGINE", "BANKPDB", "14,900", "640,000", "7,800", "380", "220,000,000", "SELECT risk_bucket FROM customer_risk WHERE customer_id = :B1"),
            ("cz7mrb1f0a21q", "Card authorization limit check", "CARD_AUTH", "BANKPDB", "5,800", "26,800,000", "2,900", "460", "15,800,000", "SELECT available_limit FROM card_limits WHERE card_no = :B1 AND status = 'A'"),
        ],
        "segments": [
            ("SYS", "SQL AREA", "LIBRARY CACHE", "0", "0", "0", "0"),
            ("FRAUD", "FRAUD_RULES", "TABLE", "1,500,000,000", "12,000,000", "0", "0"),
            ("FRAUD", "FRAUD_RULES_IX1", "INDEX", "620,000,000", "3,200,000", "0", "0"),
            ("FRAUD", "CUSTOMER_RISK_PK", "INDEX", "220,000,000", "1,400,000", "0", "0"),
        ],
        "ash": [
            ("13:00-13:10", "library cache: mutex X", "FRAUD_ENGINE", "1n0literal001", "New deploy starts creating many child cursors"),
            ("13:10-13:20", "cursor: pin S wait on X", "FRAUD_ENGINE", "1n0literal002", "Sessions wait while cursors are parsed or invalidated"),
            ("13:20-13:30", "DB CPU", "FRAUD_ENGINE", "1n0literal001", "CPU spent parsing and executing similar statements"),
            ("13:30-13:40", "latch: shared pool", "FRAUD_ENGINE", "1n0literal002", "Shared pool pressure visible"),
        ],
        "addm": [
            ("Hard parsing of SQL statements", "Hard parses are 44.7 per second and parse time is 37.1% of DB Time.", "Use bind variables in fraud rule SQL. Check CURSOR_SHARING only as a temporary mitigation after risk review.", "Very high"),
            ("Library cache contention", "library cache mutex waits and cursor pin waits account for 28.4% of DB Time.", "Reduce hard parsing and check invalidation sources such as frequent DDL or stats changes.", "High"),
        ],
        "advisor": [
            ("Bind variables", "Replace generated literal SQL with bind variables for merchant_id, amount, channel, and country.", "One reusable cursor instead of thousands of unique SQL statements."),
            ("SQL Tuning Advisor scope", "Run advisor on the normalized high-load SQL, but the main fix is application cursor sharing.", "Advisor may suggest an index, yet parse pressure remains until literals are fixed."),
            ("Shared pool review", "After fixing literals, reassess shared pool sizing and session cached cursors.", "Size memory after removing abnormal parse load."),
        ],
        "lesson": "Hard parse problems show up in Load Profile, Time Model, library cache waits, SQL ordered by Parse Calls, and Version Count. Do not diagnose only from CPU; parse CPU can look like normal SQL execution CPU until you read the parsing sections.",
    },
    {
        "file": "awrrpt-bank-05-commit-redo.html",
        "snap": (4608, 4609),
        "title": "Commit Latency and Redo Pressure",
        "summary": "A real-time notification process committed every row during a card settlement import. Customers saw delays because log file sync dominated response time.",
        "db_time_min": 3540,
        "elapsed_min": 60,
        "sessions": (1120, 1210),
        "cursors": (9.0, 9.7),
        "host": ("bkdb-prd2-rac1", 40, 20, 512),
        "load": [
            ("DB Time(s)", "59.0", "0.065", "0.018", "0.030"),
            ("DB CPU(s)", "14.2", "0.016", "0.004", "0.007"),
            ("Redo size (bytes)", "142,000,000", "156,044", "", ""),
            ("Logical read (blocks)", "1,240,000", "1,363", "", ""),
            ("Physical read (blocks)", "11,500", "13", "", ""),
            ("Physical write (blocks)", "88,000", "97", "", ""),
            ("User calls", "1,980", "2.2", "", ""),
            ("Executes (SQL)", "178,000", "196", "", ""),
            ("User commits", "36,200", "39.8", "", ""),
            ("Transactions", "910", "", "", ""),
        ],
        "wait_events": [
            ("log file sync", "2,172,000", "124,890", "57.5 ms", "58.8", "Commit"),
            ("log file parallel write", "1,980,000", "41,580", "21.0 ms", "", "System I/O"),
            ("DB CPU", "", "51,120", "", "24.1", ""),
            ("LGWR any worker group", "440,000", "12,320", "28.0 ms", "5.8", "Other"),
            ("db file sequential read", "1,180,000", "4,720", "4.0 ms", "2.2", "User I/O"),
            ("gc current grant 2-way", "620,000", "1,860", "3.0 ms", "0.9", "Cluster"),
        ],
        "wait_classes": [
            ("Commit", "2,172,000", "124,890", "57.5 ms", "58.8", "34.7"),
            ("DB CPU", "", "51,120", "", "24.1", "14.2"),
            ("System I/O", "1,980,000", "41,580", "21.0 ms", "19.6", "11.6"),
            ("Other", "440,000", "12,320", "28.0 ms", "5.8", "3.4"),
            ("User I/O", "1,180,000", "4,720", "4.0 ms", "2.2", "1.3"),
            ("Cluster", "620,000", "1,860", "3.0 ms", "0.9", "0.5"),
        ],
        "time_model": [
            ("sql execute elapsed time", "205,800", "96.9"),
            ("DB CPU", "51,120", "24.1"),
            ("PL/SQL execution elapsed time", "34,000", "16.0"),
            ("parse time elapsed", "1,100", "0.5"),
            ("DB time", "212,400", ""),
        ],
        "sql": [
            ("4k9b7t2cc2mva", "Insert card settlement notification", "CARD_SETTLE", "BANKPDB", "79,400", "2,172,000", "18,200", "1,400", "4,600,000", "INSERT INTO card_notification_queue(card_no, event_type, payload, created_ts) VALUES (:B1,:B2,:B3,SYSTIMESTAMP)"),
            ("72x5p1nww8jk9", "Update settlement import status", "CARD_SETTLE", "BANKPDB", "28,900", "2,172,000", "6,400", "700", "3,900,000", "UPDATE card_settlement_import SET status = :B1 WHERE import_id = :B2 AND row_no = :B3"),
            ("cz7mrb1f0a21q", "Card authorization limit check", "CARD_AUTH", "BANKPDB", "7,200", "27,100,000", "4,100", "620", "15,700,000", "SELECT available_limit FROM card_limits WHERE card_no = :B1 AND status = 'A'"),
        ],
        "segments": [
            ("CARDS", "CARD_NOTIFICATION_QUEUE", "TABLE", "4,600,000", "110,000", "2,172,000", "0"),
            ("CARDS", "CARD_SETTLEMENT_IMPORT", "TABLE", "3,900,000", "90,000", "2,172,000", "0"),
            ("SYS", "ONLINE REDO LOGS", "REDO", "0", "0", "0", "0"),
            ("CARDS", "CARD_LIMITS_IX1", "INDEX", "15,700,000", "84,000", "0", "0"),
        ],
        "ash": [
            ("02:00-02:10", "log file sync", "CARD_SETTLE", "4k9b7t2cc2mva", "Import begins, row-by-row commits"),
            ("02:10-02:20", "log file parallel write", "LGWR", "background", "Redo storage latency increases"),
            ("02:20-02:30", "log file sync", "CARD_SETTLE", "72x5p1nww8jk9", "Foreground sessions wait for LGWR acknowledgement"),
            ("02:30-02:40", "DB CPU", "CARD_AUTH", "cz7mrb1f0a21q", "Normal workload continues but response time is commit-bound"),
        ],
        "addm": [
            ("Commit waits are significant", "log file sync is 58.8% of DB Time. The report shows 36,200 commits per second and high redo volume.", "Batch commits in CARD_SETTLE and review redo log storage latency.", "Very high"),
            ("Redo log I/O latency", "log file parallel write averaged 21 ms, which is high for online redo.", "Work with storage team. Redo logs should be on low-latency protected storage.", "High"),
        ],
        "advisor": [
            ("Application commit batching", "Commit every logical settlement batch, not every notification row, while respecting recovery and duplicate-processing rules.", "Reduce foreground log file sync waits."),
            ("Redo and LGWR checks", "Check redo log placement, storage latency, log file size, and whether synchronous Data Guard transport contributes.", "Separate database tuning from infrastructure latency."),
            ("SQL Tuning Advisor scope", "Advisor may not improve insert SQL much. The main issue is transaction frequency and redo acknowledgement latency.", "Avoid wasting time on access path tuning for a commit bottleneck."),
        ],
        "lesson": "Commit problems are often not SQL access path problems. AWR will show log file sync for foreground sessions and log file parallel write for LGWR. Tune transaction design and redo I/O before chasing SELECT indexes.",
    },
]


GUIDE = """
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
"""


def row(values, odd=False):
    cls = "awrc" if odd else "awrnc"
    tds = []
    for value in values:
        text = escape(str(value))
        num_class = " num" if str(value).replace(",", "").replace(".", "").replace("-", "").isdigit() else ""
        tds.append(f"<td class='{cls}{num_class}'>{text if text else '&nbsp;'}</td>")
    return "<tr>" + "".join(tds) + "</tr>"


def table(headers, rows, width="980"):
    head = "".join(f"<th class='awrbg'>{escape(h)}</th>" for h in headers)
    body = "\n".join(row(r, i % 2 == 0) for i, r in enumerate(rows))
    return f"<table border='0' width='{width}' class='tdiff'><tr>{head}</tr>\n{body}\n</table>"


def nav():
    return """
<h2 class="awr"><a class="awr" name="top"></a>Main Report</h2>
<ul class="toc">
<li class="awr"><a class="awr" href="#summary">Report Summary</a></li>
<li class="awr"><a class="awr" href="#instance">Instance Efficiency and IO Profile</a></li>
<li class="awr"><a class="awr" href="#waits">Wait Events Statistics</a></li>
<li class="awr"><a class="awr" href="#sql">SQL Statistics</a></li>
<li class="awr"><a class="awr" href="#segments">Segment Statistics</a></li>
<li class="awr"><a class="awr" href="#ash">Active Session History Summary</a></li>
<li class="awr"><a class="awr" href="#addm">ADDM Report</a></li>
<li class="awr"><a class="awr" href="#advisor">SQL Tuning Advisor Practice</a></li>
</ul>
"""


def efficiency_rows(s):
    by_file = {
        "awrrpt-bank-00-baseline.html": [
            ("Buffer Nowait %", "99.94"),
            ("Buffer Hit %", "99.09"),
            ("Library Hit %", "99.62"),
            ("Execute to Parse %", "96.25"),
            ("Parse CPU to Parse Elapsed %", "88.90"),
            ("Soft Parse %", "98.92"),
            ("Latch Hit %", "99.78"),
            ("Non-Parse CPU %", "97.40"),
        ],
        "awrrpt-bank-01-cpu-sql.html": [
            ("Buffer Nowait %", "99.81"),
            ("Buffer Hit %", "99.57"),
            ("Library Hit %", "99.51"),
            ("Execute to Parse %", "95.16"),
            ("Parse CPU to Parse Elapsed %", "90.20"),
            ("Soft Parse %", "98.75"),
            ("Latch Hit %", "98.91"),
            ("Non-Parse CPU %", "99.21"),
        ],
        "awrrpt-bank-02-io-full-scan.html": [
            ("Buffer Nowait %", "99.12"),
            ("Buffer Hit %", "63.13"),
            ("Library Hit %", "99.42"),
            ("Execute to Parse %", "94.90"),
            ("Parse CPU to Parse Elapsed %", "87.30"),
            ("Soft Parse %", "98.80"),
            ("Latch Hit %", "99.44"),
            ("Non-Parse CPU %", "98.62"),
        ],
        "awrrpt-bank-03-locking.html": [
            ("Buffer Nowait %", "96.88"),
            ("Buffer Hit %", "99.17"),
            ("Library Hit %", "99.30"),
            ("Execute to Parse %", "96.10"),
            ("Parse CPU to Parse Elapsed %", "85.00"),
            ("Soft Parse %", "98.91"),
            ("Latch Hit %", "98.42"),
            ("Non-Parse CPU %", "98.00"),
        ],
        "awrrpt-bank-04-hard-parse.html": [
            ("Buffer Nowait %", "99.21"),
            ("Buffer Hit %", "99.36"),
            ("Library Hit %", "86.72"),
            ("Execute to Parse %", "64.71"),
            ("Parse CPU to Parse Elapsed %", "51.20"),
            ("Soft Parse %", "55.95"),
            ("Latch Hit %", "94.10"),
            ("Non-Parse CPU %", "62.92"),
        ],
        "awrrpt-bank-05-commit-redo.html": [
            ("Buffer Nowait %", "99.50"),
            ("Buffer Hit %", "99.07"),
            ("Library Hit %", "99.34"),
            ("Execute to Parse %", "96.90"),
            ("Parse CPU to Parse Elapsed %", "88.10"),
            ("Soft Parse %", "98.65"),
            ("Latch Hit %", "99.18"),
            ("Non-Parse CPU %", "98.01"),
        ],
    }
    return by_file[s["file"]]


def io_profile_rows(s):
    by_file = {
        "awrrpt-bank-00-baseline.html": [
            ("Database Requests", "26,700", "18,700", "8,000"),
            ("Database MB", "201.6", "131.3", "70.3"),
            ("Redo MB", "", "", "25.2"),
            ("Avg Read Latency", "", "0.70 ms", ""),
        ],
        "awrrpt-bank-01-cpu-sql.html": [
            ("Database Requests", "50,200", "42,000", "8,200"),
            ("Database MB", "369.0", "328.1", "40.9"),
            ("Redo MB", "", "", "17.4"),
            ("Avg Read Latency", "", "0.35 ms", ""),
        ],
        "awrrpt-bank-02-io-full-scan.html": [
            ("Database Requests", "66,800", "62,000", "4,800"),
            ("Database MB", "9,245.0", "9,216.0", "29.0"),
            ("Redo MB", "", "", "9.3"),
            ("Avg Read Latency", "", "24.2 ms", ""),
        ],
        "awrrpt-bank-03-locking.html": [
            ("Database Requests", "17,200", "8,100", "9,100"),
            ("Database MB", "133.5", "63.3", "70.2"),
            ("Redo MB", "", "", "36.9"),
            ("Avg Read Latency", "", "3.0 ms", ""),
        ],
        "awrrpt-bank-04-hard-parse.html": [
            ("Database Requests", "26,500", "18,000", "8,500"),
            ("Database MB", "184.0", "140.6", "43.4"),
            ("Redo MB", "", "", "16.1"),
            ("Avg Read Latency", "", "2.0 ms", ""),
        ],
        "awrrpt-bank-05-commit-redo.html": [
            ("Database Requests", "99,500", "11,500", "88,000"),
            ("Database MB", "777.3", "89.8", "687.5"),
            ("Redo MB", "", "", "135.4"),
            ("Avg Redo Write Latency", "", "", "21.0 ms"),
        ],
    }
    return by_file[s["file"]]


def parse_rows(s):
    if s["file"] == "awrrpt-bank-04-hard-parse.html":
        return [
            ("18,900", "18,900", "44.7", "1n0literal001", "FRAUD_ENGINE", "BANKPDB", "Fraud literal SQL family"),
            ("17,800", "17,800", "42.1", "1n0literal002", "FRAUD_ENGINE", "BANKPDB", "Similar fraud literal SQL"),
            ("640", "640,000", "1.5", "a91c7b0npx3vv", "FRAUD_ENGINE", "BANKPDB", "Customer risk profile"),
            ("420", "26,800,000", "1.0", "cz7mrb1f0a21q", "CARD_AUTH", "BANKPDB", "Card authorization limit check"),
        ]
    rows = []
    for i, (sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text) in enumerate(s["sql"]):
        exec_count = int(execs.replace(",", ""))
        parse_count = max(1, min(exec_count, int(exec_count * (0.002 + i * 0.001))))
        rows.append((f"{parse_count:,}", execs, f"{parse_count / max(exec_count, 1) * 100:.2f}", sql_id, module, pdb, desc))
    return sorted(rows, key=lambda r: int(r[0].replace(",", "")), reverse=True)


def version_rows(s):
    if s["file"] == "awrrpt-bank-04-hard-parse.html":
        return [
            ("2,840", "1n0literal001", "FRAUD_ENGINE", "BANKPDB", "Literal values and bind mismatch create many child cursors"),
            ("1,920", "1n0literal002", "FRAUD_ENGINE", "BANKPDB", "Similar statement text fragments shared pool"),
            ("38", "a91c7b0npx3vv", "FRAUD_ENGINE", "BANKPDB", "Multiple optimizer environments after deployment"),
            ("12", "cz7mrb1f0a21q", "CARD_AUTH", "BANKPDB", "Normal OLTP cursor variation"),
        ]
    return [
        ("8", s["sql"][0][0], s["sql"][0][2], s["sql"][0][3], "Acceptable cursor variation"),
        ("6", s["sql"][1][0], s["sql"][1][2], s["sql"][1][3], "Acceptable cursor variation"),
        ("4", s["sql"][2][0], s["sql"][2][2], s["sql"][2][3], "Stable cursor sharing"),
    ]


def report_html(s):
    snap1, snap2 = s["snap"]
    aas = s["db_time_min"] / s["elapsed_min"]
    db_info = [
        ("BANKPRD", "918273645", "bankprd", "PRIMARY", "EE", "19.20.0.0.0", "YES", "YES"),
    ]
    inst_info = [
        ("bankprd1", "1", "12-May-26 04:15", "SYS", "YES"),
    ]
    host, cpus, cores, mem = s["host"]
    host_info = [(host, "Linux x86 64-bit", cpus, cores, "2", f"{mem}.00")]
    snap_info = [
        ("Begin Snap", snap1, "12-May-26 14:00:00", s["sessions"][0], s["cursors"][0]),
        ("End Snap", snap2, "12-May-26 15:00:00", s["sessions"][1], s["cursors"][1]),
        ("Elapsed", "", f"{s['elapsed_min']} (mins)", "", ""),
        ("DB Time", "", f"{s['db_time_min']} (mins)", "", ""),
        ("Average Active Sessions", "", f"{aas:.1f}", "", ""),
    ]
    sql_rows = [
        (elapsed, execs, f"{float(elapsed.replace(',', '')) / max(float(execs.replace(',', '')), 1):.4f}", cpu, io, gets, sql_id, module, pdb, text)
        for sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text in s["sql"]
    ]
    sql_cpu_rows = sorted(
        [(cpu, execs, elapsed, gets, sql_id, module, pdb, text) for sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text in s["sql"]],
        key=lambda r: float(r[0].replace(",", "")),
        reverse=True,
    )
    sql_get_rows = sorted(
        [(gets, execs, elapsed, cpu, sql_id, module, pdb, text) for sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text in s["sql"]],
        key=lambda r: float(r[0].replace(",", "")),
        reverse=True,
    )
    sql_io_rows = sorted(
        [(io, execs, elapsed, cpu, sql_id, module, pdb, text) for sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text in s["sql"]],
        key=lambda r: float(r[0].replace(",", "")),
        reverse=True,
    )
    sql_exec_rows = sorted(
        [(execs, elapsed, cpu, io, sql_id, module, pdb, text) for sql_id, desc, module, pdb, elapsed, execs, cpu, io, gets, text in s["sql"]],
        key=lambda r: float(r[0].replace(",", "")),
        reverse=True,
    )
    addm_rows = [(name, impact, finding, action) for name, finding, action, impact in s["addm"]]
    advisor_rows = [(topic, recommendation, reason) for topic, recommendation, reason in s["advisor"]]

    return dedent(
        f"""\
        <html lang="en"><head><title>AWR Report for DB: BANKPRD, Scenario: {escape(s['title'])}</title>
        <style type="text/css">{CSS}</style></head><body class="awr">
        <h1 class="awr">WORKLOAD REPOSITORY PDB report - BANKPRD - {escape(s['title'])}</h1>
        <div class="warning"><b>Training report:</b> Mock AWR data for learning. The values are designed to resemble real production symptoms, not to represent a real bank or customer.</div>
        {table(["DB Name", "DB Id", "Unique Name", "Role", "Edition", "Release", "RAC", "CDB"], db_info, "980")}
        {table(["Instance", "Inst Num", "Startup Time", "User Name", "System Data Visible"], inst_info, "760")}
        {table(["Host Name", "Platform", "CPUs", "Cores", "Sockets", "Memory (GB)"], host_info, "760")}
        {table(["", "Snap Id", "Snap Time", "Sessions", "Cursors/Session"], snap_info, "760")}
        {nav()}
        <h2 class="awr"><a class="awr" name="summary"></a>Report Summary</h2>
        <div class="note">{escape(s['summary'])}</div>
        <h3 class="awr">Load Profile</h3>
        {table(["", "Per Second", "Per Transaction", "Per Exec", "Per Call"], s["load"], "980")}
        <h3 class="awr">How to Read This Scenario</h3>
        <div class="finding">{escape(s['lesson'])}</div>
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="instance"></a>Instance Efficiency and IO Profile</h2>
        <h3 class="awr">Instance Efficiency Percentages</h3>
        {table(["Statistic", "Value"], efficiency_rows(s), "520")}
        <div class="note">Use these percentages as clues, not as absolute health scores. A high buffer hit ratio can still hide bad SQL with huge logical reads, and a low soft parse percentage points toward cursor sharing or hard parse problems.</div>
        <h3 class="awr">IO Profile</h3>
        {table(["", "Read+Write Per Second", "Read Per Second", "Write Per Second"], io_profile_rows(s), "760")}

        <h2 class="awr"><a class="awr" name="waits"></a>Wait Events Statistics</h2>
        <h3 class="awr">Top 10 Foreground Events by Total Wait Time</h3>
        {table(["Event", "Waits", "Total Wait Time (sec)", "Avg Wait", "% DB time", "Wait Class"], s["wait_events"], "980")}
        <h3 class="awr">Wait Classes by Total Wait Time</h3>
        {table(["Wait Class", "Waits", "Total Wait Time (sec)", "Avg Wait Time", "% DB time", "Avg Active Sessions"], s["wait_classes"], "980")}
        <h3 class="awr">Time Model Statistics</h3>
        {table(["Statistic Name", "Time (s)", "% of DB Time"], s["time_model"], "760")}
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="sql"></a>SQL Statistics</h2>
        <h3 class="awr">SQL ordered by Elapsed Time</h3>
        {table(["Elapsed Time (s)", "Executions", "Elapsed per Exec (s)", "CPU Time (s)", "User I/O Time (s)", "Buffer Gets", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], sql_rows, "1200")}
        <h3 class="awr">SQL ordered by CPU Time</h3>
        {table(["CPU Time (s)", "Executions", "Elapsed Time (s)", "Buffer Gets", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], sql_cpu_rows, "1200")}
        <h3 class="awr">SQL ordered by Gets</h3>
        {table(["Buffer Gets", "Executions", "Elapsed Time (s)", "CPU Time (s)", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], sql_get_rows, "1200")}
        <h3 class="awr">SQL ordered by User I/O Wait Time</h3>
        {table(["User I/O Time (s)", "Executions", "Elapsed Time (s)", "CPU Time (s)", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], sql_io_rows, "1200")}
        <h3 class="awr">SQL ordered by Executions</h3>
        {table(["Executions", "Elapsed Time (s)", "CPU Time (s)", "User I/O Time (s)", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], sql_exec_rows, "1200")}
        <h3 class="awr">SQL ordered by Parse Calls</h3>
        {table(["Parse Calls", "Executions", "% Total Parses", "SQL Id", "SQL Module", "PDB Name", "SQL Text"], parse_rows(s), "1200")}
        <h3 class="awr">SQL ordered by Version Count</h3>
        {table(["Version Count", "SQL Id", "SQL Module", "PDB Name", "Reason to Investigate"], version_rows(s), "980")}
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="segments"></a>Segment Statistics</h2>
        <h3 class="awr">Segments by Logical Reads, Physical Reads, Changes, and Row Lock Waits</h3>
        {table(["Owner", "Object Name", "Type", "Logical Reads", "Physical Reads", "DB Block Changes", "Row Lock Waits"], s["segments"], "980")}
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="ash"></a>Active Session History Summary</h2>
        {table(["Sample Slot", "Top Event", "Module", "SQL Id", "Interpretation"], s["ash"], "980")}
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="addm"></a>ADDM Report</h2>
        <div class="note">Begin with ADDM to identify where DB Time went. Then verify each finding in the AWR tables above before taking action.</div>
        {table(["Finding", "Impact", "Evidence", "Recommended Action"], addm_rows, "1100")}
        <a class="awr" href="#top">Back to Top</a>

        <h2 class="awr"><a class="awr" name="advisor"></a>SQL Tuning Advisor Practice</h2>
        <div class="note">Use SQL Tuning Advisor when the problem is a specific SQL statement. If the bottleneck is locking, commit latency, or application behavior, advisor output may be secondary evidence rather than the fix.</div>
        {table(["Topic", "Recommendation", "Why It Matters"], advisor_rows, "1100")}

        <h2 class="awr">End of Report</h2>
        </body></html>
        """
    )


def guide_html():
    links = "\n".join(
        f"<li class='awr'><a class='awr' href='{escape(s['file'])}'>{escape(s['title'])}</a> - {escape(s['summary'])}</li>"
        for s in SCENARIOS
    )
    return dedent(
        f"""\
        <html lang="en"><head><title>Bank AWR Training Index</title>
        <style type="text/css">{CSS}</style></head><body class="awr">
        <h1 class="awr">Bank AWR Training Index</h1>
        <div class="note">Start with the study guide, then open each mock AWR report. Each report is built around a realistic production symptom a bank DBA may investigate.</div>
        <h2 class="awr">Files</h2>
        <ul class="toc">
        <li class="awr"><a class="awr" href="awr-study-guide-bank-dba.md">AWR Learning Guide for a Banking DBA</a></li>
        <li class="awr"><a class="awr" href="awrrpt-sample.html">Original basic sample AWR report</a></li>
        {links}
        </ul>
        <h2 class="awr">Practice Goal</h2>
        <div class="finding">For every report, identify the top DB Time consumer, top SQL ID, top object, ADDM finding, and whether SQL Tuning Advisor is the right tool.</div>
        </body></html>
        """
    )


def main():
    for scenario in SCENARIOS:
        (OUT / scenario["file"]).write_text(report_html(scenario), encoding="utf-8")
    (OUT / "awr-study-guide-bank-dba.md").write_text(dedent(GUIDE).strip() + "\n", encoding="utf-8")
    (OUT / "awr-training-index.html").write_text(guide_html(), encoding="utf-8")


if __name__ == "__main__":
    main()
