"""Frozen geometry for every cozy texture, computed with the builder's own code.

All rectangles are ``Rect(x, y, w, h)`` (half-open: x .. x+w-1). Masks are taken
from ``build_pack.masks`` and button pins from ``button_assets.advance_pin`` after
``button_assets.load`` has derived visible content slots, exactly as the real
build does. Nothing here is a re-implementation of those rules, so painters can
trust it. The manifests are loaded once per process.

Typical use::

    import geometry as geo
    s = geo.skin('auction_house')
    img = Image.new('RGBA', (s.width, s.height))
    ...paint...
    geo.clear_background_masks(img, s.key)
    geo.stamp_background_pin(img, s.key, 'ink_1')

Licence: MIT.
"""
from __future__ import annotations

import sys as _sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path as _Path

_HERE = _Path(__file__).resolve().parent
ROOT = _HERE.parents[1]
TOOLS = ROOT / 'tools'
for _p in (str(_HERE), str(TOOLS)):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import json  # noqa: E402

import button_assets  # noqa: E402  (repository builder module)
import build_pack  # noqa: E402  (repository builder module)
from palette import rgba  # noqa: E402

TEXTURES = ROOT / 'pack-source' / 'assets' / 'quasar_gui' / 'textures'
STATES = tuple(button_assets.STATES)  # normal, disabled, selected, pulse_1, pulse_2, pulse_3


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def right(self):
        """Exclusive right edge."""
        return self.x + self.w

    @property
    def bottom(self):
        """Exclusive bottom edge."""
        return self.y + self.h

    def box(self):
        """Inclusive PIL box (x0, y0, x1, y1)."""
        return (self.x, self.y, self.x + self.w - 1, self.y + self.h - 1)

    def crop_box(self):
        """PIL crop box (x0, y0, x1, y1) with exclusive right/bottom."""
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def intersect(self, other):
        x0, y0 = max(self.x, other.x), max(self.y, other.y)
        x1, y1 = min(self.right, other.right), min(self.bottom, other.bottom)
        return Rect(x0, y0, x1 - x0, y1 - y0) if x0 < x1 and y0 < y1 else None

    def contains(self, x, y):
        return self.x <= x < self.right and self.y <= y < self.bottom

    def moved(self, dx, dy):
        return Rect(self.x + dx, self.y + dy, self.w, self.h)

    def inset(self, n):
        return Rect(self.x + n, self.y + n, self.w - 2 * n, self.h - 2 * n)

    def tuple(self):
        return (self.x, self.y, self.w, self.h)


@dataclass(frozen=True)
class Slot:
    index: int
    x: int            # native 16x16 item footprint top-left
    y: int
    clearance: Rect   # 20x20 alpha-zero rectangle (x-2, y-2, 20, 20)


@dataclass(frozen=True)
class Button:
    id: str
    x: int
    y: int
    w: int
    h: int
    style: str            # primary | secondary | danger
    role: str             # action | info
    label: str
    lines: tuple          # explicit multi-line label (may be empty)
    icon: str | None      # close | balance | search | settings | None
    default_state: str
    source_slot: int
    slots: tuple
    pin: tuple            # (px, py) button-local advance pin
    masks: tuple          # Rect list, button-local, that must stay alpha 0
    body: Rect            # button-local drawable body (edges trimmed by masks removed)
    skin_key: str = ''

    @property
    def rect(self):
        return Rect(self.x, self.y, self.w, self.h)

    @property
    def text_lines(self):
        """The only words a painter may letter on this button."""
        return list(self.lines) if self.lines else [self.label.upper()]

    def path(self, state):
        return TEXTURES / 'buttons' / self.skin_key / self.id / f'{state}.png'


@dataclass(frozen=True)
class ArtLayer:
    id: str
    x: int
    y: int
    w: int
    h: int
    heading: str | None
    left_heading: str | None
    right_lines: tuple
    pin: tuple            # (w-1, h//2)
    container: Rect       # layer-local native container rectangle (alpha 0)
    purpose: str

    @property
    def top_strip(self):
        return Rect(0, 0, self.w, max(0, self.container.y))

    @property
    def bottom_strip(self):
        return Rect(0, self.container.bottom, self.w, max(0, self.h - self.container.bottom))

    @property
    def left_panel(self):
        return Rect(0, 0, max(0, self.container.x), self.h)

    @property
    def right_panel(self):
        return Rect(self.container.right, 0, max(0, self.w - self.container.right), self.h)


@dataclass(frozen=True)
class Skin:
    key: str
    layout: str
    width: int
    height: int
    family: str
    presentation: str
    menu_type: str
    title_anchor: tuple
    centered_title: bool
    text_safe: Rect
    inventory_label: Rect
    content_slots: tuple      # Slot list: native visible content wells (alpha 0)
    player_slots: tuple       # Slot list: 36 player wells (alpha 0)
    all_slots: tuple          # every native top slot, including painted/static ones
    static_slots: tuple       # indices of protected static artwork cells (opaque allowed)
    painted_slots: tuple      # indices covered by painted buttons
    masks: tuple              # Rect list: background alpha-zero rectangles (builder order)
    extra_transparent: tuple  # Rect list (crafting recipe toggle + arrow)
    advance_pin: Rect         # [175, 0, 1, 3] must be alpha 255
    buttons: tuple
    art_layers: tuple
    asset: str

    @property
    def background_path(self):
        return ROOT / 'pack-source' / self.asset

    def button(self, button_id):
        for b in self.buttons:
            if b.id == button_id:
                return b
        raise KeyError(f'{self.key} has no button {button_id!r}; has {[b.id for b in self.buttons]}')

    def layer(self, layer_id=None):
        if layer_id is None:
            if len(self.art_layers) != 1:
                raise KeyError(f'{self.key} has {len(self.art_layers)} art layers; name one')
            return self.art_layers[0]
        for a in self.art_layers:
            if a.id == layer_id:
                return a
        raise KeyError(f'{self.key} has no art layer {layer_id!r}')

    def button_path(self, button_id, state):
        self.button(button_id)
        return TEXTURES / 'buttons' / self.key / button_id / f'{state}.png'

    def frame_path(self, layer_id=None):
        return TEXTURES / 'frames' / self.key / f'{self.layer(layer_id).id}.png'

    @property
    def content_bbox(self):
        """Union of content-well clearances, or None when the skin has none."""
        return _union([s.clearance for s in self.content_slots])

    @property
    def player_bbox(self):
        return _union([s.clearance for s in self.player_slots])

    @property
    def title_band(self):
        """Light band that must sit under the live title: rows 0 .. text_safe bottom."""
        return Rect(0, 0, self.width, self.text_safe.bottom)

    @property
    def is_dispenser(self):
        return self.layout == 'dispenser'


def _union(rects):
    rects = [r for r in rects if r]
    if not rects:
        return None
    x0 = min(r.x for r in rects); y0 = min(r.y for r in rects)
    x1 = max(r.right for r in rects); y1 = max(r.bottom for r in rects)
    return Rect(x0, y0, x1 - x0, y1 - y0)


def _read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


@lru_cache(maxsize=1)
def _data():
    layouts = _read(ROOT / 'manifests' / 'layouts.json')['layouts']
    skins = _read(ROOT / 'manifests' / 'skins.json')['skins']
    config = button_assets.load(ROOT, layouts, skins)   # mutates skins like the builder
    return layouts, skins, config


def raw_manifests():
    """(layouts, skins, button config) after the builder's own derivation step."""
    return _data()


def _body(w, h, masks):
    """Shrink an edge by one pixel when masks cover more than its two corner pixels."""
    def covered(points):
        return sum(1 for (px, py) in points if any(m.contains(px, py) for m in masks))
    left = covered([(0, y) for y in range(h)]) > 2
    right = covered([(w - 1, y) for y in range(h)]) > 2
    top = covered([(x, 0) for x in range(w)]) > 2
    bottom = covered([(x, h - 1) for x in range(w)]) > 2
    x0 = 1 if left else 0
    y0 = 1 if top else 0
    x1 = w - (1 if right else 0)
    y1 = h - (1 if bottom else 0)
    return Rect(x0, y0, x1 - x0, y1 - y0)


@lru_cache(maxsize=None)
def skin(key):
    """Full geometry for one skin key (see ``Skin``)."""
    layouts, skins, config = _data()
    if key not in skins:
        raise KeyError(f'Unknown skin {key!r}')
    s = skins[key]
    g = layouts[s['layout']]
    screen = config['screens'].get(key, {'buttons': [], 'contentSlots': []})
    dx, dy, cw, ch = g['itemClearance']
    content_ids = set(s.get('visibleContentSlots', s.get('liveSlots', [])))

    def slot(p):
        return Slot(p['index'], p['x'], p['y'], Rect(p['x'] + dx, p['y'] + dy, cw, ch))

    content = tuple(slot(p) for p in g['slots'] if p['index'] in content_ids)
    player = tuple(slot(p) for p in g['playerSlots'])
    masks = tuple(Rect(*m) for m in build_pack.masks(g, s))
    btn_masks = [Rect(*m) for m in button_assets.masks(g, s)]
    buttons = []
    for b in screen['buttons']:
        x, y, w, h = button_assets.geometry(g, b)
        local = []
        for m in btn_masks:
            r = m.intersect(Rect(x, y, w, h))
            if r:
                local.append(r.moved(-x, -y))
        btn = Button(id=b['id'], x=x, y=y, w=w, h=h, style=b['style'], role=b['role'], label=b['label'],
                     lines=tuple(b.get('lines', [])), icon=b.get('icon'),
                     default_state=screen.get('defaultStates', {}).get(b['id'], 'normal'),
                     source_slot=b['sourceSlot'], slots=tuple(b['slots']),
                     pin=tuple(button_assets.advance_pin(g, s, b)), masks=tuple(local),
                     body=_body(w, h, local), skin_key=key)
        buttons.append(btn)
    layers = []
    for a in screen.get('artLayers', []):
        container = Rect(-a['x'], -a['y'], g['width'], g['height'])
        layers.append(ArtLayer(id=a['id'], x=a['x'], y=a['y'], w=a['width'], h=a['height'],
                               heading=a.get('heading'), left_heading=a.get('leftHeading'),
                               right_lines=tuple(a.get('rightLines', [])),
                               pin=(a['width'] - 1, a['height'] // 2), container=container,
                               purpose=a.get('purpose', '')))
    return Skin(key=key, layout=s['layout'], width=g['width'], height=g['height'], family=s['family'],
                presentation=s.get('presentation', screen.get('presentation', 'painted_controls')),
                menu_type=g['menuType'], title_anchor=tuple(g['titleAnchor']), centered_title=g['centered'],
                text_safe=Rect(*g['textSafe']), inventory_label=Rect(*g['inventoryLabel']),
                content_slots=content, player_slots=player, all_slots=tuple(slot(p) for p in g['slots']),
                static_slots=tuple(s.get('staticProtectedSlots', [])),
                painted_slots=tuple(s.get('paintedControlSlots', [])), masks=masks,
                extra_transparent=tuple(Rect(*e['rect']) for e in g['extraTransparent']),
                advance_pin=Rect(*g['advancePin']), buttons=tuple(buttons), art_layers=tuple(layers),
                asset=s['asset'])


def all_skins():
    """Every skin key in manifest order (56)."""
    return list(_data()[1].keys())


def skins_by_family():
    out = {}
    for k in all_skins():
        out.setdefault(skin(k).family, []).append(k)
    return out


# --- Mask clearing and pin stamping -----------------------------------------

def _clear(img, rects):
    for r in rects:
        x0, y0 = max(0, r.x), max(0, r.y)
        x1, y1 = min(img.width, r.right), min(img.height, r.bottom)
        if x0 < x1 and y0 < y1:
            img.paste((0, 0, 0, 0), (x0, y0, x1, y1))
    return img


def _check_size(img, w, h, what):
    if img.size != (w, h):
        raise ValueError(f'{what}: image is {img.size}, contract is {(w, h)}')
    if img.mode != 'RGBA':
        raise ValueError(f'{what}: image mode {img.mode}, need RGBA')


def clear_background_masks(img, key):
    """Set every background mask (content wells, 36 player wells, extra
    transparent rects) to (0,0,0,0). Call LAST before stamping the pin."""
    s = skin(key)
    _check_size(img, s.width, s.height, key)
    return _clear(img, s.masks)


def clear_button_masks(img, key, button_id):
    """Clear the content/player clearances that trim this button, and every
    column to the right of the advance pin."""
    b = skin(key).button(button_id)
    _check_size(img, b.w, b.h, f'{key}/{button_id}')
    _clear(img, b.masks)
    if b.pin[0] + 1 < b.w:
        _clear(img, [Rect(b.pin[0] + 1, 0, b.w - b.pin[0] - 1, b.h)])
    return img


def clear_frame_container(img, key, layer_id=None):
    """Clear the whole native container rectangle inside the frame layer."""
    a = skin(key).layer(layer_id)
    _check_size(img, a.w, a.h, f'{key}/{a.id}')
    return _clear(img, [a.container])


def stamp_background_pin(img, key, color='ink_1'):
    """Fill the advancePin rect (x175, y0, 1x3) fully opaque."""
    s = skin(key)
    c = rgba(color)
    for y in range(s.advance_pin.y, s.advance_pin.bottom):
        for x in range(s.advance_pin.x, s.advance_pin.right):
            img.putpixel((x, y), c)
    return img


def stamp_button_pin(img, key, button_id, color='ink_1'):
    """Make the button's pin pixel opaque. An already opaque pin keeps its colour,
    so a pin that lands on painted outline stays invisible."""
    b = skin(key).button(button_id)
    px, py = b.pin
    cur = img.getpixel((px, py))
    if cur[3] != 255:
        img.putpixel((px, py), rgba(color))
    return img


def stamp_frame_pin(img, key, layer_id=None, color='ink_1'):
    a = skin(key).layer(layer_id)
    px, py = a.pin
    cur = img.getpixel((px, py))
    if cur[3] != 255:
        img.putpixel((px, py), rgba(color))
    return img


def finish_background(img, key, pin_color='ink_1'):
    """clear_background_masks + stamp_background_pin."""
    clear_background_masks(img, key)
    return stamp_background_pin(img, key, pin_color)


def finish_button(img, key, button_id, pin_color='ink_1'):
    """clear_button_masks + stamp_button_pin."""
    clear_button_masks(img, key, button_id)
    return stamp_button_pin(img, key, button_id, pin_color)


def finish_frame(img, key, layer_id=None, pin_color='ink_1'):
    """clear_frame_container + stamp_frame_pin."""
    clear_frame_container(img, key, layer_id)
    return stamp_frame_pin(img, key, layer_id, pin_color)


def asset_paths(key):
    """Every pack-source PNG belonging to a skin: background, 6 per button, frames."""
    s = skin(key)
    out = [s.background_path]
    for b in s.buttons:
        out += [s.button_path(b.id, st) for st in STATES]
    out += [s.frame_path(a.id) for a in s.art_layers]
    return out
