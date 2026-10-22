#!/usr/bin/env python3
"""Composite previews of cozy textures exactly as the client layers them.

    python tools/cozy/preview.py auction_house
    python tools/cozy/preview.py trade_both_ready --content full --long-title
    python tools/cozy/preview.py ticket_invalid --state pulse_2
    python tools/cozy/preview.py trade_idle --states ready=selected,other_money=disabled
    python tools/cozy/preview.py economy_hub --outline-clearances
    python tools/cozy/preview.py economy_hub --buttons-sheet
    python tools/cozy/preview.py economy_hub --frame-alone | --background-alone
    python tools/cozy/preview.py --all            # every skin, default options

Output: a nearest-neighbour PNG (``--scale``, default 3) at ``--out`` or
``evidence/cozy-previews/<key>[-<variant>].png``. Importable API:
``render``, ``render_frame_alone``, ``render_background_alone``,
``buttons_sheet``, ``export``.

Composition order (bottom to top), matching the client: dimmed world, a
SCHEMATIC stand-in for the vanilla container texture (flat grey panel and slot
squares, drawn here, not Mojang art), native items (flat grey placeholder
squares with a count numeral), outer frame layer(s) at their artLayers
offsets, the background, each button in its chosen state, then the live
dark-grey title at the title anchor (none on the dispenser / trade_money,
x=29 on crafting) and the live "Inventory" label. Everything schematic exists
only in the preview image: this tool reads pack-source (or overrides) and
writes only under evidence/.

Licence: MIT.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import geometry as geo  # noqa: E402
import lettering as L  # noqa: E402

ROOT = geo.ROOT
OUT_DIR = ROOT / 'evidence' / 'cozy-previews'
WORLD = (38, 34, 40, 255)
TITLE_GREY = (64, 64, 64, 255)          # vanilla container label colour 0x404040
MAGENTA = (255, 0, 255, 255)
# Schematic vanilla-container stand-in (flat colours, not game art)
V_PANEL, V_DARK, V_LIGHT, V_SLOT = (198, 198, 198, 255), (85, 85, 85, 255), (250, 250, 250, 255), (139, 139, 139, 255)
ITEM_FILL, ITEM_EDGE, ITEM_TEXT = (150, 154, 164, 255), (92, 96, 108, 255), (250, 250, 250, 255)

LONG_TITLE = 'Auction House - Enchanted Netherite Pickaxe of Efficiency and Mending, Page 12 of 40'


# ---------------------------------------------------------------------------
# Asset loading
# ---------------------------------------------------------------------------

def _texture_rel(path):
    p = Path(path)
    return p.resolve().relative_to(geo.TEXTURES.resolve()).as_posix()


def load_texture(rel, overrides=None, overrides_dir=None):
    """Load a texture by its path relative to textures/ ('menu/x.png',
    'buttons/<key>/<id>/<state>.png', 'frames/<key>/<layer>.png').
    ``overrides`` maps such a path to a PIL image or file path;
    ``overrides_dir`` is a directory laid out like textures/."""
    if overrides and rel in overrides:
        v = overrides[rel]
        return (v if isinstance(v, Image.Image) else Image.open(v)).convert('RGBA')
    if overrides_dir and (Path(overrides_dir) / rel).is_file():
        return Image.open(Path(overrides_dir) / rel).convert('RGBA')
    p = geo.TEXTURES / rel
    if not p.is_file():
        raise FileNotFoundError(f'missing texture {p}')
    return Image.open(p).convert('RGBA')


def _bg_rel(s):
    return s.asset.split('textures/', 1)[1]


# ---------------------------------------------------------------------------
# Schematic layers (preview only)
# ---------------------------------------------------------------------------

def _vanilla_standin(img, s, ox, oy):
    d = ImageDraw.Draw(img)
    d.rectangle((ox, oy, ox + s.width - 1, oy + s.height - 1), fill=V_PANEL, outline=V_DARK)
    for slot in s.all_slots + s.player_slots:
        x, y = ox + slot.x - 1, oy + slot.y - 1
        d.rectangle((x, y, x + 17, y + 17), fill=V_SLOT)
        d.line((x, y, x + 16, y), fill=V_DARK); d.line((x, y, x, y + 16), fill=V_DARK)
        d.line((x + 1, y + 17, x + 17, y + 17), fill=V_LIGHT); d.line((x + 17, y + 1, x + 17, y + 17), fill=V_LIGHT)
    for r in s.extra_transparent:   # crafting: recipe-book toggle and arrow stand-ins
        x, y = ox + r.x, oy + r.y
        if r.w < 24:
            d.rectangle((x + 1, y + 1, x + r.w - 2, y + r.h - 2), fill=(96, 160, 96, 255), outline=V_DARK)
        else:
            cy = y + r.h // 2
            d.rectangle((x + 4, cy - 2, x + r.w - 10, cy + 2), fill=V_DARK)
            d.polygon([(x + r.w - 10, cy - 6), (x + r.w - 3, cy), (x + r.w - 10, cy + 6)], fill=V_DARK)


def _sample_slots(s, content):
    if content == 'empty':
        return [], []
    cs = list(s.content_slots)
    if content == 'full':
        top = cs
    else:
        top = [c for c in cs if (c.index * 7 + 2) % 3 == 0]
    ps = list(s.player_slots)
    picks = [ps[i] for i in (27, 30, 35, 4, 12) if i < len(ps)] if content == 'sample' else ps
    return top, picks


def _item(img, slot, ox, oy, count):
    d = ImageDraw.Draw(img)
    x, y = ox + slot.x, oy + slot.y
    d.rectangle((x + 1, y + 1, x + 14, y + 14), fill=ITEM_FILL, outline=ITEM_EDGE)
    d.line((x + 3, y + 3, x + 6, y + 3), fill=(190, 194, 204, 255))


def _count(img, slot, ox, oy, count):
    x, y = ox + slot.x, oy + slot.y
    if count > 1:
        t = str(count)
        w = L.text_width(t, 'sprig')
        L.draw_text(img, x + 17 - w, y + 11, t, ITEM_TEXT, shadow=(60, 60, 60, 255), face='sprig')


def _title_text(key):
    return ' '.join(w.capitalize() for w in key.split('_'))


def _live_text(img, s, ox, oy, long_title):
    if not s.is_dispenser:
        ax, ay = s.title_anchor
        text = LONG_TITLE if long_title else _title_text(s.key)
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        L.draw_text(layer, ox + ax, oy + ay, text, TITLE_GREY)
        if long_title:
            # live text is truncated to the layout text width
            clip = Image.new('RGBA', img.size, (0, 0, 0, 0))
            box = (ox + ax, oy, ox + ax + s.text_safe.w, oy + s.text_safe.bottom + 3)
            clip.paste(layer.crop(box), box[:2])
            layer = clip
        img.alpha_composite(layer)
    iv = s.inventory_label
    L.draw_text(img, ox + iv.x, oy + iv.y, 'Inventory', TITLE_GREY)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def bounds(s):
    xs = [0] + [a.x for a in s.art_layers]
    ys = [0] + [a.y for a in s.art_layers]
    x1 = max([s.width] + [a.x + a.w for a in s.art_layers])
    y1 = max([s.height] + [a.y + a.h for a in s.art_layers])
    return min(xs), min(ys), x1 - min(xs), y1 - min(ys)


def button_state_map(s, state=None, states=None):
    out = {b.id: b.default_state for b in s.buttons}
    if state:
        out = {k: state for k in out}
    for k, v in (states or {}).items():
        if k not in out:
            raise KeyError(f'{s.key} has no button {k!r}')
        if v not in geo.STATES:
            raise ValueError(f'unknown state {v!r}')
        out[k] = v
    return out


def render(key, state=None, content='sample', long_title=False, overrides=None, states=None,
           overrides_dir=None, outline_clearances=False, scale=1, schematic=True, frames=True):
    """Composite preview of ``key``. ``state`` forces one state on every
    button; ``states`` maps button id -> state (defaults come from
    button-layouts.json defaultStates). ``content``: 'sample' (about a third of
    the native wells + a few player slots), 'full' or 'empty'. Returns a PIL
    image at ``scale`` (outlines are drawn 1 px thick after scaling)."""
    s = geo.skin(key)
    bx, by, bw, bh = bounds(s) if frames else (0, 0, s.width, s.height)
    ox, oy = -bx, -by
    img = Image.new('RGBA', (bw, bh), WORLD)
    if schematic:
        _vanilla_standin(img, s, ox, oy)
        top, players = _sample_slots(s, content)
        counts = (1, 16, 64, 3, 1, 32, 7)
        for i, slot in enumerate(top + players):
            _item(img, slot, ox, oy, counts[i % 7])
        for i, slot in enumerate(top + players):   # counts overlap neighbours, like vanilla
            _count(img, slot, ox, oy, counts[i % 7])
    if frames:
        for a in s.art_layers:
            img.alpha_composite(load_texture(f'frames/{key}/{a.id}.png', overrides, overrides_dir), (ox + a.x, oy + a.y))
    img.alpha_composite(load_texture(_bg_rel(s), overrides, overrides_dir), (ox, oy))
    chosen = button_state_map(s, state, states)
    for b in s.buttons:
        img.alpha_composite(load_texture(f'buttons/{key}/{b.id}/{chosen[b.id]}.png', overrides, overrides_dir),
                            (ox + b.x, oy + b.y))
    if schematic:
        _live_text(img, s, ox, oy, long_title)
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
    if outline_clearances:
        _outline(img, [m.moved(ox, oy) for m in s.masks], scale)
    return img


def _outline(img, rects, scale, colour=MAGENTA):
    d = ImageDraw.Draw(img)
    for r in rects:
        d.rectangle((r.x * scale, r.y * scale, r.right * scale - 1, r.bottom * scale - 1), outline=colour)


def render_frame_alone(key, layer_id=None, overrides=None, overrides_dir=None, scale=1):
    """One frame layer on a neutral mid-grey backdrop."""
    s = geo.skin(key)
    a = s.layer(layer_id)
    img = Image.new('RGBA', (a.w, a.h), (128, 128, 128, 255))
    img.alpha_composite(load_texture(f'frames/{key}/{a.id}.png', overrides, overrides_dir))
    if scale != 1:
        img = img.resize((a.w * scale, a.h * scale), Image.Resampling.NEAREST)
    return img


def render_background_alone(key, outline_clearances=True, overrides=None, overrides_dir=None, scale=1):
    """The background alone on a grey checker, clearances outlined in magenta."""
    s = geo.skin(key)
    img = Image.new('RGBA', (s.width, s.height), (150, 150, 150, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, s.height, 4):
        for x in range(0, s.width, 4):
            if (x // 4 + y // 4) % 2:
                d.rectangle((x, y, x + 3, y + 3), fill=(120, 120, 120, 255))
    img.alpha_composite(load_texture(_bg_rel(s), overrides, overrides_dir))
    if scale != 1:
        img = img.resize((s.width * scale, s.height * scale), Image.Resampling.NEAREST)
    if outline_clearances:
        _outline(img, list(s.masks), scale)
    return img


def _font(size=12):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def buttons_sheet(key, scale=4, overrides=None, overrides_dir=None):
    """Every button of ``key`` in all six states at ``scale``, each over its own
    crop of the background, with id / size / style / pin labels."""
    s = geo.skin(key)
    bg = load_texture(_bg_rel(s), overrides, overrides_dir)
    font = _font(13)
    if not s.buttons:
        img = Image.new('RGBA', (520, 60), (236, 230, 220, 255))
        ImageDraw.Draw(img).text((10, 20), f'{key}: no painted button regions', fill=(40, 30, 30), font=font)
        return img
    colw = max(b.w for b in s.buttons) * scale + 14
    label_w = 230
    rows = []
    for b in s.buttons:
        rows.append((b, b.h * scale + 26))
    W = label_w + colw * len(geo.STATES)
    H = 30 + sum(h for _, h in rows)
    img = Image.new('RGBA', (W, H), (236, 230, 220, 255))
    d = ImageDraw.Draw(img)
    for i, st in enumerate(geo.STATES):
        d.text((label_w + i * colw + 4, 8), st, fill=(40, 30, 30), font=font)
    y = 30
    for b, h in rows:
        d.text((8, y + 4), b.id, fill=(40, 30, 30), font=font)
        d.text((8, y + 22), f'{b.w}x{b.h} {b.style} {b.role}', fill=(90, 70, 60), font=_font(11))
        d.text((8, y + 38), f'pin {b.pin}  default {b.default_state}', fill=(90, 70, 60), font=_font(11))
        for i, st in enumerate(geo.STATES):
            cell = Image.new('RGBA', (b.w, b.h), (90, 84, 88, 255))
            cell.alpha_composite(bg.crop((b.x, b.y, b.x + b.w, b.y + b.h)))
            cell.alpha_composite(load_texture(f'buttons/{key}/{b.id}/{st}.png', overrides, overrides_dir))
            cell = cell.resize((b.w * scale, b.h * scale), Image.Resampling.NEAREST)
            img.alpha_composite(cell, (label_w + i * colw + 4, y + 4))
        y += h
    return img


def export(img, path, caption=None):
    """Write a preview PNG (with an optional caption strip)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if caption:
        out = Image.new('RGBA', (img.width, img.height + 20), (30, 26, 30, 255))
        out.alpha_composite(img)
        ImageDraw.Draw(out).text((6, img.height + 4), caption, fill=(230, 220, 205), font=_font(12))
        img = out
    img.convert('RGB').save(path, format='PNG', compress_level=6)
    return path


def _parse_states(text):
    out = {}
    for part in filter(None, (text or '').split(',')):
        k, _, v = part.partition('=')
        out[k.strip()] = v.strip()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('key', nargs='?')
    ap.add_argument('--all', action='store_true', help='render every skin with the given options')
    ap.add_argument('--state', choices=geo.STATES, help='force one state on every button')
    ap.add_argument('--states', help='per-button states, e.g. ready=selected,close=pulse_1')
    ap.add_argument('--content', choices=('sample', 'empty', 'full'), default='sample')
    ap.add_argument('--long-title', action='store_true')
    ap.add_argument('--outline-clearances', action='store_true')
    ap.add_argument('--buttons-sheet', action='store_true')
    ap.add_argument('--frame-alone', action='store_true')
    ap.add_argument('--background-alone', action='store_true')
    ap.add_argument('--overrides-dir', type=Path, help='directory laid out like textures/ to preview instead')
    ap.add_argument('--scale', type=int, default=3)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args(argv)
    keys = geo.all_skins() if a.all else [a.key]
    if not keys or keys == [None]:
        ap.error('give a skin key or --all')
    states = _parse_states(a.states)
    for key in keys:
        if key not in geo.all_skins():
            ap.error(f'unknown skin {key!r}')
        variant = []
        if a.buttons_sheet:
            img = buttons_sheet(key, max(a.scale, 4) if a.scale == 3 else a.scale, overrides_dir=a.overrides_dir)
            variant.append('buttons')
            caption = None
        elif a.frame_alone:
            if not geo.skin(key).art_layers:
                print(f'SKIP {key}: no frame layer'); continue
            img = render_frame_alone(key, overrides_dir=a.overrides_dir, scale=a.scale)
            variant.append('frame')
            caption = f'{key} frame alone on mid-grey'
        elif a.background_alone:
            img = render_background_alone(key, True, overrides_dir=a.overrides_dir, scale=a.scale)
            variant.append('background')
            caption = f'{key} background alone; magenta = alpha-zero clearances'
        else:
            img = render(key, a.state, a.content, a.long_title, None, states, a.overrides_dir,
                         a.outline_clearances, a.scale)
            if a.state: variant.append(a.state)
            if states: variant.append('states')
            if a.content != 'sample': variant.append(a.content)
            if a.long_title: variant.append('long')
            if a.outline_clearances: variant.append('clearances')
            caption = (f'{key} PREVIEW - grey squares, titles and slot backdrop are schematic, not texture content')
        out = a.out if (a.out and not a.all) else OUT_DIR / (key + ('-' + '-'.join(variant) if variant else '') + '.png')
        export(img, out, caption)
        print(f'WROTE {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
