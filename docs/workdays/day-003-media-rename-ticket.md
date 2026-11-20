---
title: "Day 003 – Zgłoszenie: zmiana nazwy pliku w CMS nie zostaje zapisana"
date: 2026-11-21
tags: [zgłoszenie, triage, cms, media, wielojęzyczność]
---

# Day 003 – Zgłoszenie: zmiana nazwy pliku w CMS nie zostaje zapisana

<div class="ad-pills">
<span class="ad-pill hot">zgłoszenie użytkownika</span>
<span class="ad-pill">przypadek rzeczywisty · zanonimizowany</span>
<span class="ad-pill warn">przyjęte do analizy</span>
</div>

<div class="ad-kpis">
<div class="ad-kpi hot"><small>typ</small><b>ticket</b><span>zgłoszenie od jednostki</span></div>
<div class="ad-kpi warn"><small>objaw</small><b>stara nazwa / sufiks „01”</b><span>zmiana nie zostaje zapisana</span></div>
<div class="ad-kpi"><small>obszar</small><b>biblioteka mediów CMS</b><span>serwis wielojęzyczny</span></div>
<div class="ad-kpi ok"><small>status</small><b>w analizie</b><span>rozwiązanie poza zakresem tego wpisu</span></div>
</div>

!!! info "Anonimizacja"
    Nazwa zgłaszającej jednostki, nazwy plików, dostawców i produktów zostały usunięte
    lub zastąpione. Treść zgłoszenia podano w formie zredagowanej, bez danych
    identyfikujących. Szczegóły: [Zasady anonimizacji](../about/anonymization.md).

!!! note "Zakres wpisu"
    To wpis z **przyjęcia i klasyfikacji zgłoszenia** (triage). Opisuje objaw tak, jak
    zgłosił go użytkownik, oraz wstępne rozpoznanie. **Analiza przyczyny i sposób
    rozwiązania są celowo poza zakresem tego wpisu.**

## 1. Zgłoszenie

Wpłynęło zgłoszenie od jednej z jednostek korzystających z portalu. Treść w formie
zredagowanej (usunięto nazwę jednostki i dane kontaktowe):

> Po wgraniu pliku na serwer nie jesteśmy w stanie zmienić jego nazwy. Po wpisaniu nowej
> nazwy pliku i kliknięciu przycisku „zmień” strona przeładowuje się, ale plik ma starą
> nazwę lub pojawia się dopisek „01”.

## 2. Kontekst

- **Portal:** publiczny serwis repozytorium cyfrowego oparty o CMS, **wielojęzyczny**,
  współtworzony przez wiele jednostek, które samodzielnie dodają i opisują materiały.
- **Obszar zgłoszenia:** biblioteka mediów w panelu redaktora — operacja **zmiany nazwy
  wgranego pliku**.
- **Pliki:** przechowywane w zewnętrznym magazynie obiektowym (zob. [Day 002](day-002-s3-mount-oom.md)).

## 3. Rozpoznanie objawu (triage)

Na etapie przyjęcia zgłoszenia ustaliłem, co dokładnie widzi użytkownik, żeby poprawnie
sklasyfikować problem:

| Obserwacja | Opis |
|---|---|
| Przebieg | redaktor wpisuje nową nazwę pliku i zatwierdza; strona przeładowuje się bez błędu |
| Wynik A | plik zachowuje **starą nazwę** — operacja wygląda na wykonaną, ale nie została zapisana |
| Wynik B | pojawia się **dopisek „01”** — system traktuje nazwę jako zajętą i dokleja sufiks |
| Zakres | zgłoszono dla pojedynczych plików; do ustalenia, czy dotyczy większej liczby |
| Wpływ | operacja porządkowa (nazewnictwo), nie blokuje dodawania nowych plików |

**Wstępna klasyfikacja:** operacja zmiany nazwy pliku w bibliotece mediów **nie utrwala się**
poprawnie (stara nazwa albo kolizja nazw z sufiksem). Kategoria: błąd funkcjonalny panelu,
obszar mediów, priorytet średni (brak utraty danych, obejście możliwe).

## 4. Działania na tym etapie

- [x] przyjęcie i zarejestrowanie zgłoszenia
- [x] potwierdzenie i opis objawu (dwa warianty: stara nazwa / sufiks „01”)
- [x] klasyfikacja i nadanie priorytetu
- [ ] analiza przyczyny — **osobny etap, poza tym wpisem**
- [ ] komunikat zwrotny do jednostki z zaleceniami tymczasowymi

## 5. Zalecenie tymczasowe (dla zgłaszających)

Do czasu rozwiązania docelowego rekomendowane obejście: **nadawać plikom właściwe nazwy
przed wgraniem** zamiast zmieniać je po stronie panelu. To zalecenie przekazywane jest
jednostkom jako doraźna dobra praktyka.

## 6. Wnioski

- **Zgłoszenie użytkownika to opis objawu, nie przyczyny.** Zadaniem triage'u jest wiernie
  odtworzyć, co widzi użytkownik, i sklasyfikować problem — bez przedwczesnych wniosków.
- **Dwa różne wyniki tej samej operacji** (stara nazwa vs sufiks „01”) to cenna wskazówka
  diagnostyczna do dalszego etapu.
- **Dobre obejście zmniejsza presję.** Prosty komunikat do jednostek ogranicza skalę problemu,
  zanim powstanie poprawka docelowa.
