# AdminDay – IT Operations Journal

**PL:** Dziennik pracy administratora IT: prawdziwe problemy z pracy (zanonimizowane), diagnostyka krok po kroku, polecenia, wyniki i wnioski.
**EN:** An IT administrator's operations journal: real work cases (anonymized), step-by-step diagnostics, commands, results and lessons learned.

🌐 Strona / Website: https://programmingbygrzegorz.github.io/AdminDay/

## Wpisy / Entries

| # | Data / Date | Wpis / Entry |
|---|---|---|
| 001 | 2026-11-19 | [CMS portal outages: an overloaded Galera database](docs/workdays/day-001-cms-db-saturation.en.md) · [PL](docs/workdays/day-001-cms-db-saturation.md) |

## Uruchomienie lokalne / Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdocs serve
```

Następnie / Then: http://127.0.0.1:8000

## Struktura / Structure

```text
docs/        wpisy PL (*.md) i EN (*.en.md) / entries PL and EN
scripts/     skrypty diagnostyczne, tylko odczyt / read-only diagnostic scripts
mkdocs.yml   konfiguracja strony / site configuration
.github/     publikacja na GitHub Pages / GitHub Pages deployment
```

## Anonimizacja / Anonymization

Wszystkie identyfikatory środowisk (organizacje, produkty, domeny, IP, hosty, bazy, dane logowania) są usunięte lub zastąpione.
All environment identifiers (organizations, products, domains, IPs, hosts, databases, credentials) are removed or replaced.
→ [docs/about/anonymization.md](docs/about/anonymization.md)
