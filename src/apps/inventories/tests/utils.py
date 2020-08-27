import numpy as np
import cv2 as cv


def get_data_in_qr_image(img):
    qr_detector = cv.QRCodeDetector()
    data, bbox, _ = qr_detector.detectAndDecode(img)
    if bbox is not None and len(bbox) > 0:
        return data
    return None


def image_from_bytestring(bytestring):
    return cv.imdecode(np.fromstring(bytestring, np.uint8), cv.IMREAD_COLOR)
