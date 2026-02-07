from __future__ import annotations

import json
import os
from pathlib import Path

from prose.schema import DeveloperToolsInfo
from prose.utils import get_version, run, which


def collect_languages() -> dict[str, str]:
    languages = {}
    lang_checks = {
        "node": ["node", "--version"],
        "python3": ["python3", "--version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "ruby": ["ruby", "--version"],
        "java": ["java", "--version"],
        "php": ["php", "--version"],
        "perl": ["perl", "--version"],
    }
    for name, cmd in lang_checks.items():
        if which(name) or (name == "rust" and which("rustc")):
            languages[name] = get_version(cmd)
        else:
            languages[name] = "Not Found"
    return languages


def collect_sdks() -> dict[str, str]:
    sdks = {}
    if which("flutter"):
        sdks["flutter"] = get_version(["flutter", "--version"])
    else:
        sdks["flutter"] = "Not Found"

    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    sdks["android_sdk"] = android_home if android_home else "Not Found"

    try:
        # Suppress errors as xcodebuild often fails if Xcode is not fully configured
        xcode_ver = run(["xcodebuild", "-version"], log_errors=False)
        sdks["xcode"] = xcode_ver.replace("\n", " ").strip() if xcode_ver else "Not Found"
    except Exception:
        sdks["xcode"] = "Not Installed"
    return sdks


def collect_cloud_devops() -> dict[str, str]:
    cloud_devops = {}
    cloud_checks = {
        "aws": ["aws", "--version"],
        "gcloud": ["gcloud", "--version"],
        "terraform": ["terraform", "--version"],
        "kubectl": ["kubectl", "version", "--client"],
        "helm": ["helm", "version"],
    }
    for name, cmd in cloud_checks.items():
        if which(name):
            cloud_devops[name] = get_version(cmd)
        else:
            cloud_devops[name] = "Not Found"
    return cloud_devops


def collect_databases() -> dict[str, str]:
    databases = {}
    db_checks = {
        "redis": ["redis-cli", "--version"],
        "mongodb_shell": ["mongosh", "--version"],
        "mysql": ["mysql", "--version"],
        "postgresql": ["psql", "--version"],
        "sqlite": ["sqlite3", "--version"],
    }
    for name, cmd in db_checks.items():
        if which(cmd[0]):
            databases[name] = get_version(cmd)
        else:
            databases[name] = "Not Found"
    return databases


def collect_version_managers() -> dict[str, str]:
    vms = {}
    vm_checks = ["nvm", "asdf", "pyenv", "fnm", "rvm"]
    for vm in vm_checks:
        if which(vm):
            vms[vm] = "Installed"
        elif (Path.home() / f".{vm}").exists():
            vms[vm] = "Directory exists at ~"
        else:
            vms[vm] = "Not Found"
    return vms


def collect_extensions() -> dict[str, list[str]]:
    all_extensions: dict[str, list[str]] = {
        "antigravity": [],
        "vscode": [],
        "cursor": [],
        "windsurf": [],
        "zed": [],
    }

    editor_map = {
        "antigravity": "antigravity",
        "cursor": "cursor",
        "vscode": "code",
        "windsurf": "windsurf",
    }
    for display_name, cmd_name in editor_map.items():
        bin_path = which(cmd_name)
        if not bin_path:
            abs_paths = {
                "antigravity": (
                    "/Applications/Antigravity.app/Contents/Resources/app/bin/antigravity"
                ),
                "cursor": "/Applications/Cursor.app/Contents/Resources/app/bin/cursor",
                "vscode": "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
                "windsurf": "/Applications/Windsurf.app/Contents/Resources/app/bin/windsurf",
            }
            if display_name in abs_paths and Path(abs_paths[display_name]).exists():
                bin_path = abs_paths[display_name]

        if bin_path:
            exec_path = bin_path.split(" -> ")[0] if " -> " in bin_path else bin_path
            try:
                out = run([exec_path, "--list-extensions", "--show-versions"], timeout=10)
                exts = [line for line in out.splitlines() if line and "@" in line]
                if exts:
                    all_extensions[display_name] = exts
            except Exception:
                continue

    # Zed Extensions
    zed_ext_index = Path.home() / "Library/Application Support/Zed/extensions/index.json"
    if zed_ext_index.exists():
        try:
            with open(zed_ext_index, "r", encoding="utf-8") as f:
                zed_data = json.load(f)
                zed_exts = []
                for ext_id, ext_info in zed_data.get("extensions", {}).items():
                    manifest = ext_info.get("manifest", {})
                    ver = manifest.get("version")
                    if ver:
                        zed_exts.append(f"{ext_id}@{ver}")
                    else:
                        zed_exts.append(ext_id)
                all_extensions["zed"] = sorted(zed_exts)
        except Exception:
            pass
    return {k: sorted(v) for k, v in all_extensions.items()}


def collect_editors() -> list[str]:
    editors = []
    for cli in ["vim", "nvim", "emacs", "nano"]:
        if which(cli):
            editors.append(cli.capitalize())

    common_apps = [
        "Visual Studio Code.app",
        "Antigravity.app",
        "Zed.app",
        "Sublime Text.app",
        "Cursor.app",
        "Windsurf.app",
        "Android Studio.app",
    ]
    app_dir = Path("/Applications")
    if app_dir.exists():
        for app in common_apps:
            if (app_dir / app).exists():
                editors.append(app.replace(".app", ""))
        for jb in ["IntelliJ", "PyCharm", "WebStorm", "GoLand", "Rider"]:
            for variant in list(app_dir.glob(f"{jb}*.app")):
                editors.append(variant.name.replace(".app", ""))
    return sorted(list(set(editors)))


def collect_dev_tools() -> DeveloperToolsInfo:
    return {
        "languages": collect_languages(),
        "sdks": collect_sdks(),
        "cloud_devops": collect_cloud_devops(),
        "databases": collect_databases(),
        "version_managers": collect_version_managers(),
        "infra": {
            "docker": get_version(["docker", "--version"]) if which("docker") else "Not Found",
            "git": get_version(["git", "--version"]) if which("git") else "Not Found",
        },
        "extensions": collect_extensions(),
        "editors": collect_editors(),
    }
