---
title: "Day 001 – CMS portal outages: an overloaded Galera database"
date: 2026-11-19
tags: [incident, linux, mariadb, galera, apache, php-fpm, zabbix]
---

# Day 001 – CMS portal outages: an overloaded Galera database

<div class="ad-pills">
<span class="ad-pill hot">production incident</span>
<span class="ad-pill">real case · anonymized</span>
<span class="ad-pill ok">root cause found</span>
<span class="ad-pill warn">fixes planned</span>
<span class="ad-pill">2026-11-19 · about 1 day</span>
</div>

<div class="ad-kpis">
<div class="ad-kpi hot"><small>alerts / 30 days</small><b>248</b><span>15 s timeout, usually about 1 min of outage</span></div>
<div class="ad-kpi hot"><small>InnoDB buffer</small><b>0.5%</b><span>128 MB of memory for 26 GB of data</span></div>
<div class="ad-kpi warn"><small>full table scan</small><b>394 MB</b><span>on every page save in 433 tenants</span></div>
<div class="ad-kpi ok"><small>production changes</small><b>0</b><span>read-only diagnostics</span></div>
</div>

!!! info "Anonymization"
    Names of organizations, vendors, products, domains, tenants, databases, IP addresses
    and credentials were removed or replaced. Commands and results are real; only identifiers
    were changed. See [Anonymization rules](../about/anonymization.md).

## 1. Scenario

Zabbix keeps raising alerts: the main portal serving many public-sector organizations
stops responding every now and then. The alert text:

```text
Operation timed out after 15000 milliseconds with 0 bytes received
```

The reporter said: *"it kept dropping at these times yesterday and today, it wasn't like this before"*.
Task: find the cause without changing anything in production unless agreed.

## 2. Environment

<figure class="ad-chart">
--8<-- "day001-architecture.en.svg"
<figcaption>The red, "flowing" line is all SQL and file traffic from both web nodes. It hits one node, even though the cluster has three. db02 and db03 only replicate.</figcaption>
</figure>

- **Application:** a commercial PHP CMS (Laravel and Yii2 modules), 400+ tenant sites on one
  installation, one database per tenant plus the main portal database.
- **Stack:** Rocky Linux 8, Apache httpd + PHP-FPM 8.4, MariaDB 10.11 (Galera), GlusterFS.
- **My access:** SSH on an account without `NOPASSWD` sudo. Root-only commands were run by the
  account owner in their own terminal and I analyzed the output. I ran no scripts on the servers,
  only single read-only commands.

## 3. Problem

- 248 alerts in 30 days. Each one means more than 15 s without a response, usually for about a minute.
- Until 13 Nov there were 1–5 alerts per day; **from 14 Nov there were 16–24 per day**.
- Fixed points: **01:30 every night** and **every Sunday 02:00–03:18** (outages up to 15 min).

<figure class="ad-chart">
--8<-- "day001-daily.en.svg"
<figcaption>Alerts per day (monitoring data, 248 events). Sundays always stand out. From 14 Nov there are 4–5× more alerts on regular days too.</figcaption>
</figure>

<figure class="ad-chart">
--8<-- "day001-heatmap.en.svg"
<figcaption>Start hour of every alert. Three patterns are visible: a vertical stripe at 01:00 (the 01:30 job every night), Sunday blocks at 02:00–03:00, and a cluster during office hours from 14 Nov.</figcaption>
</figure>

## 4. Investigation

I worked from the outside in: monitoring → load balancer → web nodes → application → database.
Each hypothesis was confirmed or rejected with data.

### The path in short

<ul class="ad-timeline">
<li><b>Alert and access</b><span>Key-based SSH to both web nodes, with no changes to sudo configuration.</span></li>
<li><b>Web nodes are healthy</b><span>No restarts, OOM kills or network errors during the alert windows.</span></li>
<li><b>Zabbix requests get 200…</b><span>…but the alert starts exactly 15 s after the request sent at <code>:08</code>, so the site responds too slowly.</span></li>
<li><b>Request duration from log entry order</b><span>Hundreds of requests ≥ 10 s per day, on both nodes at once and only PHP.</span></li>
<li><b>Config: everything goes to db01</b><span><code>DB_HOST</code> points to one of three Galera nodes and there is no query cache.</span></li>
<li class="hot"><b>128 MB InnoDB buffer for 26 GB of data</b><span>35.8 billion disk reads, 6.9 million waits for a free buffer page.</span></li>
<li class="hot"><b>Caught live: <code>type: ALL</code> over 394 MB</b><span>Page sync from 433 tenants without an index.</span></li>
<li><b>Scheduled jobs and DDL</b><span>01:30, Sunday 02:00 and new tenant creation line up with alerts.</span></li>
<li class="ok"><b>Report and fix plan</b><span>With no change in production.</span></li>
</ul>

### Hypothesis board

<div class="ad-hypo">
<div class="ad-h no"><small>rejected</small><b>One failing web node</b><span>Both were up and slowed down at the same time.</span></div>
<div class="ad-h no"><small>rejected</small><b>Network / load balancer</b><span>0 interface errors, traffic flows every second.</span></div>
<div class="ad-h no"><small>rejected</small><b>Delay on the monitoring side</b><span>The request arrives on time; the response is what's slow.</span></div>
<div class="ad-h no"><small>rejected</small><b>Bot traffic</b><span>Grew, but does not correlate with slow minutes.</span></div>
<div class="ad-h no"><small>rejected</small><b>Saturated PHP-FPM</b><span>The pool was not full during alerts.</span></div>
<div class="ad-h no"><small>rejected</small><b>Storage / disk</b><span>No I/O errors, &lt; 1 ms on average. One episode a year earlier.</span></div>
<div class="ad-h yes"><small>confirmed</small><b>db01 overloaded</b><span>128 MB buffer, 2 vCPU, all traffic, plus GlusterFS.</span></div>
<div class="ad-h yes"><small>confirmed</small><b>Missing index in page sync</b><span><code>EXPLAIN</code>: <code>type: ALL</code>, 40,508 rows.</span></div>
<div class="ad-h part"><small>trigger</small><b>Scheduled jobs</b><span>01:30 every night, Sunday 02:00, Daily.</span></div>
<div class="ad-h part"><small>trigger</small><b>DDL for new tenants</b><span>5 new databases in 9 minutes, with 3 alerts at the same time.</span></div>
</div>

### 4.1 Web nodes: system, services, memory

```bash
uptime; free -m; nproc
systemctl list-units --type=service --state=running --no-legend
journalctl --since "2026-11-18 00:00" -o short-iso      # restarts, OOM, errors
grep -E "pswpin|pswpout|oom_kill" /proc/vmstat
ip -s link                                              # interface errors / drops
```

**Result:** no service restarts, OOM kills or network errors during the alert windows
(0 errors, 0 dropped). Constant swapping instead, because PHP-FPM uses about 1 GB of the 1.7 GB RAM.

!!! note "Hypothesis rejected"
    A single failing web node: both nodes were fine, and the cause was elsewhere.

### 4.2 Do the Zabbix requests arrive at all?

```bash
grep -hi "zabbix" *access_log* | grep -E "19/Nov/2026:(02|03|06):" \
  | awk '{print substr($4,14,5), $1, $9, $7}' | sort | uniq -c
```

**Result:** every Zabbix request that reached Apache got **HTTP 200**. Some showed up late.
The key observation: each alert starts exactly **15 s after** the request sent at second `:08`,
which means the response took until the timeout.

### 4.3 Measuring response time without `%D` in LogFormat

Apache did not log request duration, but it **writes the log line only when the request finishes**.
If a line stamped `02:43:08` appears *after* lines stamped `02:43:20`, the request took at least 12 s:

```bash
awk 'FNR==1{mx=0}
     {split(substr($4,2),a,/[\/:]/); t=a[1]*86400+a[4]*3600+a[5]*60+a[6];
      if (mx-t>=10) print FILENAME, substr($4,2), ">=", mx-t, "s", $9, $7;
      if (t>mx) mx=t}' portal-access_log*
```

**Result:** hundreds of requests per day taking ≥ 10 s, **on both web nodes in the same minutes**.
Every alert that could be matched against the logs lined up with a slow request.

### 4.4 Bots? PHP-FPM? Static files?

| Test | Command (short) | Result |
|---|---|---|
| Bot traffic | `awk -F'"' '{print $6}' access_log \| sort \| uniq -c` | growth (AI and search crawlers), **but no correlation** with slow minutes |
| PHP-FPM pool | `grep "max_children" /var/log/php-fpm/error.log*` | **not** saturated during alerts |
| Static files | split slow requests into `.css/.js/.jpg` vs PHP | **only PHP requests** are slow |
| Application errors | `grep -iE "mysql\|pdo\|deadlock\|timeout" www-error.log*` | no errors, requests were just **waiting** |

**Conclusion:** both web nodes are waiting on a **shared backend** at the same time.

### 4.5 Application config: where does database traffic go?

```bash
grep -E "^DB_HOST" /var/www/app/.env
grep -E "session.save_(handler|path)" /etc/php-fpm.d/www.conf
```

**Result:** both web nodes connect **only to `db01`**. Sessions are stored in Redis, and the
application uses no query cache at all (no Redis, Memcached or APCu).

### 4.6 Database: Galera and MariaDB status

```sql
SHOW GLOBAL STATUS WHERE Variable_name IN
 ('wsrep_cluster_size','wsrep_cluster_status','wsrep_local_state_comment',
  'wsrep_flow_control_paused','Slow_queries','Max_used_connections',
  'Innodb_buffer_pool_reads','Innodb_buffer_pool_read_requests',
  'Innodb_buffer_pool_wait_free','Created_tmp_disk_tables');
SHOW GLOBAL VARIABLES WHERE Variable_name IN
 ('innodb_buffer_pool_size','slow_query_log','long_query_time','version');
```

| Metric | Value | Meaning |
|---|---|---|
| `wsrep_cluster_status` / `state` | Primary / Synced, 3 nodes | cluster is healthy |
| `wsrep_flow_control_paused` | ≈ 0 | replication does not block writes |
| `innodb_buffer_pool_size` | **128 MB** (default) | with **26 GB** of data |
| `Innodb_buffer_pool_reads` | ~35.8 billion | reads served from disk instead of RAM |
| `Innodb_buffer_pool_wait_free` | 6.9 million | waits for a free page in the buffer |
| `Created_tmp_disk_tables` | 21% of all | sorts spilling to disk |
| `Slow_queries` (> 10 s) | 16,370 | with the slow log turned off |
| load average (2 vCPU) | 2.4 / 3.0 / 4.4 | CPU run queue |

<figure class="ad-chart">
--8<-- "day001-buffer.en.svg"
<figcaption>The scale of the problem: 0.5% of the data fits in memory. The plan is 1 GB right away (no restart); after a RAM upgrade the buffer will cover most of the frequently used data.</figcaption>
</figure>

!!! warning "Lesson from this step"
    A size query against `information_schema.tables` across hundreds of databases hung for
    over 15 s and loaded production by itself. I stopped it and measured sizes with
    `du -s /var/lib/mysql/*/` instead, which does not touch the database.

### 4.7 Caught live: a full table scan

```sql
SELECT id, user, db, time, state, LEFT(info,120)
FROM information_schema.processlist
WHERE command <> 'Sleep' AND time > 1 ORDER BY time DESC;
-- portal | 4 s | Sending data | SELECT page_id FROM page WHERE source_id = ? AND source_db = ?

EXPLAIN SELECT page_id FROM page WHERE source_id = 1 AND source_db = 1;
-- type: ALL | key: NULL | rows: 40508      <- no index, full scan of 394 MB
```

In the application code, this query runs in the function that syncs a tenant page to the main
portal. It runs **on every page save** in the editor panel:

```bash
grep -rn "source_id" app/class/ | grep -i select
grep -rn "syncPage(" app/admin/ app/class/
```

I then checked how many tenants have sync enabled. The setting lives in the `configuration`
table of each tenant database:

```bash
for db in $(mysql -Nse "SHOW DATABASES LIKE 'tenant\_%'"); do
  mysql -Nse "SELECT 1 FROM \`$db\`.configuration
              WHERE name='SyncEnabled' AND value>0" 2>/dev/null
done | wc -l
# 433
```

**433 tenants.** Every page save in any of them scans the whole 394 MB table through a
128 MB buffer. The table grows with every synced page, so the problem gets worse over time.

### 4.8 Night and Sunday outages: scheduled jobs

I took the duration of each application cron session from the journal (start and stop of the
service user's session):

```bash
grep -E "(Started|Stopped) User Manager for UID 48" journal.log \
 | awk '...'   # sessions >= 25 s
```

and matched it against the job schedule (`app/Console/Kernel.php`):

| Time | Job | Alert |
|---|---|---|
| 01:30 daily | trash cleanup (pages + files) | **every night** |
| Sunday 02:00 | weekly jobs (database housekeeping, storage statistics) | 13–17 alerts, up to 15 min outage |
| 01:10 daily | "Daily" job, dies every night on the 256 MB `memory_limit` | occasional |
| :15 hourly | page activation/deactivation | when it runs > 80 s |

### 4.9 What else I checked (and ruled out)

```bash
stat -c %W /var/lib/mysql/*/          # database creation dates – new tenants
journalctl -u mariadb | grep -E "ERROR|corruption|pending fsync"
dmesg | grep -E "task abort|I/O error"   # + convert times using /proc/uptime
awk '$3 ~ /^sd/ {print $3, $7/$4 " ms read"}' /proc/diskstats
```

- **Creating 5 new tenant databases** (DDL on Galera) at 11:27–11:36 lined up exactly with alerts.
- **InnoDB errors** `Database page corruption on disk or a failed read` on 3 tables (15–17 Nov), to be verified with `CHECK TABLE`.
- **Storage:** SCSI aborts only in one episode a year earlier, and average disk latency < 1 ms. The current problem is not storage.
- **Log retention:** the database server journal reached back only 5 days, because audit records of a health-check command every few seconds filled it up.

## 5. Root cause

!!! danger "Root cause"
    **Node `db01` is undersized and misconfigured for its role.** The InnoDB buffer
    (128 MB for 26 GB of data), 2 vCPU and all application traffic on one of three nodes
    (with GlusterFS on the same machine) mean any heavier operation blocks the database for
    tens of seconds to minutes. Both web nodes then wait, and monitoring reports a timeout.

Triggers:

1. page sync from 400+ tenants, a full table scan on every save (missing index),
2. nightly and Sunday application jobs,
3. DDL when new tenants are created.

## 6. Resolution (planned)

I changed nothing in production. The changes need agreement with the database admin and the application vendor.

| Priority | Change | Owner |
|---|---|---|
| 1 | `innodb_buffer_pool_size` 128 MB → 1 GB (online, `SET GLOBAL`), then 1.5 GB, more RAM later | DB admin |
| 1 | index `ALTER TABLE page ADD INDEX (source_id, source_db)` at night (DDL on Galera blocks the cluster) | application vendor |
| 2 | `slow_query_log=ON`, `long_query_time=2` | DB admin |
| 2 | optimize the 01:30 / Sunday 02:00 / Daily jobs | application vendor |
| 3 | proxy in front of Galera (MaxScale / ProxySQL), spread reads across 3 nodes | infrastructure |
| 3 | move GlusterFS off the database nodes | infrastructure |
| 3 | `CHECK TABLE` on the affected tables, upgrade MariaDB 10.11.x | DB admin |
| 3 | credentials in world-readable files and in the audit log: rotate and restrict access | security |

Buffer change procedure (step by step, with rollback):

```bash
free -m; ps -C mariadbd,glusterfsd -o rss=,comm=
mysql -e "SET GLOBAL innodb_buffer_pool_size = 1073741824;"
mysql -e "SHOW STATUS LIKE 'Innodb_buffer_pool_resize_status';"
# persist: [mysqld] innodb_buffer_pool_size = 1G
# rollback: SET GLOBAL innodb_buffer_pool_size = 134217728;
```

## 7. Verification (after rollout)

- [ ] growth rate of `Innodb_buffer_pool_reads` before vs after (hourly comparison)
- [ ] `EXPLAIN` of the sync query: `type: ref`, new index used
- [ ] Zabbix alert count: one week before vs one week after
- [ ] slow log: remaining queries > 2 s

## 8. Lessons learned

- **Averages lie.** A 0.1 ms average disk read and a "healthy" cluster do not rule out
  multi-second stalls. Look at individual events.
- **The access log holds more than it seems.** Entry order lets you estimate request duration
  even without `%D` in `LogFormat`. Add it anyway.
- **HA cluster ≠ load distribution.** Three Galera nodes, but the application only knows one.
- **Defaults are not configuration.** `innodb_buffer_pool_size=128M` in production means
  nobody tuned the database.
- **Diagnostics must not hurt.** Heavy `information_schema` queries and a recursive `grep` over
  a 266 GB network volume can load production by themselves. I stopped both.
- **Data first, conclusions second.** The "bots", "network", "Zabbix" and "storage" hypotheses
  all made sense, and the data rejected each of them.
- **Log retention is part of monitoring.** Without history from before 14 Nov there was no way
  to prove what changed that day.

## 9. Evidence (anonymized)

- 30-day alert distribution: 248 events, fixed 01:30 and Sunday 02:00, jump from 14 Nov.
- `EXPLAIN` of the sync query: `type: ALL`, `rows: 40508`.
- InnoDB and Galera counters from `SHOW GLOBAL STATUS`.
- Read-only diagnostic script: [`scripts/bash/db-node-diagnostics.sh`](https://github.com/programmingbygrzegorz/AdminDay/blob/main/scripts/bash/db-node-diagnostics.sh).
