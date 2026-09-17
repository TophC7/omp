#!/usr/bin/env python3
"""Install the pinned reviewed-Prewalk source and ~/.local/bin/omp-prewalk.

Requires git, Bun >= 1.3.14, Python 3, and network access on macOS or Linux.
Run after pulling this configuration repository. Ordinary omp is never replaced.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


def run(*args, cwd=None):
    subprocess.run([str(arg) for arg in args], cwd=cwd, check=True)


def install_link(link, target):
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink():
        if link.resolve() == target.resolve():
            return
        link.unlink()
    elif link.exists():
        if link.is_dir():
            raise RuntimeError(f"Refusing to replace a real directory: {link}")
        backup = link.with_name(f"{link.name}.backup-{time.time_ns()}")
        link.rename(backup)
        print(f"Preserved previous launcher at {backup}", flush=True)
    link.symlink_to(target, target_is_directory=target.is_dir())


def main():
    if len(sys.argv) > 1:
        if sys.argv[1:] in (["--help"], ["-h"]):
            print(__doc__)
            return
        raise RuntimeError("No arguments supported; use --help for prerequisites.")
    for program in ("git", "bun"):
        if not shutil.which(program):
            raise RuntimeError(f"Install {program} first; Bun is available at https://bun.sh")
    bun_version = subprocess.check_output(["bun", "--version"], text=True).strip()
    if tuple(map(int, bun_version.split("-")[0].split("."))) < (1, 3, 14):
        raise RuntimeError(f"Bun >= 1.3.14 required; found {bun_version}")
    system = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
    arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64", "AMD64": "x64"}.get(platform.machine())
    if not system or not arch:
        raise RuntimeError(f"Unsupported platform: {platform.system()}/{platform.machine()}")

    root = Path(__file__).resolve().parents[1]
    pin = json.loads((root / "prewalk/source.json").read_text())
    patch = root / "prewalk/reviewed-prewalk.patch"
    digest = hashlib.sha256(patch.read_bytes()).hexdigest()[:12]
    source = Path.home() / ".omp/prewalk" / f"{pin['version']}-{digest}"
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        run("git", "clone", "--depth", "1", "--branch", pin["tag"], pin["repository"], source)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if head != pin["baseCommit"]:
        raise RuntimeError(f"Unexpected source revision in {source}; refusing to reset existing work")
    applied = subprocess.run(
        ["git", "apply", "--reverse", "--check", str(patch)], cwd=source, capture_output=True
    ).returncode == 0
    if not applied:
        run("git", "apply", "--check", patch, cwd=source)
        run("git", "apply", patch, cwd=source)
    run("bun", "install", "--frozen-lockfile", "--registry", "https://registry.npmjs.org", "--network-concurrency", "8", cwd=source)

    # Workspace native loading deliberately ignores npm leaf packages: copy the
    # exact-version platform addon into its native directory, without a Rust build.
    tag = f"{system}-{arch}"
    native_dir = source / "packages/natives/native"
    if not any(native_dir.glob(f"pi_natives.{tag}*.node")):
        package = f"@oh-my-pi/pi-natives-{tag}"
        with tempfile.TemporaryDirectory(prefix="omp-prewalk-native-") as directory:
            temporary = Path(directory)
            (temporary / "package.json").write_text(json.dumps({
                "name": "omp-prewalk-native", "private": True,
                "dependencies": {package: pin["version"]},
            }))
            run("bun", "install", "--ignore-scripts", "--registry", "https://registry.npmjs.org", cwd=temporary)
            addons = list((temporary / "node_modules" / package).glob("*.node"))
            if not addons:
                raise RuntimeError(f"No native addon in {package}@{pin['version']}")
            for addon in addons:
                shutil.copy2(addon, native_dir / addon.name)

    run(source / "packages/coding-agent/scripts/omp", "--version")
    install_link(root / ".prewalk-source", source)
    install_link(Path.home() / ".local/bin/omp-prewalk", root / "bin/omp-prewalk")
    print("Installed omp-prewalk. Ordinary omp remains unchanged.")
    print("Ensure ~/.local/bin is on PATH. Provider credentials stay local to each computer.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from error
