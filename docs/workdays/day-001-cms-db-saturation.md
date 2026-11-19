---
title: "Day 001 – Przestoje portalu CMS: przeciążona baza Galera"
date: 2026-11-19
tags: [incident, linux, mariadb, galera, apache, php-fpm, zabbix]
---

# Day 001 – Przestoje portalu CMS: przeciążona baza Galera

<div class="ad-pills">
<span class="ad-pill hot">incydent produkcyjny</span>
<span class="ad-pill">przypadek rzeczywisty · zanonimizowany</span>
<span class="ad-pill ok">przyczyna ustalona</span>
<span class="ad-pill warn">poprawki zaplanowane</span>
<span class="ad-pill">19.11.2026 · ok. 1 dzień</span>
</div>

<div class="ad-kpis">
<div class="ad-kpi hot"><small>alerty / 30 dni</small><b>248</b><span>timeout 15 s, zwykle ok. 1 min przestoju</span></div>
<div class="ad-kpi hot"><small>bufor InnoDB</small><b>0,5%</b><span>128 MB pamięci na 26 GB danych</span></div>
<div class="ad-kpi warn"><small>pełny przegląd tabeli</small><b>394 MB</b><span>przy każdym zapisie strony w 433 jednostkach</span></div>
<div class="ad-kpi ok"><small>zmiany na produkcji</small><b>0</b><span>diagnoza wyłącznie na odczycie</span></div>
</div>

!!! info "Anonimizacja"
    Nazwy organizacji, dostawców, produktów, domen, jednostek, baz danych, adresy IP
    i dane logowania zostały usunięte lub zastąpione. Polecenia i wyniki są prawdziwe,
    zmienione są tylko identyfikatory. Szczegóły: [Zasady anonimizacji](../about/anonymization.md).

## 1. Scenariusz

Monitoring (Zabbix) wysyła serię alertów: główny portal wielu jednostek publicznych
co jakiś czas przestaje odpowiadać. Treść alertu:

```text
Operation timed out after 15000 milliseconds with 0 bytes received
```

Zgłaszający: *„w takich godzinach wczoraj i dzisiaj zrywało połączenie, wcześniej tak nie było”*.
Zadanie: ustalić przyczynę, nie zmieniając niczego na produkcji bez uzgodnienia.

## 2. Środowisko

<figure class="ad-chart">
--8<-- "day001-architecture.pl.svg"
<figcaption>Czerwona, „płynąca” linia to cały ruch SQL i plików obu frontów. Trafia na jeden węzeł, choć klaster ma trzy. db02 i db03 tylko replikują dane.</figcaption>
</figure>

- **Aplikacja:** komercyjny CMS w PHP (moduły w Laravel i Yii2), ponad 400 serwisów jednostek
  na wspólnej instalacji, osobna baza dla każdej jednostki oraz baza portalu głównego.
- **System:** Rocky Linux 8, Apache httpd + PHP-FPM 8.4, MariaDB 10.11 (Galera), GlusterFS.
- **Moje uprawnienia:** SSH na konto bez `NOPASSWD` w sudo. Polecenia wymagające roota
  wykonywał właściciel konta w swoim terminalu, a ja analizowałem wynik. Nie uruchamiałem
  żadnych skryptów na serwerach, tylko pojedyncze polecenia odczytu.

## 3. Problem

- 248 alertów w ciągu 30 dni. Każdy oznacza brak odpowiedzi strony przez ponad 15 s, zwykle przez ok. 1 min.
- Do 13.11 było 1–5 alertów dziennie, **od 14.11 jest ich 16–24 dziennie**.
- Stałe punkty: **01:30 każdej nocy** oraz **każda niedziela 02:00–03:18** (przerwy do 15 min).

<figure class="ad-chart">
--8<-- "day001-daily.pl.svg"
<figcaption>Liczba alertów dziennie (dane z monitoringu, 248 zdarzeń). Niedziele wyróżniają się zawsze. Od 14.11 alertów jest 4–5 razy więcej także w zwykłe dni.</figcaption>
</figure>

<figure class="ad-chart">
--8<-- "day001-heatmap.pl.svg"
<figcaption>Godzina rozpoczęcia każdego alertu. Widać trzy wzorce: pionowy pas o 01:00 (zadanie o 01:30 każdej nocy), niedzielne bloki o 02:00–03:00 i zagęszczenie w godzinach pracy od 14.11.</figcaption>
</figure>

## 4. Diagnostyka

Szedłem od zewnątrz do środka: monitoring → load balancer → fronty → aplikacja → baza.
Każdą hipotezę starałem się potwierdzić albo obalić danymi.

### Przebieg w skrócie

<ul class="ad-timeline">
<li><b>Alert i dostęp</b><span>Zestawienie dostępu SSH kluczem do obu frontów, bez zmian w konfiguracji sudo.</span></li>
<li><b>Fronty zdrowe</b><span>Brak restartów, OOM i błędów sieci w godzinach alertów.</span></li>
<li><b>Żądania Zabbixa dostają 200…</b><span>…ale alert startuje równo 15 s po żądaniu z <code>:08</code>, czyli strona odpowiada za wolno.</span></li>
<li><b>Czas żądania z kolejności wpisów w logu</b><span>Setki żądań ≥ 10 s dziennie, na obu frontach naraz i tylko PHP.</span></li>
<li><b>Konfiguracja: wszystko idzie na db01</b><span><code>DB_HOST</code> wskazuje jeden z trzech węzłów Galery i nie ma cache zapytań.</span></li>
<li class="hot"><b>Bufor InnoDB 128 MB na 26 GB danych</b><span>35,8 mld odczytów z dysku, 6,9 mln razy czekanie na wolny bufor.</span></li>
<li class="hot"><b>Złapane na żywo: <code>type: ALL</code> na 394 MB</b><span>Synchronizacja stron z 433 jednostek bez indeksu.</span></li>
<li><b>Zadania cykliczne i DDL</b><span>01:30, niedziela 02:00 i zakładanie nowych jednostek pokrywają się z alertami.</span></li>
<li class="ok"><b>Raport i plan naprawy</b><span>Bez żadnej zmiany na produkcji.</span></li>
</ul>

### Tablica hipotez

<div class="ad-hypo">
<div class="ad-h no"><small>obalona</small><b>Awaria jednego frontu</b><span>Oba działały, zwalniały jednocześnie.</span></div>
<div class="ad-h no"><small>obalona</small><b>Sieć / load balancer</b><span>0 błędów na interfejsach, ruch płynie w każdej sekundzie.</span></div>
<div class="ad-h no"><small>obalona</small><b>Opóźnienie po stronie monitoringu</b><span>Żądanie dociera na czas, a wolna jest odpowiedź.</span></div>
<div class="ad-h no"><small>obalona</small><b>Ruch botów</b><span>Wzrósł, ale nie koreluje z wolnymi minutami.</span></div>
<div class="ad-h no"><small>obalona</small><b>Zapchany PHP-FPM</b><span>Pula nie była pełna w czasie alertów.</span></div>
<div class="ad-h no"><small>obalona</small><b>Storage / dysk</b><span>Brak błędów I/O, średnio &lt; 1 ms. Jeden epizod rok wcześniej.</span></div>
<div class="ad-h yes"><small>potwierdzona</small><b>db01 przeciążony</b><span>Bufor 128 MB, 2 vCPU, cały ruch, a do tego GlusterFS.</span></div>
<div class="ad-h yes"><small>potwierdzona</small><b>Brak indeksu w synchronizacji</b><span><code>EXPLAIN</code>: <code>type: ALL</code>, 40 508 wierszy.</span></div>
<div class="ad-h part"><small>wyzwalacz</small><b>Zadania cykliczne</b><span>01:30 co noc, niedziela 02:00, Daily.</span></div>
<div class="ad-h part"><small>wyzwalacz</small><b>DDL nowych jednostek</b><span>5 nowych baz w 9 minut, a w tym samym czasie 3 alerty.</span></div>
</div>

### 4.1 Fronty: system, usługi, pamięć

```bash
uptime; free -m; nproc
systemctl list-units --type=service --state=running --no-legend
journalctl --since "2026-11-18 00:00" -o short-iso      # restarty, OOM, błędy
grep -E "pswpin|pswpout|oom_kill" /proc/vmstat
ip -s link                                              # błędy / dropy na interfejsie
```

**Wynik:** w godzinach alertów nie było restartów usług, OOM ani błędów sieci (0 errors, 0 dropped).
Widać za to stałe swapowanie, bo przy 1,7 GB RAM PHP-FPM zajmuje ok. 1 GB.

!!! note "Hipoteza obalona"
    Awaria pojedynczego frontu: oba fronty działały, a przyczyna leżała gdzie indziej.

### 4.2 Czy żądania Zabbixa w ogóle docierają?

```bash
grep -hi "zabbix" *access_log* | grep -E "19/Nov/2026:(02|03|06):" \
  | awk '{print substr($4,14,5), $1, $9, $7}' | sort | uniq -c
```

**Wynik:** każde żądanie Zabbixa, które dotarło do Apache, dostało **HTTP 200**.
Część z nich pojawiała się w logu z opóźnieniem. Kluczowe było spostrzeżenie, że alert
startuje dokładnie **15 s po** żądaniu z sekundy `:08`, czyli odpowiedź trwała do timeoutu.

### 4.3 Jak zmierzyć czas odpowiedzi bez `%D` w LogFormat?

Apache nie logował czasu obsługi żądania, ale **zapisuje linię do logu dopiero po zakończeniu żądania**.
Jeśli linia z czasem `02:43:08` stoi w pliku *po* liniach z `02:43:20`, to żądanie trwało co najmniej 12 s:

```bash
awk 'FNR==1{mx=0}
     {split(substr($4,2),a,/[\/:]/); t=a[1]*86400+a[4]*3600+a[5]*60+a[6];
      if (mx-t>=10) print FILENAME, substr($4,2), ">=", mx-t, "s", $9, $7;
      if (t>mx) mx=t}' portal-access_log*
```

**Wynik:** setki żądań dziennie trwających ≥ 10 s, **na obu frontach w tych samych minutach**.
Każdy alert, który dało się porównać z logami, pokrywał się z wolnym żądaniem.

### 4.4 Boty? PHP-FPM? Pliki statyczne?

| Test | Polecenie (skrót) | Wynik |
|---|---|---|
| Ruch botów | `awk -F'"' '{print $6}' access_log \| sort \| uniq -c` | wzrost (crawlery AI i wyszukiwarek), **ale bez korelacji** z wolnymi minutami |
| Pula PHP-FPM | `grep "max_children" /var/log/php-fpm/error.log*` | w godzinach alertów **nie** była pełna |
| Pliki statyczne | podział wolnych żądań na `.css/.js/.jpg` i PHP | wolne **tylko żądania PHP** |
| Błędy aplikacji | `grep -iE "mysql\|pdo\|deadlock\|timeout" www-error.log*` | brak błędów, żądania tylko **czekały** |

**Wniosek:** obie maszyny czekają jednocześnie na **wspólny backend**.

### 4.5 Konfiguracja aplikacji: dokąd idzie ruch do bazy?

```bash
grep -E "^DB_HOST" /var/www/app/.env
grep -E "session.save_(handler|path)" /etc/php-fpm.d/www.conf
```

**Wynik:** oba fronty łączą się **tylko z `db01`**. Sesje trzymane są w Redisie, a aplikacja
nie używa żadnego cache zapytań (ani Redisa, ani Memcached, ani APCu).

### 4.6 Baza: stan Galery i MariaDB

```sql
SHOW GLOBAL STATUS WHERE Variable_name IN
 ('wsrep_cluster_size','wsrep_cluster_status','wsrep_local_state_comment',
  'wsrep_flow_control_paused','Slow_queries','Max_used_connections',
  'Innodb_buffer_pool_reads','Innodb_buffer_pool_read_requests',
  'Innodb_buffer_pool_wait_free','Created_tmp_disk_tables');
SHOW GLOBAL VARIABLES WHERE Variable_name IN
 ('innodb_buffer_pool_size','slow_query_log','long_query_time','version');
```

| Wskaźnik | Wartość | Znaczenie |
|---|---|---|
| `wsrep_cluster_status` / `state` | Primary / Synced, 3 węzły | klaster zdrowy |
| `wsrep_flow_control_paused` | ≈ 0 | replikacja nie blokuje zapisów |
| `innodb_buffer_pool_size` | **128 MB** (domyślne) | przy **26 GB** danych |
| `Innodb_buffer_pool_reads` | ~35,8 mld | odczyty z dysku zamiast z RAM |
| `Innodb_buffer_pool_wait_free` | 6,9 mln | czekanie na wolne miejsce w buforze |
| `Created_tmp_disk_tables` | 21% wszystkich | sortowania na dysku |
| `Slow_queries` (> 10 s) | 16 370 | przy wyłączonym slow logu |
| load average (2 vCPU) | 2,4 / 3,0 / 4,4 | kolejka do CPU |

<figure class="ad-chart">
--8<-- "day001-buffer.pl.svg"
<figcaption>Skala problemu: w pamięci mieści się 0,5% danych. Plan zakłada 1 GB od razu (bez restartu), a po dołożeniu RAM bufor obejmie większość danych często używanych.</figcaption>
</figure>

!!! warning "Lekcja z tego kroku"
    Zapytanie o rozmiar baz przez `information_schema.tables` przy setkach baz zawiesiło
    się na ponad 15 s i samo obciążało produkcję. Przerwałem je i zmierzyłem rozmiar
    przez `du -s /var/lib/mysql/*/`, co nie dotyka bazy.

### 4.7 Złapane na żywo: pełny przegląd tabeli

```sql
SELECT id, user, db, time, state, LEFT(info,120)
FROM information_schema.processlist
WHERE command <> 'Sleep' AND time > 1 ORDER BY time DESC;
-- portal | 4 s | Sending data | SELECT page_id FROM page WHERE source_id = ? AND source_db = ?

EXPLAIN SELECT page_id FROM page WHERE source_id = 1 AND source_db = 1;
-- type: ALL | key: NULL | rows: 40508      <- brak indeksu, pełny przegląd 394 MB
```

W kodzie aplikacji to zapytanie wykonuje funkcja synchronizująca stronę jednostki z portalem głównym.
Uruchamia się **przy każdym zapisie strony** w panelu redaktora:

```bash
grep -rn "source_id" app/class/ | grep -i select
grep -rn "syncPage(" app/admin/ app/class/
```

Sprawdziłem, ile jednostek ma włączoną synchronizację. Ustawienie siedzi w tabeli
`configuration` w bazie każdej jednostki:

```bash
for db in $(mysql -Nse "SHOW DATABASES LIKE 'tenant\_%'"); do
  mysql -Nse "SELECT 1 FROM \`$db\`.configuration
              WHERE name='SyncEnabled' AND value>0" 2>/dev/null
done | wc -l
# 433
```

**433 jednostki.** Każdy zapis strony w dowolnej z nich przegląda całą tabelę 394 MB
przez bufor 128 MB. Tabela rośnie z każdą zsynchronizowaną stroną, więc problem narasta z czasem.

### 4.8 Nocne i niedzielne przestoje: zadania cykliczne

Czas trwania sesji crona aplikacji wyliczyłem z journala (start i stop sesji użytkownika usługi):

```bash
grep -E "(Started|Stopped) User Manager for UID 48" journal.log \
 | awk '...'   # sesje >= 25 s
```

i zestawiłem go z harmonogramem zadań (`app/Console/Kernel.php`):

| Godzina | Zadanie | Alert |
|---|---|---|
| 01:30 codziennie | czyszczenie kosza (strony + pliki) | **każdej nocy** |
| niedziela 02:00 | zadania tygodniowe (porządki w bazie, statystyki zajętości) | 13–17 alertów, do 15 min przerwy |
| 01:10 codziennie | zadanie „Daily”, co noc pada na `memory_limit` 256 MB | sporadycznie |
| :15 co godzinę | aktywacja/dezaktywacja stron | gdy trwa > 80 s |

### 4.9 Co jeszcze sprawdziłem (i wykluczyłem)

```bash
stat -c %W /var/lib/mysql/*/          # daty utworzenia baz – nowe jednostki
journalctl -u mariadb | grep -E "ERROR|corruption|pending fsync"
dmesg | grep -E "task abort|I/O error"   # + przeliczenie czasu z /proc/uptime
awk '$3 ~ /^sd/ {print $3, $7/$4 " ms odczyt"}' /proc/diskstats
```

- **Zakładanie 5 nowych baz jednostek** (DDL na Galerze) w godzinach 11:27–11:36 dokładnie pokryło się z alertami.
- **Błędy InnoDB** `Database page corruption on disk or a failed read` na 3 tabelach (15–17.11). Do weryfikacji przez `CHECK TABLE`.
- **Storage:** przerwania SCSI tylko w jednym epizodzie rok wcześniej, a średnie opóźnienia dysku < 1 ms. Obecny problem to nie storage.
- **Retencja logów:** journal na serwerze bazy sięgał tylko 5 dni wstecz, bo zapychał go audyt polecenia healthchecku co kilka sekund.

## 5. Przyczyna

!!! danger "Root cause"
    **Węzeł `db01` jest za słaby i źle skonfigurowany do swojej roli.** Bufor InnoDB
    (128 MB przy 26 GB danych), 2 vCPU i cały ruch aplikacji na jednym z trzech węzłów
    (do tego GlusterFS na tej samej maszynie) sprawiają, że każda cięższa operacja
    blokuje bazę na kilkanaście sekund lub kilka minut. Wtedy obie maszyny WWW czekają,
    a monitoring zgłasza timeout.

Wyzwalacze:

1. synchronizacja stron z ponad 400 jednostek, czyli pełny przegląd tabeli przy każdym zapisie (brak indeksu),
2. nocne i niedzielne zadania cykliczne aplikacji,
3. operacje DDL przy zakładaniu nowych jednostek.

## 6. Rozwiązanie (zaplanowane)

Na produkcji niczego nie zmieniałem. Zmiany wymagają uzgodnienia z administratorem baz i dostawcą aplikacji.

| Priorytet | Zmiana | Kto |
|---|---|---|
| 1 | `innodb_buffer_pool_size` 128 MB → 1 GB (online, `SET GLOBAL`), potem 1,5 GB, docelowo więcej RAM | admin baz |
| 1 | indeks `ALTER TABLE page ADD INDEX (source_id, source_db)` w nocy (DDL na Galerze blokuje klaster) | dostawca aplikacji |
| 2 | `slow_query_log=ON`, `long_query_time=2` | admin baz |
| 2 | optymalizacja zadań 01:30 / niedziela 02:00 / Daily | dostawca aplikacji |
| 3 | proxy przed Galerą (MaxScale / ProxySQL), rozłożenie odczytów na 3 węzły | infrastruktura |
| 3 | oddzielenie GlusterFS od węzłów bazy | infrastruktura |
| 3 | `CHECK TABLE` na tabelach z błędami, aktualizacja MariaDB 10.11.x | admin baz |
| 3 | dane logowania w plikach czytelnych dla wszystkich i w logu audytu: zmiana i ograniczenie dostępu | bezpieczeństwo |

Procedura zmiany bufora (krok po kroku, z możliwością wycofania):

```bash
free -m; ps -C mariadbd,glusterfsd -o rss=,comm=
mysql -e "SET GLOBAL innodb_buffer_pool_size = 1073741824;"
mysql -e "SHOW STATUS LIKE 'Innodb_buffer_pool_resize_status';"
# na stałe: [mysqld] innodb_buffer_pool_size = 1G
# wycofanie: SET GLOBAL innodb_buffer_pool_size = 134217728;
```

## 7. Weryfikacja (po wdrożeniu)

- [ ] tempo przyrostu `Innodb_buffer_pool_reads` przed zmianą i po niej (porównanie godzinowe)
- [ ] `EXPLAIN` zapytania synchronizacji: `type: ref`, użyty nowy indeks
- [ ] liczba alertów w Zabbixie: tydzień przed zmianą i tydzień po niej
- [ ] slow log: lista pozostałych zapytań > 2 s

## 8. Wnioski

- **Średnie kłamią.** Średni czas odczytu dysku 0,1 ms i „zdrowy” klaster nie wykluczają
  kilkunastosekundowych zawieszeń. Trzeba patrzeć na pojedyncze zdarzenia.
- **Log dostępu niesie więcej informacji, niż się wydaje.** Kolejność wpisów pozwala
  oszacować czas żądania, nawet bez `%D` w `LogFormat`. Warto ten parametr dodać.
- **Klaster HA ≠ rozłożenie obciążenia.** Trzy węzły Galery, ale aplikacja zna tylko jeden.
- **Domyślne wartości nie są konfiguracją.** `innodb_buffer_pool_size=128M` na produkcji
  oznacza, że nikt nie dostroił bazy.
- **Diagnostyka nie może szkodzić.** Ciężkie zapytania do `information_schema` i rekurencyjny
  `grep` po wolumenie sieciowym 266 GB potrafią same obciążyć produkcję. Przerwałem oba.
- **Najpierw dane, potem wnioski.** Hipotezy „boty”, „sieć”, „Zabbix” i „storage” były
  sensowne, ale dane każdą z nich obaliły.
- **Retencja logów to część monitoringu.** Bez historii sprzed 14.11 nie dało się
  udowodnić, co zmieniło się tego dnia.

## 9. Dowody (zanonimizowane)

- Rozkład alertów z 30 dni: 248 zdarzeń, stałe 01:30 i niedziela 02:00, skok od 14.11.
- `EXPLAIN` zapytania synchronizacji: `type: ALL`, `rows: 40508`.
- Statystyki InnoDB i Galery z `SHOW GLOBAL STATUS`.
- Skrypt diagnostyczny tylko do odczytu: [`scripts/bash/db-node-diagnostics.sh`](https://github.com/programmingbygrzegorz/AdminDay/blob/main/scripts/bash/db-node-diagnostics.sh).
