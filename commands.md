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