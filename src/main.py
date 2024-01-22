#!/usr/bin/env python3
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import cv2
from geometry_msgs.msg import PoseStamped, Twist
from mavros_msgs.srv import CommandBool, SetMode

rospy.init_node("offboard", anonymous=True)

velocity = 0


def linear_velocity_callback(date):
    global velocity
    velocity = date.twist.linear.x


setpoint_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
arming_s = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
set_mode = rospy.ServiceProxy("/mavros/set_mode", SetMode)
vel = rospy.Subscriber('/mavros/local_position/velocity_body', Twist, linear_velocity_callback)
rate = rospy.Rate(20)
count1 = 0
left = [(0.707, 0.707), (0, 1), (0.707, -0.707), (0, -1)]

array = []

point = PoseStamped()
point.pose.position.x = 1
point.pose.position.y = 1
point.pose.position.z = 2

x_pos, y_pos, z_pos = 0, 0, 0
front_qr, down_qr = None, None

for i in range(10):
    setpoint_pub.publish(point)
    rate.sleep()

set_mode(0, "OFFBOARD")
arming_s(True)


class DroneCamera:

    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub_down = rospy.Subscriber('/iris_rplidar/usb_cam/image_raw', Image, self.image_callback_down)
        self.image_sub_front = rospy.Subscriber('/r200/image_raw', Image, self.image_callback_front)

    def image_callback_front(self, data):
        global front_qr
        # Получаем изображение из сообщения ROS
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, 'bgr8')
            front_qr = scan_qr(cv_image)
        except CvBridgeError as e:
            print(e)
        return

    def image_callback_down(self, data):
        global down_qr
        # Получаем изображение из сообщения ROS
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, 'bgr8')
            down_qr = scan_qr(cv_image)
        except CvBridgeError as e:
            print(e)
        return


def read():
    return point.pose.position.x, point.pose.position.y, point.pose.position.z


def rotate():
    global count1
    if count1 == len(left) - 1:
        count1 = 0
    else:
        count1 += 1
        point.pose.orientation.z, point.pose.orientation.w = left[count1]


def scan_qr(image):
    qrCodeDetector = cv2.QRCodeDetector()

    decodedText, points, _ = qrCodeDetector.detectAndDecode(image)

    if points is not None:
        return decodedText


def get_local_pos(date):
    global x_pos, y_pos, z_pos

    position = date.pose.position

    x_pos, y_pos, z_pos = position.x, position.y, position.z

    position_sub = rospy.Subscriber("/mavros/local_position/pose", PoseStamped, get_local_pos)


def is_reached():
    target_x, target_y, target_z = read()

    distance = ((x_pos - target_x) ** 2 + (y_pos - target_y) ** 2 + (z_pos - target_z) ** 2) ** 0.5

    tolerance = 0.2

    return distance < tolerance


camera = DroneCamera()

while not rospy.is_shutdown():
    if (front_qr is not None and down_qr is not None) and (front_qr != " " and down_qr != " "):
        if front_qr == down_qr:
            point.pose.position.x += 5
            print(f"Front: {front_qr}, Down: {down_qr}")
        elif front_qr != down_qr:
            rotate()
            print(f"Front: {front_qr}, Down: {down_qr}")
        setpoint_pub.publish(point)
    rate.sleep()
