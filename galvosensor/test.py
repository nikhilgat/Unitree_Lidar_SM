import serial
import time

def rectangel(size, mP= (32768, 32768), fak=0.0):
    speed = 4000
    xM = mP[0]
    yM = mP[1]

    p1xM = int(xM - ((size / 2) * ((1-fak)))) #links oben
    p1yM = int(yM - ((size / 2) * 1))

    p2xM = int(xM - ((size / 2) * 1))
    p2yM = int(yM + ((size / 2) * 1))

    p3xM = int(xM + ((size / 2) * 1))
    p3yM = int(yM + ((size / 2) * 1))

    p4xM = int(xM + ((size / 2) * (1-fak)))
    p4yM = int(yM - ((size / 2) * 1))

    msg = f'SC\nX{p1xM}Y{p1yM}F{speed}W3000E\nX{p2xM}Y{p2yM}F{speed}W3000E\nX{p3xM}Y{p3yM}F{speed}W3000E\nX{p4xM}Y{p4yM}F{speed}W3000E\nM11eR'  # rectangle
    return msg

def square(size):
    speed = 4000
    xM = 32768
    yM = 32768

    p1xM = int(xM - size / 4)
    p1yM = int(yM - size / 2)

    p2xM = int(xM - size / 4)
    p2yM = int(yM + size / 2)

    p3xM = int(xM + size / 4)
    p3yM = int(yM + size / 2)

    p4xM = int(xM + size / 4)
    p4yM = int(yM - size / 2)

    msg = f'SC\nX{p1xM}Y{p1yM}F{speed}W3000E\nX{p2xM}Y{p2yM}F{speed}W3000E\nX{p3xM}Y{p3yM}F{speed}W3000E\nX{p4xM}Y{p4yM}F{speed}W3000E\nM11eR'  # rectangle
    return msg

def scanX(ser, steps=1000):
    startX = 0
    _msg = "X"
    while True:
        #msg = _msg + str(startX) + "Y22768F0e"
        msg = _msg + str(startX) + "Y50000F0e"
        ser.write(bytes(msg, 'utf-8'))
        time.sleep(0.1)
        if startX > 65535:
            print("done")
            break
        startX = startX + steps
    ser.write(bytes("S", 'utf-8'))

def scanY(ser, steps=1000):
    startY = 0
    _msg = "Y"
    while True:
        #msg = _msg + str(startX) + "Y22768F0e"
        msg = "X32768F0e" + _msg + str(startY)
        ser.write(bytes(msg, 'utf-8'))
        time.sleep(0.1)
        if startY > 65535:
            print("done")
            break
        startY = startY + steps
    ser.write(bytes("S", 'utf-8'))


ser = serial.Serial('COM5', baudrate=1000000)
ser.write(bytes("M11e", 'utf-8'))   #Laser on

S = 60000
D = 0.0
while S > 0:
    X = rectangel(S, ((32768, int(65535-S/2))), fak=D)
    ser.write(bytes(X, 'utf-8'))
    S = input("S")
    S = int(S)
    D = input("D")
    D = float(D)
    ser.write(bytes("S", 'utf-8'))


while True:
    msg = "X0Y32768F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

    msg = "X32768Y32768F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

    msg = "X65535Y32768F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

    msg = "X32768Y0F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

    msg = "X32768Y32768F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

    msg = "X32768Y655358F0e"
    ser.write(bytes(msg, 'utf-8'))
    input()
    ser.write(bytes("S", 'utf-8'))

scanX(ser)
scanY(ser)
#
# while True:
#     pass
#
# X ="SC\nX22768Y22768F0W5000E\nX42768Y22768F0W5000E\nX42768Y42768F0W5000E\nX22768Y42768F0W5000E\nM11eR"     # 4 Points forming an rectangle
# X ="SC\nX22768Y22768F0W5000E\nX42768Y22768F0W5000E\nX42768Y32768F0W5000E\nX22768Y32768F0W5000E\nX22768Y42768F0W5000E\nX42768Y42768F0W5000E\nM11eR" # 6 Points forming an S
# X ="SC\nX32768Y42768F3000E\nX22768Y22768F3000E\nX42768Y22768F3000E\nM11eR" # triangle
# X ="SC\nX22768Y22768F3000E\nX42768Y22768F3000E\nX42768Y42768F3000E\nX22768Y42768F3000E\nM11eR"     # rectangle
# X ="SC\nX0Y0F3000E\nX0Y65535F3000E\nX65535Y65535F3000E\nX65535Y0F3000E\nM11eR"     # rectangle
# speed = 1000
# X =f'SC\nX0Y0F{speed}W3000E\nX0Y65535F{speed}W3000E\nX65535Y65535F{speed}W3000E\nX65535Y0F{speed}W3000E\nM11eR'     # rectangle
# print(X)
# ser.write(bytes(X, 'utf-8'))
#
while True:
    pass