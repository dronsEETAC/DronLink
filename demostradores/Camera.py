import threading
import time

import cv2 as cv
import numpy as np


class Camera(object):
    def __init__(self):
        self.cap = cv.VideoCapture(0)
        self.videoStreaming = False
        self.frequency = 0 # numero de frames por segundo en el video streaming



    def setColorDetectionParams (self, colorDetectionParams):
        '''
        {   'showColorCode': False,
            'colors': [{'name': 'rojo','code':4}, ...],
            'addColorName': True,
            'addContourn': True
        }
        '''
        self.colorDetectionParams = colorDetectionParams

    def DetectColor(self, frame):

        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        if self.colorDetectionParams['showColorCode']:
            shape = frame.shape
            cv.circle(frame, (shape[1]//2, shape[0]//2), 10, (0, 0, 255), -1)
            code = hsv[shape[1]//2, shape[0]//2]
            codeMsg = 'H: '+str(code[0])+ ' S: '+str(code[1])+ ' V: '+str(code[2])
            cv.putText(
                img=frame,
                text=codeMsg,
                org=(shape[1]//2-180, shape[0]//2+50),
                fontFace=cv.FONT_HERSHEY_TRIPLEX,
                fontScale=1,
                color=(255, 255, 255),
                thickness=0,
            )

            return frame, None
        else:
            marge = 5

            detectedColour = "none"
            # ignore selected contour with area less that this
            minimumSize = 0
            areaBiggestContour = 0
            code = None

            for i in range (0, len( self.colorDetectionParams['colors'])):
                color = self.colorDetectionParams['colors'][i]

                lowerLimit = np.array([color['code'] - marge, 50, 50])
                upperLimit = np.array([color['code'] + marge, 255, 255])

                # for each color:
                #   find contours of this color
                #   get the biggest contour
                #   check if the contour is within the target rectangle (if area = 'small')
                #   check if the contour has the minimun area
                #   keet this contour if it is the biggest by the moment


                mask = cv.inRange(hsv, lowerLimit, upperLimit)
                kernel = np.ones((5, 5), np.uint8)
                mask = cv.erode(mask, kernel, iterations=5)
                mask = cv.dilate(mask, kernel, iterations=5)
                mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
                mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
                contours, hierarchy = cv.findContours(
                    mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
                )
                if len(contours) > 0:
                    contour = max(contours, key=cv.contourArea)
                    if cv.contourArea(contour) > areaBiggestContour:
                        areaBiggestContour = cv.contourArea(contour)
                        detectedColour = color['name']
                        detectedContour = contour
                        code = i
            if detectedColour != "none" and areaBiggestContour > minimumSize:
                if self.colorDetectionParams['addColorName']:
                    cv.putText(
                        img=frame,
                        text=detectedColour,
                        org=(50, 50),
                        fontFace=cv.FONT_HERSHEY_TRIPLEX,
                        fontScale=2,
                        color=(255, 255, 255),
                        thickness=1,
                )
                if self.colorDetectionParams['addContourn']:
                    cv.drawContours(frame, [detectedContour], 0, (0, 255, 0), 3)

            return frame, code

    def TakePicture (self):
        for n in range(1, 50):
            # en este bucle descarto las primeras fotos, que a veces salen en negro
            ret, frame = self.cap.read()
        return ret, frame

    def _start_video_stream (self, callback, params):
        while self.videoStreaming:
            # Read Frame
            ret, frame = self.cap.read()
            frame, code = self.DetectColor(frame)
            #frame, color = self.colorDetector.DetectColor(frame)
            if ret:
                if params != None:
                    callback (frame, code, params)
                else:
                    callback(frame, code)

                time.sleep(1/ self.frequency)

    def setFrequency (self, frequency):
        self.frequency = frequency

    def StartVideoStream (self, frequency, callback, params = None):
        self.videoStreaming = True
        self.frequency = frequency
        streamingThread = threading.Thread(
            target=self._start_video_stream,
            args=[callback, params])
        streamingThread.start()


    def StopVideoStream (self):
        self.videoStreaming = False

    def Close (self):
        self.cap.release()
