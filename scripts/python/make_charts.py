"""Generate theme-aware SVG charts for AdminDay entries.

Input : docs/assets/data/day-001-alerts.csv  (anonymized: start timestamp, duration in s)
Output: docs/assets/charts/day001-daily.{pl,en}.svg
        docs/assets/charts/day001-heatmap.{pl,en}.svg

Colors are not hard-coded: every shape carries a CSS class styled in
docs/stylesheets/extra.css, so charts follow the light/dark theme.
SVGs contain no blank lines, so they can be inlined with pymdownx.snippets.

Usage:  python scripts/python/make_charts.py
"""
from __future__ import annotations

import csv
import datetime as dt
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs/assets/data/day-001-alerts.csv"
OUT = ROOT / "docs/assets/charts"

TXT = {
    "pl": {
        "days": ["pn", "wt", "śr", "cz", "pt", "so", "nd"],
        "daily_title": "Alerty dziennie · 20.10–19.11.2026",
        "y": "alerty",
        "leg_norm": "zwykły dzień",
        "leg_sun": "niedziela (zadania tygodniowe 02:00)",
        "leg_hot": "od 14.11",
        "jump": "od 14.11: 4–5× więcej",
        "heat_title": "Kiedy strona przestaje odpowiadać · godzina rozpoczęcia alertu",
        "band": "godziny pracy",
        "night": "01:30 – co noc",
        "sunday": "niedziela 02:00–03:18",
        "less": "mniej",
        "more": "więcej",
    },
    "en": {
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "daily_title": "Alerts per day · 20 Oct – 19 Nov 2026",
        "y": "alerts",
        "leg_norm": "regular day",
        "leg_sun": "Sunday (weekly jobs at 02:00)",
        "leg_hot": "from 14 Nov",
        "jump": "from 14 Nov: 4–5× more",
        "heat_title": "When the site stops responding · hour the alert started",
        "band": "office hours",
        "night": "01:30 – every night",
        "sunday": "Sunday 02:00–03:18",
        "less": "less",
        "more": "more",
    },
}

JUMP = dt.date(2026, 11, 14)


def load() -> list[dt.datetime]:
    with DATA.open(encoding="utf-8") as f:
        return [dt.datetime.strptime(r["start"], "%Y-%m-%d %H:%M:%S") for r in csv.DictReader(f)]


def days_range(events: list[dt.datetime]) -> list[dt.date]:
    d, last, out = events[0].date(), events[-1].date(), []
    while d <= last:
        out.append(d)
        d += dt.timedelta(days=1)
    return out


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def daily(events, lang: str) -> str:
    t = TXT[lang]
    days = days_range(events)
    cnt = Counter(e.date() for e in events)
    W, H, L, R, T, B = 920, 320, 46, 16, 64, 44
    pw, ph = W - L - R, H - T - B
    ymax = 25
    slot = pw / len(days)
    bw = slot * 0.66
    y = lambda v: T + ph - v / ymax * ph
    p = [f'<svg class="ad-svg" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(t["daily_title"])}">']
    p.append(f'<text class="c-title" x="{L}" y="22">{esc(t["daily_title"])}</text>')
    lx = L
    for cls, label in (("c-bar", t["leg_norm"]), ("c-sun", t["leg_sun"]), ("c-hot", t["leg_hot"])):
        p.append(f'<rect class="{cls}" x="{lx}" y="34" width="12" height="12" rx="2"/>')
        p.append(f'<text class="c-leg" x="{lx + 18}" y="44">{esc(label)}</text>')
        lx += 30 + len(label) * 6.6
    for v in range(0, ymax + 1, 5):
        p.append(f'<line class="c-grid" x1="{L}" y1="{y(v):.1f}" x2="{W - R}" y2="{y(v):.1f}"/>')
        p.append(f'<text class="c-axis" x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end">{v}</text>')
    p.append(f'<text class="c-axis" transform="translate(12 {T + ph / 2}) rotate(-90)" text-anchor="middle">{esc(t["y"])}</text>')
    jump_x = None
    for i, d in enumerate(days):
        v = cnt.get(d, 0)
        x = L + i * slot + (slot - bw) / 2
        cls = "c-sun" if d.weekday() == 6 else ("c-hot" if d >= JUMP else "c-bar")
        if d == JUMP:
            jump_x = L + i * slot
        if v:
            p.append(f'<rect class="{cls}" x="{x:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{ph - (y(v) - T):.1f}" rx="2"><title>{d:%d.%m}: {v}</title></rect>')
        if v >= 8:
            p.append(f'<text class="c-val" x="{x + bw / 2:.1f}" y="{y(v) - 5:.1f}" text-anchor="middle">{v}</text>')
        if i % 3 == 0 or i == len(days) - 1:
            p.append(f'<text class="c-axis" x="{x + bw / 2:.1f}" y="{T + ph + 18}" text-anchor="middle">{d:%d.%m}</text>')
            p.append(f'<text class="c-axis c-dim" x="{x + bw / 2:.1f}" y="{T + ph + 32}" text-anchor="middle">{t["days"][d.weekday()]}</text>')
    p.append(f'<line class="c-base" x1="{L}" y1="{T + ph}" x2="{W - R}" y2="{T + ph}"/>')
    if jump_x is not None:
        x2 = W - R
        p.append(f'<rect class="c-zone" x="{jump_x:.1f}" y="{T}" width="{x2 - jump_x:.1f}" height="{ph}"/>')
        p.append(f'<line class="c-mark" x1="{jump_x:.1f}" y1="{T - 4}" x2="{jump_x:.1f}" y2="{T + ph}"/>')
        p.append(f'<text class="c-note" x="{jump_x + 6:.1f}" y="{T + 12}">{esc(t["jump"])}</text>')
    p.append("</svg>")
    return "".join(p)


def heatmap(events, lang: str) -> str:
    t = TXT[lang]
    days = days_range(events)
    cnt = Counter((e.date(), e.hour) for e in events)
    cw, ch, gap = 26, 14, 2
    L, T = 84, 66
    W = L + 24 * (cw + gap) + 20
    H = T + len(days) * (ch + gap) + 66
    gx = lambda h: L + h * (cw + gap)
    gy = lambda i: T + i * (ch + gap)
    level = lambda v: 0 if v == 0 else 1 if v == 1 else 2 if v == 2 else 3 if v <= 4 else 4
    p = [f'<svg class="ad-svg" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(t["heat_title"])}">']
    p.append(f'<text class="c-title" x="{L}" y="22">{esc(t["heat_title"])}</text>')
    band_x, band_w = gx(8) - 1, 8 * (cw + gap)
    p.append(f'<rect class="c-band" x="{band_x}" y="{T - 6}" width="{band_w}" height="{len(days) * (ch + gap) + 4}" rx="4"/>')
    p.append(f'<text class="c-leg" x="{band_x + band_w / 2}" y="{T - 30}" text-anchor="middle">{esc(t["band"])} 08–16</text>')
    for h in range(24):
        p.append(f'<text class="c-axis" x="{gx(h) + cw / 2}" y="{T - 12}" text-anchor="middle">{h:02d}</text>')
    for i, d in enumerate(days):
        sun = d.weekday() == 6
        lab_cls = "c-axis c-sunlab" if sun else "c-axis"
        p.append(f'<text class="{lab_cls}" x="{L - 8}" y="{gy(i) + ch - 3}" text-anchor="end">{t["days"][d.weekday()]} {d:%d.%m}</text>')
        for h in range(24):
            v = cnt.get((d, h), 0)
            tip = f'<title>{d:%d.%m} {h:02d}:00 – {v}</title>' if v else ""
            p.append(f'<rect class="h{level(v)}" x="{gx(h)}" y="{gy(i)}" width="{cw}" height="{ch}" rx="2">{tip}</rect>')
    p.append(f'<rect class="c-ring" x="{gx(1) - 2}" y="{T - 4}" width="{cw + 4}" height="{len(days) * (ch + gap)}" rx="4"/>')
    by = gy(len(days)) + 20
    p.append(f'<text class="c-note" x="{gx(1) - 2}" y="{by}">↑ {esc(t["night"])}</text>')
    p.append(f'<text class="c-note c-note-sun" x="{gx(17)}" y="{by}" text-anchor="start">{esc(t["sunday"])}: ' + {"pl": "do 15 min przerwy", "en": "up to 15 min outage"}[lang] + "</text>")
    lx = W - 20 - 5 * 18 - 70
    ly = by + 18
    p.append(f'<text class="c-leg" x="{lx - 6}" y="{ly + 10}" text-anchor="end">{esc(t["less"])}</text>')
    for k in range(5):
        p.append(f'<rect class="h{k}" x="{lx + k * 18}" y="{ly}" width="14" height="12" rx="2"/>')
    p.append(f'<text class="c-leg" x="{lx + 5 * 18 + 4}" y="{ly + 10}">{esc(t["more"])}</text>')
    p.append("</svg>")
    return "".join(p)


ARCH = {
    "pl": dict(
        title="Architektura środowiska (zanonimizowana)", inet="Internet", inet2="mieszkańcy · redaktorzy · boty",
        mon="Monitoring", mon2="GET / co 60 s · timeout 15 s", lb="Firewall / load balancer", lb2="VIP · SNAT na adres wewnętrzny",
        web="Apache + PHP-FPM (max 50)", spec="2 vCPU · 1,7 GB RAM · swap", cron="+ zadania cron aplikacji", nocron="bez zadań cron",
        cache="Redis", cache2="tylko sesje PHP", flow="100% zapytań SQL + pliki (GlusterFS)", sess="sesje",
        db1a="MariaDB 10.11 + GlusterFS", db1b="bufor InnoDB 128 MB / 26 GB", db1c="2 vCPU · 3,7 GB RAM · load 2,4–4,4",
        rep="replika · bez ruchu aplikacji", cluster="klaster MariaDB Galera · 3 pełne kopie danych",
    ),
    "en": dict(
        title="Environment architecture (anonymized)", inet="Internet", inet2="citizens · editors · bots",
        mon="Monitoring", mon2="GET / every 60 s · 15 s timeout", lb="Firewall / load balancer", lb2="VIP · SNAT to internal address",
        web="Apache + PHP-FPM (max 50)", spec="2 vCPU · 1.7 GB RAM · swapping", cron="+ application cron jobs", nocron="no cron jobs",
        cache="Redis", cache2="PHP sessions only", flow="100% of SQL + files (GlusterFS)", sess="sessions",
        db1a="MariaDB 10.11 + GlusterFS", db1b="InnoDB buffer 128 MB / 26 GB", db1c="2 vCPU · 3.7 GB RAM · load 2.4–4.4",
        rep="replica · no application traffic", cluster="MariaDB Galera cluster · 3 full copies of the data",
    ),
}


def architecture(lang: str) -> str:
    a = {k: esc(v) for k, v in ARCH[lang].items()}
    return f"""<svg class="ad-svg ad-arch" viewBox="0 0 960 600" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{a['title']}">
<defs>
<marker id="m-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="a-head"/></marker>
<marker id="m-h" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="a-head-hot"/></marker>
</defs>
<rect x="380" y="12" width="200" height="52" rx="26" class="a-box"/>
<text x="480" y="36" text-anchor="middle" class="a-name">{a['inet']}</text>
<text x="480" y="54" text-anchor="middle" class="a-sub">{a['inet2']}</text>
<rect x="716" y="12" width="224" height="52" rx="8" class="a-box"/>
<text x="732" y="35" class="a-name">{a['mon']}</text>
<text x="732" y="53" class="a-sub">{a['mon2']}</text>
<path d="M716 40 L652 40 L652 128 L632 128" class="a-ln" marker-end="url(#m-a)"/>
<path d="M480 64 L480 100" class="a-ln" marker-end="url(#m-a)"/>
<rect x="330" y="102" width="300" height="60" rx="8" class="a-box-acc"/>
<text x="346" y="127" class="a-name">{a['lb']}</text>
<text x="346" y="147" class="a-sub">{a['lb2']}</text>
<path d="M420 162 L300 220" class="a-ln" marker-end="url(#m-a)"/>
<path d="M540 162 L660 220" class="a-ln" marker-end="url(#m-a)"/>
<rect x="130" y="222" width="300" height="112" rx="8" class="a-box"/>
<text x="146" y="248" class="a-name">web01</text>
<text x="146" y="270" class="a-sub">{a['web']}</text>
<text x="146" y="290" class="a-hot">{a['spec']}</text>
<text x="146" y="312" class="a-hot">{a['cron']}</text>
<rect x="530" y="222" width="280" height="112" rx="8" class="a-box"/>
<text x="546" y="248" class="a-name">web02</text>
<text x="546" y="270" class="a-sub">{a['web']}</text>
<text x="546" y="290" class="a-hot">{a['spec']}</text>
<text x="546" y="312" class="a-sub">{a['nocron']}</text>
<rect x="832" y="228" width="118" height="78" rx="8" class="a-box"/>
<text x="846" y="254" class="a-name">cache01</text>
<text x="846" y="274" class="a-sub">{a['cache']}</text>
<text x="846" y="292" class="a-sub">{a['cache2']}</text>
<path d="M280 334 L280 356 L891 356 L891 308" class="a-ln-dash"/>
<path d="M700 334 L700 356" class="a-ln-dash"/>
<text x="740" y="350" class="a-label">{a['sess']}</text>
<path d="M210 334 L200 428" class="a-ln-hot a-flow" marker-end="url(#m-h)"/>
<path d="M600 334 L280 428" class="a-ln-hot a-flow" marker-end="url(#m-h)"/>
<text x="436" y="398" class="a-label-hot">{a['flow']}</text>
<rect x="40" y="414" width="900" height="176" rx="12" class="a-cluster"/>
<text x="56" y="582" class="a-label">{a['cluster']}</text>
<rect x="66" y="434" width="268" height="126" rx="8" class="a-box-hot"/>
<circle cx="316" cy="452" r="6" class="a-pulse"/>
<text x="82" y="460" class="a-name">db01</text>
<text x="82" y="482" class="a-sub">{a['db1a']}</text>
<text x="82" y="504" class="a-hot">{a['db1b']}</text>
<text x="82" y="526" class="a-hot">{a['db1c']}</text>
<rect x="366" y="434" width="268" height="126" rx="8" class="a-box-dim"/>
<text x="382" y="460" class="a-name">db02</text>
<text x="382" y="482" class="a-sub">{a['rep']}</text>
<rect x="666" y="434" width="268" height="126" rx="8" class="a-box-dim"/>
<text x="682" y="460" class="a-name">db03</text>
<text x="682" y="482" class="a-sub">{a['rep']}</text>
<path d="M336 497 L364 497" class="a-ln-rep" marker-start="url(#m-a)" marker-end="url(#m-a)"/>
<path d="M636 497 L664 497" class="a-ln-rep" marker-start="url(#m-a)" marker-end="url(#m-a)"/>
</svg>"""


BUF = {
    "pl": dict(title="Bufor InnoDB a ilość danych", data="dane: 26 GB", now="dziś: 128 MB (0,5%)",
               step="krok 1: 1 GB", target="po dołożeniu RAM: ~10 GB"),
    "en": dict(title="InnoDB buffer pool vs data size", data="data: 26 GB", now="today: 128 MB (0.5%)",
               step="step 1: 1 GB", target="after a RAM upgrade: ~10 GB"),
}


def buffer(lang: str) -> str:
    b = {k: esc(v) for k, v in BUF[lang].items()}
    W, L, full = 920, 20, 880
    px = lambda gb: max(3.0, gb / 26 * full)
    rows = [("b-now", 0.125, b["now"]), ("b-step", 1, b["step"]), ("b-target", 10, b["target"])]
    p = [f'<svg class="ad-svg" viewBox="0 0 {W} 214" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{b["title"]}">',
         f'<text class="c-title" x="{L}" y="22">{b["title"]}</text>']
    for i, (cls, gb, label) in enumerate(rows):
        y = 44 + i * 56
        p.append(f'<rect class="b-data" x="{L}" y="{y}" width="{full}" height="26" rx="5"/>')
        p.append(f'<rect class="{cls}" x="{L}" y="{y}" width="{px(gb):.1f}" height="26" rx="5"/>')
        p.append(f'<text class="c-leg b-txt" x="{L + px(gb) + 10:.1f}" y="{y + 18}">{label}</text>')
        p.append(f'<text class="c-axis" x="{L + full - 8}" y="{y + 18}" text-anchor="end">{b["data"]}</text>')
    p.append("</svg>")
    return "".join(p)


def main() -> None:
    events = load()
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("pl", "en"):
        (OUT / f"day001-architecture.{lang}.svg").write_text(architecture(lang), encoding="utf-8")
        (OUT / f"day001-buffer.{lang}.svg").write_text(buffer(lang), encoding="utf-8")
        (OUT / f"day001-daily.{lang}.svg").write_text(daily(events, lang), encoding="utf-8")
        (OUT / f"day001-heatmap.{lang}.svg").write_text(heatmap(events, lang), encoding="utf-8")
    print(f"{len(events)} alerts -> charts written to {OUT}")


if __name__ == "__main__":
    main()
