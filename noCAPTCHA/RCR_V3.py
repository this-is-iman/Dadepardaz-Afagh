import time
import pyautogui
import cv2
import mss
import numpy
import os
from skimage.metrics import structural_similarity
from win32con import MOUSEEVENTF_MOVE, MOUSEEVENTF_ABSOLUTE, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_LEFTDOWN
from win32api import mouse_event, GetCursorPos
from random import randint, choice
import math
import shelve
import mouse


path_main = os.getcwd()
path_general = os.path.join(path_main, 'Files')
temp_general_GT_Detect = cv2.imread(os.path.join(path_general, 'GT_Detect.png'), cv2.IMREAD_COLOR)
temp_general_GT_Slide = cv2.imread(os.path.join(path_general, 'GT_Slide.png'), cv2.IMREAD_COLOR)
temp_general_GT_Slide_Load = cv2.imread(os.path.join(path_general, 'GT_Slide_Load.png'), cv2.IMREAD_COLOR)
temp_general_GT_Icon = cv2.imread(os.path.join(path_general, 'GT_Icon.png'), cv2.IMREAD_COLOR)
temp_general_LoadingForGT = cv2.imread(os.path.join(path_general, 'Loading.png'), cv2.IMREAD_COLOR)

shelf = shelve.open(os.path.join(path_general, 'humanSlides'))
records = shelf.get('komail')
shelf.close()

box_general_procc = {"top": 104, "left": 448, "width": 919, "height": 936}
threshold_gt = 1 - 0.97
top, left, width, height = "top", "left", "width", "height"
x, y, w, h = 0, 1, 2, 3
shapeX, shapeY = 1, 0


def recorded_gt(xrel):
    init_pos = GetCursorPos()
    movesTmp = records[xrel]
    evnts = list()
    _x = 0
    _y = 1
    _time = 2
    #   00 = {ButtonEvent: 3} ButtonEvent(event_type='down', button='left', time=1626013455.5597281)
    #   01 = {MoveEvent: 3}   MoveEvent(x=1325, y=371, time=1626013455.9594526)
    #   02 = {ButtonEvent: 3} ButtonEvent(event_type='up', button='left', time=1626013456.6232336)
    evnts.append(mouse.ButtonEvent(event_type='down', button='left', time=movesTmp[0][_time]))
    for itm in movesTmp[1:-1]:
        evnts.append(mouse.MoveEvent(x=itm[_x]+init_pos[_x], y=itm[_y]+init_pos[_y], time=itm[_time]))
    evnts.append(mouse.ButtonEvent(event_type='up', button='left', time=movesTmp[-1][_time]))
    return evnts

def bezierItTo(endpoint=None, area=(0, 0), deviation=30, speed=80, controls=2, move=False, rel=None):
    init_pos = GetCursorPos()
    if rel is None:
        fin_pos = (endpoint[0] + randint(0, area[0]), endpoint[1] + randint(0, area[1]))
    else:
        fin_pos = (init_pos[0] + rel[0] + randint(0, area[0]), init_pos[1] + rel[1] + randint(0, area[1]))
    coordinates = [init_pos]
    for i in range(controls):
        controlPoint = (
        init_pos[0] + choice((-1, 1)) * abs(math.ceil(fin_pos[0]) - math.ceil(init_pos[0])) * 0.01 * randint(round(deviation / 2), deviation),
        init_pos[1] + choice((-1, 1)) * abs(math.ceil(fin_pos[1]) - math.ceil(init_pos[1])) * 0.01 * randint(round(deviation / 2), deviation))
        coordinates.append(controlPoint)
    coordinates.append(fin_pos)
    numberOfPoints = len(coordinates)
    pascal_row = [1]
    x_, numerator = 1, (numberOfPoints - 1)
    for denominator in range(1, (numberOfPoints - 1)//2+1):
        x_ *= numerator
        x_ /= denominator
        pascal_row.append(x_)
        numerator -= 1
    if (numberOfPoints - 1) & 1 == 0:
        pascal_row.extend(reversed(pascal_row[:-1]))
    else:
        pascal_row.extend(reversed(pascal_row))
    combinations = pascal_row
    bezier = list()
    for t in [t / (speed * 100.0) for t in range((speed * 100) + 1)]:
        tpowers = (t ** i for i in range(numberOfPoints))
        upowers = reversed([(1 - t) ** i for i in range(numberOfPoints)])
        coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
        bezier.append(list(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*coordinates)))
    if move:
        for point in bezier:
            mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, int(point[0] * 65535.0 / 1920), int(point[1] * 65535.0 / 1080))
    return bezier

def handle_gt(timeout=120.0):   # returns:  e: error, t: timeout, s: success, f: fuck
    gtLoc = int()
    threshold_gt = 1 - 0.98
    # matchMethod = cv2.TM_SQDIFF_NORMED
    firstRun = True
    deadline = time.time() + timeout

    dl = time.time() + 10
    while dl > time.time() and deadline > time.time():
        img_bgr = cv2.cvtColor(numpy.array(mss.mss().grab(box_general_procc)), cv2.COLOR_BGRA2BGR)
        gtVal, maxVal, gtLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_GT_Detect, cv2.TM_SQDIFF_NORMED))
        if gtVal < threshold_gt:
            dl = 1
            break
    if deadline <= time.time():
        return 't'
    elif dl != 1:
        return 'e'

    gtArea = {"top": box_general_procc[top] + gtLoc[y] + 2 - 1, "left": box_general_procc[left] + gtLoc[x] + 2 - 44,
              "width": temp_general_GT_Detect.shape[shapeX] - temp_general_GT_Detect.shape[shapeY] - 4,
              "height": temp_general_GT_Detect.shape[shapeY] - 4}

    deviation = randint(20, 40)
    speed = randint(80, 90)
    bezGoToGT = bezierItTo((gtArea[left], gtArea[top]), (gtArea[width], gtArea[height]), deviation, speed)
    delay_BeforeClick = randint(150, 250) / 1000.0
    delay_ClickDuration = randint(60, 210) / 1000.0

    for point in bezGoToGT:
        mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, int(point[0] * 65535.0 / 1920), int(point[1] * 65535.0 / 1080))

    dl = time.time() + delay_BeforeClick
    while dl >= time.time():
        pass
    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0)
    dl = time.time() + delay_ClickDuration
    while dl >= time.time():
        pass
    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0)

    gldVal = int()
    sldVal, sldLoc = int(), int()
    icnVal = int()
    agnVal = int()
    minVal = float()


    while deadline > time.time():

        dl = time.time() + 10
        while dl > time.time() and deadline > time.time():
            img_bgr = cv2.cvtColor(numpy.array(mss.mss().grab(box_general_procc)), cv2.COLOR_BGRA2BGR)
            gldVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_LoadingForGT, cv2.TM_SQDIFF_NORMED))
            sldVal, maxVal, sldLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_GT_Slide, cv2.TM_SQDIFF_NORMED))
            icnVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_GT_Icon, cv2.TM_SQDIFF_NORMED))
            minVal = min([gldVal, sldVal, icnVal])
            if minVal < threshold_gt:
                dl = 1
                break

        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'e'
        elif gldVal == minVal:
            return 's'
        elif sldVal == minVal:
            pass
        elif icnVal == minVal:
            return 'f'

        img_bgr = cv2.cvtColor(numpy.array(mss.mss().grab(box_general_procc)), cv2.COLOR_BGRA2BGR)
        sldVal, maxVal, sldLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_GT_Slide, cv2.TM_SQDIFF_NORMED))
        imageArea = {"top": box_general_procc[top] + sldLoc[y] + 10 - 173, "left": box_general_procc[left] + sldLoc[x] + 10 - 1, "width": 260, "height": 160}
        sliderArea = {"top": box_general_procc[top] + sldLoc[y] + 179 - 173, "left": box_general_procc[left] + sldLoc[x] + 12 - 1, "width": 50, "height": 50}

        dl = time.time() + 30
        while dl > time.time() and deadline > time.time():
            img_t = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2BGR)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_t, temp_general_GT_Slide_Load, cv2.TM_SQDIFF_NORMED))
            if minVal > threshold_gt:
                pyautogui.hotkey('alt', 'shift', 'z')
                dl = time.time() + 0.1
                while dl > time.time():
                    pass
                dl = 1
                break
        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'e'

        img_3 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)
        pyautogui.hotkey('alt', 'shift', 'x')
        dl = time.time() + 5
        while dl > time.time() and deadline > time.time():
            pyautogui.hotkey('alt', 'shift', 'x')
            img_1 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)
            (score, diff) = structural_similarity(img_1.copy(), img_3.copy(), full=True)
            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contoursS = contours[0] if len(contours) == 2 else contours[1]
            if len(contoursS) == 0:
                continue
            c = max(contoursS, key=cv2.contourArea)
            if 10000 > cv2.contourArea(c) > 225:
                dl = 1
                break
        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'r'
        img_1 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)

        pyautogui.hotkey('alt', 'shift', 'y')
        dl = time.time() + 5
        while dl > time.time() and deadline > time.time():
            pyautogui.hotkey('alt', 'shift', 'y')
            img_2 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)
            (score, diff) = structural_similarity(img_2.copy(), img_1.copy(), full=True)
            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contoursS = contours[0] if len(contours) == 2 else contours[1]
            if len(contoursS) == 0:
                continue
            c = max(contoursS, key=cv2.contourArea)
            if 100000 > cv2.contourArea(c) > 1:
                dl = 1
                break
        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'r'
        img_2 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)

        pyautogui.hotkey('alt', 'shift', 'z')
        dl = time.time() + 5
        while dl > time.time() and deadline > time.time():
            pyautogui.hotkey('alt', 'shift', 'z')
            img_3 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)
            (score, diff) = structural_similarity(img_3.copy(), img_2.copy(), full=True)
            diff = (diff * 255).astype("uint8")
            thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contoursS = contours[0] if len(contours) == 2 else contours[1]
            if len(contoursS) == 0:
                continue
            c = max(contoursS, key=cv2.contourArea)
            if 100000 > cv2.contourArea(c) > 1:
                dl = 1
                break
        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'r'
        img_3 = cv2.cvtColor(numpy.array(mss.mss().grab(imageArea)), cv2.COLOR_BGRA2GRAY)

        (score, diff) = structural_similarity(img_1.copy(), img_2.copy(), full=True)
        diff = (diff * 255).astype("uint8")
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contoursT = contours[0] if len(contours) == 2 else contours[1]
        if len(contoursS) == 0:
            return 'e'
        c = max(contoursT, key=cv2.contourArea)
        X, Y, W, H = cv2.boundingRect(c)
        target = (X + round(W/2), Y + round(H/2))

        (score, diff) = structural_similarity(img_2.copy(), img_3.copy(), full=True)
        diff = (diff * 255).astype("uint8")
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contoursS = contours[0] if len(contours) == 2 else contours[1]
        if len(contoursS) == 0:
            return 'e'
        c = max(contoursS, key=cv2.contourArea)
        X, Y, W, H = cv2.boundingRect(c)
        slce = (X + round(W/2), Y + round(H/2))

        distance = target[x] - slce[x]

        if distance < 1:
            return 'e'

        if firstRun:
            firstRun = False
            deviation = randint(20, 40)
            speed = randint(35, 45)
            bezGoToSlider = bezierItTo((sliderArea[left], sliderArea[top]), (sliderArea[width], sliderArea[height]), deviation, speed) ################
            delay_BeforeClick = randint(150, 250) / 1000.0
            for point in bezGoToSlider:
                mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, int(point[0] * 65535.0 / 1920), int(point[1] * 65535.0 / 1080))
            dl = time.time() + delay_BeforeClick
            humGoToTarget = recorded_gt(distance)
            while dl >= time.time():
                pass
        else:
            humGoToTarget = recorded_gt(distance)

        mouse.play(humGoToTarget)

        dl = time.time() + 10
        while dl > time.time() and deadline > time.time():
            img_bgr = cv2.cvtColor(numpy.array(mss.mss().grab(box_general_procc)), cv2.COLOR_BGRA2BGR)
            gldVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(cv2.matchTemplate(img_bgr, temp_general_LoadingForGT, cv2.TM_SQDIFF_NORMED))
            if gldVal < threshold_gt:
                dl = 1
                break
        if deadline <= time.time():
            return 't'
        elif dl != 1:
            return 'e'
        elif gldVal < threshold_gt:
            return 's'

    return 't'


time.sleep(3)
handle_gt()
