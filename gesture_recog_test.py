import cv2
import mediapipe as mp
import numpy as np
import time
import serial

cap = cv2.VideoCapture(0)

# ser = serial.Serial("COM5", 115200, timeout=0.5)

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=2,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils



def build_and_send_packet(roll, pitch, thrust, yaw):
    packet = b'BP'
    packet = packet + bytearray([roll, pitch, thrust, yaw])
    # ser.write(packet)


pTime = 0
cTime = 0
point1_index=4
point2_index=8
distances ={}
key = 0

analog_roll = 50
analog_pitch = 50
analog_thrust = 0
analog_yaw = 50

def calculate_angle(p1,p2,p3):
        p1=np.array(p1)
        p2=np.array(p2)
        p3=np.array(p3)

        v1=p1-p2
        v2=p3-p2
        dot=np.dot(v1,v2)
        mag1=np.linalg.norm(v1)
        mag2=np.linalg.norm(v2)

        rad=np.arccos(dot / (mag1*mag2))
        degree=np.degrees(rad)
        return degree

while key != 27:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks)
    cv2.circle(img,(840,350),2,(255,0,0), cv2.FILLED)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                # print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x *w), int(lm.y*h)
                #if id ==0:
                lmList.append([id,cx,cy])
                text = str(id)
                cv2.circle(img, (cx,cy), 3, (255,0,255), cv2.FILLED)
                cv2.putText(img,text,(cx,cy),cv2.FONT_HERSHEY_SIMPLEX,.5,(255,255,255),1)
            angle1 = calculate_angle(lmList[0][1:],lmList[5][1:],lmList[17][1:])
            #print(angle1)
            for i in range(len(lmList)):
                distances.setdefault(lmList[i][0],{})
                for j in range(i+1,len(lmList)):  
                    distances.setdefault(lmList[j][0],{})
                    x1, y1 = lmList[i][1], lmList[i][2]
                    x2, y2 = lmList[j][1], lmList[j][2]
                    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    distances[lmList[i][0]][lmList[j][0]] = distance
                    distances[lmList[j][0]][lmList[i][0]] = distance

            #Roll
            # roll_activated = False
            # if(distances[5][8] > 10):
            #     roll_activated = True
            # if(roll_activated):
            #     roll_distance = distances[7][8]

            #Pitch
            angle2= calculate_angle(lmList[1][1:],lmList[0][1:],lmList[17][1:])
            distancePitch = distances[11][12]
            # print("dist 11-12 %d", distancePitch)
            if(distancePitch<44):
                cv2.putText(img,'Pitch up', (10,120), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_pitch = 100
            elif(distancePitch>50):
                cv2.putText(img,'Pitch down', (10,120), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_pitch = 0
            else:
                cv2.putText(img,'Pitch neutral', (10,120), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_pitch = 50
            
            #Thrust
            # print(distances[0][12])
            # 0%
            if(distances[0][12]<250):
                cv2.putText(img,'Thrust 0%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 0
            # 10%
            elif(distances[0][12] > 250 and distances[0][12] < 275):
                cv2.putText(img,'Thrust 10%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 10
            # 20%
            elif(distances[0][12] > 275 and distances[0][12] < 300):
                cv2.putText(img,'Thrust 20%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 20
            # 30%
            elif(distances[0][12] > 300 and distances[0][12] < 325):
                cv2.putText(img,'Thrust 30%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 30
            
            # 40%
            elif(distances[0][12] > 325 and distances[0][12] < 350):
                cv2.putText(img,'Thrust 40%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 40
            # 50%
            elif(distances[0][12] > 350 and distances[0][12] < 375):
                cv2.putText(img,'Thrust 50%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 50
            # 60%
            elif(distances[0][12] > 375 and distances[0][12] < 400):
                cv2.putText(img,'Thrust 60%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 60
            # 70%
            elif(distances[0][12] > 400 and distances[0][12] < 425):
                cv2.putText(img,'Thrust 70%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 70
            # 80%
            elif(distances[0][12] > 425 and distances[0][12] < 450):
                cv2.putText(img,'Thrust 80%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 80
            # 90%
            elif(distances[0][12] > 450 and distances[0][12] < 475):
                cv2.putText(img,'Thrust 90%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 90            
            # 100%
            else:
                cv2.putText(img,'Thrust 100%', (10,80), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_thrust = 100
           
            #Yaw
            disLeft=np.sqrt((lmList[12][1] - 0) ** 2 + (lmList[12][2] - 0) ** 2)
            disRight=np.sqrt((lmList[12][1] - 1080) ** 2 + (lmList[12][2] - 0) ** 2)
            change = disLeft - disRight
            print("disLeft-disRight %d",change)
            if(change < 230):
                cv2.putText(img,'Yaw 0%', (10,160), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_yaw = 0
            elif(change < -100):
                cv2.putText(img,'Yaw Right', (10,160), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_yaw = 100
            else:
                cv2.putText(img,'Yaw Neutral', (10,160), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
                analog_yaw = 50
                
                
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    build_and_send_packet(0, analog_pitch, analog_pitch, analog_yaw)
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    #cv2.putText(img,str(int(fps)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
    
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
