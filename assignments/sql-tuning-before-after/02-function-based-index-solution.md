# Solution 2 - Function-Based Customer Search

## Expected Problem

The query applies a function to the indexed column:

```sql
UPPER(full_name)
```

A normal index on `FULL_NAME` stores the original value, not the uppercased expression. Oracle may therefore choose a full table scan.

## Before Test

```sql
ALTER SESSION SET statistics_level = ALL;

SELECT /* a2_customer_name_search */
       customer_id,
       full_name,
       mobile_no,
       status
FROM a2_customers
WHERE UPPER(full_name) = 'SOK CHAN';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected before observations:

```text
TABLE ACCESS FULL is likely
Predicate shows UPPER("FULL_NAME")='SOK CHAN'
Normal index IDX_A2_CUSTOMERS_NAME may not be used
```

## Tuning Change

```sql
CREATE INDEX idx_a2_customers_upper_name
ON a2_customers(UPPER(full_name));

BEGIN
  DBMS_STATS.GATHER_TABLE_STATS(
    ownname => USER,
    tabname => 'A2_CUSTOMERS',
    cascade => TRUE,
    method_opt => 'FOR ALL COLUMNS SIZE AUTO'
  );
END;
/
```

## After Test

```sql
SELECT /* a2_customer_name_search */
       customer_id,
       full_name,
       mobile_no,
       status
FROM a2_customers
WHERE UPPER(full_name) = 'SOK CHAN';

SELECT *
FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(NULL,NULL,'ALLSTATS LAST +PREDICATE'));
```

Expected after observations:

```text
INDEX RANGE SCAN on IDX_A2_CUSTOMERS_UPPER_NAME
Lower buffer gets
Lower elapsed time
```

## Alternative Application Fix

If the application stores a normalized search column, for example `FULL_NAME_UPPER`, the query can avoid applying a function at runtime:

```sql
WHERE full_name_upper = 'SOK CHAN'
```

That design can also support a normal index.

## Production Note

Function-based indexes add DML and storage cost. They are useful when the application cannot be changed and the expression is frequently searched.

