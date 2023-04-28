import socket
import time
import numpy as np

IP = '127.0.0.1'
PORT = 5700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Start degrees for x, y, z
# x and y as one variable, will be calculated wit sin and cos
# z starts off 15 degrees for different sinus data
angle_x_y = 0
angle_z = 15

# calculates sinus (from https://numpy.org/doc/stable/reference/generated/numpy.sin.html)
def get_sin(angle):
    return np.sin(angle * np.pi / 180)

# calculates cosinus
def get_cos(angle):
    return np.cos(angle * np.pi / 180)

# checks if angle is at a full turn
def check_full_turn (angle):
    if angle == 360:
        return True
    return False

# random number gets checked for modulo 5, returns 1 for pressed when number can be divided by 5
def get_button_one_press():
    if np.random.randint(0,20) % 5 != 0:
        return 0
    return 1

while True:
    # creates the data string for accelerometer data
    data_string_accelerometer = f'{{"x":{get_sin(angle_x_y)},"y":{get_cos(angle_x_y)},"z":{get_sin(angle_z)}}}'
    message_accelerometer = '{"accelerometer" : ' + data_string_accelerometer + '}'

    # creates button one data/message
    message_button_one = f'{{"button_1": {get_button_one_press()}}}'

    print(message_accelerometer)
    print(message_button_one)

    sock.sendto(message_accelerometer.encode(), (IP, PORT))
    sock.sendto(message_button_one.encode(), (IP, PORT))

    # check for whole turn and if so sets it back to 0 to prevent big numbers
    if (check_full_turn(angle_x_y)):
        angle_x_y = 0

    if (check_full_turn(angle_z)):
        angle_z = 0

    # angle adds up 15 degrees for sinus/cosinus curve   
    angle_x_y += 15
    angle_z += 15

    time.sleep(0.5)