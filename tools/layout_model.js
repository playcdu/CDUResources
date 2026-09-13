/* Pure layout contract shared by the offline helper and Node regression tests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.LayoutModel = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const clone = value => JSON.parse(JSON.stringify(value));
  const stable = value => JSON.stringify(value, function (key, item) {
    return item && !Array.isArray(item) && typeof item === 'object'
      ? Object.keys(item).sort().reduce((out, k) => { out[k] = item[k]; return out; }, {}) : item;
  });
  const fail = message => { throw new Error(message); };
  function geometry(layout, slots) {
    if (!Array.isArray(slots) || !slots.length || slots.some(n => !Number.isInteger(n)) || new Set(slots).size !== slots.length) fail('Choose unique native slots');
    const points = slots.map(n => layout.slots.find(p => p.index === n) || fail('A button cannot leave the native top inventory'));
    const x = Math.min(...points.map(p => p.x)) - 1, y = Math.min(...points.map(p => p.y)) - 1;
    const width = Math.max(...points.map(p => p.x)) - x + 17, height = Math.max(...points.map(p => p.y)) - y + 17;
    const expected = layout.slots.filter(p => p.x >= x && p.x < x + width && p.y >= y && p.y < y + height).map(p => p.index);
    if (width * height !== slots.length * 324 || expected.length !== slots.length || expected.some(n => !slots.includes(n))) fail('Use a complete rectangle of adjacent 18px native slots');
    return {x, y, width, height};
  }
  function protectedSlots(screen) { return [...new Set([...(screen.contentSlots || []), ...(screen.contentRegion?.slots || [])])]; }
  function immutable(config) {
    const copy = clone(config);
    for (const screen of Object.values(copy.screens)) {
      if (screen.contentRegion) { delete screen.contentRegion.slots; delete screen.contentSlots; }
      for (const button of screen.buttons) {
        delete button.slots; delete button.label; delete button.style; delete button.lines;
      }
    }
    return copy;
  }
  function validate(config, baseline, data) {
    if (stable(immutable(config)) !== stable(immutable(baseline))) fail('Action IDs, source slots, roles, content source identities and undeclared metadata are immutable. Import a project for this exact binding set.');
    for (const [key, screen] of Object.entries(config.screens)) {
      const layout = data.layouts[data.skins[key].layout], used = new Set(), protectedSet = new Set(protectedSlots(screen));
      if (screen.contentRegion) {
        const slots=screen.contentRegion.slots;
        if (slots.length!==baseline.screens[key].contentRegion.slots.length) fail('Native display capacity is fixed');
        geometry(layout,slots);
        if (!Array.isArray(screen.contentSlots) || stable([...screen.contentSlots].sort((a,b)=>a-b))!==stable([...slots].sort((a,b)=>a-b))) fail('Native display masks must match their destinations');
      }
      for (const button of screen.buttons) {
        geometry(layout, button.slots);
        if (typeof button.label !== 'string' || button.label.length > 120 || !['primary', 'secondary', 'danger'].includes(button.style)) fail('Use a label of at most 120 characters and a supported style');
        if (button.lines !== undefined && (!Array.isArray(button.lines) || button.lines.length > 8 || button.lines.some(s => typeof s !== 'string' || s.length > 120))) fail('Use at most eight short label lines');
        for (const slot of button.slots) {
          if (protectedSet.has(slot)) fail('That rectangle covers protected native content');
          if (used.has(slot)) fail('Button rectangles cannot overlap');
          used.add(slot);
        }
      }
    }
    return config;
  }
  function slotsBetween(layout, first, last) {
    const a = layout.slots.find(p => p.index === first), b = layout.slots.find(p => p.index === last);
    if (!a || !b) fail('Drag from one native top slot to another');
    return layout.slots.filter(p => p.x >= Math.min(a.x,b.x) && p.x <= Math.max(a.x,b.x) && p.y >= Math.min(a.y,b.y) && p.y <= Math.max(a.y,b.y)).map(p => p.index);
  }
  function slotAt(layout, x, y) { return layout.slots.find(p => x >= p.x-1 && x < p.x+17 && y >= p.y-1 && y < p.y+17)?.index; }
  function moveSlots(layout, slots, dx, dy) {
    return slots.map(n => {
      const p = layout.slots.find(p => p.index === n);
      return layout.slots.find(q => q.x === p.x+dx*18 && q.y === p.y+dy*18)?.index ?? fail('Move stays inside native top slots');
    });
  }
  function pngDimensions(data) {
    if (typeof data !== 'string' || data.length > 24000000 || !/^data:image\/png;base64,[A-Za-z0-9+/]*={0,2}$/.test(data)) fail('Import a PNG data URL under 18 MB');
    const raw = typeof Buffer !== 'undefined' ? Buffer.from(data.split(',')[1], 'base64') : Uint8Array.from(atob(data.split(',')[1]), c => c.charCodeAt(0));
    const signature = [137,80,78,71,13,10,26,10];
    if (raw.length < 33 || signature.some((n,i) => raw[i] !== n) || String.fromCharCode(...raw.slice(12,16)) !== 'IHDR') fail('Invalid PNG header');
    const view = new DataView(raw.buffer, raw.byteOffset, raw.byteLength);
    return {width:view.getUint32(16), height:view.getUint32(20)};
  }
  function expectedAsset(data, config, asset) {
    for (const [key, skin] of Object.entries(data.skins)) {
      const layout = data.layouts[skin.layout];
      if (asset === skin.asset) return {width:layout.width,height:layout.height};
      const screen = config.screens[key];
      if (!screen) continue;
      for (const b of screen.buttons) if (['normal','disabled','selected','pulse_1','pulse_2','pulse_3'].some(state => asset === `assets/quasar_gui/textures/buttons/${key}/${b.id}/${state}.png`)) return geometry(layout,b.slots);
      for (const layer of screen.artLayers || []) if (asset === `assets/quasar_gui/textures/frames/${key}/${layer.id}.png`) return {width:layer.width,height:layer.height};
    }
    fail('PNG is not a declared artwork asset');
  }
  class Project {
    constructor(data) { this.data=data; this.baseline=clone(data.config); this.config=clone(data.config); this.images={}; this.history=[]; validate(this.config,this.baseline,data); }
    save() { this.history.push({config:clone(this.config),images:clone(this.images)}); if(this.history.length>50)this.history.shift(); }
    update(key, id, patch) {
      const next=clone(this.config), b=next.screens[key]?.buttons.find(b=>b.id===id);
      if(!b)fail('Select an existing audited binding');
      if(Object.keys(patch).some(k=>!['slots','label','style','lines'].includes(k)))fail('Only layout and presentation fields can change');
      Object.assign(b,clone(patch)); validate(next,this.baseline,this.data); this.save();this.config=next;return b;
    }
    updateContent(key, slots) {
      const next=clone(this.config), screen=next.screens[key];
      if (!screen?.contentRegion) fail('This screen has no movable native display mapping');
      screen.contentRegion.slots=clone(slots);screen.contentSlots=[...slots].sort((a,b)=>a-b);
      validate(next,this.baseline,this.data);this.save();this.config=next;
    }
    image(asset,data) {
      const size=pngDimensions(data), expected=expectedAsset(this.data,this.config,asset);
      if(size.width!==expected.width || size.height!==expected.height)fail(`PNG must stay ${expected.width}×${expected.height}px; no automatic resize`);
      this.save();this.images[asset]={...size,data};
    }
    undo() {const previous=this.history.pop();if(previous){this.config=previous.config;this.images=previous.images;}return !!previous;}
    reset() {this.save();this.config=clone(this.baseline);this.images={};}
    exportProject() {return {schemaVersion:1,kind:'cdu-layout-project',bindingSignature:stable(immutable(this.baseline)),layouts:clone(this.config),images:clone(this.images)};}
    importProject(value) {
      if(value?.schemaVersion!==1 || value.kind!=='cdu-layout-project' || value.bindingSignature!==stable(immutable(this.baseline)))fail('Project bindings differ from this helper; rebuild it from the current repository');
      validate(value.layouts,this.baseline,this.data);
      const images=value.images || {};
      for(const [asset,item] of Object.entries(images)){
        const expected=expectedAsset(this.data,value.layouts,asset), actual=pngDimensions(item.data);
        if(actual.width!==expected.width || actual.height!==expected.height || item.width!==actual.width || item.height!==actual.height)fail('Imported PNG dimensions do not match declared artwork');
      }
      this.save();this.config=clone(value.layouts);this.images=clone(images);
    }
    importLayout(value) {validate(value,this.baseline,this.data);this.save();this.config=clone(value);}
  }
  return {clone,stable,geometry,protectedSlots,immutable,validate,slotsBetween,slotAt,moveSlots,pngDimensions,expectedAsset,Project};
});
