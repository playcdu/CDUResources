"""Artist tooling regressions. Aseprite subprocess output is simulated, never claimed as a real export."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
import artist

class ArtistTools(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        (self.root/'manifests').mkdir()
        (self.root/'artwork').mkdir()
        self.write('artist-projects.json',{'schemaVersion':1,'projects':[]})
        self.write('artist-exports.json',{'schemaVersion':1,'projects':{}})
    def tearDown(self): self.temp.cleanup()
    def write(self,name,value): (self.root/'manifests'/name).write_text(json.dumps(value),encoding='utf-8')
    def fixture(self):
        raw=bytearray(128);struct.pack_into('<IHHHH',raw,0,128,0xA5E0,2,36,18)
        (self.root/'artwork/button.aseprite').write_bytes(raw)
        project={'id':'button','source':'artwork/button.aseprite','canvas':{'width':36,'height':18},'outputs':[{'frame':0,'tag':'normal','asset':'assets/quasar_gui/textures/buttons/test/button/normal.png'},{'frame':1,'tag':'selected','asset':'assets/quasar_gui/textures/buttons/test/button/selected.png'}]}
        self.write('artist-projects.json',{'schemaVersion':1,'projects':[project]})
        return project
    def export(self,project=None,run=None):
        with patch.object(artist,'locate_aseprite',return_value='unit-test-aseprite'),patch.object(artist.subprocess,'run',side_effect=run or self.simulate_export):
            artist.export_projects(self.root)
    def simulate_export(self,command,**kwargs):
        self.assertEqual(command[1],'--batch');self.assertIn('--frame-range',command)
        self.assertEqual(command[-2],'--save-as')
        self.assertFalse(any(flag in command for flag in ('--scale','--trim','--crop','--script')))
        Image.new('RGBA',(36,18),(30,80,120,255)).save(command[-1])
    def test_png_only_needs_no_aseprite(self):
        with patch.object(artist,'locate_aseprite',side_effect=AssertionError('should not execute')):
            self.assertEqual(artist.export_projects(self.root),0)
    def test_new_project_exports_all_indexed_frames_and_source_stays_unchanged(self):
        p=self.fixture();before=(self.root/p['source']).read_bytes();self.export(p)
        self.assertEqual(artist.verify_exports(self.root),1);self.assertEqual((self.root/p['source']).read_bytes(),before)
        with patch.object(artist,'locate_aseprite',side_effect=AssertionError('current receipts need no binary')):artist.export_projects(self.root)
    def test_source_change_rejects_stale_receipt(self):
        p=self.fixture();self.export(p);source=self.root/p['source'];source.write_bytes(source.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'Stale'):artist.verify_exports(self.root)
    def test_mapping_change_rejects_stale_receipt(self):
        p=self.fixture();self.export(p);p['outputs'][0]['frame']=1;self.write('artist-projects.json',{'schemaVersion':1,'projects':[p]})
        with self.assertRaisesRegex(ValueError,'Stale'):artist.verify_exports(self.root)
    def test_independent_png_edit_is_preserved(self):
        p=self.fixture();self.export(p);png=self.root/'pack-source'/p['outputs'][0]['asset'];Image.new('RGBA',(36,18),'red').save(png);before=png.read_bytes()
        with self.assertRaisesRegex(ValueError,'PNG changed independently'):artist.export_projects(self.root)
        self.assertEqual(png.read_bytes(),before)
    def test_invalid_png_edit_is_also_preserved(self):
        p=self.fixture();self.export(p);png=self.root/'pack-source'/p['outputs'][0]['asset'];Image.new('RGBA',(1,1),'red').save(png);before=png.read_bytes()
        with self.assertRaisesRegex(ValueError,'PNG changed independently'):artist.export_projects(self.root)
        self.assertEqual(png.read_bytes(),before)
    def test_failed_frame_preflight_does_not_replace_any_png(self):
        p=self.fixture();self.export(p);paths=[self.root/'pack-source'/o['asset'] for o in p['outputs']];before=[x.read_bytes() for x in paths];source=self.root/p['source'];source.write_bytes(source.read_bytes()+b'new')
        counter=[0]
        def bad(command,**kwargs):
            counter[0]+=1;Image.new('RGBA',(36,18) if counter[0]==1 else (1,1),'green').save(command[-1])
        with self.assertRaisesRegex(ValueError,'canvas'):self.export(p,bad)
        self.assertEqual([x.read_bytes() for x in paths],before)
    def test_source_change_during_export_rejects_output(self):
        p=self.fixture()
        def changing(command,**kwargs):
            self.simulate_export(command,**kwargs);source=self.root/p['source'];source.write_bytes(source.read_bytes()+b'x')
        with self.assertRaisesRegex(ValueError,'changed during'):self.export(p,changing)
        self.assertFalse((self.root/'pack-source'/p['outputs'][0]['asset']).exists())
    def test_canvas_frame_and_source_header_guards(self):
        p=self.fixture();self.assertEqual(artist.aseprite_header(self.root/p['source']),(2,36,18));p['outputs'][0]['frame']=2;self.write('artist-projects.json',{'schemaVersion':1,'projects':[p]})
        with self.assertRaisesRegex(ValueError,'frame is outside'):self.export(p)
        p['outputs'][0]['frame']=0;p['canvas']['width']=37;self.write('artist-projects.json',{'schemaVersion':1,'projects':[p]})
        with self.assertRaisesRegex(ValueError,'canvas differs'):self.export(p)
    def test_paths_and_duplicate_outputs_rejected(self):
        for value in ('../escape','/absolute','C:/other','a\\b'):
            with self.assertRaises(ValueError):artist.safe_path(self.root,value)
        p=self.fixture();p['outputs'].append(p['outputs'][0]);self.write('artist-projects.json',{'schemaVersion':1,'projects':[p]})
        with self.assertRaisesRegex(ValueError,'Duplicate'):artist.load_projects(self.root)
    def preview(self,content=b'unit-test-pack'):
        output=self.root/'deliverables';output.mkdir(exist_ok=True);(output/'quasar-gui.zip').write_bytes(content)
        sha=hashlib.sha1(content).hexdigest();(output/f'quasar-gui-layouts-{sha}.json').write_text(json.dumps({'schemaVersion':1,'packSha1':sha,'registry':{'skins':{}}}))
        profile=self.root/'minecraft';profile.mkdir(exist_ok=True);return profile
    def test_explicit_preview_install_and_owned_repeat_leave_options_unchanged(self):
        profile=self.preview();(profile/'options.txt').write_text('unchanged');artist.install_preview(profile,self.root)
        self.preview(b'new-pack');artist.install_preview(profile,self.root)
        self.assertEqual((profile/'options.txt').read_text(),'unchanged');self.assertEqual((profile/'resourcepacks/quasar-gui-artist-preview.zip').read_bytes(),b'new-pack')
    def test_unowned_or_changed_preview_files_are_never_overwritten(self):
        profile=self.preview();dest=profile/'resourcepacks/quasar-gui-artist-preview.zip';dest.parent.mkdir();dest.write_bytes(b'my-pack')
        with self.assertRaisesRegex(ValueError,'unowned'):artist.install_preview(profile,self.root)
        self.assertEqual(dest.read_bytes(),b'my-pack');self.assertFalse((profile/'config/invdebug-layouts/current.json').exists())
        dest.unlink();artist.install_preview(profile,self.root);current=profile/'config/invdebug-layouts/current.json';current.write_text('operator edit')
        self.preview(b'new');before=dest.read_bytes()
        with self.assertRaisesRegex(ValueError,'independently changed'):artist.install_preview(profile,self.root)
        self.assertEqual(dest.read_bytes(),before)
    def test_preview_hash_mismatch_rejected(self):
        profile=self.preview();sidecar=next((self.root/'deliverables').glob('quasar-gui-layouts-*.json'));sidecar.write_text(json.dumps({'schemaVersion':1,'packSha1':'wrong','registry':{}}))
        with self.assertRaisesRegex(ValueError,'hash'):artist.install_preview(profile,self.root)
    def test_receipt_directory_rejected_before_either_artifact_is_copied(self):
        profile=self.preview();(profile/'config/invdebug-layouts/artist-install.json').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError,'regular file'):artist.install_preview(profile,self.root)
        self.assertFalse((profile/'resourcepacks/quasar-gui-artist-preview.zip').exists())
        self.assertFalse((profile/'config/invdebug-layouts/current.json').exists())
    def test_explicit_aseprite_executable_discovery(self):
        executable=self.root/'Aseprite.exe';executable.write_bytes(b'not executable; path discovery only')
        self.assertEqual(artist.locate_aseprite(str(executable)),str(executable.resolve()))

if __name__=='__main__':unittest.main(verbosity=2)
