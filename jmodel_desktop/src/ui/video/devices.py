from pathlib import Path

from PySide6.QtMultimedia import QMediaDevices


def list_v4l2_devices_linux():
    results = []
    base = Path("/sys/class/video4linux")
    if not base.exists():
        return results

    for entry in sorted(base.iterdir()):
        dev = entry.name  # video0, video1...
        name_file = entry / "name"
        label = name_file.read_text(errors="ignore").strip() if name_file.exists() else dev
        results.append((f"/dev/{dev}", label))
    return results