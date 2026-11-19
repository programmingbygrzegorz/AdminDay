# Zasady anonimizacji

Repozytorium jest publiczne, a opisane przypadki pochodzą z prawdziwej pracy.
Przed publikacją każdego wpisu stosuję poniższe zasady.

## Czego nigdy nie publikuję

| Kategoria | Przykład | Zamiast tego |
|---|---|---|
| Organizacja, klient, jednostki | nazwy urzędów, firm, dostawców | „organizacja”, „dostawca aplikacji”, „dostawca hostingu” |
| Produkty niszowe identyfikujące klienta | nazwa komercyjnego CMS | „komercyjny CMS w PHP” |
| Domeny i adresy e-mail | `portal.example.pl` | `portal.example` lub brak |
| Adresy IP i nazwy hostów | `10.x.x.x`, nazwy serwerów | `web01`, `db01`, `cache01` |
| Nazwy baz, tabel i kolumn własnych aplikacji | nazwy baz jednostek | `tenant_*`, `portal`, `source_id` |
| Dane logowania i klucze | hasła, tokeny, sole | nigdy, nawet zamaskowane fragmenty |
| Dane osobowe | imiona, nazwiska, treści dokumentów | nigdy |
| Ścieżki identyfikujące produkt | katalogi z nazwą produktu | `/var/www/app` |

## Co publikuję

- architekturę w ujęciu ogólnym (role serwerów, technologie, przepływ ruchu),
- polecenia diagnostyczne i ich wyniki (liczby, statystyki, plany zapytań),
- daty, skalę problemu i wnioski,
- standardowe technologie (Linux, Apache, MariaDB, Zabbix itp.) wraz z wersjami.

## Kontrola przed commitem

```bash
# szukanie pozostawionych identyfikatorów – lista słów trzymana poza repozytorium
grep -rniEf ~/adminday-blocklist.txt docs/ scripts/
grep -rnE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" docs/ scripts/
```

Surowe logi trzymam poza repozytorium (katalog `raw/` jest w `.gitignore`).
