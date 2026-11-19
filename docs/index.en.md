---
title: Home
hide:
  - navigation
  - toc
---

<section class="ad-hero">
<div>
<p class="ad-eyebrow">IT Operations Journal</p>
<h1 class="ad-title">AdminDay<span class="ad-dot">_</span></h1>
<p class="ad-lead">Real problems from IT administration work: from a monitoring alert, through diagnostics and commands, to the root cause and lessons learned. Data anonymized, commands and results real.</p>
<a class="md-button md-button--primary" href="workdays/day-001-cms-db-saturation/">Latest entry: Day 001</a>
<a class="md-button" href="workdays/">Workdays</a>
</div>
<div class="ad-term" aria-label="Sample diagnostic session">
<div class="ad-term-bar"><i></i><i></i><i></i><span>day-001 · diagnostics</span></div>
<pre><span class="e">[ALERT]</span> portal: Operation timed out after 15000 ms
<span class="p">$</span> journalctl --since today | grep -E "OOM|error"
<span class="m">  … no errors on web01 / web02</span>
<span class="p">$</span> awk '…' access_log   <span class="m"># entry order = request duration</span>
<span class="w">  02:43:08  GET /  ≥ 15 s  (both web nodes at once)</span>
<span class="p">$</span> mysql -e "SHOW GLOBAL STATUS …"
<span class="w">  innodb_buffer_pool_size = 128M  /  data: 26G</span>
<span class="p">$</span> EXPLAIN SELECT … FROM page WHERE source_id = ?
<span class="e">  type: ALL   rows: 40508   key: NULL</span>
<span class="ok">✔ root cause: db01 overloaded, missing index</span>
<span class="p">$</span> <span class="ad-cursor"></span></pre>
</div>
</section>

<div class="ad-kpis">
<div class="ad-kpi"><small>entries</small><b>1</b><span>real case, anonymized</span></div>
<div class="ad-kpi hot"><small>alerts analyzed</small><b>248</b><span>30 days of monitoring history</span></div>
<div class="ad-kpi warn"><small>hypotheses</small><b>10</b><span>6 rejected by data, 4 confirmed</span></div>
<div class="ad-kpi ok"><small>production changes</small><b>0</b><span>read-only diagnostics</span></div>
</div>

## Latest entry

<div class="ad-entry">
<div>
<span class="ad-pill hot">incident · real</span>
<h3><a href="workdays/day-001-cms-db-saturation/">Day 001 – CMS portal outages: an overloaded Galera database</a></h3>
<p>248 "15 s timeout" alerts in a month. Healthy web nodes, clean network, and the cause sat in the database: a 128 MB buffer for 26 GB of data, all traffic on one of three nodes, and a query scanning 394 MB on every page save.</p>
<span class="ad-pill">Linux</span> <span class="ad-pill">MariaDB Galera</span> <span class="ad-pill">Apache / PHP-FPM</span> <span class="ad-pill">Zabbix</span>
</div>
<figure class="ad-chart">
--8<-- "day001-daily.en.svg"
</figure>
</div>

## Areas

<div class="grid cards" markdown>

-   :material-calendar-check:{ .lg .middle } __Workdays__ <span class="ad-live">1 entry</span>

    ---

    Day-to-day administration work, one day at a time, in one documentation standard.

    [:octicons-arrow-right-24: Entries](workdays/index.md)

-   :material-alert-octagon:{ .lg .middle } __Incidents__ <span class="ad-live">1</span>

    ---

    Failures and outages: symptoms, hypotheses, evidence, root cause and fix plan.

    [:octicons-arrow-right-24: Incidents](incidents/index.md)

-   :material-server-network:{ .lg .middle } __Infrastructure__ <span class="ad-soon">soon</span>

    ---

    Linux, Windows Server, virtualization, networking, database clusters.

-   :material-shield-lock:{ .lg .middle } __Security__ <span class="ad-soon">soon</span>

    ---

    Vulnerabilities, hardening, access and credential reviews.

-   :material-robot-industrial:{ .lg .middle } __Automation__ <span class="ad-soon">soon</span>

    ---

    PowerShell, Bash, Python, Ansible: scripts from real tasks.

-   :material-file-document-multiple:{ .lg .middle } __Documentation__

    ---

    Entry standard and data anonymization rules for a public repository.

    [:octicons-arrow-right-24: Rules](about/anonymization.md)

</div>
