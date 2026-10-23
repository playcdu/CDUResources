"""Standard Faithful compositions: the shared starting point every painter builds on.

These functions turn geometry + primitives into the canonical base look, so
the twelve painters share one grammar and only add family identity on top.
Signatures mirror tools/soulrend/compose.py (and tools/cozy/compose.py), so
the painter workflow is identical:

    base_background(key, seed)        light grey bevelled panel in a black
                                      outline, inset slot trays round every
                                      clearance, the family accent line under
                                      the title band, one family pictogram
                                      tile in the largest static region
    base_frame(key, layer_id, seed)   a bevelled side-panel extension round
                                      the container (40 px each side, 8 px
                                      strips) carrying only the family
                                      pictogram
    paint_button(key, button_id, seed)  normal state in the right grammar
                                      (primary gold-bevel stone / secondary
                                      stone / danger red stone / info recessed
                                      plate / page-turn stone + arrow / icon /
                                      close red stone + X)
    button_states(normal, key, button_id)  all six states via the shared transforms
    save_png / save_button_states / output paths

Everything returned is already finished (masks cleared, pins stamped) and can
be re-finished safely after further painting with ``finish_*``.

Licence: MIT.
"""
from __future__ import annotations

import sys as _sys
import weakref as _weakref
from pathlib import Path as _Path

if __name__ == 'compose':                 # imported by its plain name from tools/faithful
    # one module object per process (see palette.py)
    if 'faithful.compose' in _sys.modules:
        _sys.modules[__name__] = _sys.modules['faithful.compose']
    else:
        _sys.modules['faithful.compose'] = _sys.modules[__name__]
_TOOLS = _Path(__file__).resolve().parents[1]
for _p in (str(_TOOLS), str(_TOOLS / 'cozy')):
    if _p not in _sys.path:
        _sys.path.append(_p)

from PIL import Image  # noqa: E402

import geometry as geo  # noqa: E402  (theme-agnostic, tools/cozy/geometry.py)
from faithful import icons  # noqa: E402
from faithful import lettering as L  # noqa: E402
from faithful import primitives as P  # noqa: E402
from faithful.palette import (ENDER_PANEL_RAMP, GREY, INK, PANEL_RAMP,  # noqa: E402
                              accent_for, rgba)

PIN = rgba('ink_0')          # pin colour passed explicitly: geometry's own default is not ours
DISPENSER_LABEL = 'OFFERED MONEY'
ACCENT_Y = 14                # the family accent line: the free row under the title glyph rows (5-13)
LABEL_LIGHT = 'grey_7'       # white button lettering ...
LABEL_SHADOW = 'ink_1'       # ... with a dark (+1, +1) shadow
LABEL_DARK = 'ink_1'         # dark text on info plates and the panel


def new(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def normalise(img):
    """RGBA copy whose fully transparent pixels are exactly (0, 0, 0, 0)."""
    out = img.convert('RGBA')
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            if px[x, y][3] == 0 and px[x, y] != (0, 0, 0, 0):
                px[x, y] = (0, 0, 0, 0)
    return out


def save_png(img, path):
    """Deterministic RGBA PNG (same settings as the builder)."""
    path = _Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalise(img).save(path, format='PNG', compress_level=9, optimize=False)
    return path


def sheet_for(key):
    """Panel ramp (outline, dark bevel, panel, light bevel) for a skin: the
    purple-tinted variant on the ender chest, light grey otherwise."""
    return ENDER_PANEL_RAMP if key == 'ender_chest' else PANEL_RAMP


wood_for = sheet_for          # cozy-compatible name


def finish_background(img, key):
    return geo.finish_background(img, key, PIN)


def finish_button(img, key, button_id):
    return geo.finish_button(img, key, button_id, PIN)


def finish_frame(img, key, layer_id=None):
    return geo.finish_frame(img, key, layer_id, PIN)


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def bands(key):
    """(title_band, inventory_band) Rects of the panel that carry live text.

    The title band spans rows 2 .. 14 (rows 5-13 carry the live title glyphs);
    the inventory band fills the rows between the lowest clearance above the
    label and the player grid. In the Faithful look both are simply the light
    panel; they are returned so painters keep motifs out of them and so the
    inset trays draw no dark run inside them."""
    s = geo.skin(key)
    title = geo.Rect(3, 2, s.width - 6, 13)
    inv = s.inventory_label
    above = [m.bottom for m in s.masks if m.bottom <= inv.y + 1]
    below = [m.y for m in s.masks if m.y >= inv.y + 4]
    top = max([inv.y - 1] + above)
    bottom = min([inv.y + 9] + below) - 1      # exclusive
    return title, geo.Rect(3, top, s.width - 6, bottom - top)


def text_rows(key):
    """The rectangles where live vanilla glyphs land (same as validate.py):
    title rows anchor_y-1 .. anchor_y+7 over the text-safe width (none on the
    dispenser) and inventory rows label_y-1 .. label_y+7."""
    s = geo.skin(key)
    out = []
    if not s.is_dispenser:
        out.append(geo.Rect(s.text_safe.x, s.title_anchor[1] - 1, s.text_safe.w, 9))
    iv = s.inventory_label
    out.append(geo.Rect(iv.x, iv.y - 1, iv.w, 9))
    return out


def accent_colour(key):
    """The family accent line colour (accent ramp step 1), or None when the
    skin is plain (templates, crafting)."""
    acc = accent_for(key)
    if not acc.get('line'):
        return None
    ramp = acc['accent']
    return ramp[min(1, len(ramp) - 1)] if len(ramp) > 2 else ramp[0]


def draw_accent_line(img, key, y=ACCENT_Y, colour=None):
    """The 1 px family accent line under the title band, over the text-safe
    columns, drawn only on plain panel pixels (it breaks round an inset tray
    or a button that reaches that row). Returns the pixels drawn."""
    s = geo.skin(key)
    colour = colour or accent_colour(key)
    if colour is None:
        return set()
    panel = tuple(sheet_for(key)[2])
    drawn = set()
    x0, x1 = s.text_safe.x, s.text_safe.right - 1
    for x in range(x0, x1 + 1):
        if P.get(img, x, y)[3] and tuple(P.get(img, x, y)[:3]) == panel:
            P.put(img, x, y, colour)
            drawn.add((x, y))
    return drawn


def static_regions(key):
    """Static decorative cells (staticProtectedSlots) merged into rectangles
    (16 px per cell, inset 1 px from the 18 px slot) that no painted button
    covers. Returns a list of Rects, largest first."""
    s = geo.skin(key)
    cells = sorted({(sl.x, sl.y) for sl in s.all_slots if sl.index in s.static_slots}, key=lambda c: (c[1], c[0]))
    runs = []
    for (x, y) in cells:
        if runs and runs[-1][1] == y and runs[-1][0] + runs[-1][2] + 2 == x:
            rx, ry, rw, rh = runs[-1]
            runs[-1] = (rx, ry, rw + 18, rh)
        else:
            runs.append((x, y, 16, 16))
    merged = []
    for r in runs:                       # stack identical runs on consecutive rows
        for i, m in enumerate(merged):
            if m[0] == r[0] and m[2] == r[2] and m[1] + m[3] + 2 == r[1]:
                merged[i] = (m[0], m[1], m[2], m[3] + 18)
                break
        else:
            merged.append(r)
    out = []
    for (x, y, w, h) in merged:
        rect = geo.Rect(x, y, w, h)
        if any(b.rect.intersect(rect) for b in s.buttons):
            continue
        out.append(rect)
    return sorted(out, key=lambda r: -r.w * r.h)


def pictogram_tile(img, rect, name, ramp=None):
    """A recessed panel-coloured tile on ``rect`` with pictogram ``name``
    centred (or nothing when ``name`` is None)."""
    ramp = ramp or PANEL_RAMP
    return P.pictogram_tile(img, rect.tuple() if hasattr(rect, 'tuple') else rect, name, fill_colour=ramp[2])


def base_background(key, seed=0, wells='inset', title=True, inventory=True, ramp=None, label='auto',
                    accent=True, pictograms=True):
    """Canonical background for ``key``: the light grey panel (``bevel_panel``:
    black outline with notched corners, white top/left bevel, dark grey
    bottom/right bevel), the vanilla-style inset tray round every native
    clearance, the family accent line under the title band (``accent``),
    and one 16x16 recessed tile with the family pictogram centred in the
    largest static decorative region (``pictograms``; other static cells
    stay plain panel). On the dispenser (trade_money) ``label='auto'``
    letters the static OFFERED MONEY label in PLAIN ink_1, centred on x=88.
    ``title`` / ``inventory`` are accepted for API parity: the panel is light
    everywhere, so both bands are always light. Masks are cleared and the
    advance pin stamped."""
    s = geo.skin(key)
    ramp = ramp or sheet_for(key)
    img = new(s.width, s.height)
    P.bevel_panel(img, (0, 0, s.width, s.height), ramp, radius=2)
    acc = accent_for(key)
    regions = static_regions(key)
    if pictograms and acc.get('pictogram') and regions:
        r = regions[0]                                   # one small tile, in the largest region
        pictogram_tile(img, geo.Rect(r.x + (r.w - 16) // 2, r.y + (r.h - 16) // 2, 16, 16), acc['pictogram'], ramp)
    if s.is_dispenser and label == 'auto':
        L.draw_text_centered(img, 88, s.title_anchor[1], DISPENSER_LABEL, LABEL_DARK)
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    if wells:
        P.inset_well(img, holes, protect=text_rows(key))
    if accent:
        draw_accent_line(img, key)
    finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

TILE = 24                    # side-panel pictogram tile size


def side_tile(img, panel, name=None, y=12, size=TILE, ramp=None, text=None):
    """The one thing a Faithful side panel carries: a recessed ``size`` x
    ``size`` tile centred in ``panel`` (a Rect) with its top at ``y``,
    holding pictogram ``name``. ``text`` letters a TINY caption instead (for
    an art director's exception only: frames carry no words). Returns box."""
    ramp = ramp or PANEL_RAMP
    x = panel.x + (panel.w - size) // 2
    box = (x, y, size, size)
    P.inset_box(img, box, ramp[2])
    if text:
        L.draw_text_centered(img, x + size // 2, y + (size - 5) // 2, text, LABEL_DARK, face='tiny')
    elif name:
        w, h = icons.pictogram_size(name)
        icons.draw_pictogram(img, name, x + (size - w) // 2, y + (size - h) // 2)
    return box


def side_banner(img, panel, text=None, y=12, seed=0, chain_from=None, ramp=None, crest=None, h=None):
    """Soulrend-compatible name for ``side_tile``: ``crest`` is the pictogram."""
    return side_tile(img, panel, crest, y, text=text)


def side_tag(img, panel, text, y, seed=0, twine_from=None):
    """Cozy-compatible name for ``side_tile`` with a TINY caption."""
    return side_tile(img, panel, None, y, text=text)


def heading_plaque(img, cx, y, text=None, width=None, name=None):
    """A small recessed plate centred on ``cx`` with its top row at ``y`` (8
    px tall, fits the 8 px top strip). Wordless by default (frames carry no
    words); ``text`` letters it in TINY ink_1. Returns its box."""
    w = (L.text_width(text, 'tiny') + 8) if text else (width or 24)
    x = cx - w // 2
    P.inset_box(img, (x, y, w, 7), PANEL_RAMP[2])
    if text:
        L.draw_text(img, x + 4, y + 1, text, LABEL_DARK, face='tiny')
    return (x, y, w, 7)


heading_ribbon = heading_plaque       # cozy-compatible name


def base_frame(key, layer_id=None, seed=0, heading=False, ramp=None):
    """Canonical outer frame: a side-panel extension in the vanilla bevel
    language. The whole 256-wide layer is one light grey panel
    (``bevel_panel``: black outline, radius-2 notched corners, white
    top/left and dark grey bottom/right bevel) round the transparent
    container; a 1 px dark grey drop shadow runs down the container's right
    side and along its bottom; each 40 px side panel carries one recessed
    tile with the family pictogram near its top (plain skins: no tile). The
    8 px top and bottom strips carry only the bevel. ``heading`` is accepted
    for API parity and ignored unless it is a string (then a TINY plaque).
    The native container is cleared and the advance pin stamped."""
    s = geo.skin(key)
    a = s.layer(layer_id)
    ramp = ramp or sheet_for(key)
    img = new(a.w, a.h)
    P.bevel_panel(img, (0, 0, a.w, a.h), ramp, radius=2)
    c = a.container
    P.vline(img, c.right, c.y + 2, c.bottom, ramp[1])
    P.hline(img, c.x + 2, c.right, c.bottom, ramp[1])
    # side panels: a recessed groove (dark then white) sets each 40 px panel
    # apart from the rim, like a separate panel docked to the container
    for gx in (c.x - 6, c.right + 4):
        P.vline(img, gx, 4, a.h - 5, ramp[1])
        P.vline(img, gx + 1, 4, a.h - 5, ramp[3])
    name = accent_for(key).get('pictogram')
    if name:
        for panel in (geo.Rect(0, 0, c.x - 6, a.h), geo.Rect(c.right + 6, 0, a.w - c.right - 6, a.h)):
            side_tile(img, panel, name, y=c.y + 4, ramp=ramp)
    if isinstance(heading, str) and c.y >= 8:
        heading_plaque(img, a.w // 2, 0, heading)
    finish_frame(img, key, a.id)
    return img


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def button_kind(button):
    """close | icon | info | page_prev | page_next | primary | secondary | danger."""
    if button.icon == 'close':
        return 'close'
    if button.icon or (button.w == 18 and button.h == 18):
        return 'icon'
    if button.role == 'info':
        return 'info'
    if button.id in ('previous', 'prev'):
        return 'page_prev'
    if button.id == 'next':
        return 'page_next'
    return button.style


def _label_options(button, tiny=True):
    """(lines, face, gap) candidates in preference order: PLAIN capitals,
    PLAIN mixed case (label only), TINY capitals. Never invents words."""
    options = [(list(button.text_lines), 'plain', 2)]
    if not button.lines:
        options.append(([button.label], 'plain', 2))
    if tiny:
        options.append(([t.upper() for t in button.text_lines], 'tiny', 1))
    return options


def _label_height(lines, face, gap):
    """Full glyph extent of a label block: every line's cap height plus the
    gaps, plus the descender rows when the LAST line uses them (g j p q y)."""
    f = L.FACES[face]
    return (len(lines) - 1) * (f.cap_height + gap) + L.text_height(lines[-1], face)


def _label_plan(button, box, tiny=True):
    """Choose (lines, face, gap) that fit ``box``. Descenders count."""
    _, _, w, h = box
    for lines, face, gap in _label_options(button, tiny):
        tall = _label_height(lines, face, gap)
        if all(L.text_width(t, face) <= w for t in lines) and tall <= h:
            return lines, face, gap
    raise ValueError(f'label {button.text_lines} does not fit {box} for {button.id}')


def _layout_offsets(lines, face, gap):
    f = L.FACES[face]
    return [(-(L.text_width(t, face) // 2), i * (f.cap_height + gap)) for i, t in enumerate(lines)]


def label_layout(button, box):
    """[(x, y, text, face)] for each line ``letter`` draws in ``box``,
    centred on the full glyph extent (descenders included)."""
    lines, face, gap = _label_plan(button, box)
    x, y, w, h = box
    total = _label_height(lines, face, gap)
    top = y + (h - total + 1) // 2
    cx = x + (w + 1) // 2
    return [(cx + dx, top + dy, t, face) for (dx, dy), t in zip(_layout_offsets(lines, face, gap), lines)]


def label_pixels(layout):
    """Glyph pixel set of a ``label_layout`` (no shadow, no halo)."""
    out = set()
    for lx, ly, t, face in layout:
        out.update((lx + px, ly + py) for px, py in L._pixels(t, face))
    return out


_LETTERED = {}      # id(img) -> (weakref, {(skin_key, button_id): glyph pixel set})
_EXTRAS = {}        # id(img) -> (weakref, {(skin_key, button_id): arrow / X pixel set})


def _remember(registry, img, button, pixels):
    for k in [k for k, (ref, _) in registry.items() if ref() is None]:
        del registry[k]
    entry = registry.get(id(img))
    if entry is None or entry[0]() is not img:
        entry = (_weakref.ref(img), {})
        registry[id(img)] = entry
    entry[1].setdefault((button.skin_key, button.id), set()).update(pixels)


def _recall(registry, img, button):
    entry = registry.get(id(img))
    if entry is None or entry[0]() is not img:
        return None
    return entry[1].get((button.skin_key, button.id))


def lettered_pixels(img, button):
    """The glyph pixels ``letter`` drew for ``button`` on this exact image
    object, or None (another image, a copy, or hand lettering)."""
    return _recall(_LETTERED, img, button)


def letter(img, button, box, colour, shadow=None):
    """Letter the button's own label centred in ``box``. Returns (lines, face).
    The glyph pixels are remembered for ``lettering_mask``."""
    layout = label_layout(button, box)
    pix = label_pixels(layout)
    if pix:
        P.restore_cuts(img, min(x for x, _ in pix) - 1, max(x for x, _ in pix) + 1,
                       box[1] - 3, box[1] + box[3] + 2)
    for lx, ly, t, face in layout:
        L.draw_text(img, lx, ly, t, colour, shadow, face=face)
    _remember(_LETTERED, img, button, pix)
    return [t for _, _, t, _ in layout], layout[0][3]


def remember_extras(img, button, pixels):
    """Register glyph-like non-letter pixels (a page arrow, the close X) so
    ``button_states`` protects them like lettering and disabled dims them."""
    _remember(_EXTRAS, img, button, pixels)


def primary_face(img, body, seed=0):
    """Grey stone button with a gold top/left bevel (and a broken second gold
    row on plates at least 26 px wide). Returns the text box (white
    lettering with an ink_1 shadow; the box leaves the shadow its column)."""
    x, y, w, h = body
    P.stone_button(img, body, 'gold', seed)
    top = 3 if (w >= 26 and h >= 12) else 2
    return (x + 2, y + top, w - 5, h - top - 3)


def secondary_face(img, body, seed=0, rivets=None):
    """Plain grey stone button. Returns the text box. (``rivets`` is
    accepted for API parity and ignored.)"""
    x, y, w, h = body
    P.stone_button(img, body, 'plain', seed)
    return (x + 2, y + 2, w - 5, h - 5)


def danger_face(img, body, seed=0):
    """Stone button with a muted red face and red bevel. Returns the text box."""
    x, y, w, h = body
    P.stone_button(img, body, 'red', seed)
    return (x + 2, y + 2, w - 5, h - 5)


def info_face(img, body, seed=0):
    """Flat recessed grey plate (no outline, no raised bevel): clearly
    read-only. Returns the text box (dark ink_1 lettering, no shadow)."""
    x, y, w, h = body
    P.flat_plate(img, body)
    return (x + 1, y + 1, w - 2, h - 2)


def page_face(img, body, direction, seed=0):
    """Plain stone button with a small arrow glyph on the side the page turns
    (next: right, previous: left). Returns (text box, arrow pixel set)."""
    x, y, w, h = body
    P.stone_button(img, body, 'plain', seed)
    aw, ah = P.arrow_size('right')
    ay = y + 2 + (h - 11) // 2          # same top row as a centred PLAIN label
    if direction == 'next':
        ax = x + w - 3 - aw - 1
        arrow = P.arrow_glyph(img, ax, ay, 'right', LABEL_LIGHT, LABEL_SHADOW)
        box = (x + 2, y + 2, ax - 2 - (x + 2), h - 5)
    else:
        ax = x + 3
        arrow = P.arrow_glyph(img, ax, ay, 'left', LABEL_LIGHT, LABEL_SHADOW)
        bx = ax + aw + 2
        box = (bx, y + 2, x + w - 3 - bx, h - 5)
    return box, arrow


def icon_face(img, button, body, seed=0):
    """Backing + icon for 18x18 icon controls and the 18x72 balance column:
    read-only (info) icons sit on a recessed plate, action icons on a plain
    stone button. Returns the icon pixel set (protected like lettering by
    ``button_states``: selected and the pulses never change it, disabled
    turns it into a grey_5 silhouette inside its black outline)."""
    x, y, w, h = body
    if button.role == 'info':
        inner = P.flat_plate(img, body)
    else:
        inner = P.stone_button(img, body, 'plain', seed, texture=False)
    placed = []
    if h > 36 and button.icon == 'balance':
        placed.append(('balance', (x, y + 3, w, 13)))
        placed += [('coin', (x, y + 22 + k * 7, w, 5)) for k in range(4)]
    else:
        placed.append((button.icon or 'rank', inner))
    pixels = set()
    for name, box in placed:
        icons.draw_icon(img, name, box)
        pixels |= icons.icon_pixels(name, box)
    return pixels


def paint_button(key, button_id, seed=0):
    """Normal state for one button region in the shared grammar. The result is
    finished (masks cleared, pin stamped) and ready for ``button_states``."""
    s = geo.skin(key)
    b = s.button(button_id)
    img = new(b.w, b.h)
    body = b.body.tuple()
    kind = button_kind(b)
    if kind == 'close':
        face = P.stone_button(img, body, 'red', seed, texture=False)
        remember_extras(img, b, icons.draw_x(img, face, LABEL_LIGHT, LABEL_SHADOW))
    elif kind == 'icon':
        remember_extras(img, b, icon_face(img, b, body, seed))
    elif kind == 'primary':
        letter(img, b, primary_face(img, body, seed), LABEL_LIGHT, shadow=LABEL_SHADOW)
    elif kind == 'secondary':
        letter(img, b, secondary_face(img, body, seed), LABEL_LIGHT, shadow=LABEL_SHADOW)
    elif kind == 'danger':
        letter(img, b, danger_face(img, body, seed), LABEL_LIGHT, shadow=LABEL_SHADOW)
    elif kind == 'info':
        letter(img, b, info_face(img, body, seed), LABEL_DARK)
    elif kind in ('page_prev', 'page_next'):
        box, arrow = page_face(img, body, 'next' if kind == 'page_next' else 'prev', seed)
        remember_extras(img, b, arrow)
        letter(img, b, box, LABEL_LIGHT, shadow=LABEL_SHADOW)
    finish_button(img, key, button_id)
    return img


# ---------------------------------------------------------------------------
# Lettering detection (from the label geometry, never by guessing shapes first)
# ---------------------------------------------------------------------------

def _label_strings(button):
    out = []
    for t in list(button.text_lines) + [button.label, button.label.upper()]:
        for v in (t, t.upper(), t.title()):
            if v and v not in out:
                out.append(v)
            for word in v.split():
                if word not in out:
                    out.append(word)
    return out


def _templates(strings):
    seen = set()
    out = []
    chars = sorted({ch for t in strings for ch in t if not ch.isspace()})
    for face in ('plain', 'tiny'):
        for t in list(strings) + chars:
            pts = tuple(sorted(L._pixels(t, face)))
            if len(pts) < 4 or (face, pts) in seen:
                continue
            seen.add((face, pts))
            w = max(x for x, _ in pts) + 1
            h = max(y for _, y in pts) + 1
            out.append((pts, w, h, len(t) == 1))
    return out


RIM_RINGS = 2        # outline + first inner ring: never lettering, never protected


def _match(img, rel, min_share=0.9):
    """Best placement of the relative pixel set ``rel`` where >= ``min_share``
    of its pixels share one opaque colour and at most half of the other
    pixels of its bounding box do. Returns the image pixel set or empty."""
    W, H = img.size
    px = img.load()
    x0 = min(x for x, _ in rel); y0 = min(y for _, y in rel)
    rel = [(x - x0, y - y0) for x, y in rel]
    tw = max(x for x, _ in rel) + 1; th = max(y for _, y in rel) + 1
    if tw > W or th > H:
        return set(), 0.0
    glyph = set(rel)
    others = [(x, y) for y in range(th) for x in range(tw) if (x, y) not in glyph]
    n = len(rel)
    allowed = n - int(n * min_share)
    best, best_score = set(), 0.0
    for oy in range(0, H - th + 1):
        for ox in range(0, W - tw + 1):
            counts = {}
            miss = 0
            for (x, y) in rel:
                c = px[ox + x, oy + y]
                if c[3] == 0:
                    miss += 1
                else:
                    counts[c] = counts.get(c, 0) + 1
                if miss > allowed:
                    break
            if miss > allowed or not counts:
                continue
            c, hits = max(counts.items(), key=lambda kv: kv[1])
            if hits < n - allowed:
                continue
            same = sum(1 for (x, y) in others if px[ox + x, oy + y] == c)
            if same > len(others) // 2:
                continue
            score = hits / n
            if score > best_score:
                best_score = score
                best = {(ox + x, oy + y) for (x, y) in rel}
    return best, best_score


def _search_label(img, button):
    """Whole-label template search (every (lines, face, gap) option of the
    button's own label, at every offset). Returns the best hit's pixels."""
    best, best_score = set(), 0.0
    for lines, face, gap in _label_options(button):
        rel = []
        for (dx, dy), t in zip(_layout_offsets(lines, face, gap), lines):
            rel += [(dx + gx, dy + gy) for gx, gy in L._pixels(t, face)]
        if len(rel) < 6:
            continue
        hit, score = _match(img, rel)
        if score > best_score:
            best, best_score = hit, score
    return best


def _shape_search(img, button):
    """Last resort for hand lettering: words and characters of the label
    matched by shape and one colour."""
    W, H = img.size
    px = img.load()
    found = set()
    templates = _templates(_label_strings(button))
    rows, inks = set(), set()
    for want_single in (False, True):
        for pts, w, h, single in templates:
            if single != want_single:
                continue
            glyph = set(pts)
            others = [(x, y) for y in range(h) for x in range(w) if (x, y) not in glyph]
            first = pts[0]
            for oy in range(0, H - h + 1):
                if single and (not rows or not any(oy + k in rows for k in range(h))):
                    continue
                for ox in range(0, W - w + 1):
                    c = px[ox + first[0], oy + first[1]]
                    if c[3] == 0 or (single and c not in inks):
                        continue
                    if any(px[ox + x, oy + y] != c for x, y in pts):
                        continue
                    same = sum(1 for x, y in others if px[ox + x, oy + y] == c)
                    if (same == 0) if single else (same <= len(others) // 4):
                        found.update((ox + x, oy + y) for x, y in pts)
        if not want_single:
            rows = {y for (_, y) in found}
            inks = {px[x, y] for (x, y) in found}
    return found


def _grow(pixels, size):
    W, H = size
    grown = set(pixels)
    for (x, y) in pixels:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if 0 <= x + dx < W and 0 <= y + dy < H:
                    grown.add((x + dx, y + dy))
    return grown


def lettering_mask(img, button, halo=True):
    """The set of the button's own lettering pixels in a painted image (plus,
    with ``halo``, a 1 px 8-neighbour halo that holds the text shadow).

    Sources, in order: (1) the exact glyph pixels ``letter`` drew on this
    image object; (2) a whole-label template search (the label's own lines,
    face and spacing, >= 90 % of its pixels in one colour), which finds
    lettering on copies and in hand-chosen boxes; (3) for genuinely
    hand-lettered labels, the word / character shape search, whose hits on
    the outline and first inner ring are discarded. Transparent pixels are
    never part of the mask. Icons and unlettered faces return an empty set."""
    if button.icon or button_kind(button) in ('close', 'icon'):
        return set()
    W, H = img.size
    a = img.getchannel('A').load()
    found = lettered_pixels(img, button)
    found = {p for p in (found or ()) if 0 <= p[0] < W and 0 <= p[1] < H and a[p[0], p[1]]}
    if not found:
        found = _search_label(img, button)
    if not found:
        found = _shape_search(img, button)
        if found:
            dist = P.edge_distance(img, RIM_RINGS)
            found = {(x, y) for (x, y) in found if dist[y][x] is not None and dist[y][x] >= RIM_RINGS}
    if halo and found:
        found = _grow(found, img.size)
    return {(x, y) for (x, y) in found if a[x, y]}


def extras_mask(img, button):
    """Glyph-like pixels that are not letters: the page arrow on prev/next,
    the close X and the icons of icon controls. From the registry when this
    image was painted by ``paint_button``, else by a template search (white
    arrow or X; exact sprite match for icons)."""
    W, H = img.size
    a = img.getchannel('A').load()
    found = _recall(_EXTRAS, img, button)
    found = {p for p in (found or ()) if 0 <= p[0] < W and 0 <= p[1] < H and a[p[0], p[1]]}
    if found:
        return found
    kind = button_kind(button)
    if kind == 'icon':
        return _find_icons(img, button)
    if kind == 'close':
        shapes = [sorted(icons.x_cross(8))]
    elif kind in ('page_prev', 'page_next'):
        shapes = [sorted((i, j) for j, r in enumerate(P.ARROWS[d]) for i, c in enumerate(r) if c == '#')
                  for d in (('right', 'left') if kind == 'page_next' else ('left', 'right'))]
    else:
        return set()
    for rel in shapes:
        hit, score = _match(img, rel, min_share=1.0)
        if hit and all(tuple(img.getpixel(p)[:3]) == GREY[7] for p in hit):
            return hit
    return set()


def _find_icons(img, button):
    """Exact sprite search for the button's icon(s) on a copy: every opaque
    cell of the sprite must match its colour. Returns the union of hits."""
    names = ['balance', 'coin'] if button.icon == 'balance' else [button.icon or 'rank']
    W, H = img.size
    px = img.load()
    found = set()
    for name in names:
        cells = [(i, j, P.SK[c]) for j, r in enumerate(icons.ICONS[name]) for i, c in enumerate(r) if c not in '. ']
        sw, sh = P.sprite_size(icons.ICONS[name])
        for oy in range(0, H - sh + 1):
            for ox in range(0, W - sw + 1):
                if all(px[ox + i, oy + j][3] and tuple(px[ox + i, oy + j][:3]) == c for i, j, c in cells):
                    found |= {(ox + i, oy + j) for i, j, _ in cells}
    return found


def lettering_footprint(img, glyphs):
    """``glyphs`` plus the shadow pixels actually drawn under them (the
    (+1, +1) neighbour that holds ink_1 and is not itself a glyph)."""
    W, H = img.size
    px = img.load()
    out = set(glyphs)
    for (x, y) in glyphs:
        q = (x + 1, y + 1)
        if q not in glyphs and q[0] < W and q[1] < H and px[q][3] and tuple(px[q][:3]) == INK[1]:
            out.add(q)
    return out


def state_masks(normal, button):
    """(glyphs, extras, footprint, protect) for a painted normal frame:
    lettering glyph pixels, arrow / X pixels, glyph-like pixels plus their
    drawn shadow (selected never changes these), and that footprint plus a
    1 px halo round every glyph (the pulses never change these)."""
    glyphs = lettering_mask(normal, button, halo=False)
    extras = extras_mask(normal, button)
    core = glyphs | extras
    footprint = lettering_footprint(normal, core)
    a = normal.getchannel('A').load()
    protect = {p for p in _grow(core, normal.size) | footprint if a[p[0], p[1]]} if core else set()
    return glyphs, extras, footprint, protect


def button_states(normal, key, button_id, overrides=None):
    """Six finished state images from one painted normal frame using the
    shared transforms; ``overrides`` maps state -> hand-adjusted image.

    Lettering and glyph-like extras (page arrow, close X) keep their shape and
    alpha in every state: selected keeps every glyph and shadow pixel, the
    pulses also keep a 1 px halo round each glyph, and disabled recolours
    the glyphs in place to the disabled grey (grey_5) on a flat dark face."""
    b = geo.skin(key).button(button_id)
    glyphs, extras, footprint, protect = state_masks(normal, b)
    out = {}
    for st in geo.STATES:
        img = (overrides or {}).get(st) or P.make_state(normal, st, protect=protect, glyphs=glyphs,
                                                        footprint=footprint, extras=extras)
        out[st] = finish_button(img, key, button_id)
    return out


def save_button_states(states, key, button_id, root=None):
    """Write the six PNGs (to pack-source by default, or under ``root``
    laid out as textures/buttons/<key>/<id>/<state>.png)."""
    s = geo.skin(key)
    paths = []
    for st, img in states.items():
        p = s.button_path(button_id, st) if root is None else \
            _Path(root) / 'buttons' / key / button_id / f'{st}.png'
        paths.append(save_png(img, p))
    return paths
