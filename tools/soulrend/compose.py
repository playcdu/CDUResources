"""Standard Soulrend compositions: the shared starting point every painter builds on.

These functions turn geometry + primitives into the canonical base look, so
the twelve painters share one grammar and only add family identity on top.
Signatures mirror tools/cozy/compose.py, so the painter workflow is identical:

    base_background(key, seed)        umber sheet in an iron rim, bone-white
                                      vellum title + inventory bands, iron-framed
                                      stone sockets round every clearance
    base_frame(key, layer_id, seed)   mossy dungeon masonry round the container,
                                      iron border with rivets, cast shadow, gold
                                      corner filigree, a wordless heraldic plaque
    paint_button(key, button_id, seed)  normal state in the right grammar
                                      (primary iron plate / secondary vellum strip /
                                      danger blood cloth / info stone tablet /
                                      page-turn torn vellum / icon / close seal)
    button_states(normal, key, button_id)  all six states via the shared transforms
    save_png / save_button_states / output paths

Everything returned is already finished (masks cleared, pins stamped) and can
be re-finished safely after further painting with geometry.finish_*.

Licence: MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

if __name__ == 'compose':
    _sys.modules.setdefault('soulrend.compose', _sys.modules[__name__])
_TOOLS = _Path(__file__).resolve().parents[1]
for _p in (str(_TOOLS), str(_TOOLS / 'cozy')):
    if _p not in _sys.path:
        _sys.path.append(_p)

from PIL import Image  # noqa: E402

import geometry as geo  # noqa: E402  (theme-agnostic, tools/cozy/geometry.py)
from soulrend import icons  # noqa: E402
from soulrend import lettering as L  # noqa: E402
from soulrend import primitives as P  # noqa: E402
from soulrend.palette import (BLOOD, GOLD, INK, IRON, STONE, UMBER, VELLUM, VOID_SHEET,  # noqa: E402
                              rgba)

PIN = rgba('ink_0')          # pin colour passed explicitly: geometry's own default is not ours
FRAME_STONE = STONE          # masonry ramp of outer frames
DISPENSER_LABEL = 'OFFERED MONEY'


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
    """Sheet ramp for a skin: obsidian for the ender chest, umber otherwise."""
    return VOID_SHEET if key == 'ender_chest' else UMBER


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
    """(title_band, inventory_band) Rects that hold vellum for live text.

    The title band spans rows 2 .. 14 (rows 5-13 carry the live title glyphs);
    the inventory band fills the rows between the lowest clearance above the
    label and the player grid. Its first row may be the socket lip row of the
    grid above: the lip is drawn over the vellum only where the grid is, so
    the glyph row inv.y - 1 stays light everywhere else."""
    s = geo.skin(key)
    title = geo.Rect(3, 2, s.width - 6, 13)
    inv = s.inventory_label
    above = [m.bottom for m in s.masks if m.bottom <= inv.y + 1]
    below = [m.y for m in s.masks if m.y >= inv.y + 4]
    top = max([inv.y - 1] + above)
    bottom = min([inv.y + 9] + below) - 1      # exclusive
    return title, geo.Rect(3, top, s.width - 6, bottom - top)


CLASP = ['oooo', 'odco', 'ocbo', 'obbo', 'obao', 'oHgo', 'ohgo', 'obao', 'obao', 'ocbo', 'obao', 'oaao', 'oooo']
CORNER_BRACKET = ['ooooo.', 'oddcbo', 'ocoooo', 'oco...', 'obo...', 'ooo...']


def band_clasps(img, band):
    """Iron clasps with a gold rivet holding both ends of a vellum band
    (4 px wide, outside the live-text columns 8 .. 167)."""
    rows = CLASP[:band.h] if band.h < len(CLASP) else CLASP + ['obao'] * (band.h - len(CLASP))
    if band.h < len(CLASP):
        rows = rows[:-1] + ['oooo']
    P.sprite(img, band.x, band.y, rows)
    P.sprite(img, band.right - 4, band.y, rows)


def corner_bracket(img, x, y, corner):
    """6x6 blackened-iron L bracket for a sheet or frame corner."""
    P.sprite(img, x, y, CORNER_BRACKET, flip_x='r' in corner, flip_y='b' in corner)


def base_background(key, seed=0, wells='socket', title=True, inventory=True, ramp=None, label='auto'):
    """Canonical background for ``key``: a flat dark umber sheet (scuffed, not
    noisy) inside an ink_0 rim and a 1 px blackened-iron band; bone-white
    vellum title band held by iron clasps; vellum inventory band; recessed
    iron-framed stone sockets round every native clearance; iron corner
    brackets. On the dispenser (trade_money) ``label='auto'`` letters the
    static OFFERED MONEY label in GRAVEN ink_0, centred on x=88. Masks are
    cleared and the advance pin stamped."""
    s = geo.skin(key)
    ramp = ramp or sheet_for(key)
    img = new(s.width, s.height)
    P.umber_panel(img, (1, 1, s.width - 2, s.height - 2), seed, ramp)
    P.ink_outline(img, (0, 0, s.width, s.height), 'ink_0', radius=2)
    # 1 px blackened-iron band just inside the rim: cold light top-left
    P.bevel(img, (1, 1, s.width - 2, s.height - 2), IRON[2], INK[1])
    P.highlight_edge(img, (1, 1, s.width - 2, s.height - 2), IRON[3], 'tl', broken=7, seed=seed)
    for corner, (x, y) in (('bl', (1, s.height - 7)), ('br', (s.width - 7, s.height - 7))):
        corner_bracket(img, x, y, corner)
    tband, iband = bands(key)
    protect = []
    if title:
        P.vellum_strip(img, tband.tuple(), seed, outline='ink_1', deckle='t', heavy='b')
        band_clasps(img, tband)
        protect.append(tband.tuple())
        if s.is_dispenser and label == 'auto':
            L.draw_text_centered(img, 88, tband.y + 3, DISPENSER_LABEL, 'ink_0')
    if inventory:
        # no ink rim top/bottom: the socket lips above and below frame it
        P.vellum_strip(img, iband.tuple(), seed + 1, outline='ink_1', deckle='', fibres=False)
        P.hline(img, iband.x + 1, iband.right - 2, iband.y, VELLUM[3])
        P.hline(img, iband.x + 1, iband.right - 2, iband.bottom - 1, VELLUM[1])
        band_clasps(img, iband)
        protect.append(iband.tuple())
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    if wells == 'socket':
        P.socket_well(img, holes, protect=protect)
    elif wells == 'carved':
        P.carved_well(img, holes, protect=protect)
    for r in s.extra_transparent:
        P.carved_well(img, [r.tuple()], protect=protect, depth=2)
    finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

def heading_plaque(img, cx, y, text=None, width=None):
    """A blackened-iron plaque 8 px tall with a gold rim and gold scroll ends,
    centred on ``cx`` with its top row at ``y``. With ``text`` it is lettered
    in RUNE gold_2 (rows 2-6); without text (the Soulrend default: frames
    carry no words) it shows a small gold fleur flourish. Returns its box."""
    if text:
        tw = L.text_width(text, 'rune')
        w = tw + 8
    else:
        w = width or 30
    x = cx - w // 2
    P.ink_outline(img, (x, y, w, 8), 'ink_0', radius=1, fill_colour=IRON[0])
    P.hline(img, x + 1, x + w - 2, y + 1, GOLD[2])
    P.vline(img, x + 1, y + 2, y + 6, GOLD[1])
    P.vline(img, x + w - 2, y + 2, y + 6, GOLD[0])
    P.hline(img, x + 2, x + w - 3, y + 6, IRON[1])
    if text:
        L.draw_text(img, x + 4, y + 2, text, 'gold_2', face='rune')
    else:
        P.sprite(img, cx - 5, y + 2, ['.hh.....hh.', 'h..hHHHh..h', '.g.......g.'])
        P.put(img, cx, y + 5, GOLD[2])
    P.gold_filigree(img, x - 5, y, 'scroll', 'tl')
    P.gold_filigree(img, x + w, y, 'scroll', 'tr')
    return (x - 5, y, w + 10, 8)


heading_ribbon = heading_plaque       # cozy-compatible name


def base_frame(key, layer_id=None, seed=0, heading=False, ramp=None):
    """Canonical outer frame: mossy slate ashlar (7 px courses) round the
    container, an ink_0 rim with a 2 px blackened-iron border riveted every
    16 px, gold filigree in the four corners, a 2 px cast shadow right of and
    below the container, and a heraldic plaque centred in the top strip.

    The plaque is wordless by default: Soulrend frames carry no painted words
    (``heading=True`` letters the artLayers heading in RUNE for a painter who
    has been told otherwise). The native container is cleared and the advance
    pin stamped."""
    s = geo.skin(key)
    a = s.layer(layer_id)
    ramp = ramp or FRAME_STONE
    img = new(a.w, a.h)
    P.stone_blocks(img, (1, 1, a.w - 2, a.h - 2), seed, ramp, course=7, moss=0.10)
    c = a.container
    P.ink_outline(img, (0, 0, a.w, a.h), 'ink_0', radius=3)
    # 2 px iron border
    P.bevel(img, (1, 1, a.w - 2, a.h - 2), IRON[2], IRON[0])
    P.bevel(img, (2, 2, a.w - 4, a.h - 4), IRON[1], INK[1])
    for x in range(10, a.w - 10, 16):
        P.put(img, x, 1, IRON[3]); P.put(img, x, a.h - 2, IRON[3])
    for y in range(12, a.h - 10, 16):
        P.put(img, 1, y, IRON[3]); P.put(img, a.w - 2, y, IRON[3])
    # iron lintel and sill: the container sits in a carved recess
    P.hline(img, c.x - 1, c.right, c.y - 1, INK[1])
    P.vline(img, c.x - 1, c.y - 1, c.bottom, INK[1])
    # cast shadow of the sheet onto the wall
    for k in (0, 1):
        P.vline(img, c.right + k, c.y + 2 + k, c.bottom - 1 + k, INK[0] if k == 0 else ramp[0])
        P.hline(img, c.x + 2 + k, c.right + k, c.bottom + k, INK[0] if k == 0 else ramp[0])
    for corner, (x, y) in (('tl', (3, 3)), ('tr', (a.w - 10, 3)), ('bl', (3, a.h - 10)), ('br', (a.w - 10, a.h - 10))):
        P.gold_filigree(img, x, y, 'corner', corner)
    if c.y >= 8:
        heading_plaque(img, a.w // 2, 0, a.heading if heading and a.heading else None)
    finish_frame(img, key, a.id)
    return img


def side_banner(img, panel, text=None, y=12, seed=0, chain_from=None, ramp=BLOOD, crest='chevron', h=None):
    """Hang a small tattered heraldic banner centred in a side ``panel`` Rect,
    rod at ``y``, optionally on a chain from point ``chain_from``. With
    ``text`` it is lettered in RUNE vellum_3 (cozy ``side_tag`` behaviour);
    the Soulrend default is a wordless banner bearing ``crest``. Returns box."""
    if text:
        tw = L.text_width(text, 'rune')
        w = max(tw + 6, 12)
        h = h or 16
    else:
        w = 13
        h = h or 24
    x = panel.x + (panel.w - w) // 2
    if chain_from:
        P.chain(img, chain_from[0], chain_from[1], x + w // 2, y - 1, sag=0, seed=seed)
    P.banner(img, x, y, w, h, ramp, seed, emblem=None if text else crest)
    if text:
        L.draw_text(img, x + 3, y + 4, text, 'vellum_3', face='rune')
    return (x, y, w, h)


def side_tag(img, panel, text, y, seed=0, twine_from=None):
    """Cozy-compatible alias of ``side_banner`` with lettering."""
    return side_banner(img, panel, text, y, seed, chain_from=twine_from)


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


def _label_plan(button, box, rune=True):
    """Choose (lines, face, gap) that fit ``box``: GRAVEN capitals, then GRAVEN
    mixed case (label only), then RUNE capitals (unless ``rune`` is False).
    Never invents words."""
    _, _, w, h = box
    options = [(button.text_lines, 'graven')]
    if not button.lines:
        options.append(([button.label], 'graven'))
    if rune:
        options.append(([t.upper() for t in button.text_lines], 'rune'))
    for lines, face in options:
        f = L.FACES[face]
        gap = 2 if face == 'graven' else 1
        tall = len(lines) * f.cap_height + (len(lines) - 1) * gap
        if all(L.text_width(t, face) <= w for t in lines) and tall <= h:
            return lines, face, gap
    raise ValueError(f'label {button.text_lines} does not fit {box} for {button.id}')


def letter(img, button, box, colour, shadow=None):
    """Letter the button's own label centred in ``box``. Returns (lines, face)."""
    lines, face, gap = _label_plan(button, box)
    f = L.FACES[face]
    x, y, w, h = box
    total = len(lines) * f.cap_height + (len(lines) - 1) * gap
    top = y + (h - total + 1) // 2
    for i, t in enumerate(lines):
        L.draw_text_centered(img, x + (w + 1) // 2, top + i * (f.cap_height + gap), t, colour, shadow, face=face)
    return lines, face


def primary_face(img, body, seed=0):
    """Blackened iron plate with a tarnished-gold rim, raised inner bevel, a
    cold glint and gold rivets on plates of at least 26x12. Returns the text
    box (gold lettering goes here)."""
    x, y, w, h = body
    P.iron_plate(img, body, rim='gold', rivets=(w >= 26 and h >= 12), seed=seed)
    return (x + 4, y + 3, w - 8, h - 6)


def secondary_face(img, body, seed=0, rivets='auto'):
    """Bone-white vellum strip with hand-cut top and bottom edges, pinned at
    each end by an iron rivet (dropped when the label needs the room or the
    strip is narrower than 30 px). Returns the text box."""
    x, y, w, h = body
    if rivets == 'auto':
        rivets = w >= 30
    P.vellum_strip(img, body, seed, outline='ink_1', deckle='tb', heavy='br')
    if rivets:
        cy = y + (h - 3) // 2
        P.rivet(img, x + 2, cy, 'iron', size=3)
        P.rivet(img, x + w - 5, cy, 'iron', size=3)
        return (x + 6, y + 2, w - 12, h - 4)
    return (x + 2, y + 2, w - 4, h - 4)


def danger_face(img, body, seed=0):
    """Blood-red cloth stretched on the frame, vertical folds, iron studs in
    the corners. Returns the text box (vellum_3 lettering, blood_0 shadow)."""
    x, y, w, h = body
    P.cloth_panel(img, body, BLOOD, seed, studs=(w >= 24 and h >= 10))
    return (x + 4, y + 3, w - 8, h - 6)


def info_face(img, body, seed=0):
    """Carved stone tablet: flat stone_3 face with an INWARD chiselled bevel,
    no rim highlight, no rivets: clearly read-only. Returns the text box."""
    x, y, w, h = body
    P.stone_tablet(img, body, seed)
    return (x + 2, y + 2, w - 4, h - 4)


def page_face(img, body, direction, seed=0):
    """Torn vellum page: a strip whose top edge is torn and whose corner
    curls the way the page turns (next: bottom-right; previous: bottom-left).
    Returns the text box on the side away from the curl."""
    x, y, w, h = body
    P.vellum_strip(img, body, seed, outline='ink_1', deckle='b', heavy='br')
    P.torn_edge(img, (x, y, w, 3), 't', seed, depth=1)
    size = 6 if h >= 16 else 5
    P.page_curl(img, body, 'br' if direction == 'next' else 'bl', size)
    pad = 3
    if direction == 'next':
        return (x + pad, y + 2, w - pad - size - 1, h - 4)
    return (x + size + 1, y + 2, w - pad - size - 1, h - 4)


def icon_face(img, button, body, seed=0):
    """Backing + icon for 18x18 icon controls and the 18x72 balance column:
    read-only (info) icons sit on a carved stone tablet, action icons on a
    riveted vellum square."""
    x, y, w, h = body
    if button.role == 'info':
        P.stone_tablet(img, body, seed)
    else:
        P.vellum_strip(img, body, seed, outline='ink_1', deckle='', heavy='br')
    if h > 36 and button.icon == 'balance':
        P.chain(img, x + w // 2, y + 2, x + w // 2, y + 6, seed=seed, shadow=None)
        icons.draw_icon(img, 'balance', (x, y + 7, w, 16))
        for k in range(3):
            icons.draw_icon(img, 'coin', (x, y + 30 + k * 7, w, 5))
        P.rivet(img, x + w // 2 - 1, y + h - 6, 'iron', size=3)
    else:
        icons.draw_icon(img, button.icon or 'rank', body)


def paint_button(key, button_id, seed=0):
    """Normal state for one button region in the shared grammar. The result is
    finished (masks cleared, pin stamped) and ready for ``button_states``."""
    s = geo.skin(key)
    b = s.button(button_id)
    img = new(b.w, b.h)
    body = b.body.tuple()
    kind = button_kind(b)
    if kind == 'close':
        icons.close_seal(img, body, seed)
    elif kind == 'icon':
        icon_face(img, b, body, seed)
    elif kind == 'primary':
        letter(img, b, primary_face(img, body, seed), 'gold_2', shadow='ink_0')
    elif kind == 'secondary':
        # GRAVEN with rivets, else GRAVEN without them, else RUNE with rivets
        rivets = 'auto'
        try:
            _label_plan(b, secondary_face(new(b.w, b.h), body, seed), rune=False)
        except ValueError:
            try:
                _label_plan(b, secondary_face(new(b.w, b.h), body, seed, rivets=False), rune=False)
                rivets = False     # the label needs the rivets' room
            except ValueError:
                try:
                    _label_plan(b, secondary_face(new(b.w, b.h), body, seed))
                except ValueError:
                    rivets = False
        letter(img, b, secondary_face(img, body, seed, rivets), 'ink_0')
    elif kind == 'danger':
        letter(img, b, danger_face(img, body, seed), 'vellum_3', shadow='blood_0')
    elif kind == 'info':
        letter(img, b, info_face(img, body, seed), 'ink_0')
    elif kind in ('page_prev', 'page_next'):
        letter(img, b, page_face(img, body, 'next' if kind == 'page_next' else 'prev', seed), 'ink_0')
    finish_button(img, key, button_id)
    return img


def _label_strings(button):
    """Every spelling a painter may legitimately letter: lines, label, their
    upper/mixed case, and the individual words of each."""
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
    """(pixel tuple, bbox w, bbox h, single-char) for each string in each face,
    plus the single characters those strings use."""
    seen = set()
    out = []
    chars = sorted({ch for t in strings for ch in t if not ch.isspace()})
    for face in ('graven', 'rune'):
        for t in list(strings) + chars:
            pts = tuple(sorted(L._pixels(t, face)))
            if len(pts) < 4 or (face, pts) in seen:
                continue
            seen.add((face, pts))
            w = max(x for x, _ in pts) + 1
            h = max(y for _, y in pts) + 1
            out.append((pts, w, h, len(t) == 1))
    return out


def lettering_mask(img, button, halo=True):
    """Find the button's own lettering in a painted image and return the set of
    its pixels (plus, with ``halo``, a 1 px 8-neighbour halo that holds the
    text shadow and the contrast ring round each letter).

    Detection matches the GRAVEN/RUNE rendering of the label, its lines, their
    words and their single characters at every offset: a hit needs every glyph
    pixel to share one opaque colour while at least 75 % (whole strings) or
    100 % (single characters) of the other pixels in the glyph box differ from
    it, so flat fills never match. Single characters (for hand-kerned
    lettering) only count on rows where a whole word or line was found and in
    that lettering's colour, so negative space or a stray shape in a page curl
    can never pass for a letter. Icons
    and unlettered faces return an empty set (the transforms then only spare
    ink)."""
    if button.icon or button_kind(button) in ('close', 'icon'):
        return set()
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
                if single and rows and not any(oy + k in rows for k in range(h)):
                    continue
                for ox in range(0, W - w + 1):
                    c = px[ox + first[0], oy + first[1]]
                    if c[3] == 0 or (single and inks and c not in inks):
                        continue
                    if any(px[ox + x, oy + y] != c for x, y in pts):
                        continue
                    same = sum(1 for x, y in others if px[ox + x, oy + y] == c)
                    if (same == 0) if single else (same <= len(others) // 4):
                        found.update((ox + x, oy + y) for x, y in pts)
        if not want_single:
            rows = {y for (_, y) in found}
            inks = {px[x, y] for (x, y) in found}
    if halo and found:
        grown = set(found)
        for (x, y) in found:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if 0 <= x + dx < W and 0 <= y + dy < H:
                        grown.add((x + dx, y + dy))
        found = grown
    return found


def button_states(normal, key, button_id, overrides=None):
    """Six finished state images from one painted normal frame using the
    shared transforms; ``overrides`` maps state -> hand-adjusted image.

    The button's lettering (``lettering_mask``) keeps its shape and alpha in
    every state: selected keeps the glyph pixels exactly, pulses keep the
    glyphs and their 1 px halo exactly, and disabled recolours the glyphs into
    the dead-stone lettering register (gold and vellum -> iron_3, ink stays
    ink) so the whole control reads inert.
    The close seal (``button_kind == 'close'``) uses
    ``primitives.make_disabled_seal`` so its disabled frame is dead grey wax
    with an ink X."""
    b = geo.skin(key).button(button_id)
    glyphs = lettering_mask(normal, b, halo=False)
    protect = lettering_mask(normal, b, halo=True) if glyphs else set()
    seal = button_kind(b) == 'close'
    out = {}
    for st in geo.STATES:
        img = (overrides or {}).get(st) or P.make_state(normal, st, protect=protect, seal=seal, glyphs=glyphs)
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
