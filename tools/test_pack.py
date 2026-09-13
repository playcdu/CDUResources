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
import button_assets

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
                if 'visibleContentSlots' in skin:
                    self.assertEqual(live,set(skin['visibleContentSlots'])|set(skin['paintedControlSlots']))
                else:
                    expected=(set(controls[key]['live_slots_union'])&top)-decor
                    self.assertEqual(live,expected)

    def test_button_regions_frames_and_real_content(self):
        config=read_json(ROOT/'manifests/button-layouts.json');runtime=read_json(ROOT/'manifests/runtime-registry.json')
        seen=set()
        for key,screen in config['screens'].items():
            skin=self.skins[key];g=self.layouts[skin['layout']];regions=runtime['skins'][key]['buttonRegions']
            self.assertEqual(set(screen['contentSlots']),set(skin['visibleContentSlots']))
            for b,r in zip(screen['buttons'],regions):
                self.assertEqual(r['slots'],b['slots']);self.assertEqual(r['sourceSlot'],b['sourceSlot'])
                self.assertEqual(set(r['states']),set(button_assets.STATES))
                x,y,w,h=button_assets.geometry(g,b)
                for state,f in r['states'].items():
                    self.assertNotIn(f['glyph'],seen);seen.add(f['glyph'])
                    self.assertEqual(g['titleAnchor'][0]+sum(ADVANCES[c] for c in f['prefix']),x)
                    self.assertEqual(sum(ADVANCES[c] for c in f['prefix']+f['suffix'])+f['advance'],0)
                    self.assertEqual(6+7-f['ascent'],y)
                    button_assets.validate_button((ROOT/'pack-source'/f['asset']).read_bytes(),g,skin,b,state)
        self.assertEqual(len(self.skins['trade_idle']['visibleContentSlots']),40)
        self.assertEqual(self.skins['auction_confirm']['visibleContentSlots'],[20])

    def test_carrier_exact_threshold_ranges_and_normal_paper(self):
        with zipfile.ZipFile(io.BytesIO(self.raw)) as z:
            model=json.loads(z.read(button_assets.PAPER_MODEL))
            def resolve(value):
                chosen='vanilla paper'
                for override in model['overrides']:
                    if value>=override['predicate']['custom_model_data']:chosen=override['model']
                return chosen
            self.assertEqual(resolve(0),'vanilla paper')
            for value in [1,194731]:self.assertEqual(resolve(value),'quasar_gui:item/button_carrier')
            for value in [2,37,194730,194732,200000]:self.assertEqual(resolve(value),'quasar_gui:item/paper_default')
            self.assertEqual(json.loads(z.read('assets/quasar_gui/models/item/button_carrier.json'))['elements'],[])
            self.assertNotIn('overrides',json.loads(z.read('assets/quasar_gui/models/item/paper_default.json')))

    def test_reject_paper_exception_drift_and_extra_minecraft_paths(self):
        with zipfile.ZipFile(io.BytesIO(self.raw)) as z:files={n:z.read(n) for n in z.namelist()}
        model=json.loads(files[button_assets.PAPER_MODEL]);model['overrides'][2]['predicate']['custom_model_data']=194730
        files[button_assets.PAPER_MODEL]=json.dumps(model).encode()
        with self.assertRaisesRegex(ValueError,'carrier'):validate_pack(zip_bytes(files),self.layouts,self.skins)
        files[button_assets.PAPER_MODEL]=json.dumps(button_assets.MODELS[button_assets.PAPER_MODEL]).encode()
        files['assets/minecraft/models/item/stone.json']=b'{}'
        with self.assertRaisesRegex(ValueError,'Unexpected'):validate_pack(zip_bytes(files),self.layouts,self.skins)

    def test_reject_unreviewed_metadata_fields(self):
        with zipfile.ZipFile(io.BytesIO(self.raw)) as z:files={n:z.read(n) for n in z.namelist()}
        meta=json.loads(files['pack.mcmeta']);meta['filter']={'block':[{'namespace':'minecraft'}]}
        files['pack.mcmeta']=json.dumps(meta).encode()
        with self.assertRaisesRegex(ValueError,'metadata'):validate_pack(zip_bytes(files),self.layouts,self.skins)

    def test_merge_rejects_paper_override_and_overlay(self):
        for name,path in [('paper-conflict.zip',button_assets.PAPER_MODEL),('paper-overlay.zip','v34/'+button_assets.PAPER_MODEL)]:
            op=self.operator_pack(name,{path:b'{}'})
            with self.assertRaisesRegex(ValueError,'conflict'):merge(op,ROOT/'deliverables/quasar-gui.zip',self.new_output(name+'-merged.zip'))

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
