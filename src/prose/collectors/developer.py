from __future__ import annotations

import json
import os
from pathlib import Path

from prose.schema import (
    BrowserInfo,
    DeveloperToolsInfo,
    DockerContainer,
    DockerImage,
    DockerInfo,
    GitConfig,
)
from prose.utils import get_version, run, verbose_log, which


def collect_docker_info() -> DockerInfo:
    """Collect Docker daemon status, containers, and images information."""
    if not which("docker"):
        return {
            "installed": False,
            "version": "Not Found",
            "running": False,
            "containers_total": 0,
            "containers_running": 0,
            "images_count": 0,
            "containers": [],
            "images": [],
        }

    version = get_version(["docker", "--version"])

    # Check if Docker daemon is running
    running = False
    containers_total = 0
    containers_running = 0
    images_count = 0
    containers_list: list[DockerContainer] = []
    images_list: list[DockerImage] = []

    try:
        # Test if daemon is accessible
        run(["docker", "info"], timeout=5, log_errors=False)
        running = True

        # Get detailed containers info
        containers_output = run(["docker", "ps", "-a", "--format", "json"], log_errors=False)
        if containers_output:
            for line in containers_output.splitlines():
                if line.strip():
                    try:
                        container_data = json.loads(line)
                        containers_list.append(
                            {
                                "id": container_data.get("ID", "")[:12],
                                "name": container_data.get("Names", ""),
                                "image": container_data.get("Image", ""),
                                "status": container_data.get("Status", ""),
                                "ports": container_data.get("Ports", ""),
                                "created": container_data.get("CreatedAt", ""),
                            }
                        )
                    except json.JSONDecodeError:
                        pass
            containers_total = len(containers_list)

        running_output = run(["docker", "ps", "--format", "json"], log_errors=False)
        if running_output:
            containers_running = len([line for line in running_output.splitlines() if line.strip()])

        # Get detailed images info
        images_output = run(["docker", "images", "--format", "json"], log_errors=False)
        if images_output:
            for line in images_output.splitlines():
                if line.strip():
                    try:
                        image_data = json.loads(line)
                        images_list.append(
                            {
                                "repository": image_data.get("Repository", ""),
                                "tag": image_data.get("Tag", ""),
                                "id": image_data.get("ID", "")[:12],
                                "size": image_data.get("Size", ""),
                                "created": image_data.get("CreatedAt", ""),
                            }
                        )
                    except json.JSONDecodeError:
                        pass
            images_count = len(images_list)
    except Exception:
        pass

    return {
        "installed": True,
        "version": version,
        "running": running,
        "containers_total": containers_total,
        "containers_running": containers_running,
        "images_count": images_count,
        "containers": containers_list,
        "images": images_list,
    }


def collect_browsers() -> list[BrowserInfo]:
    """Detect installed web browsers and their versions."""
    browsers: list[BrowserInfo] = []

    browser_configs: dict[str, dict[str, str | list[str]]] = {
        "Google Chrome": {
            "path": "/Applications/Google Chrome.app",
            "version_cmd": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--version",
            ],
        },
        "Firefox": {
            "path": "/Applications/Firefox.app",
            "version_cmd": ["/Applications/Firefox.app/Contents/MacOS/firefox", "--version"],
        },
        "Safari": {
            "path": "/Applications/Safari.app",
            "version_cmd": [
                "defaults",
                "read",
                "/Applications/Safari.app/Contents/Info.plist",
                "CFBundleShortVersionString",
            ],
        },
        "Microsoft Edge": {
            "path": "/Applications/Microsoft Edge.app",
            "version_cmd": [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                "--version",
            ],
        },
        "Brave Browser": {
            "path": "/Applications/Brave Browser.app",
            "version_cmd": [
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
                "--version",
            ],
        },
        "Opera": {
            "path": "/Applications/Opera.app",
            "version_cmd": ["/Applications/Opera.app/Contents/MacOS/Opera", "--version"],
        },
        "Arc": {
            "path": "/Applications/Arc.app",
            "version_cmd": [
                "defaults",
                "read",
                "/Applications/Arc.app/Contents/Info.plist",
                "CFBundleShortVersionString",
            ],
        },
        "Vivaldi": {
            "path": "/Applications/Vivaldi.app",
            "version_cmd": ["/Applications/Vivaldi.app/Contents/MacOS/Vivaldi", "--version"],
        },
    }

    for browser_name, config in browser_configs.items():
        browser_path = str(config["path"])
        installed = Path(browser_path).exists()
        version = "Unknown"

        if installed:
            try:
                version_cmd = config["version_cmd"]
                if isinstance(version_cmd, list):
                    version_output = run(version_cmd, timeout=3, log_errors=False)
                    if version_output:
                        # Extract version number
                        version = version_output.strip().split()[-1]
            except Exception:
                version = "Installed"

        browsers.append(
            {
                "name": browser_name,
                "installed": installed,
                "version": version if installed else "Not Installed",
                "path": browser_path if installed else "",
            }
        )

    return browsers


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
    vm_checks = ["nvm", "asdf", "pyenv", "fnm", "rvm", "rbenv", "goenv", "volta", "mise", "rustup"]
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


def collect_git_config() -> GitConfig:
    """Collect Git global configuration."""
    verbose_log("Collecting Git configuration...")

    config: GitConfig = {
        "user_name": None,
        "user_email": None,
        "core_editor": None,
        "credential_helper": None,
        "aliases": {},
        "other_settings": {},
    }

    if not which("git"):
        return config

    try:
        output = run(["git", "config", "--list", "--global"], log_errors=False)
        for line in output.splitlines():
            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            if key == "user.name":
                config["user_name"] = value
            elif key == "user.email":
                config["user_email"] = value
            elif key == "core.editor":
                config["core_editor"] = value
            elif key == "credential.helper":
                config["credential_helper"] = value
            elif key.startswith("alias."):
                alias_name = key.replace("alias.", "")
                config["aliases"][alias_name] = value
            else:
                config["other_settings"][key] = value
    except Exception:
        pass

    return config


def collect_terminal_emulators() -> list[str]:
    """Detect installed terminal emulator applications."""
    verbose_log("Detecting terminal emulators...")
    terminals = []

    # System Terminal.app (always present on macOS)
    system_terminal = Path("/System/Applications/Utilities/Terminal.app")
    if system_terminal.exists():
        terminals.append("Terminal")

    terminal_apps = {
        "iTerm": "/Applications/iTerm.app",
        "Warp": "/Applications/Warp.app",
        "Hyper": "/Applications/Hyper.app",
        "Alacritty": "/Applications/Alacritty.app",
        "Kitty": "/Applications/kitty.app",
        "Ghostty": "/Applications/Ghostty.app",
        "WezTerm": "/Applications/WezTerm.app",
        "Rio": "/Applications/Rio.app",
    }

    for name, path in terminal_apps.items():
        if Path(path).exists():
            terminals.append(name)

    return sorted(terminals)


def collect_shell_frameworks() -> dict[str, str]:
    """Detect installed shell frameworks and enhancements."""
    verbose_log("Detecting shell frameworks...")
    frameworks: dict[str, str] = {}

    # oh-my-zsh
    omz_path = Path.home() / ".oh-my-zsh"
    if omz_path.exists():
        frameworks["oh-my-zsh"] = "Installed"

    # oh-my-bash
    omb_path = Path.home() / ".oh-my-bash"
    if omb_path.exists():
        frameworks["oh-my-bash"] = "Installed"

    # Starship prompt
    if which("starship"):
        frameworks["starship"] = get_version(["starship", "--version"])

    # Powerlevel10k
    p10k_path = Path.home() / ".p10k.zsh"
    if p10k_path.exists():
        frameworks["powerlevel10k"] = "Installed"

    # zinit
    zinit_path = Path.home() / ".local/share/zinit"
    if zinit_path.exists():
        frameworks["zinit"] = "Installed"

    # antigen
    antigen_path = Path.home() / ".antigen"
    if antigen_path.exists():
        frameworks["antigen"] = "Installed"

    # Fig (now Amazon Q)
    if which("fig"):
        frameworks["fig"] = get_version(["fig", "--version"])

    return frameworks


def collect_dev_tools() -> DeveloperToolsInfo:
    return {
        "languages": collect_languages(),
        "sdks": collect_sdks(),
        "cloud_devops": collect_cloud_devops(),
        "databases": collect_databases(),
        "version_managers": collect_version_managers(),
        "infra": {
            "git": get_version(["git", "--version"]) if which("git") else "Not Found",
        },
        "extensions": collect_extensions(),
        "editors": collect_editors(),
        "docker": collect_docker_info(),
        "browsers": collect_browsers(),
        "git_config": collect_git_config(),
        "terminal_emulators": collect_terminal_emulators(),
        "shell_frameworks": collect_shell_frameworks(),
    }
