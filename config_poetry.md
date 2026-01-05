# Recrea el venv con acceso al sistema
rm -rf .venv

python3 -m venv --system-site-packages .venv
poetry env use .venv/bin/python
poetry install

# Anexa tu user-site (~/.local/...) al venv con un .pth

Esto “pega” el sitio donde está tu cv2 real:

echo "$HOME/.local/lib/python3.10/site-packages" > .venv/lib/python3.10/site-packages/userlocal.pth

D) Prueba
poetry run python -c "import cv2; print('cv2', cv2.__version__, cv2.__file__)"