import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import branch_publish as publish


def fixture(extra=None):
    files = {'pack.mcmeta': publish.encoded({'pack': {'pack_format': 15, 'supported_formats': [9, 34], 'description': 'Test'}}),
             'assets/minecraft/models/item/paper.json': b'{}', 'assets/quasar_gui/font/menu.json': b'{"providers": []}',
             'assets/quasar_gui/textures/test.png': b'unchanged-art', **(extra or {})}
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        for name, data in files.items():
            info = zipfile.ZipInfo(name)
            info.filename = name  # Preserve deliberately unsafe backslashes on Windows too.
            archive.writestr(info, data)
    raw = output.getvalue()
    layout = publish.encoded({'schemaVersion': 1, 'packSha1': hashlib.sha1(raw).hexdigest(), 'skins': {}})
    return raw, layout


class BranchPublisherTests(unittest.TestCase):
    def test_variant_is_deterministic_preserves_art_and_rebinds_layout(self):
        raw, layout = fixture()
        result, sidecar = publish.variant_26(raw, layout)
        self.assertEqual((result, sidecar), publish.variant_26(raw, layout))
        original = publish.validate_zip(raw, 'legacy')
        converted, binding = publish.validate_pair(result, sidecar, '26.1.2')
        for name in ('assets/quasar_gui/font/menu.json', 'assets/quasar_gui/textures/test.png'):
            self.assertEqual(original[name], converted[name])
        self.assertEqual(binding['packSha1'], hashlib.sha1(result).hexdigest())
        self.assertNotEqual(binding['packSha1'], hashlib.sha1(raw).hexdigest())

    def test_rejects_zip_traversal_scripts_and_wrong_sidecar(self):
        for path in ('../escape.png', '/absolute.json', 'assets/a\\b.json', 'assets/evil.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                publish.validate_pair(*fixture({path: b'x'}), 'legacy')
        raw, _ = fixture()
        with self.assertRaises(ValueError):
            publish.validate_pair(raw, b'{"schemaVersion":1,"skins":{},"packSha1":"bad"}', 'legacy')

    def test_failed_build_keeps_last_good_release_and_reports_failure(self):
        old = {'name': 'art/cozy', 'head': 'a'*40, 'published_commit': 'a'*40, 'releases': [{'sha1': 'b'*40}, {'sha1': 'c'*40}]}
        sent = []
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'plan.json'
            publish.write_json(path, {'branches': [{'name': 'art/cozy', 'head': 'd'*40, 'needs_build': True, 'id': 'missing'}]})
            with patch.object(publish, 'catalog', return_value={'branches': [old]}), \
                 patch.object(publish, 'github_branches', return_value=[{'name': 'art/cozy', 'head': 'd'*40}]), \
                 patch.object(publish, 'oidc_token', return_value='test'), \
                 patch.object(publish, 'request', side_effect=lambda url, data, headers: sent.append(json.loads(data)) or {'branches': []}):
                with self.assertRaises(SystemExit): publish.publish(path, Path(folder))
        row = sent[0]['branches'][0]
        self.assertEqual(row['status'], 'failed')
        self.assertEqual(row['published_commit'], 'a'*40)
        self.assertEqual(row['releases'], ['b'*40, 'c'*40])

    def test_superseded_build_is_pending_and_deleted_branch_is_removed(self):
        sent = []
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'plan.json'
            publish.write_json(path, {'branches': [{'name': 'art/cozy', 'head': 'a'*40, 'needs_build': True, 'id': 'old'},
                                                  {'name': 'deleted', 'head': 'b'*40, 'needs_build': True, 'id': 'deleted'}]})
            with patch.object(publish, 'catalog', return_value={'branches': []}), \
                 patch.object(publish, 'github_branches', return_value=[{'name': 'art/cozy', 'head': 'c'*40}]), \
                 patch.object(publish, 'oidc_token', return_value='test'), \
                 patch.object(publish, 'request', side_effect=lambda url, data, headers: sent.append(json.loads(data)) or {'branches': []}):
                publish.publish(path, Path(folder))
        self.assertEqual(len(sent[0]['branches']), 1)
        self.assertEqual(sent[0]['branches'][0]['status'], 'pending')


if __name__ == '__main__': unittest.main()
