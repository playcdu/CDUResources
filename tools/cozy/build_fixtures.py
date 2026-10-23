#!/usr/bin/env python3
"""Build the cozy fixture gallery: self-contained HTML pages for claude.ai.

    python tools/cozy/build_fixtures.py            # build every page, then check them
    python tools/cozy/build_fixtures.py --check    # only re-check pages already built
    python tools/cozy/build_fixtures.py --theme soulrend   # the Soulrend gallery
    python tools/cozy/build_fixtures.py --theme faithful   # the Faithful gallery

Writes under ``evidence/cozy-fixtures/`` (gitignored):

* ``index.html``           every skin as a card, the palette and the typeface specimen
* ``family-<family>.html`` per family (split into ``-1``, ``-2`` ... when a page
  would pass the size budget): composites, every button in all six states,
  frames alone, raw backgrounds with clearances outlined
* ``before-after.html``    baseline midnight artwork (commit ``BASELINE``) beside cozy

Every image is a PNG data URI produced by ``preview.py``; pages carry no
external resources. Cross-page links are literal ``{{URL:<page>}}`` tokens that
the publisher replaces with the published URLs. Composites are SCHEMATIC: the
grey item squares, slot backdrop and titles are drawn by the preview tool, not
taken from the game. Output is deterministic for a given checkout (no clock,
no randomness). Reads pack-source and ``git show`` only; never writes outside
evidence/. See docs/COZY-FIXTURES.md.

``--theme {cozy,soulrend,faithful}`` (default: $QUASAR_GUI_THEME, else cozy; the
flag wins) switches the page titles ("Cozy GUI Fixtures" / "Soulrend GUI
Fixtures" / "Faithful GUI Fixtures",
"<Theme> <Family> Family", "Midnight vs <Theme>"), the palette swatches and
aliases, the typeface specimen, a theme provenance note (Faithful: "No Mojang
pixels", under the schematic caveat on every page), the schematic lettering,
the page colour tokens, the output directory (``evidence/<theme>-fixtures/``)
and the URL map
(``tools/<theme>/fixture_urls.json``). The textures shown are always the ones
in pack-source on the current checkout. The Soulrend gallery is described in
docs/SOULREND-FIXTURES.md, the Faithful one in docs/FAITHFUL-FIXTURES.md.

Licence: MIT.
"""
from __future__ import annotations

import argparse
import json
import base64
import html
import importlib
import io
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PIL import Image, ImageChops  # noqa: E402

import geometry as geo  # noqa: E402
import lettering as L  # noqa: E402
import palette as pal  # noqa: E402
import preview as pv  # noqa: E402

ROOT = geo.ROOT
OUT = ROOT / 'evidence' / 'cozy-fixtures'
BASELINE = '037c5ef7cb5dbe6fe5ab04dadcb2d2c44cd0372e'
HARD_LIMIT = 16 * 1000 * 1000          # publisher limit (16 MB, decimal to be safe)
URL_MAP_PATH = ROOT / 'tools' / 'cozy' / 'fixture_urls.json'   # published artifact URLs, tracked
ARTIFACT_PREFIX = 'https://claude.ai/artifact/'
THEME_ENV = 'QUASAR_GUI_THEME'

# Everything that differs between the theme galleries. ``faces`` are
# (attribute, display name, description) of the two lettering faces.
THEME_CONFIG = {
    'cozy': {
        'name': 'Cozy', 'branch': 'art/cozy-theme',
        'out': ROOT / 'evidence' / 'cozy-fixtures',
        'urls': ROOT / 'tools' / 'cozy' / 'fixture_urls.json',
        'doc': 'docs/COZY-FIXTURES.md',
        'blurb': 'cozy hand-drawn pixel-art replacement',
        'faces': (('HEARTH', 'HEARTH', 'mixed case, the main face'),
                  ('SPRIG', 'SPRIG', 'uppercase only, for tight labels and stack counts')),
        'tokens': None,
    },
    'soulrend': {
        'name': 'Soulrend', 'branch': 'art/soulrend-theme',
        'out': ROOT / 'evidence' / 'soulrend-fixtures',
        'urls': ROOT / 'tools' / 'soulrend' / 'fixture_urls.json',
        'doc': 'docs/SOULREND-FIXTURES.md',
        'blurb': 'Soulrend dark-fantasy pixel-art replacement',
        'faces': (('GRAVEN', 'GRAVEN', 'a thin medieval serif in mixed case, the main face'),
                  ('RUNE', 'RUNE', 'carved capitals for tight labels, banners and stack counts')),
        # page colour tokens: (light mode, dark mode)
        'tokens': ({'--bg': '#e6ddc8', '--surface': '#f1eadb', '--surface-2': '#d9ccb0', '--fg': '#1f1717',
                    '--muted': '#5a4c44', '--line': '#c4b494', '--accent': '#7e1e22', '--link': '#6e2a1c',
                    '--link-hover': '#9a3a26', '--eyebrow': '#5e4a2c', '--note-bg': '#e9d9b4',
                    '--note-line': '#98763a', '--code-bg': '#ddd0b4'},
                   {'--bg': '#161213', '--surface': '#221b19', '--surface-2': '#2e2522', '--fg': '#ece4d2',
                    '--muted': '#b9ab96', '--line': '#3e3430', '--accent': '#e07a68', '--link': '#d8b464',
                    '--link-hover': '#f0cf86', '--eyebrow': '#7fc9cf', '--note-bg': '#2a201c',
                    '--note-line': '#98763a', '--code-bg': '#2e2522'}),
    },
    'faithful': {
        'name': 'Faithful', 'branch': 'art/faithful',
        'out': ROOT / 'evidence' / 'faithful-fixtures',
        'urls': ROOT / 'tools' / 'faithful' / 'fixture_urls.json',
        'doc': 'docs/FAITHFUL-FIXTURES.md',
        'blurb': 'Faithful vanilla-style pixel-art replacement',
        'faces': (('PLAIN', 'PLAIN', 'an original 5-wide face in mixed case that sits beside the game font, the main face'),
                  ('TINY', 'TINY', 'compact capitals for tight two-line labels and stack counts')),
        'pure_bw': True,
        # one sentence, shown in its own note under the schematic caveat on every page
        'provenance': ('<strong>No Mojang pixels.</strong> Every texture, sprite and PLAIN / TINY glyph shown here '
                       'was drawn from scratch for this pack, and no Minecraft jar, vanilla resource pack, font '
                       'bitmap or screenshot was opened, sampled or traced to make them.'),
        # the palette aliases the index lists (docs/FAITHFUL-STYLE-GUIDE.md section 2)
        'aliases': ('OUTLINE', 'TEXT_DARK', 'TEXT_LIGHT', 'SHADOW', 'TEXT_DISABLED', 'GLOW', 'TITLE_BAND', 'SHEET',
                    'PANEL', 'BEVEL_LIGHT', 'BEVEL_DARK', 'SLOT_FILL', 'SLOT_SHADOW', 'BUTTON_FACE', 'BUTTON_LIT',
                    'DISABLED_FACE'),
        # page colour tokens: (light mode, dark mode), a neutral grey scheme
        'tokens': ({'--bg': '#e4e4e4', '--surface': '#f2f2f2', '--surface-2': '#d2d2d2', '--fg': '#1c1c1c',
                    '--muted': '#555555', '--line': '#bdbdbd', '--accent': '#3a6a2c', '--link': '#2c4f8c',
                    '--link-hover': '#1e3a6e', '--eyebrow': '#5a5a5a', '--note-bg': '#ececd8',
                    '--note-line': '#a08a3a', '--code-bg': '#dadada'},
                   {'--bg': '#181818', '--surface': '#232323', '--surface-2': '#2e2e2e', '--fg': '#ececec',
                    '--muted': '#a8a8a8', '--line': '#3c3c3c', '--accent': '#8fce6c', '--link': '#8eb4ec',
                    '--link-hover': '#b6d0f6', '--eyebrow': '#c6c6c6', '--note-bg': '#2a2a22',
                    '--note-line': '#a08a3a', '--code-bg': '#2e2e2e'}),
    },
}
THEME = dict(THEME_CONFIG['cozy'], key='cozy')
_COZY_PAL, _COZY_L = pal, L          # the cozy modules imported above


def resolve_theme(name=None):
    """Explicit name, else $QUASAR_GUI_THEME, else 'cozy'."""
    theme = name or os.environ.get(THEME_ENV) or 'cozy'
    if theme not in THEME_CONFIG:
        raise ValueError(f'unknown theme {theme!r}; choose one of {", ".join(THEME_CONFIG)}')
    return theme


def configure(name=None):
    """Point the module at a theme: output dir, URL map, palette, lettering,
    preview lettering and strings. Returns the theme key."""
    global OUT, URL_MAP_PATH, pal, L, THEME
    key = resolve_theme(name)
    THEME = dict(THEME_CONFIG[key], key=key)
    OUT = THEME['out']
    URL_MAP_PATH = THEME['urls']
    pv.set_theme(key)
    if key == 'cozy':
        pal, L = _COZY_PAL, _COZY_L
    else:
        pal = importlib.import_module(f'{key}.palette')
        L = importlib.import_module(f'{key}.lettering')
    return key


def url_map():
    """{{URL:<page>}} -> published URL, read from the tracked map (empty when absent)."""
    return json.loads(URL_MAP_PATH.read_text(encoding='utf-8')) if URL_MAP_PATH.is_file() else {}


def resolve_links(text, urls):
    """Replace known {{URL:<page>}} tokens with published URLs; unknown tokens stay."""
    return re.sub(r'\{\{URL:([^}]+)\}\}', lambda m: urls.get(m.group(1), m.group(0)), text)
PAGE_BUDGET = 14 * 1000 * 1000         # split a family page before it passes this

FAMILY_ORDER = ['economy', 'auction', 'chest_shop', 'trade', 'ticket', 'admin_shop',
                'guild_bank', 'prefixes', 'invsee', 'utility']
FAMILY_NAME = {'economy': 'Economy', 'auction': 'Auction', 'chest_shop': 'Chest Shop', 'trade': 'Trade',
               'ticket': 'Ticket', 'admin_shop': 'Admin Shop', 'guild_bank': 'Guild Bank',
               'prefixes': 'Prefixes', 'invsee': 'Invsee', 'utility': 'Utility'}
# Sensible sub-groups, used only when a family must be split (adjacent groups are
# packed together while they fit the budget).
SPLIT_GROUPS = {
    'chest_shop': [['chest_shop', 'chest_shop_owner', 'chest_shop_ads', 'chest_shop_search'],
                   ['chest_shop_listing_enabled', 'chest_shop_listing_disabled', 'chest_shop_buy', 'chest_shop_sell'],
                   ['chest_shop_settings', 'chest_shop_upgrade', 'chest_shop_upgrade_confirm',
                    'chest_shop_upgrade_disabled']],
    'auction': [['auction_house', 'auction_search', 'auction_mine', 'auction_watchlist'],
                ['auction_confirm', 'auction_duration']],
    'utility': [['trashcan', 'ender_chest', 'crafting'], [f'template_chest_{n}' for n in range(1, 7)]],
    'guild_bank': [['guild_bank_select_1', 'guild_bank_select_3'], [f'guild_bank_{n}' for n in range(1, 7)]],
}
BEFORE_AFTER = ['economy_hub', 'economy_log', 'auction_house', 'auction_confirm', 'auction_duration',
                'chest_shop', 'chest_shop_listing_enabled', 'chest_shop_buy', 'trade_self_ready', 'trade_money',
                'ticket_valid', 'ticket_invalid', 'admin_shop_categories', 'guild_bank_3', 'prefixes_6',
                'invsee_offline', 'trashcan', 'ender_chest', 'crafting', 'template_chest_6']
CELL_BACKDROP = (90, 84, 88, 255)      # same backdrop preview.buttons_sheet uses under a button crop
SCHEMATIC_NOTE = ('Schematic composite, not a gameplay screenshot. Every picture is drawn by '
                  '<code>tools/cozy/preview.py</code> from the pack-source PNGs: the grey item squares, '
                  'flat slot backdrop, dimmed world colour, titles and the &ldquo;Inventory&rdquo; label are '
                  'synthetic stand-ins for what the client draws live.')


# ---------------------------------------------------------------------------
# Image encoding
# ---------------------------------------------------------------------------

def _scaled(img, n):
    return img if n == 1 else img.resize((img.width * n, img.height * n), Image.Resampling.NEAREST)


def png_bytes(img):
    """Smallest lossless PNG we can make cheaply: an exact palette image when the
    picture has at most 256 colours (pixel art nearly always does), else RGB(A)."""
    has_alpha = img.mode == 'RGBA' and img.getextrema()[3][0] < 255
    src = img.convert('RGBA' if has_alpha else 'RGB')
    best = None
    if not has_alpha and src.getcolors(256) is not None:
        p = src.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
        if ImageChops.difference(p.convert('RGB'), src).getbbox() is None:
            best = p
    buf = io.BytesIO()
    (best or src).save(buf, format='PNG', optimize=True)
    return buf.getvalue()


def data_uri(img):
    return 'data:image/png;base64,' + base64.b64encode(png_bytes(img)).decode('ascii')


def img_tag(img, alt, cls='', display_scale=1):
    w, h = img.width * display_scale, img.height * display_scale
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{data_uri(img)}" width="{w}" height="{h}" alt="{html.escape(alt)}" '
            f'decoding="async">')


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------

def _swatch_tokens():
    return '\n'.join(f'  --sw-{n}: rgb({c[0]} {c[1]} {c[2]});' for n, c in pal.NAMED.items())


CSS = """
:root {
  --bg: #f3ead7;
  --surface: #fbf5e8;
  --surface-2: #eadcc0;
  --fg: #2e1c1b;
  --muted: #6b5446;
  --line: #d6c09a;
  --accent: #9c3a36;
  --link: #7a3b1e;
  --link-hover: #a4502a;
  --eyebrow: #85593a;
  --note-bg: #f6e2bd;
  --note-line: #c4924c;
  --code-bg: #ebdec4;
  --art-bg: #8a8a8a;
  --shadow: rgb(84 50 36 / 0.12);
  color-scheme: light;
%SWATCHES%
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1f1611;
    --surface: #2a1e17;
    --surface-2: #36271e;
    --fg: #f0e4cc;
    --muted: #c4ac90;
    --line: #4b3628;
    --accent: #e3907a;
    --link: #f0b97c;
    --link-hover: #ffd29e;
    --eyebrow: #d4a574;
    --note-bg: #3a2a1b;
    --note-line: #a27636;
    --code-bg: #36271e;
    --art-bg: #8a8a8a;
    --shadow: rgb(0 0 0 / 0.35);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #1f1611;
  --surface: #2a1e17;
  --surface-2: #36271e;
  --fg: #f0e4cc;
  --muted: #c4ac90;
  --line: #4b3628;
  --accent: #e3907a;
  --link: #f0b97c;
  --link-hover: #ffd29e;
  --eyebrow: #d4a574;
  --note-bg: #3a2a1b;
  --note-line: #a27636;
  --code-bg: #36271e;
  --art-bg: #8a8a8a;
  --shadow: rgb(0 0 0 / 0.35);
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 1rem;
  line-height: 1.55;
  overflow-x: hidden;
}
.wrap {
  max-width: 1180px;
  margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 24px;
}
h1, h2, h3, h4 { text-wrap: balance; line-height: 1.2; margin: 0 0 0.5rem; }
h1 { font-size: clamp(1.75rem, 1.2rem + 2.4vw, 2.6rem); letter-spacing: -0.01em; }
h2 { font-size: clamp(1.35rem, 1.1rem + 1vw, 1.75rem); margin-top: 2.5rem; }
h3 { font-size: 1.15rem; margin-top: 1.5rem; }
h4 { font-size: 1rem; margin-top: 1.25rem; }
p { margin: 0 0 0.85rem; max-width: 72ch; }
a { color: var(--link); text-underline-offset: 0.18em; }
a:hover { color: var(--link-hover); }
code { font-family: ui-monospace, "Cascadia Mono", Consolas, Menlo, monospace; font-size: 0.9em;
       background: var(--code-bg); padding: 0.05em 0.3em; border-radius: 4px; overflow-wrap: anywhere; }
img { max-width: 100%; height: auto; image-rendering: pixelated; image-rendering: crisp-edges; display: block; }
.eyebrow { text-transform: uppercase; letter-spacing: 0.09em; font-size: 0.74rem; font-weight: 650;
           color: var(--eyebrow); margin: 0 0 0.35rem; }
.lede { font-size: 1.08rem; color: var(--muted); }
.muted { color: var(--muted); }
.small { font-size: 0.88rem; }
.topnav { display: flex; flex-wrap: wrap; gap: 0.4rem 1rem; margin-bottom: 1.25rem; font-size: 0.92rem; }
.note { background: var(--note-bg); border-left: 4px solid var(--note-line); border-radius: 6px;
        padding: 0.75rem 1rem; margin: 1rem 0 1.5rem; max-width: 80ch; }
.note p { margin: 0; }
.note strong { color: var(--accent); }
.toc { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 0.75rem 1rem 0.9rem;
       margin: 1rem 0 2rem; }
.toc ol { margin: 0.25rem 0 0; padding-left: 1.4rem; columns: 16rem; column-gap: 2rem; }
.toc li { break-inside: avoid; margin: 0.1rem 0; }
.parts { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0 0; padding: 0; list-style: none; }
.parts a, .parts span { display: inline-block; padding: 0.2rem 0.65rem; border: 1px solid var(--line);
       border-radius: 999px; text-decoration: none; font-size: 0.9rem; }
.parts span { background: var(--surface-2); }
.grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr)); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; overflow: hidden;
        display: flex; flex-direction: column; box-shadow: 0 1px 2px var(--shadow); min-width: 0; }
.card .thumb { display: block; background: var(--art-bg); padding: 8px; }
.card .thumb img { margin: 0 auto; }
.card-body { padding: 0.75rem 0.9rem 0.9rem; display: flex; flex-direction: column; gap: 0.35rem; flex: 1; }
.card-body h3 { margin: 0; font-size: 1rem; }
.facts { display: grid; grid-template-columns: auto 1fr; gap: 0.1rem 0.75rem; margin: 0; font-size: 0.88rem; }
.facts dt { color: var(--muted); }
.facts dd { margin: 0; min-width: 0; overflow-wrap: anywhere; }
.card-body .more { margin-top: auto; font-size: 0.9rem; }
.famhead { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.25rem 1rem; }
.famhead h2 { margin-bottom: 0.25rem; }
.famlinks { display: flex; flex-wrap: wrap; gap: 0.4rem 1rem; list-style: none; padding: 0; margin: 0.5rem 0 1rem; }
figure { margin: 0; min-width: 0; }
.art { background: var(--art-bg); padding: 10px; border-radius: 8px; display: inline-block; max-width: 100%; }
figcaption { font-size: 0.86rem; color: var(--muted); margin-top: 0.4rem; max-width: 72ch; }
.skin { border-top: 2px solid var(--line); padding-top: 1.25rem; margin-top: 2.5rem; scroll-margin-top: 12px; }
.skin > h2 { margin-top: 0; }
.figs { display: grid; gap: 1.25rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr));
        align-items: start; margin-top: 0.75rem; }
.sheet { overflow-x: auto; -webkit-overflow-scrolling: touch; border: 1px solid var(--line); border-radius: 8px;
         background: var(--surface); margin-top: 0.5rem; max-width: 100%; }
.sheet table { border-collapse: collapse; font-size: 0.86rem; }
.sheet th, .sheet td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--line); text-align: left;
                       vertical-align: top; }
.sheet thead th { position: sticky; top: 0; background: var(--surface-2); font-weight: 600; white-space: nowrap; }
.sheet td.meta { min-width: 13rem; max-width: 18rem; }
.sheet td.meta dl { display: grid; grid-template-columns: auto 1fr; gap: 0.05rem 0.5rem; margin: 0.3rem 0 0; }
.sheet td.meta dt { color: var(--muted); }
.sheet td.meta dd { margin: 0; overflow-wrap: anywhere; }
.sheet td.state { background: var(--art-bg); }
.sheet td.state img { max-width: none; }
.sheet .def { display: inline-block; margin-left: 0.3rem; font-size: 0.72rem; text-transform: uppercase;
              letter-spacing: 0.06em; color: var(--accent); }
.empty { color: var(--muted); font-style: italic; }
.pair { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr));
        align-items: start; }
.tag { display: inline-block; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;
       padding: 0.1rem 0.5rem; border-radius: 999px; border: 1px solid var(--line); margin-bottom: 0.4rem; }
.tag.base { background: var(--surface-2); }
.tag.cozy { background: var(--note-bg); border-color: var(--note-line); }
.ramps { display: grid; gap: 1rem; }
.ramp { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 0.75rem 0.9rem; }
.ramp h3 { margin: 0 0 0.5rem; font-size: 1rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.75rem; list-style: none; margin: 0; padding: 0; }
.chip { width: 7.5rem; font-size: 0.82rem; }
.chip .sw { height: 2.75rem; border-radius: 6px; border: 1px solid var(--line); margin-bottom: 0.3rem; }
.chip code { background: none; padding: 0; }
.spec { list-style: none; padding: 0; margin: 0.5rem 0 1rem; display: grid; gap: 0.25rem; }
table.plain { border-collapse: collapse; font-size: 0.9rem; margin: 0.5rem 0 1rem; }
table.plain th, table.plain td { border-bottom: 1px solid var(--line); padding: 0.35rem 0.6rem; text-align: left; vertical-align: top; }
.tablewrap { overflow-x: auto; max-width: 100%; }
footer { margin-top: 3rem; border-top: 1px solid var(--line); padding-top: 1rem; font-size: 0.85rem; color: var(--muted); }
"""


def _swatch_classes():
    return '\n'.join(f'.sw-{n} {{ background: var(--sw-{n}); }}' for n in pal.NAMED)


def _themed_css():
    """CSS with the active theme's colour tokens (cozy keeps CSS as written)."""
    if not THEME['tokens']:
        return CSS
    light, dark = THEME['tokens']
    css = CSS.replace('.tag.cozy {', f'.tag.{THEME["key"]} {{')   # the replacement-side tag
    head, sep, tail = css.partition('@media')

    def sub(part, values):
        for k, v in values.items():
            part = re.sub(rf'(\n\s*{re.escape(k)}:\s*)#[0-9a-fA-F]{{3,8}};', rf'\g<1>{v};', part)
        return part
    return sub(head, light) + sep + sub(tail, dark)


def page(title, body, swatches=False):
    css = _themed_css().replace('%SWATCHES%', _swatch_tokens() if swatches else '')
    if swatches:
        css += _swatch_classes() + '\n'
    return (f'<title>{html.escape(title)}</title>\n'
            '<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<style>{css}</style>\n'
            f'<div class="wrap">\n{body}\n</div>\n')


def note():
    caveat = (f'<div class="note" role="note"><p><strong>Schematic composite, not a gameplay screenshot.</strong> '
              f'{SCHEMATIC_NOTE[len("Schematic composite, not a gameplay screenshot. "):]}</p></div>')
    if THEME.get('provenance'):         # a theme's own provenance statement (Faithful: no Mojang pixels)
        caveat += f'<div class="note" role="note"><p>{THEME["provenance"]}</p></div>'
    return caveat


def esc(s):
    return html.escape(str(s))


def head_sha():
    r = subprocess.run(['git', 'show', '-s', '--format=%H', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() or 'unknown'


def textures_dirty():
    r = subprocess.run(['git', 'status', '--porcelain', '--', 'pack-source/assets/quasar_gui/textures'],
                       cwd=ROOT, capture_output=True, text=True)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# Facts about a skin
# ---------------------------------------------------------------------------

def frame_text(s):
    if not s.art_layers:
        return 'no'
    return 'yes, ' + ', '.join(f'{a.id} {a.w}x{a.h}' for a in s.art_layers)


def presentation_text(s):
    return s.presentation.replace('_', ' ')


def family_token(family, part=None):
    return f'family-{family}' + (f'-{part}' if part else '')


def family_title(family):
    return f'{THEME["name"]} {FAMILY_NAME[family]} Family'


# ---------------------------------------------------------------------------
# Family pages
# ---------------------------------------------------------------------------

def button_cell(key, b, state, bg):
    cell = Image.new('RGBA', (b.w, b.h), CELL_BACKDROP)
    cell.alpha_composite(bg.crop((b.x, b.y, b.x + b.w, b.y + b.h)))
    cell.alpha_composite(pv.load_texture(f'buttons/{key}/{b.id}/{state}.png'))
    return _scaled(cell, 4)


def buttons_table(s):
    if not s.buttons:
        return ('<p class="empty">No painted button regions: this screen keeps its native content '
                '(presentation: ' + esc(presentation_text(s)) + ').</p>')
    bg = pv.load_texture(pv._bg_rel(s))
    head = ''.join(f'<th scope="col"><code>{st}</code></th>' for st in geo.STATES)
    rows = []
    for b in s.buttons:
        label = ' / '.join(b.text_lines)
        meta = (f'<strong><code>{esc(b.id)}</code></strong>'
                f'<dl><dt>Size</dt><dd>{b.w}x{b.h} at ({b.x}, {b.y})</dd>'
                f'<dt>Style</dt><dd>{esc(b.style)}</dd><dt>Role</dt><dd>{esc(b.role)}</dd>'
                f'<dt>Label</dt><dd>{esc(b.label)}' + (f' (lettered &ldquo;{esc(label)}&rdquo;)' if label != b.label else '')
                + '</dd>'
                + (f'<dt>Icon</dt><dd>{esc(b.icon)}</dd>' if b.icon else '')
                + f'<dt>Default</dt><dd>{esc(b.default_state)}</dd></dl>')
        cells = []
        for st in geo.STATES:
            img = button_cell(s.key, b, st, bg)
            cells.append(f'<td class="state">{img_tag(img, f"{b.id} button, {st} state, 4x")}</td>')
        rows.append(f'<tr><td class="meta">{meta}</td>{"".join(cells)}</tr>')
    return (f'<div class="sheet" tabindex="0" role="region" aria-label="{esc(s.key)} buttons in six states">'
            f'<table><thead><tr><th scope="col">Button</th>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            '<p class="small muted">Each state is shown at 4x over its own crop of the background '
            '(dark backdrop where the background is transparent), exactly as <code>preview.buttons_sheet</code> '
            'composes it.</p>')


def skin_section(key):
    s = geo.skin(key)
    acc = pal.accent_for(key, s.family)
    acc_name = pal.ramp_of(acc['accent'][0])[0]
    sec_name = pal.ramp_of(acc['secondary'][0])[0]
    facts = (f'<dl class="facts"><dt>Layout</dt><dd>{esc(s.layout)}, {s.width}x{s.height} ({esc(s.menu_type)})</dd>'
             f'<dt>Presentation</dt><dd>{esc(presentation_text(s))}</dd>'
             f'<dt>Buttons</dt><dd>{len(s.buttons)} ({len(s.buttons) * len(geo.STATES)} state PNGs)</dd>'
             f'<dt>Frame</dt><dd>{esc(frame_text(s))}</dd>'
             f'<dt>Content wells</dt><dd>{len(s.content_slots)} native + {len(s.player_slots)} player</dd>'
             f'<dt>Accent</dt><dd>{esc(acc_name)} / {esc(sec_name)}: {esc(acc["motif"])}</dd>'
             f'<dt>Background</dt><dd><code>pack-source/{esc(s.asset)}</code></dd></dl>')
    comp = pv.render(key, content='sample', scale=3)
    full = pv.render(key, content='full', long_title=True, scale=3)
    figs = [
        f'<figure><div class="art">{img_tag(comp, f"{key} composite with sample items, 3x")}</div>'
        f'<figcaption>Composite at 3x: default button states, about a third of the wells filled with schematic '
        f'items, sample title &ldquo;{esc(pv._title_text(key))}&rdquo;.</figcaption></figure>',
        f'<figure><div class="art">{img_tag(full, f"{key} composite with every well filled and a long title, 3x")}</div>'
        f'<figcaption>Long title / full content at 3x: every native and player well filled, an over-long title '
        f'clipped to the text-safe width the client uses.</figcaption></figure>',
    ]
    frames = []
    for a in s.art_layers:
        fr = pv.render_frame_alone(key, a.id, scale=3)
        frames.append(f'<figure><div class="art">{img_tag(fr, f"{key} {a.id} frame alone on mid-grey, 3x")}</div>'
                      f'<figcaption>Outer frame <code>{esc(a.id)}</code> alone ({a.w}x{a.h}, offset {a.x}, {a.y}) '
                      f'on a neutral mid-grey backdrop at 3x; the hole is the native container.</figcaption></figure>')
    if not frames:
        frames.append('<p class="empty">This screen has no outer frame layer.</p>')
    bgimg = pv.render_background_alone(key, outline_clearances=True, scale=3)
    bgfig = (f'<figure><div class="art">{img_tag(bgimg, f"{key} raw background with clearances outlined, 3x")}</div>'
             f'<figcaption>Raw background at 3x on a grey checker; magenta outlines mark every alpha-zero '
             f'clearance (content wells, player wells, extra transparent rectangles).</figcaption></figure>')
    return (f'<section class="skin" id="{esc(key)}" aria-labelledby="h-{esc(key)}">'
            f'<p class="eyebrow">{esc(FAMILY_NAME[s.family])} family</p>'
            f'<h2 id="h-{esc(key)}"><code>{esc(key)}</code></h2>{facts}'
            f'<h3>Composites</h3><div class="figs">{"".join(figs)}</div>'
            f'<h3>Buttons in all six states</h3>{buttons_table(s)}'
            f'<h3>Frame and background</h3><div class="figs">{"".join(frames)}{bgfig}</div>'
            '<p class="small"><a href="#top">Back to top</a></p></section>')


def plan_parts(family, keys, sizes):
    """Group skins into pages under PAGE_BUDGET; [keys] when the family fits."""
    overhead = 60_000
    if sum(sizes[k] for k in keys) + overhead <= PAGE_BUDGET:
        return [keys]
    groups = SPLIT_GROUPS.get(family, [[k] for k in keys])
    assert sorted(k for g in groups for k in g) == sorted(keys), f'{family}: split groups do not cover the family'
    # break any group that is itself too big, skin by skin
    chunks = []
    for g in groups:
        cur, n = [], overhead
        for k in g:
            if cur and n + sizes[k] > PAGE_BUDGET:
                chunks.append(cur); cur, n = [], overhead
            cur.append(k); n += sizes[k]
        chunks.append(cur)
    # pack adjacent chunks together while they fit
    parts, cur, n = [], [], overhead
    for c in chunks:
        cs = sum(sizes[k] for k in c)
        if cur and n + cs > PAGE_BUDGET:
            parts.append(cur); cur, n = [], overhead
        cur += c; n += cs
    parts.append(cur)
    return parts


def family_pages(family, keys, all_parts):
    sections = {k: skin_section(k) for k in keys}
    sizes = {k: len(v.encode('utf-8')) for k, v in sections.items()}
    parts = plan_parts(family, keys, sizes)
    all_parts[family] = parts
    pages = []
    nbtn = sum(len(geo.skin(k).buttons) for k in keys)
    nfr = sum(len(geo.skin(k).art_layers) for k in keys)
    acc = pal.FAMILY_ACCENT[family]
    for i, part in enumerate(parts, 1):
        split = len(parts) > 1
        token = family_token(family, i if split else None)
        title = f'{FAMILY_NAME[family]} Part {i}' if split else family_title(family)
        toc = ''.join(f'<li><a href="#{esc(k)}">{esc(k)}</a></li>' for k in part)
        partnav = ''
        if split:
            items = []
            for j, p in enumerate(parts, 1):
                lbl = f'Part {j}: {esc(p[0])} &ndash; {esc(p[-1])}' if len(p) > 1 else f'Part {j}: {esc(p[0])}'
                items.append(f'<li><span aria-current="page">{lbl}</span></li>' if j == i else
                             f'<li><a href="{{{{URL:{family_token(family, j)}}}}}">{lbl}</a></li>')
            partnav = f'<p class="eyebrow">This family is split across {len(parts)} pages</p><ul class="parts">{"".join(items)}</ul>'
        h1 = (f'{THEME["name"]} {esc(FAMILY_NAME[family])} family' + (f', part {i} of {len(parts)}' if split else ''))
        body = (f'<nav class="topnav" aria-label="Gallery"><a href="{{{{URL:index}}}}">Back to index</a>'
                f'<a href="{{{{URL:before-after}}}}">Midnight vs {THEME["name"]}</a></nav>'
                f'<header id="top"><p class="eyebrow">CDUResources {THEME["name"].lower()} theme &middot; fixture gallery</p>'
                f'<h1>{h1}</h1>'
                f'<p class="lede">{len(keys)} skins, {nbtn} painted buttons ({nbtn * len(geo.STATES)} state PNGs) '
                f'and {nfr} outer frames. Accent motif: {esc(acc["motif"])}.'
                + (f' This page shows {len(part)} of them.' if split else '') + '</p></header>'
                + note()
                + f'<nav class="toc" aria-label="Contents"><p class="eyebrow">Contents</p>{partnav}<ol>{toc}</ol></nav>'
                + ''.join(sections[k] for k in part)
                + f'<footer><a href="{{{{URL:index}}}}">Back to index</a> &middot; generated by '
                  '<code>tools/cozy/build_fixtures.py</code></footer>')
        name = token + '.html'
        pages.append((name, page(title, body)))
    return pages


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def part_of(all_parts, family, key):
    parts = all_parts[family]
    if len(parts) == 1:
        return family_token(family)
    for i, p in enumerate(parts, 1):
        if key in p:
            return family_token(family, i)
    raise KeyError(key)


def index_page(by_family, all_parts, sha):
    total_btn = sum(len(geo.skin(k).buttons) for k in geo.all_skins())
    total_fr = sum(len(geo.skin(k).art_layers) for k in geo.all_skins())
    fam_links = []
    for f in FAMILY_ORDER:
        parts = all_parts[f]
        if len(parts) == 1:
            fam_links.append(f'<li><a href="{{{{URL:{family_token(f)}}}}}">{esc(FAMILY_NAME[f])}</a> '
                             f'<span class="muted small">({len(by_family[f])})</span></li>')
        else:
            sub = ', '.join(f'<a href="{{{{URL:{family_token(f, i)}}}}}">part {i}</a>' for i in range(1, len(parts) + 1))
            fam_links.append(f'<li>{esc(FAMILY_NAME[f])} <span class="muted small">({len(by_family[f])})</span>: {sub}</li>')
    groups = []
    for f in FAMILY_ORDER:
        cards = []
        for k in by_family[f]:
            s = geo.skin(k)
            thumb = pv.render(k, content='sample', scale=1)
            target = f'{{{{URL:{part_of(all_parts, f, k)}}}}}#{k}'
            cards.append(
                f'<article class="card" id="card-{esc(k)}">'
                f'<a class="thumb" href="{target}" aria-label="Open {esc(k)} on its family page">'
                f'{img_tag(_scaled(thumb, 2), f"{k} composite thumbnail, 2x")}</a>'
                f'<div class="card-body"><p class="eyebrow">{esc(FAMILY_NAME[f])}</p>'
                f'<h3><code>{esc(k)}</code></h3>'
                f'<dl class="facts"><dt>Geometry</dt><dd>{esc(s.layout)}, {s.width}x{s.height}</dd>'
                f'<dt>Buttons</dt><dd>{len(s.buttons)}</dd>'
                f'<dt>Frame</dt><dd>{esc(frame_text(s))}</dd>'
                f'<dt>Content</dt><dd>{esc(presentation_text(s))}</dd></dl>'
                f'<a class="more" href="{target}">Open on the family page</a></div></article>')
        nb = sum(len(geo.skin(k).buttons) for k in by_family[f])
        parts = all_parts[f]
        head_link = (f'<a href="{{{{URL:{family_token(f)}}}}}">Open the family page</a>' if len(parts) == 1 else
                     'Pages: ' + ', '.join(f'<a href="{{{{URL:{family_token(f, i)}}}}}">part {i}</a>'
                                           for i in range(1, len(parts) + 1)))
        groups.append(f'<section id="fam-{f}" aria-labelledby="fh-{f}"><div class="famhead">'
                      f'<h2 id="fh-{f}">{esc(FAMILY_NAME[f])}</h2><span class="muted small">{len(by_family[f])} skins, '
                      f'{nb} buttons &middot; {head_link}</span></div>'
                      f'<p class="small muted">Motif: {esc(pal.FAMILY_ACCENT[f]["motif"])}.</p>'
                      f'<div class="grid">{"".join(cards)}</div></section>')
    ramps = []
    for rname, cols in pal.RAMPS.items():
        chips = ''.join(f'<li class="chip"><div class="sw sw-{pal.name_of(c)}" role="img" aria-label="{pal.name_of(c)} swatch"></div>'
                        f'<code>{pal.name_of(c)}</code><br><span class="muted">{c[0]}, {c[1]}, {c[2]}</span></li>'
                        for c in cols)
        ramps.append(f'<div class="ramp"><h3>{esc(rname)} <span class="muted small">({len(cols)}, dark to light)</span></h3>'
                     f'<ul class="chips">{chips}</ul></div>')
    # every single-colour alias the active palette defines (cozy has the first seven only)
    aliases = [(a, getattr(pal, a)) for a in THEME.get('aliases') or
               ('OUTLINE', 'OUTLINE_DEEP', 'TEXT_DARK', 'TEXT_LIGHT', 'TEXT_GOLD',
                'SHADOW', 'GLOW', 'SOUL_GLOW', 'TITLE_BAND', 'SHEET')
               if hasattr(pal, a)]
    alias_txt = ', '.join(f'<code>{a}</code> = <code>{pal.name_of(c)}</code>' for a, c in aliases)
    spec = L.specimen(scale=1)
    (h_attr, h_name, h_desc), (s_attr, s_name, s_desc) = THEME['faces']
    H, S = getattr(L, h_attr), getattr(L, s_attr)
    body = (f'<nav class="topnav" aria-label="Gallery"><a href="#families">Families</a><a href="#palette">Palette</a>'
            f'<a href="#typeface">Typeface</a><a href="{{{{URL:before-after}}}}">Midnight vs {THEME["name"]}</a></nav>'
            f'<header id="top"><p class="eyebrow">CDUResources &middot; {THEME["branch"]}</p>'
            f'<h1>{THEME["name"]} GUI fixtures</h1>'
            f'<p class="lede">Every texture of the {THEME["blurb"]} for the Quasar GUI pack: '
            f'{len(geo.all_skins())} screens, {total_btn} painted buttons in six states each '
            f'({total_btn * len(geo.STATES)} PNGs) and {total_fr} outer frames, grouped by family.</p></header>'
            + note()
            + '<h2 id="what">What this is</h2>'
              '<p>These pages let you inspect the artwork without checking out the branch. Each picture is a '
              'schematic composite made by the repository&rsquo;s preview tool, layering the texture PNGs the way '
              'the client does: dimmed world, a flat stand-in for the vanilla container, schematic items, the outer '
              'frame, the menu background, each button in its default state, then the live title and '
              '&ldquo;Inventory&rdquo; label. They are not gameplay screenshots: the grey squares, slot backdrop and '
              'titles are synthetic. Family pages add every button in all six states at 4x, each frame alone and '
              'each raw background with its transparent clearances outlined.</p>'
            + f'<p class="small muted">Built from commit <code>{esc(sha[:12])}</code>. Thumbnails are rendered at 1x '
              'and scaled 2x nearest-neighbour.</p>'
            + f'<h3>Pages</h3><ul class="famlinks">{"".join(fam_links)}'
              f'<li><a href="{{{{URL:before-after}}}}">Midnight vs {THEME["name"]}</a> <span class="muted small">(before / after)</span></li></ul>'
            + f'<div id="families">{"".join(groups)}</div>'
            + f'<h2 id="palette">Master palette</h2>'
              f'<p>{len(pal.NAMED)} named colours in {len(pal.RAMPS)} ramps, each ordered dark to light; {"pure black and white allowed (the vanilla language uses them)" if THEME.get("pure_bw") else "no pure black or white"}. '
              f'Textures use only these colours, at alpha 0 or 255. Aliases: {alias_txt}.</p>'
              f'<div class="ramps">{"".join(ramps)}</div>'
            + f'<h2 id="typeface">Bespoke pixel typeface</h2>'
              '<p>Two original faces drawn for the pack (CC0-1.0), used for every painted label.</p>'
              f'<ul class="spec"><li><strong>{h_name}</strong>: cap {H.cap_height} / x {H.x_height} / desc '
              f'{H.descender} / track {H.tracking}; {h_desc}.</li>'
              f'<li><strong>{s_name}</strong>: cap {S.cap_height} / track {S.tracking}; {s_desc}.</li></ul>'
              f'<figure><div class="art">{img_tag(spec, f"Typeface specimen of {h_name} and {s_name} with fit checks", display_scale=3)}</div>'
              '<figcaption>Specimen from <code>lettering.specimen()</code>, shown 3x: both faces, fit checks against '
              'the tightest button widths, kerning pairs, shadow and outline treatments.</figcaption></figure>'
            + f'<footer>Generated by <code>tools/cozy/build_fixtures.py</code>; see <code>{THEME["doc"]}</code>.</footer>')
    return page(f'{THEME["name"]} GUI Fixtures', body, swatches=True)


# ---------------------------------------------------------------------------
# Before / after
# ---------------------------------------------------------------------------

def _git_blob(path):
    r = subprocess.run(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def extract_baseline(keys, dest):
    """Write the baseline PNGs of ``keys`` under dest/pack-source/assets/quasar_gui/textures.
    Returns (textures dir, {key: [missing relative paths]})."""
    tex = Path(dest) / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'
    missing = {}
    for k in keys:
        for p in geo.asset_paths(k):
            rel = p.resolve().relative_to(ROOT.resolve()).as_posix()
            blob = _git_blob(rel)
            if blob is None:
                missing.setdefault(k, []).append(rel)
                continue
            out = Path(dest) / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(blob)
    return tex, missing


def before_after_page(all_parts):
    with tempfile.TemporaryDirectory(prefix='cozy-baseline-') as tmp:
        tex, missing = extract_baseline(BEFORE_AFTER, tmp)
        if missing:
            raise SystemExit(f'baseline commit lacks textures, refusing to mix artwork: {missing}')
        rows = []
        for k in BEFORE_AFTER:
            s = geo.skin(k)
            before = pv.render(k, overrides_dir=tex, scale=3)
            after = pv.render(k, scale=3)
            after_alt = f'{k} {THEME["name"].lower()} replacement composite, 3x'
            fam = f'{{{{URL:{part_of(all_parts, s.family, k)}}}}}#{k}'
            rows.append(
                f'<section class="skin" id="{esc(k)}" aria-labelledby="h-{esc(k)}">'
                f'<p class="eyebrow">{esc(FAMILY_NAME[s.family])} family &middot; {esc(s.layout)} {s.width}x{s.height}</p>'
                f'<h2 id="h-{esc(k)}"><code>{esc(k)}</code></h2>'
                f'<div class="pair">'
                f'<figure><span class="tag base">Baseline &middot; midnight</span>'
                f'<div class="art">{img_tag(before, f"{k} baseline midnight artwork composite, 3x")}</div>'
                f'<figcaption>Before: midnight artwork from commit <code>{BASELINE[:7]}</code>.</figcaption></figure>'
                f'<figure><span class="tag {THEME["key"]}">{THEME["name"]} &middot; replacement</span>'
                f'<div class="art">{img_tag(after, after_alt)}</div>'
                f'<figcaption>After: {THEME["name"].lower()} artwork on <code>{THEME["branch"]}</code>.</figcaption></figure></div>'
                f'<p class="small"><a href="{fam}">Every texture of {esc(k)}</a> &middot; <a href="#top">Back to top</a></p>'
                '</section>')
    toc = ''.join(f'<li><a href="#{esc(k)}">{esc(k)}</a></li>' for k in BEFORE_AFTER)
    fams = sorted({geo.skin(k).family for k in BEFORE_AFTER}, key=FAMILY_ORDER.index)
    body = (f'<nav class="topnav" aria-label="Gallery"><a href="{{{{URL:index}}}}">Back to index</a></nav>'
            f'<header id="top"><p class="eyebrow">CDUResources {THEME["name"].lower()} theme &middot; before and after</p>'
            f'<h1>Midnight vs {THEME["name"]}</h1>'
            f'<p class="lede">{len(BEFORE_AFTER)} representative screens covering all {len(fams)} families. '
            f'The left (or upper) picture of each pair is the <strong>baseline midnight</strong> artwork from commit '
            f'<code>{BASELINE}</code>; the right (or lower) one is the <strong>{THEME["name"].lower()} replacement</strong>.</p></header>'
            + note()
            + '<p class="small muted">Both sides use the same schematic items, title and default button states, so '
              'only the texture PNGs differ.</p>'
            + f'<nav class="toc" aria-label="Contents"><p class="eyebrow">Contents</p><ol>{toc}</ol></nav>'
            + ''.join(rows)
            + '<footer><a href="{{URL:index}}">Back to index</a> &middot; generated by '
              '<code>tools/cozy/build_fixtures.py</code></footer>')
    return page(f'Midnight vs {THEME["name"]}', body)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

VOID = {'meta', 'img', 'br', 'hr', 'input', 'link', 'source', 'wbr', 'col', 'area', 'base', 'embed', 'track'}


class _Checker(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.hrefs, self.ids, self.srcs = [], [], [], set(), []
        self.first_tag = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.first_tag = self.first_tag or tag
        if tag in ('html', 'head', 'body') or tag == '!doctype':
            self.errors.append(f'forbidden <{tag}>')
        if 'id' in a:
            if a['id'] in self.ids:
                self.errors.append(f'duplicate id {a["id"]}')
            self.ids.add(a['id'])
        if 'href' in a:
            self.hrefs.append(a['href'])
        if 'src' in a:
            self.srcs.append(a['src'])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'unbalanced </{tag}> (open: {self.stack[-3:]})')
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()

    def handle_decl(self, decl):
        self.errors.append(f'forbidden declaration <!{decl}>')


TOKEN = re.compile(r'^\{\{URL:(index|before-after|family-[a-z_]+(?:-\d+)?)\}\}(#[a-z0-9_]+)?$')
HEX = re.compile(r'#[0-9a-fA-F]{3,8}\b|rgb\(')


def check_page(path, known_tokens):
    text = path.read_text(encoding='utf-8')
    size = path.stat().st_size
    c = _Checker()
    c.feed(text)
    c.close()
    errs = list(c.errors)
    if c.stack:
        errs.append(f'unclosed tags {c.stack}')
    if not text.startswith('<title>'):
        errs.append('does not start with <title>')
    if size >= HARD_LIMIT:
        errs.append(f'{size} bytes >= {HARD_LIMIT}')
    if 'schematic composite, not a gameplay screenshot' not in text.lower():
        errs.append('missing schematic caveat')
    for h in c.hrefs:
        if h.startswith('#'):
            if h[1:] not in c.ids:
                errs.append(f'broken in-page anchor {h}')
            continue
        if h.startswith(ARTIFACT_PREFIX):
            continue
        m = TOKEN.match(h)
        if not m:
            errs.append(f'unresolved non-token link {h!r}')
        elif m.group(1) not in known_tokens:
            errs.append(f'unknown token {m.group(1)}')
    for s in c.srcs:
        if not s.startswith('data:image/png;base64,'):
            errs.append(f'external resource {s[:60]!r}')
    if re.search(r'(?:src|href)\s*=\s*["\']?(?:https?:)?//', text.replace(ARTIFACT_PREFIX, 'artifact:')) or '@import' in text or 'url(' in text:
        errs.append('external reference found')
    # colour literals must only appear in the token blocks at the top of <style>
    style = text.split('<style>', 1)[1].split('</style>', 1)[0]
    rules = style.split('* { box-sizing', 1)[1]
    if HEX.search(rules):
        errs.append('colour literal outside the token blocks')
    if HEX.search(text.split('</style>', 1)[1].replace('&#', '')):
        errs.append('colour literal in markup')
    tokens = sorted(set(re.findall(r'\{\{URL:[^}]+\}\}', text)))
    return size, errs, tokens


def run_checks(names):
    known = {n[:-5] for n in names}
    ok = True
    print()
    for n in names:
        size, errs, tokens = check_page(OUT / n, known)
        status = 'OK  ' if not errs else 'FAIL'
        print(f'{status} {n:34s} {size:>11,d} bytes  {size / 1e6:6.2f} MB  links: {" ".join(tokens)}')
        for e in errs[:12]:
            print(f'       {e}')
        ok &= not errs
    return ok


# ---------------------------------------------------------------------------

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    dirty = textures_dirty()
    if dirty:
        print(f'WARNING: {len(dirty)} uncommitted texture changes; pages show the working tree')
    sha = head_sha()
    by_family = geo.skins_by_family()
    assert set(by_family) == set(FAMILY_ORDER), sorted(by_family)
    assert len(geo.all_skins()) == 56
    for f in OUT.glob('*.html'):           # drop pages from an earlier split plan
        f.unlink()
    all_parts, names = {}, []
    urls = url_map()
    for fam in FAMILY_ORDER:
        for name, text in family_pages(fam, by_family[fam], all_parts):
            text = resolve_links(text, urls)
            (OUT / name).write_text(text, encoding='utf-8', newline='\n')
            names.append(name)
            print(f'WROTE {name:34s} {len(text.encode("utf-8")):>11,d} bytes')
    for name, text in (('before-after.html', before_after_page(all_parts)),
                       ('index.html', index_page(by_family, all_parts, sha))):
        text = resolve_links(text, urls)
        (OUT / name).write_text(text, encoding='utf-8', newline='\n')
        names.append(name)
        print(f'WROTE {name:34s} {len(text.encode("utf-8")):>11,d} bytes')
    for fam, parts in all_parts.items():
        if len(parts) > 1:
            print(f'SPLIT {fam}: ' + ' | '.join(f'{i}: {", ".join(p)}' for i, p in enumerate(parts, 1)))
    return sorted(names, key=lambda n: (n != 'index.html', n))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='only check pages already in the output directory')
    ap.add_argument('--theme', choices=tuple(THEME_CONFIG), help='gallery theme (default: '
                    f'${THEME_ENV}, else cozy)')
    a = ap.parse_args(argv)
    try:
        configure(a.theme)
    except ValueError as exc:
        ap.error(str(exc))
    names = (sorted((p.name for p in OUT.glob('*.html')), key=lambda n: (n != 'index.html', n))
             if a.check else build())
    return 0 if run_checks(names) else 1


if __name__ == '__main__':
    sys.exit(main())
