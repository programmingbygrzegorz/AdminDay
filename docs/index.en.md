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
<a class="md-button md-button--primary" href="workdays/day-003-media-rename-ticket/">Latest entry: Day 003</a>
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
<div class="ad-kpi"><small>entries</small><b>3</b><span>real case, anonymized</span></div>
<div class="ad-kpi hot"><small>alerts analyzed</small><b>248</b><span>30 days of monitoring history</span></div>
<div class="ad-kpi warn"><small>hypotheses</small><b>10</b><span>6 rejected by data, 4 confirmed</span></div>
<div class="ad-kpi ok"><small>production changes</small><b>0</b><span>read-only diagnostics</span></div>
</div>

## Latest entry

<div class="ad-entry">
<div>
<span class="ad-pill hot">ticket · real</span>
<h3><a href="workdays/day-003-media-rename-ticket/">Day 003 – Ticket: a media file rename that never saves</a></h3>
<p>Intake and triage of a unit's ticket: after renaming an uploaded file the old name stays or a "01" suffix appears. The entry covers symptom triage and an interim recommendation; root-cause analysis is out of scope.</p>
<span class="ad-pill">CMS</span> <span class="ad-pill">media</span> <span class="ad-pill">triage</span> <span class="ad-pill">multilingual</span>
</div>
</div>

## Areas

<div class="grid cards" markdown>

-   :material-calendar-check:{ .lg .middle } __Workdays__ <span class="ad-live">3 entries</span>

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
