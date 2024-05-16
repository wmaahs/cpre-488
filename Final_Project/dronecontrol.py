import serial
import time
import keyboard
import pygame

def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n

pygame.init()
pygame.joystick.init()
controller = pygame.joystick.Joystick(0)
controller.init()

print("Controllers: "+str(pygame.joystick.get_count()))
print("Axes: "+str(controller.get_numaxes()))

thrust = 127
yaw = 127
pitch = 127
roll = 127

ser = serial.Serial('COM31', 115200, timeout=0.05)

while not keyboard.is_pressed('q'):
    pygame.event.pump()
    print("0: "+ str(controller.get_axis(0)) + " 1: "+str(controller.get_axis(1)) + " 2: "+str(controller.get_axis(2)) +" 3: "+str(controller.get_axis(3))+" 4: "+str(controller.get_axis(4))  + " 5: "+str(controller.get_axis(5)))
    
    thrust = int(controller.get_axis(1)*-127.5 + 127.5)
    thrust = clamp(thrust,0,255)

    yaw = int(controller.get_axis(0)*127.5/3 + 127.5)
    yaw = clamp(yaw,0,255)

    roll = int(controller.get_axis(2)*-127.5 + 127.5)
    roll = clamp(roll,0,255)

    pitch = int(controller.get_axis(3)*127.5 + 127.5)
    pitch = clamp(pitch,0,255)

    checksum = (66+80+thrust+yaw+pitch+roll) % 256
    ser.write(b'BP')
    ser.write(bytearray([thrust,yaw,pitch,roll,checksum]))

    time.sleep(0.005)

    line = ser.readline()
    print(line)

    time.sleep(0.005)

ser.write(b'BP')
ser.write(bytearray([0,255,255,255]))
ser.write(b'BP')
ser.write(bytearray([0,255,255,255]))
ser.close()
controller.quit()
pygame.quit()