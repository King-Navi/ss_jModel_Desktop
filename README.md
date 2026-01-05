```bash
sudo apt update
sudo apt install -y \
  python3-gi gir1.2-gtk-4.0 \
  gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad

```

```bash
sudo apt update
sudo apt install -y libxcb-cursor0
sudo apt install -y python3.10-venv
```


(Opcional)
```bash
sudo apt install -y \
  libxkbcommon-x11-0 \
  libxcb-icccm4 \
  libxcb-image0 \
  libxcb-keysyms1 \
  libxcb-render-util0 \
  libxcb-xinerama0 \
  libxcb-randr0 \
  libxcb-xfixes0 \
  libxcb-sync1 \
  libxcb-xkb1 \
  libxcb-shape0

```


```bash
poetry run pyside6-rcc jmodel_desktop/src/resources/views.qrc -o jmodel_desktop/src/resources/views_rc.py

```

```bash
poetry run pyside6-designer
```
