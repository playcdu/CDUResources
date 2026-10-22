"""Standard cozy compositions: the shared starting point every painter builds on.

These functions turn geometry + primitives into the canonical base look, so the
twelve painters share one grammar and only add family identity on top:

    base_background(key, seed)        wood sheet, parchment title + inventory
                                      bands, stitched wells around every clearance
    base_frame(key, layer_id, seed)   darker wood board around the container,
                                      cast shadow, brass corners, heading ribbon
    paint_button(key, button_id, seed)  normal state in the right grammar
                                      (primary brass plank / secondary linen tag /
                                      danger wax / page-turn curl / icon)
    button_states(normal, key, button_id)  all six states via the shared transforms
    save_png / save_button_states / output paths

Everything returned is already finished (masks cleared, pins stamped) and can
be re-finished safely after further painting with geometry.finish_*.

Licence: MIT.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_HERE = str(_Path(__file__).resolve().parent)
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

from PIL import Image  # noqa: E402

import geometry as geo  # noqa: E402
import icons  # noqa: E402
import lettering as L  # noqa: E402
import primitives as P  # noqa: E402
from palette import BERRY, BRASS, ENDER_WOOD, INK, PARCHMENT, WOOD, accent_for  # noqa: E402

# Darker board used by outer frames, so the menu sheet reads as lying on it.
FRAME_WOOD = [INK[1], WOOD[0], WOOD[1], WOOD[2], WOOD[3]]


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


def wood_for(key):
    return ENDER_WOOD if key == 'ender_chest' else WOOD


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------

def bands(key):
    """(title_band, inventory_band) Rects that hold parchment for live text.

    The title band spans rows 2 .. 14 (rows 5-13 carry vanilla title glyphs);
    the inventory band fills the rows between the lowest clearance above the
    label and the player grid, keeping one row each side for the well lips."""
    s = geo.skin(key)
    title = geo.Rect(3, 2, s.width - 6, 13)
    inv = s.inventory_label
    above = [m.bottom for m in s.masks if m.bottom <= inv.y + 1]
    below = [m.y for m in s.masks if m.y >= inv.y + 4]
    top = max([inv.y - 2] + above) + 1
    bottom = min([inv.y + 9] + below) - 1      # exclusive
    return title, geo.Rect(3, top, s.width - 6, bottom - top)


def base_background(key, seed=0, wells='stitched', title=True, inventory=True, ramp=None):
    """Canonical background for ``key``: horizontal oiled planks, rounded ink
    rim (heavier bottom-right), parchment title band pinned with brass tacks,
    parchment inventory band, recessed stitched wells framing every native
    clearance. Masks are cleared and the advance pin stamped."""
    s = geo.skin(key)
    ramp = ramp or wood_for(key)
    img = new(s.width, s.height)
    P.planks(img, (1, 1, s.width - 2, s.height - 2), ramp, seed, board=9)
    P.ink_outline(img, (0, 0, s.width, s.height), 'ink_1', radius=2, heavy='br')
    P.highlight_edge(img, (0, 0, s.width, s.height), ramp[4], 'tl', broken=6, seed=seed, inset=1)
    tband, iband = bands(key)
    protect = []
    if title:
        P.parchment_panel(img, tband.tuple(), seed, outline='ink_2', fibres=True)
        P.tack(img, tband.x + 2, tband.y + 5, small=True)
        P.tack(img, tband.right - 3, tband.y + 5, small=True)
        protect.append(tband.tuple())
    if inventory:
        # no ink rim: the well lips above and below frame it, glyph rows stay light
        P.parchment_panel(img, iband.tuple(), seed + 1, outline=None, fibres=False)
        protect.append(iband.tuple())
    holes = P.merge_holes(s.content_slots) + P.merge_holes(s.player_slots)
    if wells == 'stitched':
        P.stitched_well(img, holes, protect=protect)
    elif wells == 'wood':
        P.wood_well(img, holes, protect=protect)
    for r in s.extra_transparent:
        P.well_frame(img, [r.tuple()], 'wood', depth=2, protect=protect)
    geo.finish_background(img, key)
    return img


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------

RIBBON_TAIL = ['oooo', 'o11o', '.o1o', '..oo', '..oo', '.o1o', 'o11o', 'oooo']


def heading_ribbon(img, cx, y, text, ramp=PARCHMENT, ink='ink_1'):
    """Parchment ribbon 8 px tall (fits the frame's top strip) with swallowtail
    ends and SPRIG lettering, centred on ``cx`` with its top row at ``y``:
    row 0 ink, row 1 cream highlight, rows 2-6 lettering, row 7 ink.
    Returns its box."""
    tw = L.text_width(text, 'sprig')
    w = tw + 10
    x = cx - w // 2
    key = {'o': ink, '1': ramp[0]}
    P.sprite(img, x - 3, y, RIBBON_TAIL, key)
    P.sprite(img, x + w - 1, y, RIBBON_TAIL, key, flip_x=True)
    P.ink_outline(img, (x, y, w, 8), ink, radius=0, fill_colour=ramp[2])
    P.hline(img, x + 1, x + w - 2, y + 1, ramp[3])
    P.hline(img, x + 1, x + w - 2, y + 6, ramp[1])
    L.draw_text(img, x + 5, y + 2, text, 'ink_0', face='sprig')
    return (x - 3, y, w + 6, 8)


def brass_corner(img, x, y, corner):
    """6x6 brass L-bracket for an outer frame corner ('tl', 'tr', 'bl', 'br')."""
    rows = ['ooooo.', 'o3322o', 'o2oooo', 'o2o...', 'o2o...', '.oo...']
    P.sprite(img, x, y, rows, {'o': INK[0], '3': BRASS[3], '2': BRASS[1]},
             flip_x='r' in corner, flip_y='b' in corner)


def base_frame(key, layer_id=None, seed=0, heading=True):
    """Canonical outer frame: darker vertical boards, rounded ink_0 rim, brass
    corner brackets, a 2 px cast shadow right of and below the container, and
    the artLayers heading on a parchment ribbon in the top strip. The native
    container is cleared and the advance pin stamped."""
    s = geo.skin(key)
    a = s.layer(layer_id)
    img = new(a.w, a.h)
    ramp = FRAME_WOOD if key != 'ender_chest' else [INK[0]] + ENDER_WOOD[:4]
    P.planks(img, (1, 1, a.w - 2, a.h - 2), ramp, seed, board=11, vertical=True, seams=ramp[0], grain=0.55)
    c = a.container
    # horizontal beams across the top and bottom strips frame the side boards
    for beam in ((1, 1, a.w - 2, c.y - 1), (1, c.bottom, a.w - 2, a.h - c.bottom - 1)):
        if beam[3] >= 3:
            P.fill(img, beam, ramp[2])
            P._grain(img, beam, ramp, (seed, beam[1]), 0.5, False)
            P.hline(img, beam[0], beam[0] + beam[2] - 1, beam[1], ramp[3])
            P.hline(img, beam[0], beam[0] + beam[2] - 1, beam[1] + beam[3] - 1, ramp[0])
    P.ink_outline(img, (0, 0, a.w, a.h), 'ink_0', radius=3)
    P.highlight_edge(img, (0, 0, a.w, a.h), ramp[3], 'tl', broken=5, seed=seed, inset=1)
    # cast shadow of the sheet onto the board
    for k in (0, 1):
        P.vline(img, c.right + k, c.y + 2 + k, c.bottom - 1 + k, INK[1] if k == 0 else ramp[0])
        P.hline(img, c.x + 2 + k, c.right + k, c.bottom + k, INK[1] if k == 0 else ramp[0])
    for corner, (x, y) in (('tl', (2, 2)), ('tr', (a.w - 8, 2)), ('bl', (2, a.h - 8)), ('br', (a.w - 8, a.h - 8))):
        brass_corner(img, x, y, corner)
    if heading and a.heading:
        heading_ribbon(img, a.w // 2, 0, a.heading)
    geo.finish_frame(img, key, a.id, 'ink_0')
    return img


def side_tag(img, panel, text, y, seed=0, twine_from=None):
    """Hang a linen tag with SPRIG lettering centred in a side ``panel`` Rect,
    top at ``y``, optionally on twine from point ``twine_from``. Returns box."""
    tw = L.text_width(text, 'sprig')
    w = max(tw + 6, 14)
    x = panel.x + (panel.w - w) // 2
    if twine_from:
        P.twine(img, twine_from[0], twine_from[1], x + w // 2, y, sag=0)
    P.linen_tag(img, (x, y, w, 9), eyelet=None, seed=seed)
    L.draw_text(img, x + 3, y + 2, text, 'ink_0', face='sprig')
    return (x, y, w, 9)


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

def button_kind(button):
    """close | icon | page_prev | page_next | primary | secondary | danger."""
    if button.icon == 'close':
        return 'close'
    if button.icon or (button.w == 18 and button.h == 18):
        return 'icon'
    if button.id in ('previous', 'prev'):
        return 'page_prev'
    if button.id == 'next':
        return 'page_next'
    return button.style


def _label_plan(button, box):
    """Choose (lines, face) that fit ``box``: HEARTH capitals, then HEARTH
    mixed case (label only), then SPRIG capitals. Never invents words."""
    _, _, w, h = box
    options = [(button.text_lines, 'hearth')]
    if not button.lines:
        options.append(([button.label], 'hearth'))
    options.append(([t.upper() for t in button.text_lines], 'sprig'))
    for lines, face in options:
        f = L.FACES[face]
        gap = 2 if face == 'hearth' else 1
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
    """Brass-plated plank: wood rim (outline + 1 px oiled wood), brass plate
    inset 2 px with a brass_0 rim, rivets, lit top, shaded bottom. Returns the
    text box."""
    x, y, w, h = body
    P.plank(img, body, WOOD, seed, 'ink_1', radius=1, grain=0.6)
    px, py, pw, ph = x + 2, y + 2, w - 4, h - 4
    P.brass_plate(img, (px, py, pw, ph), rivets=(pw >= 30 and ph >= 12), outline='brass_0')
    pad = 4 if pw >= 30 else 2
    return (px + pad, py + 2, pw - 2 * pad, ph - 4)


def secondary_face(img, body, seed=0, eyelet='auto'):
    """Linen tag with clipped eyelet corners and a running stitch. ``eyelet``
    'auto' picks left (wide), top (tall) or none."""
    x, y, w, h = body
    if eyelet == 'auto':
        eyelet = 'left' if w >= 36 and h <= 20 else ('top' if h >= 36 and w < 36 else None)
        if w >= 54 and h >= 30:
            eyelet = 'left'
    box = P.linen_tag(img, body, eyelet=eyelet, seed=seed)
    bx, by, bw, bh = box
    return (bx + 1, by + 2, bw - 2, bh - 4)


def danger_face(img, body, seed=0):
    """Red wax slab with a small pressed seal on the left when there is room."""
    x, y, w, h = body
    inner = P.wax_slab(img, body, BERRY, seed, drips=2 if w >= 36 else 1)
    ix, iy, iw, ih = inner
    if w >= 50 and h <= 24:
        r = min(5, (ih - 1) // 2 + 1)
        cx, cy = x + 3 + r, y + (h - 2) // 2
        P.wax_seal(img, cx, cy, r, BERRY, seed, drip=False)
        return (cx + r + 2, iy + 1, ix + iw - (cx + r + 2) - 2, ih - 2)
    return (ix + 2, iy + 1, iw - 4, ih - 2)


def page_face(img, body, direction, seed=0):
    """Parchment sheet with a curled corner pointing the way the page turns
    (next: bottom-right; previous: bottom-left)."""
    x, y, w, h = body
    P.parchment_panel(img, body, seed, outline='ink_1', fibres=True)
    size = 6 if h >= 16 else 5
    P.page_curl(img, body, 'br' if direction == 'next' else 'bl', size)
    pad = 3
    if direction == 'next':
        return (x + pad, y + 2, w - pad - size - 1, h - 4)
    return (x + size + 1, y + 2, w - pad - size - 1, h - 4)


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
        x, y, w, h = body
        P.linen_tag(img, body, eyelet=None, seed=seed)
        if b.h > 36 and b.icon == 'balance':
            P.stitch_line(img, x + 2, y + 3, x + 2, y + h - 4, 'parch_0', 2, 2)
            P.stitch_line(img, x + w - 3, y + 3, x + w - 3, y + h - 4, 'parch_0', 2, 2)
            P.tack(img, x + w // 2, y + 3)
            icons.draw_icon(img, 'balance', (x, y + 8, w, 16))
            for k in range(3):
                icons.draw_icon(img, 'coin', (x, y + 30 + k * 7, w, 5))
            P.tack(img, x + w // 2, y + h - 6)
        else:
            icons.draw_icon(img, b.icon or 'rank', body)
    elif kind == 'primary':
        letter(img, b, primary_face(img, body, seed), 'ink_0', shadow='brass_3')
    elif kind == 'secondary':
        trial = new(b.w, b.h)
        try:
            _label_plan(b, secondary_face(trial, body, seed))
            eyelet = 'auto'
        except ValueError:
            eyelet = None          # the label needs the eyelet's room
        letter(img, b, secondary_face(img, body, seed, eyelet), 'ink_0')
    elif kind == 'danger':
        letter(img, b, danger_face(img, body, seed), 'parch_3', shadow='berry_0')
    elif kind in ('page_prev', 'page_next'):
        letter(img, b, page_face(img, body, 'next' if kind == 'page_next' else 'prev', seed), 'ink_0')
    geo.finish_button(img, key, button_id)
    return img


def button_states(normal, key, button_id, overrides=None):
    """Six finished state images from one painted normal frame using the
    shared transforms; ``overrides`` maps state -> hand-adjusted image."""
    out = {}
    for st in geo.STATES:
        img = (overrides or {}).get(st) or P.make_state(normal, st)
        out[st] = geo.finish_button(img, key, button_id)
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
