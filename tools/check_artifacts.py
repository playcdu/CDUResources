"""Build and verify the same portable resource-pack artifacts locally and in CI."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import platform
import subprocess
import sys
from pathlib import Path

import PIL

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ("quasar-gui.zip", "quasar-gui-artist-kit.zip")


def run(script):
    subprocess.run([sys.executable, str(ROOT / "tools" / script)], cwd=ROOT, check=True)


def checksums():
    result = {}
    sha1=(ROOT/'deliverables/quasar-gui.zip.sha1').read_text().strip()
    for name in ARTIFACTS+('quasar-gui-layouts-'+sha1+'.json',):
        raw = (ROOT / "deliverables" / name).read_bytes()
        result[name] = {"bytes": len(raw), "sha1": hashlib.sha1(raw).hexdigest(),
                        "sha256": hashlib.sha256(raw).hexdigest()}
    return result


def main():
    evidence = ROOT / "evidence"
    evidence.mkdir(exist_ok=True)
    report = {"status": "running", "python": platform.python_version(), "pillow": PIL.__version__,
              "clientRendering": "not_tested", "gameplay": "not_tested",
              "productStatus": "implemented_pending_client_validation"}
    try:
        expected_python = (ROOT / ".python-version").read_text().strip()
        expected_pillow = (ROOT / "requirements.txt").read_text().strip().split("==")[1]
        python_ok=platform.python_version()==expected_python if os.environ.get('CI') else sys.version_info[:2]==(3,12)
        if not python_ok or PIL.__version__ != expected_pillow:
            raise RuntimeError(f"Use Python 3.12 locally ({expected_python} in CI) and Pillow {expected_pillow}")
        if (ROOT/'tools/artist.py').is_file():
            subprocess.run([sys.executable,str(ROOT/'tools/artist.py'),'verify-exports'],cwd=ROOT,check=True)
            run('test_artist.py')
            report['artistToolTests']='passed'
        node=shutil.which('node')
        if node:
            subprocess.run([node,str(ROOT/'tools/test_layout_model.cjs')],cwd=ROOT,check=True)
            report['layoutModelTests']='passed'
        elif os.environ.get('CI'):
            raise RuntimeError('CI requires Node for the layout model regression tests')
        else:
            report['layoutModelTests']='not run locally; Node unavailable; required in CI'
        run("build_pack.py")
        run("test_pack.py")
        tests = json.loads((evidence / "pack-tests/test-results.json").read_text())
        if tests["testsRun"] < 14 or tests["failures"] or tests["errors"]:
            raise RuntimeError("Foundation pack tests did not all pass")
        # Tests create evidence included in the kit. Both compared builds include it.
        run("build_pack.py")
        first = checksums()
        run("build_pack.py")
        second = checksums()
        if first != second:
            raise RuntimeError("Repeated resource pack or artist kit builds differ")
        run("verify_artist_handoff.py")
        report.update(status="passed", testsRun=tests["testsRun"],
                      packAndArtistKitByteDeterministic=True, standaloneHandoffAndOverrideGuide=True,
                      artifacts=second)
        (ROOT / "deliverables/checksums.json").write_text(json.dumps(second, indent=2) + "\n", encoding="utf-8")
    except Exception as error:
        report.update(status="failed", error=str(error))
        raise
    finally:
        (evidence / "ci-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
