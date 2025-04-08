import cv2

def select_crop_box(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to read video.")
        return None

    roi = []

    def mouse_callback(event, x, y, flags, param):
        nonlocal roi, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            roi = [(x, y)]
        elif event == cv2.EVENT_LBUTTONUP:
            roi.append((x, y))
            cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)
            cv2.imshow("Select Crop Area", frame)

    cv2.namedWindow("Select Crop Area")
    cv2.setMouseCallback("Select Crop Area", mouse_callback)

    print("Draw a rectangle to select the crop area. Press Enter when done.")
    while True:
        cv2.imshow("Select Crop Area", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter
            break
        elif key == 27:  # Esc
            cv2.destroyAllWindows()
            return None

    cv2.destroyAllWindows()

    if len(roi) != 2:
        print("No crop area selected.")
        return None

    x1, y1 = roi[0]
    x2, y2 = roi[1]
    x = min(x1, x2)
    y = min(y1, y2)
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    return (x, y, w, h)
