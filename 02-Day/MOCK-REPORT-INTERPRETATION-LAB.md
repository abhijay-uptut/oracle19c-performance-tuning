# Day 2 Mock Report Interpretation Lab

## Low-Memory Path For AWR, ADDM, And SQL Tuning Advisor

Use this lab when the training VM cannot generate enough data for a quality AWR report.

This is now the recommended path for low-memory environments.

The goal is not to fake the learning. The goal is to practice the real DBA workflow using curated production-style evidence.

---

# Files Used

| File | Purpose |
| ---- | ------- |
| `02-Day/mock-reports/awr_day2_mock_incident.txt` | AWR-style incident evidence |
| `02-Day/mock-reports/addm_day2_mock_incident.txt` | ADDM-style findings and recommendations |
| `02-Day/mock-reports/sql_tuning_advisor_day2_mock.txt` | SQL Tuning Advisor-style recommendation and before/after plan |

---

# Scenario

At 11:00 AM:

```text
Customer statement screen is slow.
Branch dashboard is slow.
Fund transfer confirmation sometimes hangs.
```

The application team cannot provide SQL text.

The DBA receives AWR, ADDM, and SQL Tuning Advisor output.

The trainees must interpret the reports and produce a production-safe tuning recommendation.

---

# Part 1 - AWR Interpretation

Open:

```text
02-Day/mock-reports/awr_day2_mock_incident.txt
```

## Step 1 - Confirm Window And DB Time

Answer:

| Question | Answer |
| -------- | ------ |
| Begin snapshot | |
| End snapshot | |
| Elapsed time | |
| DB time | |
| Is DB time higher than elapsed time? | |
| What does that mean? | |

Expected reasoning:

```text
DB Time is higher than elapsed time, so multiple sessions were active or waiting during the window.
This is a real workload-level issue, not only one user's perception.
```

---

## Step 2 - Identify Wait Direction

Fill this from Top Foreground Events:

| Rank | Event | Wait Class | % DB Time | First Interpretation |
| ---- | ----- | ---------- | --------: | -------------------- |
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

Expected reasoning:

```text
User I/O is a major symptom, but we should not blame storage yet.
We must identify which SQL caused the reads.
```

---

## Step 3 - Identify Top SQL

Fill this from SQL ordered by Elapsed Time, Gets, and Reads:

| SQL ID | Appears In Which Sections? | Executions | Main Symptom | Priority |
| ------ | -------------------------- | ---------: | ------------ | -------- |
| | | | | |
| | | | | |
| | | | | |

Expected primary SQL:

```text
g8m1s9k2p6z0a
```

Why:

```text
It is high in elapsed time, buffer gets, and physical reads.
It is the customer statement SQL, which matches the business complaint.
```

---

# Part 2 - ADDM Interpretation

Open:

```text
02-Day/mock-reports/addm_day2_mock_incident.txt
```

Fill this:

| Finding | Impact | Related SQL/Event | Recommendation | Validation Needed |
| ------- | ------ | ----------------- | -------------- | ----------------- |
| | | | | |
| | | | | |
| | | | | |

Expected interpretation:

```text
ADDM prioritizes SQL_ID g8m1s9k2p6z0a.
It recommends SQL Tuning Advisor.
The I/O finding supports the AWR evidence, but SQL access path must be validated before blaming storage.
The commit finding is real but lower priority than the customer statement SQL.
```

---

# Part 3 - SQL Tuning Advisor Interpretation

Open:

```text
02-Day/mock-reports/sql_tuning_advisor_day2_mock.txt
```

Fill this:

| Item | Answer |
| ---- | ------ |
| SQL ID tuned | |
| Recommendation type | |
| Estimated benefit | |
| Suggested command | |
| Current plan problem | |
| Expected improved plan | |
| Before buffers/exec | |
| After buffers/exec | |
| Is this safe to apply directly? | |

Expected interpretation:

```text
SQL Tuning Advisor recommends an index on CUSTOMER_ID, TXN_TS DESC.
This directly matches the WHERE clause and ORDER BY.
The before/after plan shows much lower buffers and reads.
It is still not safe to apply blindly because indexes add DML cost and storage.
```

---

# Part 4 - Final DBA Recommendation

Each trainee must write:

```text
During the 10:45-11:15 incident window, DB Time was [x] against elapsed time [y].

The top wait direction was [wait class/events], mainly caused by SQL_ID [sql_id].

AWR evidence:
[SQL_ID appeared in elapsed/gets/reads sections with metrics]

ADDM evidence:
[finding, impact, recommendation]

SQL Tuning Advisor evidence:
[recommendation and estimated benefit]

Proposed fix:
[candidate index/profile/stats/rewrite]

Validation:
[before/after plan, elapsed, buffers, reads]

Production caution:
[DML impact, storage, duplicate index check, rollback, change approval]
```

---

# Answer Key

Use this after trainees complete the exercise.

## AWR Key

| Item | Expected Answer |
| ---- | --------------- |
| Begin snap | 14801 |
| End snap | 14802 |
| Elapsed time | 30.25 minutes |
| DB Time | 74.80 minutes |
| Top wait | `db file scattered read`, 35.0% DB time |
| Other major symptoms | DB CPU, temp reads, `log file sync`, sequential reads |
| Top SQL | `g8m1s9k2p6z0a` |
| Top SQL symptom | high elapsed time, high gets, high reads |
| Hot segment | `DAY2_TXN_BIG` |

Correct conclusion:

```text
The main pain is not simply "the database is slow."
The customer statement SQL is reading too much from DAY2_TXN_BIG.
```

---

## ADDM Key

| Finding | Expected Conclusion |
| ------- | ------------------- |
| High-load SQL | tune `g8m1s9k2p6z0a` first |
| User I/O waits | likely SQL-driven I/O, validate plan before blaming storage |
| Commit latency | lower priority, review transfer commit frequency |

Correct conclusion:

```text
ADDM supports the AWR evidence and tells us to run SQL Tuning Advisor on the top SQL.
```

---

## SQL Tuning Advisor Key

| Item | Expected Answer |
| ---- | --------------- |
| Recommendation | create index on `DAY2_TXN_BIG(customer_id, txn_ts DESC)` |
| Estimated benefit | 91.4% |
| Current plan | full table scan with high buffers and reads |
| Improved plan | descending index range scan with lower buffers and reads |
| Before buffers | 128,034 per execution |
| After buffers | 412 per execution |
| Safe directly? | no, validate DML/storage/duplicate index/change approval |

Correct final recommendation:

```text
Test an invisible composite index on CUSTOMER_ID, TXN_TS DESC.
If before/after metrics remain strong and DML overhead is acceptable, deploy through change control.
Rollback is DROP INDEX.
```

---

# Trainer Flow

Recommended 90-minute delivery:

| Time | Activity |
| ---- | -------- |
| 10 min | Explain incident scenario |
| 20 min | Trainees read AWR and fill evidence table |
| 15 min | Group review of AWR pain points |
| 15 min | Trainees read ADDM and map findings to AWR |
| 15 min | Trainees read SQL Tuning Advisor report |
| 15 min | Final DBA recommendation and discussion |

Keep repeating:

```text
Report evidence
  -> SQL_ID
  -> plan problem
  -> advisor recommendation
  -> before/after proof
  -> production risk
```
