"""Generuje obrazy terminala (SVG) z prawdziwych, zanonimizowanych wyników poleceń.

Użycie: python scripts/python/make_terminal_shots.py
Wynik: docs/assets/screens/<nazwa>.svg

Każdy plik wejściowy docs/assets/screens/src/<nazwa>.txt:
  - pierwsza linia: tytuł okna
  - linie zaczynające się od "$ " to polecenia (rysowane z promptem)
  - linie zaczynające się od "!" są podświetlane na czerwono, od "+" na zielono, od "~" na szaro
"""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs/assets/screens/src"
OUT = ROOT / "docs/assets/screens"

FONT = 13
LINE = 19
CHAR_W = 7.85
PAD_X = 18
TOP = 44
BG, BAR, FG = "#0d1117", "#161b22", "#c9d1d9"
COLORS = {"!": "#ff7b72", "+": "#7ee787", "~": "#8b949e"}
PROMPT_USER, PROMPT_PATH = "#7ee787", "#79c0ff"


def esc(s: str) -> str:
    # spacje jako twarde, żeby wyrównanie kolumn przetrwało w każdej przeglądarce
    return escape(s).replace(" ", "\u00a0")


def render(name: str, text: str) -> str:
    lines = text.rstrip("\n").split("\n")
    title, body = lines[0], lines[1:]
    longest = max(len(l) + (11 if l.startswith("$ ") else 0) for l in body + [title])
    width = int(longest * CHAR_W + PAD_X * 2 + 10)
    width = max(width, 560)
    height = TOP + LINE * len(body) + 18
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>',
        f'<path d="M0 10a10 10 0 0 1 10-10h{width-20}a10 10 0 0 1 10 10v20H0z" fill="{BAR}"/>',
        '<circle cx="18" cy="15" r="5.5" fill="#ff5f57"/>',
        '<circle cx="36" cy="15" r="5.5" fill="#febc2e"/>',
        '<circle cx="54" cy="15" r="5.5" fill="#28c840"/>',
        f'<text x="{width/2}" y="19.5" fill="#8b949e" font-size="12" text-anchor="middle" '
        f'font-family="JetBrains Mono, Consolas, Menlo, DejaVu Sans Mono, monospace">{escape(title)}</text>',
        f'<g font-family="JetBrains Mono, Consolas, Menlo, DejaVu Sans Mono, monospace" font-size="{FONT}" xml:space="preserve">',
    ]
    y = TOP + 4
    for raw in body:
        if raw.startswith("$ "):
            host, _, cmd = raw[2:].partition(" ")
            out.append(
                f'<text x="{PAD_X}" y="{y}"><tspan fill="{PROMPT_USER}">root@{escape(host)}</tspan>'
                f'<tspan fill="{FG}">:</tspan><tspan fill="{PROMPT_PATH}">~</tspan>'
                f'<tspan fill="{FG}">#\u00a0{esc(cmd)}</tspan></text>'
            )
        else:
            color = COLORS.get(raw[:1])
            txt = raw[1:] if color else raw
            out.append(f'<text x="{PAD_X}" y="{y}" fill="{color or FG}">{esc(txt)}</text>')
        y += LINE
    out += ["</g>", "</svg>"]
    return "\n".join(out) + "\n"


def main() -> None:
    for src in sorted(SRC.glob("*.txt")):
        svg = render(src.stem, src.read_text(encoding="utf-8"))
        (OUT / f"{src.stem}.svg").write_text(svg, encoding="utf-8")
        print("ok", src.stem)


if __name__ == "__main__":
    main()
