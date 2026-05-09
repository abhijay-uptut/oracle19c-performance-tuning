1. connect to docker oracle instance:
```
docker exec -it oracle-ee bash
```

2. connect to sqlplus:
```
sqlplus / as sysdba
```

3. to exit sqlplus:
```
exit;
```

4. look for the service names to connect:
```
SQL> select name from v$services;

NAME
----------------------------------------------------------------
ORCLCDBXDB
SYS$BACKGROUND
SYS$USERS
ORCLCDB
orclpdb1
```

Step 1: Switch into PDB

```
ALTER SESSION SET CONTAINER=ORCLPDB1;
```

Step 2: Confirm you are inside PDB

```
SHOW CON_NAME;
```

Step 3: Create lab user
```
CREATE USER abhijay IDENTIFIED BY abhijay123;
```

Then give permissions:

```
GRANT CONNECT, RESOURCE, DBA TO abhijay;
ALTER USER abhijay QUOTA UNLIMITED ON USERS;
```
For training labs, this is fine.

Run this inside SQLPlus:
```
conn abhijay/abhijay123@orclpdb1
```



## Step 2: Create the `transactions` table

Paste this in SQL Developer and press **F5**:

```sql
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE transactions PURGE';
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

CREATE TABLE transactions (
  transaction_id    NUMBER PRIMARY KEY,
  customer_id       NUMBER,
  account_id        NUMBER,
  branch_id         NUMBER,
  transaction_date  DATE,
  transaction_type  VARCHAR2(20),
  amount            NUMBER(12,2),
  status            VARCHAR2(20),
  remarks           VARCHAR2(200)
);
```

Meaning:

* First block deletes old `transactions` table if it exists.
* `CREATE TABLE` makes the table for Day 1 labs.
* This table stores fake banking transaction data.

Step 3: Insert 300,000 transaction rows

Paste this and press F5:

```
BEGIN
  FOR i IN 1..300000 LOOP
    INSERT INTO transactions (
      transaction_id,
      customer_id,
      account_id,
      branch_id,
      transaction_date,
      transaction_type,
      amount,
      status,
      remarks
    )
    VALUES (
      i,
      MOD(i, 10000) + 1,
      MOD(i, 50000) + 1,
      MOD(i, 100) + 1,
      SYSDATE - MOD(i, 730),
      CASE MOD(i, 4)
        WHEN 0 THEN 'DEBIT'
        WHEN 1 THEN 'CREDIT'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'ATM'
      END,
      ROUND(DBMS_RANDOM.VALUE(100, 100000), 2),
      CASE MOD(i, 5)
        WHEN 0 THEN 'FAILED'
        ELSE 'SUCCESS'
      END,
      'Banking transaction test data'
    );

    IF MOD(i, 10000) = 0 THEN
      COMMIT;
    END IF;
  END LOOP;
END;
/

COMMIT;

```