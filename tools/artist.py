"""Repository-local Aseprite export, PNG freshness checks, and artist entry points."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import sys
import tempfile
import venv
import webbrowser

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(root, value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("Use a repository-relative forward-slash path")
    parts = PurePosixPath(value)
    if parts.is_absolute() or ".." in parts.parts:
        raise ValueError("Path escapes repository: " + value)
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Path escapes repository: " + value)
    return path


def project_signature(project):
    return digest(json.dumps(project, sort_keys=True, separators=(",", ":")).encode())


def load_projects(root=ROOT):
    manifest = read_json(root / "manifests/artist-projects.json")
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("projects"), list):
        raise ValueError("Unsupported artist-projects schema")
    seen_ids, seen_outputs = set(), set()
    for project in manifest["projects"]:
        name = project["id"]
        if not isinstance(name, str) or not name or name in seen_ids:
            raise ValueError("Project ids must be nonempty and unique")
        seen_ids.add(name)
        source = safe_path(root, project["source"])
        if source.suffix.lower() not in (".aseprite", ".ase") or not source.is_file():
            raise ValueError("Missing Aseprite source: " + project["source"])
        canvas = project["canvas"]
        if any(type(canvas.get(k)) is not int or not 1 <= canvas[k] <= 4096 for k in ("width", "height")):
            raise ValueError("Canvas dimensions must be integers from 1 to 4096")
        if not isinstance(project.get("outputs"), list) or not project["outputs"]:
            raise ValueError("Every registered project needs frame outputs")
        for output in project["outputs"]:
            if type(output.get("frame")) is not int or output["frame"] < 0:
                raise ValueError("Frame indices start at zero")
            asset = output["asset"]
            if not isinstance(asset, str) or not asset.startswith("assets/quasar_gui/textures/") or not asset.endswith(".png"):
                raise ValueError("Exports must target Quasar PNG assets")
            safe_path(root, "pack-source/" + asset)
            if asset in seen_outputs:
                raise ValueError("Duplicate output asset: " + asset)
            seen_outputs.add(asset)
    return manifest["projects"]


def aseprite_header(path):
    """Read only the documented binary header: dimensions and frame count."""
    raw = path.read_bytes()
    if len(raw) < 128 or struct.unpack_from("<H", raw, 4)[0] != 0xA5E0:
        raise ValueError("Invalid Aseprite file header: " + str(path))
    frames, width, height = struct.unpack_from("<HHH", raw, 6)
    return frames, width, height


def locate_aseprite(explicit=None):
    candidates = [explicit, os.environ.get("ASEPRITE_EXE"), shutil.which("aseprite"), shutil.which("aseprite.exe")]
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            candidates.extend([str(Path(base) / "Aseprite/Aseprite.exe"),
                               str(Path(base) / "Steam/steamapps/common/Aseprite/Aseprite.exe")])
    candidates.extend([str(Path.home() / "scoop/apps/aseprite/current/aseprite.exe"),
                       "D:/SteamLibrary/steamapps/common/Aseprite/Aseprite.exe",
                       "/Applications/Aseprite.app/Contents/MacOS/aseprite"])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    return None


def png_check(path, canvas):
    from PIL import Image
    with Image.open(path) as image:
        if image.format != "PNG" or image.mode != "RGBA" or image.size != (canvas["width"], canvas["height"]):
            raise ValueError("Export must be an RGBA PNG with unchanged canvas dimensions: " + str(path))


def receipt_entry(project, root=ROOT):
    outputs = {}
    for output in project["outputs"]:
        path = safe_path(root, "pack-source/" + output["asset"])
        png_check(path, project["canvas"])
        outputs[output["asset"]] = {"frame": output["frame"], "sha256": digest(path.read_bytes())}
    return {"source": project["source"], "source_sha256": digest(safe_path(root, project["source"]).read_bytes()),
            "mapping_sha256": project_signature(project), "outputs": outputs}


def verify_exports(root=ROOT):
    projects = load_projects(root)
    receipts_path = root / "manifests/artist-exports.json"
    receipts = read_json(receipts_path) if receipts_path.is_file() else {"schemaVersion": 1, "projects": {}}
    if receipts.get("schemaVersion") != 1:
        raise ValueError("Unsupported artist export receipt schema")
    for project in projects:
        expected = receipt_entry(project, root)
        if receipts.get("projects", {}).get(project["id"]) != expected:
            raise ValueError("Stale or missing PNG export for " + project["id"] + ". Export its Aseprite source locally and commit source, PNGs and artist-exports.json together.")
    print(f"PASS: {len(projects)} registered Aseprite projects match committed PNG export receipts")
    return len(projects)


def export_projects(root=ROOT, executable=None, force=False):
    projects = load_projects(root)
    receipt_path = root / "manifests/artist-exports.json"
    old = read_json(receipt_path) if receipt_path.exists() else {"schemaVersion": 1, "projects": {}}
    pending = []
    for project in projects:
        prior = old.get("projects", {}).get(project["id"])
        try:
            current = receipt_entry(project, root)
        except (FileNotFoundError, ValueError):
            current = None
        if current is not None and current == prior and not force:
            continue
        # An independently edited PNG is valuable: never silently replace it.
        if prior and digest(safe_path(root, project["source"]).read_bytes()) == prior.get("source_sha256") and project_signature(project) == prior.get("mapping_sha256") and not force:
            raise ValueError("PNG changed independently for " + project["id"] + ". Preserve that edit, unregister it for PNG-only work, or explicitly use export --force.")
        pending.append(project)
    if not pending:
        return verify_exports(root)
    executable = locate_aseprite(executable)
    if not executable:
        raise ValueError("Aseprite export is needed. Install your own Aseprite copy and set ASEPRITE_EXE, or export registered PNGs on a workstation with Aseprite. CI uses committed PNGs.")
    exports_dir = root / ".cache/aseprite-export"
    exports_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=exports_dir, prefix="frames-") as temporary:
        staged = []
        for project in pending:
            source = safe_path(root, project["source"])
            frames, width, height = aseprite_header(source)
            if (width, height) != (project["canvas"]["width"], project["canvas"]["height"]):
                raise ValueError("Aseprite canvas differs from declared dimensions: " + project["id"])
            source_hash = digest(source.read_bytes())
            for i, output in enumerate(project["outputs"]):
                frame = output["frame"]
                if frame >= frames:
                    raise ValueError("Requested frame is outside the Aseprite source: " + project["id"])
                destination = Path(temporary) / f"asset-{len(staged):04d}-frame.png"
                # A single frame, no crop, trim, scale, scripts or source save operation.
                command = [executable, "--batch", str(source), "--frame-range", f"{frame},{frame}",
                           "--color-mode", "rgb", "--save-as", str(destination)]
                subprocess.run(command, check=True, cwd=root)
                if not destination.is_file():
                    matches = list(Path(temporary).glob(destination.stem + "*.png"))
                    if len(matches) != 1:
                        raise ValueError("Aseprite did not produce exactly one selected frame")
                    destination = matches[0]
                from PIL import Image
                with Image.open(destination) as image:
                    if image.format != "PNG" or image.size != (width, height):
                        raise ValueError("Aseprite changed the export canvas")
                    rgba = image.convert("RGBA")
                rgba.save(destination, format="PNG", compress_level=9, optimize=False)
                png_check(destination, project["canvas"])
                staged.append((destination, safe_path(root, "pack-source/" + output["asset"])))
            if digest(source.read_bytes()) != source_hash:
                raise ValueError("Aseprite source changed during export; retry after saving")
        # All frames validate before any generated PNG is replaced; source documents are untouched.
        for source, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    receipts = {"schemaVersion": 1, "projects": {p["id"]: receipt_entry(p, root) for p in projects}}
    receipt_path.write_text(json.dumps(receipts, indent=2) + "\n", encoding="utf-8", newline="\n")
    return verify_exports(root)


def setup(root=ROOT):
    expected = (root / ".python-version").read_text().strip()
    actual = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[:2] != (3, 12):
        raise ValueError(f"Artist tools require Python 3.12; found {actual}. CI pins {expected}. Set PYTHON_EXE to Python 3.12 and run Setup Artist Tools.cmd again.")
    environment = root / ".venv"
    if environment.is_symlink() or not environment.resolve().is_relative_to(root.resolve()):
        raise ValueError("The repository environment must not be an external symlink")
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if python.is_file():
        subprocess.run([str(python), "-c", "import sys; assert sys.version_info[:2] == (3, 12), 'Repository environment must use Python 3.12'"], check=True)
    else:
        venv.EnvBuilder(with_pip=True).create(environment)
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")], check=True, cwd=root)
    print("Artist tools are installed only in " + str(environment))
    print("Aseprite: " + (locate_aseprite() or "not found; PNG-only work is available"))


def build(root=ROOT):
    export_projects(root)  # No Aseprite is needed when sources/receipts are already current.
    subprocess.run([sys.executable, str(root / "tools/check_artifacts.py")], check=True, cwd=root)
    if (root / "tools/build_artist_editor.py").is_file():
        subprocess.run([sys.executable, str(root / "tools/build_artist_editor.py")], check=True, cwd=root)
    print("Ready pack and artist kit: " + str(root / "deliverables"))


def install_preview(profile, root=ROOT):
    """Copy only this tool's dedicated preview artifacts into an explicitly chosen profile."""
    profile = Path(profile).expanduser().resolve()
    if not profile.is_dir():
        raise ValueError("--minecraft must name an existing Minecraft instance directory")
    pack = root / "deliverables/quasar-gui.zip"
    pack_bytes = pack.read_bytes()
    pack_sha1 = hashlib.sha1(pack_bytes).hexdigest()
    sidecar = root / f"deliverables/quasar-gui-layouts-{pack_sha1}.json"
    envelope = read_json(sidecar)
    if envelope.get("schemaVersion") != 1 or envelope.get("packSha1") != pack_sha1 or not isinstance(envelope.get("registry"), dict):
        raise ValueError("Built layout sidecar does not match the pack hash")
    outputs = {"resourcepacks/quasar-gui-artist-preview.zip": pack_bytes,
               "config/invdebug-layouts/current.json": sidecar.read_bytes()}
    receipt_path = safe_path(profile, "config/invdebug-layouts/artist-install.json")
    if receipt_path.exists() and not receipt_path.is_file():
        raise ValueError("Preview ownership receipt path must be a regular file")
    receipt = read_json(receipt_path) if receipt_path.is_file() else {}
    if receipt and receipt.get("owner") != "CDUResources.artist-preview.v1":
        raise ValueError("Existing preview ownership receipt belongs to another tool")
    destinations = {}
    for relative, content in outputs.items():
        destination = safe_path(profile, relative)
        if destination.exists() and (not destination.is_file() or digest(destination.read_bytes()) != receipt.get("files", {}).get(relative)):
            raise ValueError("Refusing to replace an existing unowned or independently changed preview file: " + str(destination))
        destinations[relative] = destination
    # Preflight every destination before copying either artifact; options.txt is never read or written.
    for relative, destination in destinations.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".cdu-preview-", delete=False) as pending:
            pending.write(outputs[relative])
            temporary = Path(pending.name)
        try:
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    receipt = {"owner": "CDUResources.artist-preview.v1", "packSha1": pack_sha1,
               "files": {key: digest(content) for key, content in outputs.items()}}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Preview copied to " + str(profile))
    print("Enable quasar-gui-artist-preview once in Resource Packs. After each update, press F3+T, then run /invdebug quasar reload. No mod rebuild is needed.")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("setup")
    sub.add_parser("locate")
    export = sub.add_parser("export")
    export.add_argument("--aseprite")
    export.add_argument("--force", action="store_true", help="Explicitly regenerate PNGs, including independent PNG edits")
    sub.add_parser("verify-exports")
    sub.add_parser("build")
    sub.add_parser("open-layout")
    install = sub.add_parser("install-preview")
    install.add_argument("--minecraft", required=True, help="Explicit Minecraft instance directory")
    args = parser.parse_args()
    try:
        if args.command == "setup": setup()
        elif args.command == "locate": print(locate_aseprite() or "Aseprite not found; set ASEPRITE_EXE or use PNG-only editing")
        elif args.command == "export": export_projects(executable=args.aseprite, force=args.force)
        elif args.command == "verify-exports": verify_exports()
        elif args.command == "build": build()
        elif args.command == "install-preview": install_preview(args.minecraft)
        else:
            subprocess.run([sys.executable, str(ROOT / "tools/build_artist_editor.py")], check=True, cwd=ROOT)
            webbrowser.open((ROOT / "LAYOUT-EDITOR.html").as_uri())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, "Artist tools: " + str(error) + "\n")


if __name__ == "__main__":
    main()
