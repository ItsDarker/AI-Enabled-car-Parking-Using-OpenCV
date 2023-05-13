import cv2
import pickle
import cvzone
import numpy as np

cap = cv2.VideoCapture('carParkingInput.mp4')

with open('parkingSlotPosition', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


def checkParkingSpace(imgPro):
    spaceCounter = 0

    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y: y + height, x: x + width]

        count = cv2.countNonZero(imgCrop)
        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1

        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)


while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()

    imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgB = cv2.GaussianBlur(imgG, (3, 3), 1)
    imgT = cv2.adaptiveThreshold(imgB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgM = cv2.medianBlur(imgT, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgD = cv2.dilate(imgM, kernel, iterations=1)
    checkParkingSpace(imgD)
    cv2.imshow("Image", img)
    cv2.waitKey(10)