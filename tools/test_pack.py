#!/usr/bin/env python3
"""Meaningful static pack checks and a texture-only replacement/merge exercise."""
import contextlib
import hashlib
import io
import json
import shutil
import unittest
import zipfile
from pathlib import Path
from PIL import Image
from build_pack import ROOT, ADVANCES, build, read_json, registry, space, validate_pack, validate_png, zip_bytes
from merge_pack import merge

class PackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layouts=read_json(ROOT/'manifests/layouts.json')['layouts']
        cls.skins=read_json(ROOT/'manifests/skins.json')['skins']
        cls.raw=(ROOT/'deliverables/quasar-gui.zip').read_bytes()
        cls.out=ROOT/'evidence/pack-tests';cls.out.mkdir(parents=True,exist_ok=True)

    def test_pack_contract(self):
        report=validate_pack(self.raw,self.layouts,self.skins)
        self.assertEqual(report['skinCount'],len(self.skins))

    def test_menu_coverage_and_geometry(self):
        screens=read_json(ROOT/'manifests/menu-coverage.json')['screens']
        for screen in screens:
            skin=self.skins[screen['skin_key']];g=self.layouts[skin['layout']]
            self.assertEqual(g['menuType'],screen['container_type'])
            self.assertEqual(skin['asset'],screen['asset_path'])
            self.assertEqual(skin['slotRoles'],screen['slot_roles'])
        for rows in range(1,7):self.assertIn(f'template_chest_{rows}',self.skins)
        self.assertEqual(len(self.layouts['dispenser']['slots']),9)
        self.assertEqual(len(self.layouts['crafting']['slots']),10)
        for g in self.layouts.values():
            self.assertEqual(len(g['playerSlots']),36)
            ids=[s['index'] for s in g['slots']+g['playerSlots']]
            self.assertEqual(len(ids),len(set(ids)))
            for s in g['slots']+g['playerSlots']:
                self.assertTrue(2<=s['x']<=g['width']-18)
                self.assertTrue(2<=s['y']<=g['height']-18)

    def test_spacing_and_title_origin(self):
        r=registry(self.layouts,self.skins)
        for i in range(-511,512):self.assertEqual(sum(ADVANCES[c] for c in space(i)),i)
        for key,s in r['skins'].items():
            g=self.layouts[s['geometry']];anchor=g['titleAnchor'][0]
            self.assertEqual(anchor+sum(ADVANCES[c] for c in s['prefix']),0)
            self.assertEqual(sum(ADVANCES[c] for c in s['prefix']+s['suffix'])+s['advance'],0)
            self.assertEqual(g['titleAnchor'][1]+7-g['ascent'],0)
        self.assertEqual((176-160)//2,8)

    def test_live_slot_mask_authority(self):
        controls={s['skin_key']:s for s in read_json(ROOT/'manifests/control-map.json')['screens']}
        for key,skin in self.skins.items():
            g=self.layouts[skin['layout']];top={p['index'] for p in g['slots']}
            live=set(skin['liveSlots']);static=set(skin['staticProtectedSlots']);decor=set(skin['removedDecorations'])
            self.assertEqual(live|static|decor,top)
            self.assertFalse(live&static or live&decor or static&decor)
            if key in controls:
                expected=(set(controls[key]['live_slots_union'])&top)-decor
                self.assertEqual(live,expected)

    def test_zip_determinism_and_hash(self):
        with contextlib.redirect_stdout(io.StringIO()):
            first,_=build(output=self.out/'determinism-a.zip',kit=False)
            second,_=build(output=self.out/'determinism-b.zip',kit=False)
        self.assertEqual(first,second)
        self.assertEqual(first,self.raw)
        self.assertEqual(hashlib.sha1(first).hexdigest(),(ROOT/'deliverables/quasar-gui.zip.sha1').read_text().strip())

    def test_texture_only_replacement(self):
        skin=self.skins['auction_house'];g=self.layouts[skin['layout']]
        source=ROOT/'pack-source'/skin['asset'];before=source.read_bytes()
        override=self.out/'overrides'/skin['asset'];override.parent.mkdir(parents=True,exist_ok=True)
        image=Image.open(source).convert('RGBA');image.putpixel((3,4),(178,91,153,255));image.save(override)
        before_override=override.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):changed,report=build(self.out/'overrides',self.out/'texture-only-r2.zip',kit=False)
        self.assertNotEqual(changed,self.raw);self.assertEqual(source.read_bytes(),before)
        self.assertEqual(override.read_bytes(),before_override)
        with zipfile.ZipFile(io.BytesIO(self.raw)) as a,zipfile.ZipFile(io.BytesIO(changed)) as b:
            changed_names=[n for n in a.namelist() if a.read(n)!=b.read(n)]
            self.assertEqual(changed_names,[skin['asset']])
        (self.out/'texture-only-exercise.json').write_text(json.dumps(dict(status='passed-static',
            changedFiles=changed_names,oldSha1=hashlib.sha1(self.raw).hexdigest(),newSha1=report['sha1'],
            javaChanged=False,fontProvidersChanged=False,canonicalSourcePreserved=True,overridesPreserved=True),indent=2)+'\n')

    def test_reject_opaque_item_well(self):
        s=self.skins['auction_house'];g=self.layouts[s['layout']]
        image=Image.open(ROOT/'pack-source'/s['asset']).convert('RGBA');image.putpixel((8,18),(255,0,0,255))
        b=io.BytesIO();image.save(b,format='PNG')
        with self.assertRaisesRegex(ValueError,'interaction'):validate_png(b.getvalue(),g,s,'bad')

    def test_reject_changed_advance_pin(self):
        s=self.skins['auction_house'];g=self.layouts[s['layout']]
        image=Image.open(ROOT/'pack-source'/s['asset']).convert('RGBA');image.putpixel((175,0),(0,0,0,0))
        b=io.BytesIO();image.save(b,format='PNG')
        with self.assertRaisesRegex(ValueError,'advance pin'):validate_png(b.getvalue(),g,s,'bad')

    def test_reject_provider_drift(self):
        with zipfile.ZipFile(io.BytesIO(self.raw)) as z:files={n:z.read(n) for n in z.namelist()}
        p=json.loads(files['assets/quasar_gui/font/menu.json']);p['providers'][1]['ascent']=12
        files['assets/quasar_gui/font/menu.json']=json.dumps(p).encode()
        with self.assertRaisesRegex(ValueError,'metric'):validate_pack(zip_bytes(files),self.layouts,self.skins)

    def operator_pack(self,name,extra=None,meta=None):
        files={'pack.mcmeta':json.dumps(meta or {'pack':{'pack_format':9,'description':'Operator fixture'}}).encode(),
               'assets/example/lang/en_us.json':b'{"sample":"Operator fixture"}'}
        files.update(extra or {});path=self.out/name;path.write_bytes(zip_bytes(files));return path

    def new_output(self,name):
        path=self.out/name
        if path.exists():path.unlink()  # exact test fixture under this workspace
        return path

    def test_merge_preserves_operator_metadata_and_hash(self):
        op=self.operator_pack('operator.zip');out=self.new_output('merged.zip')
        report=merge(op,ROOT/'deliverables/quasar-gui.zip',out)
        with zipfile.ZipFile(op) as a,zipfile.ZipFile(out) as b:
            self.assertEqual(json.loads(a.read('pack.mcmeta')),json.loads(b.read('pack.mcmeta')))
            self.assertEqual(a.read('assets/example/lang/en_us.json'),b.read('assets/example/lang/en_us.json'))
        self.assertEqual(report['sha1'],hashlib.sha1(out.read_bytes()).hexdigest())
        second=self.new_output('merged-repeat.zip');merge(op,ROOT/'deliverables/quasar-gui.zip',second)
        self.assertEqual(out.read_bytes(),second.read_bytes())

    def test_merge_rejects_path_collision(self):
        op=self.operator_pack('conflict.zip',{'assets/quasar_gui/font/menu.json':b'{}'})
        with self.assertRaisesRegex(ValueError,'conflicts'):merge(op,ROOT/'deliverables/quasar-gui.zip',self.new_output('bad-merge.zip'))

    def test_merge_rejects_overlay_override(self):
        op=self.operator_pack('overlay.zip',{'v34/assets/quasar_gui/font/menu.json':b'{}'})
        with self.assertRaisesRegex(ValueError,'overlay'):merge(op,ROOT/'deliverables/quasar-gui.zip',self.new_output('bad-overlay.zip'))

    def test_merge_rejects_filter(self):
        op=self.operator_pack('filter.zip',meta={'pack':{'pack_format':9,'description':'Fixture'},'filter':{'block':[{'namespace':'.*'}]}})
        with self.assertRaisesRegex(ValueError,'filter'):merge(op,ROOT/'deliverables/quasar-gui.zip',self.new_output('bad-filter.zip'))

    def test_merge_never_overwrites(self):
        op=self.operator_pack('no-overwrite.zip')
        with self.assertRaises(ValueError):merge(op,ROOT/'deliverables/quasar-gui.zip',op)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PackTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    out=ROOT/'evidence/pack-tests';out.mkdir(parents=True,exist_ok=True)
    (out/'test-results.json').write_text(json.dumps(dict(testsRun=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        staticValidation='passed' if result.wasSuccessful() else 'failed',actualClientLoading='untested',actualClientInteraction='untested'),indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
