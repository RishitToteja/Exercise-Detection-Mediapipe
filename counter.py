import cv2
import mediapipe as mp
import numpy as np
import PoseModule as pm
import Squat as sq

cap = cv2.VideoCapture(0)
detector = pm.poseDetector()
count = 0
direction = 0
form = 0
feedback = "Fix Form"
side = input("Which side are your filming? L/R: ")
hip_angles = sq.angle_ref[side]['hip']
knee_angles = sq.angle_ref[side]['knee']
squat_type = input(
    "What type of squat are you doing? A. Just below parallel  B. Deep  C. Front squat  D. Squat hold ")
min_depth = sq.sq_type[squat_type][0]
if squat_type == 'A' or squat_type == 'D':
    max_depth = sq.sq_type[squat_type][1]

while cap.isOpened():  # -
    ret, img = cap.read()  # 640 x 480-------------
    # Determi-ne dimensions of video - Help with creation of box in Line 43
    width = cap.get(3)  # float `width`
    height = cap.get(4)  # float `height`
    # print(width, height--)

    img = detector.findPose(img, False)
    lmList = detector.findPosition(img, False)
    # print(lmList)
    if len(lmList) != 0:

        hip = detector.findAngle(
            img, hip_angles[0], hip_angles[1], hip_angles[2])
        knee = detector.findAngle(
            img, knee_angles[0], knee_angles[1], knee_angles[2])

        # Percentage of success of squat
        per = np.interp(hip, (min_depth, 130), (0, 100))

        # Bar to show squat progress
        bar = np.interp(hip, (min_depth, 130), (380, 50))

        if squat_type == 'A' or squat_type == 'D':
            reverse_per = np.interp(hip, (0, max_depth), (0, 100))
            reverse_bar = np.interp(hip, (0, max_depth), (500, 380))

        # Check to ensure right form before starting the program
        if hip > 130 and knee > 160:
            form = 1

        # Check for full range of motion for the squat
        if form == 1:
            if per == 0:
                if squat_type == 'A' or squat_type == 'D':
                    if hip < max_depth:
                        feedback = "Too low!"

                    if max_depth < hip < min_depth:
                        feedback = "Just nice"

                else:
                    feedback = "Just nice"

                if direction == 0:
                    count += 0.5
                    direction = 1

            if per == 100:
                if hip > 120 and knee > 140:
                    feedback = "Down"
                if direction == 1:
                    count += 0.5
                    direction = 0

            if 100 > per > 0:
                feedback = "Go Lower"

            # Draw Bar
            if form == 1:
                cv2.rectangle(img, (540, 50), (560, 380), (0, 255, 0), 3)
                cv2.rectangle(img, (540, int(bar)), (560, 380),
                              (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'{int(per)}%', (420, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                            (0, 235, 0), 2)

                if squat_type == 'A' or squat_type == 'D':
                    cv2.rectangle(img, (540, 380), (560, 500), (0, 0, 255), 3)
                    cv2.rectangle(img, (540, int(reverse_bar)),
                                  (560, 500), (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, f'{int(100-reverse_per)}%', (600, 430), cv2.FONT_HERSHEY_PLAIN, 2,
                                (0, 0, 255), 2)

            # Squat counter
            cv2.rectangle(img, (0, 380), (100, 480), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (25, 455), cv2.FONT_HERSHEY_PLAIN, 5,
                        (255, 0, 0), 5)

            # Feedback
            cv2.rectangle(img, (500, 0), (640, 40),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, feedback, (500, 40), cv2.FONT_HERSHEY_PLAIN, 2,
                        (0, 255, 0), 2)

    cv2.imshow('Squat counter', img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
