import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import os

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8)


class DragImg():
    def __init__(self, path, posOrigin, imgType):

        self.posOrigin = posOrigin
        self.imgType = imgType
        self.path = path

        if self.imgType == 'png':
            self.img = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
        else:
            self.img = cv2.imread(self.path)

        # self.img = cv2.resize(self.img, (0,0),None,0.4,0.4)

        self.size = self.img.shape[:2]

    def update(self, cursor):
        ox, oy = self.posOrigin
        h, w = self.size

        # Check if in region
        if ox < cursor[0] < ox + w and oy < cursor[1] < oy + h:
            self.posOrigin = cursor[0] - w // 2, cursor[1] - h // 2
            return True
        return False


path = "ImagesPNG"
myList = os.listdir(path)
print(myList)

listImg = []
for x, pathImg in enumerate(myList):
    if 'png' in pathImg:
        imgType = 'png'
    else:
        imgType = 'jpg'
    listImg.append(DragImg(f'{path}/{pathImg}', [50 + x * 300, 50], imgType))

f = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if f == 0:
        if hands:
            lmList = hands[0]['lmList']
            length, info, img = detector.findDistance(lmList[8][:2], lmList[12][:2], img)
            if length < 60:
                cursor = lmList[8]
                for imgObject in listImg:
                    if imgObject.update(cursor):
                        break

        try:

            for imgObject in listImg:

                h, w = imgObject.size
                ox, oy = imgObject.posOrigin
                if imgObject.imgType == "png":
                    img = cvzone.overlayPNG(img, imgObject.img, [ox, oy])
                else:
                    img[oy:oy + h, ox:ox + w] = imgObject.img

        except:
            pass
    
    tog = 0
    px, py = listImg[0].posOrigin
    sx, sy = listImg[0].size
    for i in range(1, 4):
        rx, ry = 0, 0
        imgObject = listImg[i]
        ox, oy = imgObject.posOrigin
        if i == 1 or i ==  3:
            if (sx - 10) <= (px - ox) <= 2 * sx:
                rx = 1
        if i == 1 and (py - sy) <= oy <= (py + sy):
            ry = 1
        if i == 2 and (px - sx) <= ox <= (px + sx):
            rx = 1
        if i == 2 or i == 3 and (sy - 10) <= (py - oy) <= (sy + 10):
            ry = 1
        if rx == 1 and ry == 1:
            tog += 1
    if tog == 3:
        f = 1
    
    if f == 1:
        cv2.rectangle(img, (500, 100), (800, 150),(255, 0, 255), thickness = -1)
        cv2.putText(img, "SOLVED!", (550, 135), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)
        cv2.rectangle(img, (500, 200), (800, 250),(255, 0, 255), thickness = -1)
        cv2.putText(img, "Click Q to Quit", (550, 235), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break