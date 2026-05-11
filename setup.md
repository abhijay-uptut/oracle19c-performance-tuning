Here’s the clean command history you can save.

## 1. Edit listener host

```bash
vi $ORACLE_HOME/network/admin/listener.ora
```

Change old IP:

```text
HOST=192.168.1.28
```

to:

```text
HOST=0.0.0.0
```

Save in vi:

```text
Esc
:wq
```

---

## 2. Start listener

```bash
lsnrctl start
```

Check status:

```bash
lsnrctl status
```

At first it showed:

```text
The listener supports no services
```

---

## 3. Login as SYSDBA

```bash
sqlplus / as sysdba
```

Check PDBs:

```sql
show pdbs;
```

Output showed:

```text
PDB1  READ WRITE
```

---

## 4. Switch to PDB1

```sql
ALTER SESSION SET CONTAINER=PDB1;
```

Confirm:

```sql
show con_name;
```

---

## 5. Create user inside PDB1

```sql
CREATE USER abhijay IDENTIFIED BY abhijay123;
```

Grant permissions:

```sql
GRANT CONNECT, RESOURCE, DBA TO abhijay;
```

Give space quota:

```sql
ALTER USER abhijay QUOTA UNLIMITED ON USERS;
```

---

## 6. Fix local listener

Check old listener setting:

```sql
SHOW PARAMETER local_listener;
```

It showed old IP:

```text
192.168.1.28
```

Fix it:

```sql
ALTER SYSTEM SET LOCAL_LISTENER='(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))' SCOPE=BOTH;
```

Register services:

```sql
ALTER SYSTEM REGISTER;
```

Exit:

```sql
exit
```

---

## 7. Check listener again

```bash
lsnrctl status
```

Now it showed:

```text
Service "pdb1.localdomain" has 1 instance(s).
```

---

## 8. Connect as new user

```bash
sqlplus abhijay/abhijay123@//localhost:1521/pdb1.localdomain
```

Or inside SQL*Plus:

```sql
conn abhijay/abhijay123@//localhost:1521/pdb1.localdomain
```

Verify:

```sql
show user;
show con_name;
```

Expected:

```text
USER is "ABHIJAY"

CON_NAME
------------------------------
PDB1
```


You’re using **SQL Developer on Windows**, but Oracle DB is inside **Linux VM**.

So in SQL Developer:

```text
Hostname = localhost
```

means **Windows localhost**, not Linux VM localhost.

That’s why it says:

```text
No listener at host localhost port 1521
```

### Fix

In Linux VM terminal, run:

```bash
hostname -I
```

or:

```bash
ip addr show ens33
```

Find IP like:

```text
192.168.1.xx
```

Then in SQL Developer use:

```text
Username: abhijay
Password: abhijay123
Hostname: <Linux VM IP>
Port: 1521
Service name: pdb1.localdomain
```

Example:

```text
Hostname: 192.168.1.35
Port: 1521
Service name: pdb1.localdomain
```

Keep **Service name** selected, not SID.

Also make sure VM network is **Bridged** or **NAT with port forwarding**. Since PuTTY works, use the same VM IP you used in PuTTY.
