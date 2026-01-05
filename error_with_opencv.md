La idea es: quitar el OpenCV de pip de ~/.local e instalar/usar uno que sí venga con GStreamer (en Jetson suele ser el de JetPack/apt).

Desinstala el OpenCV de tu usuario (pip):

python3 -m pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python


Instala OpenCV del sistema (Ubuntu/Jetson):

sudo apt-get update
sudo apt-get install -y python3-opencv gstreamer1.0-tools


Verifica que ahora cv2 venga del sistema y si trae GStreamer:

python3 -c "import cv2; print(cv2.__file__); print([l for l in cv2.getBuildInformation().splitlines() if 'GStreamer' in l])"
