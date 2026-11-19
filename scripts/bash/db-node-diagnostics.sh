#!/bin/bash
# =============================================================================
#  db-node-diagnostics.sh – READ-ONLY health snapshot of a MariaDB/Galera node
#  AdminDay · Day 001 (CMS portal outages caused by an overloaded Galera node)
# =============================================================================
#  Changes nothing: only SHOW / EXPLAIN / small SELECTs, journalctl, du, dmesg.
#  Run as root on each Galera node. Output goes to the screen and to
#  /tmp/db_diag_<host>_<date>.txt (credentials masked).
#
#  Optional settings (environment variables):
#    PORTAL_DB      main portal database         (default: portal)
#    SYNC_TABLE     table hit by the sync query   (default: page)
#    SYNC_COLS      columns of the sync lookup    (default: source_id,source_db)
#    TENANT_PREFIX  prefix of tenant databases     (default: tenant_)
#    SYNC_KEY       config key enabling the sync   (default: SyncEnabled)
#
#  Do NOT run anything heavier (information_schema.tables size scans,
#  CHECK TABLE) during business hours – they can cause the very outage
#  you are investigating.
# =============================================================================
set -u
PORTAL_DB=${PORTAL_DB:-portal}
SYNC_TABLE=${SYNC_TABLE:-page}
SYNC_COLS=${SYNC_COLS:-source_id,source_db}
TENANT_PREFIX=${TENANT_PREFIX:-tenant_}
SYNC_KEY=${SYNC_KEY:-SyncEnabled}
OUT="/tmp/db_diag_$(hostname -s)_$(date +%Y%m%d_%H%M).txt"
MYSQL="timeout 60 mysql --connect-timeout=10"

[ "$(id -u)" -eq 0 ] || { echo "Run as root."; exit 1; }
section() { printf '\n== %s\n' "$1"; }
mask()    { sed -E 's/(auth=|password=)[^"&[:space:]]+/\1***/Ig'; }

{
echo "host: $(hostname -s)  date: $(date '+%F %T')"

section "Resources"
echo "vCPU: $(nproc)"; free -m; uptime

section "Buffer pool vs data size"
$MYSQL -e "SELECT @@version AS version,
                  ROUND(@@innodb_buffer_pool_size/1048576) AS buffer_pool_MB,
                  @@slow_query_log AS slow_log, @@long_query_time AS slow_log_s;"
DATADIR=$($MYSQL -Nse "SELECT @@datadir")
echo "data size: $(du -sh "$DATADIR" 2>/dev/null | cut -f1)   (measured with du, not information_schema)"

section "InnoDB / server counters since start"
$MYSQL -e "SHOW GLOBAL STATUS WHERE Variable_name IN
  ('Uptime','Questions','Slow_queries','Threads_running','Max_used_connections',
   'Innodb_buffer_pool_read_requests','Innodb_buffer_pool_reads','Innodb_buffer_pool_wait_free',
   'Created_tmp_tables','Created_tmp_disk_tables','Innodb_row_lock_time_max');"

section "Galera"
$MYSQL -e "SHOW GLOBAL STATUS WHERE Variable_name IN
  ('wsrep_cluster_size','wsrep_cluster_status','wsrep_local_state_comment',
   'wsrep_flow_control_paused','wsrep_local_recv_queue_avg','wsrep_local_send_queue_avg');"
echo "client connections by source host (is this node taking all the traffic?):"
$MYSQL -Nse "SELECT SUBSTRING_INDEX(host,':',1), COUNT(*) FROM information_schema.processlist
             GROUP BY 1 ORDER BY 2 DESC LIMIT 10;"

if $MYSQL -Nse "SHOW DATABASES LIKE '$PORTAL_DB'" | grep -q .; then
  section "Index check: $PORTAL_DB.$SYNC_TABLE ($SYNC_COLS)"
  $MYSQL -e "SELECT index_name, GROUP_CONCAT(column_name ORDER BY seq_in_index) AS cols
             FROM information_schema.statistics
             WHERE table_schema='$PORTAL_DB' AND table_name='$SYNC_TABLE' GROUP BY index_name;"
  c1=${SYNC_COLS%%,*}; c2=${SYNC_COLS#*,}
  echo "EXPLAIN (type: ALL = full table scan):"
  $MYSQL "$PORTAL_DB" -e "EXPLAIN SELECT 1 FROM \`$SYNC_TABLE\` WHERE \`$c1\`=1 AND \`$c2\`=1;"
fi

section "Tenants with sync enabled"
n=0
for db in $($MYSQL -Nse "SHOW DATABASES LIKE '${TENANT_PREFIX//_/\\_}%'"); do
  $MYSQL -Nse "SELECT 1 FROM \`$db\`.configuration WHERE name='$SYNC_KEY' AND value>0" 2>/dev/null | grep -q 1 && n=$((n+1))
done
echo "$n"

section "Databases created in the last 90 days (DDL on Galera blocks the cluster)"
lim=$(date -d '-90 days' +%s)
for d in "$DATADIR"/*/; do b=$(stat -c %W "$d" 2>/dev/null); [ "${b:-0}" -gt "$lim" ] 2>/dev/null && echo "$(date -d @"$b" '+%F %H:%M')  $(basename "$d")"; done | sort

section "InnoDB errors in the journal"
echo "journal starts: $(journalctl --no-pager -q | head -1 | cut -c1-15)"
journalctl -u mariadb --no-pager -q | grep -vE "InnoDB: [0-9a-f]{64}$" \
  | grep -E "\[ERROR\]|corruption|failed read|pending fsync" | cut -c1-200 | tail -15

section "Disk errors (dmesg times converted to wall clock)"
up=$(cut -d. -f1 /proc/uptime); now=$(date +%s)
dmesg | grep -iE "task abort|i/o error|hung_task" | tail -10 | while read -r l; do
  t=$(sed -E 's/^\[ *([0-9]+)\..*/\1/' <<<"$l"); echo "$(date -d @$((now-up+t)) '+%F %T')  ${l#*] }"; done
awk '$3 ~ /^sd[a-z]$/ && $4>0 {printf "%s avg read %.2f ms, avg write %.2f ms\n", $3, $7/$4, ($8>0?$11/$8:0)}' /proc/diskstats

section "Queries running longer than 2 s right now"
$MYSQL -e "SELECT id, db, time, state, LEFT(info,120) AS query FROM information_schema.processlist
           WHERE command<>'Sleep' AND time>2 ORDER BY time DESC LIMIT 15;"
} 2>&1 | mask | tee "$OUT"

echo; echo "saved: $OUT"
