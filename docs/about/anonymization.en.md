# Anonymization rules

This repository is public and the cases come from real work.
Every entry goes through these rules before it is published.

## Never published

| Category | Example | Replaced with |
|---|---|---|
| Organization, customer, tenants | names of offices, companies, vendors | "organization", "application vendor", "hosting provider" |
| Niche products that identify the customer | name of a commercial CMS | "commercial PHP CMS" |
| Domains and e-mail addresses | `portal.example.pl` | `portal.example` or nothing |
| IP addresses and hostnames | `10.x.x.x`, server names | `web01`, `db01`, `cache01` |
| Custom database, table and column names | tenant database names | `tenant_*`, `portal`, `source_id` |
| Credentials and keys | passwords, tokens, salts | never, not even masked fragments |
| Personal data | names, document contents | never |
| Paths that identify a product | directories named after the product | `/var/www/app` |

## Published

- architecture at a general level (server roles, technologies, traffic flow),
- diagnostic commands and their output (numbers, counters, query plans),
- dates, scale of the problem and lessons learned,
- standard technologies (Linux, Apache, MariaDB, Zabbix, etc.) with versions.

## Pre-commit check

```bash
# look for leftover identifiers – the word list is kept outside the repository
grep -rniEf ~/adminday-blocklist.txt docs/ scripts/
grep -rnE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" docs/ scripts/
```

Raw logs stay outside the repository (`raw/` is in `.gitignore`).
