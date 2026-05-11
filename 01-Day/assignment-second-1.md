# Assignment First 1 - Banking Index Design Lab

# Scenario

You are supporting the card authorization platform of a bank.

The fraud operations team has reported that several screens are slow during business hours:

* recent card activity lookup
* authorization reference lookup
* merchant investigation search
* fraud review queue
* failed authorization monitoring

Your task is to study the workload queries, inspect their execution plans, and create suitable indexes.

Do not create indexes blindly. For every index you create, you must be able to explain:

* which query it supports
* why the column order is correct
* whether the predicate is selective
* whether the index may add write cost
* whether the before and after plans prove improvement

---

# Setup Instructions

Run the following script first.

This script only creates the table and seed data. It does not create the indexes required for the assignment.

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON

BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE card_authorizations PURGE';
EXCEPTION
  WHEN OTHERS THEN
    IF SQLCODE != -942 THEN
      RAISE;
    END IF;
END;
/

CREATE TABLE card_authorizations (
    auth_id            NUMBER PRIMARY KEY,
    card_id            NUMBER,
    customer_id        NUMBER,
    branch_id          NUMBER,
    auth_reference     VARCHAR2(30),
    merchant_name      VARCHAR2(100),
    merchant_category  VARCHAR2(30),
    terminal_id        VARCHAR2(30),
    auth_time          DATE,
    amount             NUMBER(12,2),
    currency_code      VARCHAR2(3),
    auth_status        VARCHAR2(20),
    risk_score         NUMBER(3),
    channel            VARCHAR2(20),
    response_code      VARCHAR2(10)
);

BEGIN
  FOR i IN 1..250000 LOOP
    INSERT INTO card_authorizations (
      auth_id,
      card_id,
      customer_id,
      branch_id,
      auth_reference,
      merchant_name,
      merchant_category,
      terminal_id,
      auth_time,
      amount,
      currency_code,
      auth_status,
      risk_score,
      channel,
      response_code
    )
    VALUES (
      i,
      CASE
        WHEN i <= 60000 THEN 900001
        ELSE MOD(i,40000) + 1
      END,
      MOD(i,15000) + 1,
      MOD(i,80) + 1,
      'AUTH' || LPAD(i,10,'0'),
      CASE
        WHEN MOD(i,500) = 0 THEN 'Acme Pay Services'
        WHEN MOD(i,500) = 1 THEN 'ACME PAY SERVICES'
        WHEN MOD(i,8) = 2 THEN 'Metro Fuel Station'
        WHEN MOD(i,8) = 3 THEN 'Global Travel Desk'
        WHEN MOD(i,8) = 4 THEN 'QuickMart Online'
        WHEN MOD(i,8) = 5 THEN 'City Hospital Billing'
        WHEN MOD(i,8) = 6 THEN 'Blue Electronics'
        ELSE 'Neighborhood Grocery'
      END,
      CASE MOD(i,6)
        WHEN 0 THEN 'GROCERY'
        WHEN 1 THEN 'FUEL'
        WHEN 2 THEN 'TRAVEL'
        WHEN 3 THEN 'HEALTHCARE'
        WHEN 4 THEN 'ECOMMERCE'
        ELSE 'ELECTRONICS'
      END,
      'TERM' || LPAD(MOD(i,500) + 1,5,'0'),
      SYSDATE - MOD(i,730),
      ROUND(DBMS_RANDOM.VALUE(5,250000),2),
      CASE WHEN MOD(i,20) = 0 THEN 'USD' ELSE 'MYR' END,
      CASE
        WHEN MOD(i,100) < 2 THEN 'HELD'
        WHEN MOD(i,100) < 8 THEN 'DECLINED'
        WHEN MOD(i,100) < 10 THEN 'REVERSED'
        ELSE 'APPROVED'
      END,
      CASE
        WHEN MOD(i,100) < 2 THEN 95 + MOD(i,5)
        WHEN MOD(i,100) < 8 THEN 70 + MOD(i,25)
        ELSE MOD(i,70)
      END,
      CASE MOD(i,4)
        WHEN 0 THEN 'POS'
        WHEN 1 THEN 'ATM'
        WHEN 2 THEN 'ECOM'
        ELSE 'MOBILE'
      END,
      CASE
        WHEN MOD(i,100) < 8 THEN '05'
        WHEN MOD(i,100) < 10 THEN '91'
        ELSE '00'
      END
    );

    IF MOD(i,10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

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

# Validate Setup

```sql
SELECT COUNT(*) AS total_authorizations
FROM card_authorizations;

SELECT auth_status, COUNT(*) AS row_count
FROM card_authorizations
GROUP BY auth_status
ORDER BY auth_status;

SELECT card_id, COUNT(*) AS row_count
FROM card_authorizations
WHERE card_id = 900001
GROUP BY card_id;

SELECT auth_id, auth_reference, merchant_name, auth_status, risk_score
FROM card_authorizations
WHERE auth_id IN (1000, 50000, 100000);
```

Expected observations:

```text
TOTAL_AUTHORIZATIONS = 250000
CARD_ID 900001 has many rows
HELD is a small percentage of the table
APPROVED is the majority of the table
Merchant names have mixed case
```

---

# Trainee Tasks

Use the following settings before testing:

```sql
SET LINESIZE 220
SET PAGESIZE 100
SET TIMING ON
ALTER SESSION SET statistics_level = ALL;
```

For every query below:

1. Run the query without adding a new index.
2. Capture the execution plan.
3. Decide whether an index is useful.
4. Create the index or indexes you think are appropriate.
5. Gather statistics after creating indexes.
6. Run the query again.
7. Compare the before and after plan.
8. Explain the reason for your index design.

Use this after running a query when you need runtime evidence:

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

---

# Workload Query 1 - Recent Activity For A Card

The card servicing screen shows the latest authorizations for one card.

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

Your task:

* decide the best index for this access pattern
* explain the column order
* check whether the sort operation changes after indexing

---

# Workload Query 2 - Authorization Reference Lookup

The dispute team searches by authorization reference copied from the payment switch.

```sql
SELECT *
FROM card_authorizations
WHERE auth_reference = 'AUTH0000123456';
```

Your task:

* decide whether this should use a unique or non-unique index
* explain why this lookup is highly selective

---

# Workload Query 3 - Case-Insensitive Merchant Investigation

Fraud analysts search for a merchant regardless of how the merchant name was stored.

```sql
SELECT auth_id,
       auth_time,
       merchant_name,
       amount,
       auth_status
FROM card_authorizations
WHERE UPPER(merchant_name) = 'ACME PAY SERVICES';
```

Your task:

* identify why a normal index on `merchant_name` may not be enough
* create an index that matches the query expression
* explain the difference between an access predicate and a filter predicate

---

# Workload Query 4 - Fraud Review Queue

Fraud operations reviews held authorizations with very high risk scores.

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

Your task:

* decide whether `auth_status` alone is enough
* decide the correct composite index
* explain how equality and range predicates affect index column order

---

# Workload Query 5 - Failed Authorizations By Terminal

Operations monitors declined transactions for a specific terminal during the last 7 days.

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

Your task:

* design a composite index for terminal-specific failed authorization monitoring
* justify the leading column
* explain whether all predicates can be used efficiently by the index

---

# Deliverable

Submit:

* the indexes you created
* before and after execution plans for each workload query
* a short explanation for each index
* one index you decided not to create, if any, and why
