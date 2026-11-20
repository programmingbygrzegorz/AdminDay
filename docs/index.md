---
title: Start
hide:
  - navigation
  - toc
---

<section class="ad-hero">
<div>
<p class="ad-eyebrow">IT Operations Journal · dziennik administratora</p>
<h1 class="ad-title">AdminDay<span class="ad-dot">_</span></h1>
<p class="ad-lead">Prawdziwe problemy z pracy administratora IT: od alertu w monitoringu, przez diagnostykę i polecenia, do przyczyny i wniosków. Dane zanonimizowane, polecenia i wyniki prawdziwe.</p>
<a class="md-button md-button--primary" href="workdays/day-003-media-rename-ticket/">Najnowszy wpis: Day 003</a>
<a class="md-button" href="workdays/">Dziennik pracy</a>
</div>
<div class="ad-term" aria-label="Przykładowy przebieg diagnozy">
<div class="ad-term-bar"><i></i><i></i><i></i><span>day-001 · diagnostics</span></div>
<pre><span class="e">[ALERT]</span> portal: Operation timed out after 15000 ms
<span class="p">$</span> journalctl --since today | grep -E "OOM|error"
<span class="m">  … brak błędów na web01 / web02</span>
<span class="p">$</span> awk '…' access_log   <span class="m"># kolejność wpisów = czas żądania</span>
<span class="w">  02:43:08  GET /  ≥ 15 s  (oba fronty naraz)</span>
<span class="p">$</span> mysql -e "SHOW GLOBAL STATUS …"
<span class="w">  innodb_buffer_pool_size = 128M  /  dane: 26G</span>
<span class="p">$</span> EXPLAIN SELECT … FROM page WHERE source_id = ?
<span class="e">  type: ALL   rows: 40508   key: NULL</span>
<span class="ok">✔ root cause: db01 przeciążony, brak indeksu</span>
<span class="p">$</span> <span class="ad-cursor"></span></pre>
</div>
</section>

<div class="ad-kpis">
<div class="ad-kpi"><small>wpisy</small><b>3</b><span>przypadek rzeczywisty, zanonimizowany</span></div>
<div class="ad-kpi hot"><small>alerty przeanalizowane</small><b>248</b><span>30 dni historii z monitoringu</span></div>
<div class="ad-kpi warn"><small>hipotezy</small><b>10</b><span>6 obalonych danymi, 4 potwierdzone</span></div>
<div class="ad-kpi ok"><small>zmiany na produkcji</small><b>0</b><span>diagnoza tylko na odczycie</span></div>
</div>

## Najnowszy wpis

<div class="ad-entry">
<div>
<span class="ad-pill hot">zgłoszenie · rzeczywiste</span>
<h3><a href="workdays/day-003-media-rename-ticket/">Day 003 – Zgłoszenie: zmiana nazwy pliku w CMS nie zostaje zapisana</a></h3>
<p>Przyjęcie i klasyfikacja zgłoszenia od jednostki: po zmianie nazwy wgranego pliku zostaje stara nazwa albo pojawia się sufiks „01”. Wpis pokazuje rozpoznanie objawu (triage) i zalecenie tymczasowe; analiza przyczyny jest poza zakresem.</p>
<span class="ad-pill">CMS</span> <span class="ad-pill">media</span> <span class="ad-pill">triage</span> <span class="ad-pill">wielojęzyczność</span>
</div>
</div>

## Obszary

<div class="grid cards" markdown>

-   :material-calendar-check:{ .lg .middle } __Dziennik pracy__ <span class="ad-live">3 wpisy</span>

    ---

    Codzienna praca administratora, dzień po dniu, w jednym standardzie dokumentacji.

    [:octicons-arrow-right-24: Wpisy](workdays/index.md)

-   :material-alert-octagon:{ .lg .middle } __Incydenty__ <span class="ad-live">1</span>

    ---

    Awarie i przestoje: objawy, hipotezy, dowody, przyczyna i plan naprawy.

    [:octicons-arrow-right-24: Incydenty](incidents/index.md)

-   :material-server-network:{ .lg .middle } __Infrastruktura__ <span class="ad-soon">wkrótce</span>

    ---

    Linux, Windows Server, wirtualizacja, sieci, klastry baz danych.

-   :material-shield-lock:{ .lg .middle } __Bezpieczeństwo__ <span class="ad-soon">wkrótce</span>

    ---

    Podatności, utwardzanie systemów, przeglądy uprawnień i haseł.

-   :material-robot-industrial:{ .lg .middle } __Automatyzacja__ <span class="ad-soon">wkrótce</span>

    ---

    PowerShell, Bash, Python, Ansible: skrypty z prawdziwych zadań.

-   :material-file-document-multiple:{ .lg .middle } __Dokumentacja__

    ---

    Standard wpisu i zasady anonimizacji danych w publicznym repozytorium.

    [:octicons-arrow-right-24: Zasady](about/anonymization.md)

</div>
