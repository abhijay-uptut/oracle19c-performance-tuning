# Solution First 1 - Banking Index Design Lab

# Objective

This solution shows one reasonable indexing strategy for the card authorization workload.

The exact execution plan can vary by Oracle version, data statistics, and environment. Focus on the access path, predicate section, estimated rows, actual rows, buffers, and whether the index matches the SQL pattern.

---

# Common Session Settings

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
SET AUTOTRACE OFF
ALTER SESSION SET statistics_level = ALL;
```

Use this after running a query to inspect runtime evidence:

```sql
SELECT *
FROM TABLE(
  DBMS_XPLAN.DISPLAY_CURSOR(
    NULL,
    NULL,
    'ALLSTATS LAST +PREDICATE'
  )
);
```

Use this after index changes:

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname    => USER,
    tabname    => 'CARD_AUTHORIZATIONS',
    method_opt => 'FOR ALL COLUMNS SIZE AUTO',
    cascade    => TRUE
  );
END;
/
```

---

# Step 1 - Baseline The Workload

Before creating indexes, run each workload query and capture the plan.

Example:

```sql
EXPLAIN PLAN FOR
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE card_id = 900001
AND auth_time >= SYSDATE - 90
ORDER BY auth_time DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected before indexes:

```text
Most workload queries will either full scan CARD_AUTHORIZATIONS or do more work than needed.
```

Explanation:

The table has 250,000 rows. Without supporting secondary indexes, Oracle has limited choices. It may scan the table, apply filters, and sort the remaining rows.

---

# Step 2 - Query 1: Recent Activity For A Card

## Problem Query

```sql
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE card_id = 900001
AND auth_time >= SYSDATE - 90
ORDER BY auth_time DESC;
```

## Recommended Index

```sql
CREATE INDEX idx_ca_card_time_desc
ON card_authorizations(card_id, auth_time DESC);
```

## Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CARD_AUTHORIZATIONS', cascade => TRUE);
END;
/
```

## Validate

```sql
EXPLAIN PLAN FOR
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE card_id = 900001
AND auth_time >= SYSDATE - 90
ORDER BY auth_time DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
The index can use CARD_ID as the leading equality predicate and AUTH_TIME as the range predicate.
The descending date order may reduce or remove the need for a separate sort.
```

Explanation:

This screen starts with one card and then narrows to a date range. That makes `card_id` the correct leading column. `auth_time DESC` matches the requested latest-first display.

---

# Step 3 - Query 2: Authorization Reference Lookup

## Problem Query

```sql
SELECT *
FROM card_authorizations
WHERE auth_reference = 'AUTH0000123456';
```

## Recommended Index

```sql
CREATE UNIQUE INDEX idx_ca_auth_reference_uq
ON card_authorizations(auth_reference);
```

## Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CARD_AUTHORIZATIONS', cascade => TRUE);
END;
/
```

## Validate

```sql
EXPLAIN PLAN FOR
SELECT *
FROM card_authorizations
WHERE auth_reference = 'AUTH0000123456';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected after:

```text
INDEX UNIQUE SCAN IDX_CA_AUTH_REFERENCE_UQ
TABLE ACCESS BY INDEX ROWID CARD_AUTHORIZATIONS
```

Explanation:

`auth_reference` is generated as one unique value per authorization. A unique index communicates that rule to Oracle and supports a highly selective single-row lookup.

---

# Step 4 - Query 3: Case-Insensitive Merchant Investigation

## Problem Query

```sql
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE UPPER(merchant_name) = 'ACME PAY SERVICES';
```

## Incorrect Or Incomplete Index

```sql
CREATE INDEX idx_ca_merchant_name
ON card_authorizations(merchant_name);
```

Explanation:

A normal index on `merchant_name` matches predicates such as:

```sql
WHERE merchant_name = 'ACME PAY SERVICES'
```

It does not directly match:

```sql
WHERE UPPER(merchant_name) = 'ACME PAY SERVICES'
```

## Recommended Index

```sql
CREATE INDEX idx_ca_upper_merchant
ON card_authorizations(UPPER(merchant_name));
```

## Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CARD_AUTHORIZATIONS', cascade => TRUE);
END;
/
```

## Validate

```sql
EXPLAIN PLAN FOR
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE UPPER(merchant_name) = 'ACME PAY SERVICES';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected after:

```text
INDEX RANGE SCAN IDX_CA_UPPER_MERCHANT
```

Explanation:

The function-based index stores the expression `UPPER(merchant_name)`. The query predicate now matches the indexed expression, so Oracle can use it as an access predicate instead of applying the function as a filter after scanning many rows.

Production note:

This query may still return many rows because the merchant is common in the seed data. An index can help locate matching entries, but selectivity still matters.

---

# Step 5 - Query 4: Fraud Review Queue

## Problem Query

```sql
SELECT auth_id,
       card_id,
       auth_time,
       merchant_name,
       amount,
       risk_score
FROM card_authorizations
WHERE auth_status = 'HELD'
AND risk_score >= 95
ORDER BY risk_score DESC;
```

## Recommended Index

```sql
CREATE INDEX idx_ca_status_risk_desc
ON card_authorizations(auth_status, risk_score DESC);
```

## Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CARD_AUTHORIZATIONS', cascade => TRUE);
END;
/
```

## Validate

```sql
EXPLAIN PLAN FOR
SELECT auth_id,
       card_id,
       auth_time,
       merchant_name,
       amount,
       risk_score
FROM card_authorizations
WHERE auth_status = 'HELD'
AND risk_score >= 95
ORDER BY risk_score DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
The equality predicate on AUTH_STATUS comes first.
The range and ordering column RISK_SCORE comes next.
```

Explanation:

`auth_status = 'HELD'` is selective in this data set. Once Oracle finds held rows, `risk_score >= 95` narrows them further. The descending risk score order also matches the review queue priority.

Why not only `auth_status`?

An index on only `auth_status` can find held rows, but it cannot also support the risk score range and ordering. The composite index is better aligned to the whole query.

---

# Step 6 - Query 5: Failed Authorizations By Terminal

## Problem Query

```sql
SELECT auth_id,
       auth_time,
       card_id,
       amount,
       response_code
FROM card_authorizations
WHERE terminal_id = 'TERM00103'
AND auth_status = 'DECLINED'
AND auth_time >= SYSDATE - 7
ORDER BY auth_time DESC;
```

## Recommended Index

```sql
CREATE INDEX idx_ca_terminal_status_time
ON card_authorizations(terminal_id, auth_status, auth_time DESC);
```

## Gather Stats

```sql
BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(USER, 'CARD_AUTHORIZATIONS', cascade => TRUE);
END;
/
```

## Validate

```sql
EXPLAIN PLAN FOR
SELECT auth_id,
       auth_time,
       card_id,
       amount,
       response_code
FROM card_authorizations
WHERE terminal_id = 'TERM00103'
AND auth_status = 'DECLINED'
AND auth_time >= SYSDATE - 7
ORDER BY auth_time DESC;

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY);
```

Expected teaching point:

```text
TERMINAL_ID and AUTH_STATUS are equality predicates.
AUTH_TIME is a range predicate and also supports latest-first ordering.
```

Explanation:

The monitoring screen starts with one terminal, then one status, then a recent time window. Equality columns should generally come before the range column in this index. `auth_time DESC` matches the order required by the screen.

---

# Step 7 - Confirm Created Indexes

```sql
SELECT index_name,
       uniqueness,
       visibility
FROM user_indexes
WHERE table_name = 'CARD_AUTHORIZATIONS'
ORDER BY index_name;
```

```sql
SELECT index_name,
       column_name,
       column_position,
       descend
FROM user_ind_columns
WHERE table_name = 'CARD_AUTHORIZATIONS'
ORDER BY index_name, column_position;
```

For function-based indexes, inspect expressions:

```sql
SELECT index_name,
       column_expression,
       column_position
FROM user_ind_expressions
WHERE table_name = 'CARD_AUTHORIZATIONS'
ORDER BY index_name, column_position;
```

---

# Step 8 - Final Index List

```sql
CREATE INDEX idx_ca_card_time_desc
ON card_authorizations(card_id, auth_time DESC);

CREATE UNIQUE INDEX idx_ca_auth_reference_uq
ON card_authorizations(auth_reference);

CREATE INDEX idx_ca_upper_merchant
ON card_authorizations(UPPER(merchant_name));

CREATE INDEX idx_ca_status_risk_desc
ON card_authorizations(auth_status, risk_score DESC);

CREATE INDEX idx_ca_terminal_status_time
ON card_authorizations(terminal_id, auth_status, auth_time DESC);
```

---

# Step 9 - Discussion: Indexes Not To Create Blindly

Avoid creating these without stronger evidence:

```sql
CREATE INDEX idx_ca_auth_status
ON card_authorizations(auth_status);
```

Reason:

`auth_status` alone is not enough for most workload queries. `APPROVED` is the majority of rows, so this index may be low value for broad approved-status searches. For the fraud queue, `(auth_status, risk_score DESC)` is more useful.

```sql
CREATE INDEX idx_ca_merchant_name
ON card_authorizations(merchant_name);
```

Reason:

The workload query uses `UPPER(merchant_name)`. A normal index on `merchant_name` does not directly match that expression.

```sql
CREATE INDEX idx_ca_auth_time
ON card_authorizations(auth_time);
```

Reason:

The workload does not search by date alone. It searches by card plus date, or terminal plus status plus date. Indexes should follow workload patterns, not isolated columns.

---

# Step 10 - Production Explanation Template

For each index, trainees should be able to say:

```text
I created this index because the query filters first by <leading column>.
The next column supports <range/order/filter>.
The before plan showed <full scan/sort/filter>.
The after plan showed <index range scan/index unique scan/reduced sort>.
The index has DML cost, so it is justified only because this query is frequent or business critical.
```
