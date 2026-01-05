import time

import cv2
from ultralytics import YOLO

model_path = "./models/yolo11n.pt"  # change this
device = "/dev/video0"


def build_gst_pipeline_mjpeg(device="/dev/video0", width=1280, height=720, fps=30):
    return (
        f"v4l2src device={device} io-mode=2 ! "
        f"image/jpeg,width={width},height={height},framerate={fps}/1 ! "
        "jpegdec ! videoconvert ! "
        "queue leaky=downstream max-size-buffers=1 ! "
        "appsink max-buffers=1 drop=true sync=false"
    )


def main():


    pipeline = build_gst_pipeline_mjpeg(device=device, width=1280, height=720, fps=30)
    print("GStreamer pipeline:\n", pipeline)

    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    if not cap.isOpened():
        raise RuntimeError("Could not open /dev/video0 via GStreamer. (Does your OpenCV have GStreamer enabled?)")

    model = YOLO(model_path, task="detect")

    infer_period = 1.0 / 6.0  # 6 fps inference (adjust)
    last_infer = 0.0
    last_annotated = None

    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            time.sleep(0.01)
            continue

        now = time.monotonic()
        if (now - last_infer) >= infer_period:
            last_infer = now
            results = model.predict(frame, verbose=False)
            last_annotated = results[0].plot()  # BGR annotated image (numpy)

        # If inference hasn't run yet, show raw frame
        view = last_annotated if last_annotated is not None else frame
        cv2.imshow("YOLO + GStreamer (/dev/video0)", view)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
