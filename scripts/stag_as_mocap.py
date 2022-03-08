#!/usr/bin/python3

import rospy as rp

import numpy as np

from stag_ros.msg import STagMarker, STagMarkerArray
from geometry_msgs.msg import PoseStamped

from tf.transformations import quaternion_matrix, quaternion_from_matrix


class STagAsMoCap():

    def __init__(self,):
        rp.init_node('stag_as_mocap_node')

        self.H_cam_drone = np.array([[0, -1,  0,  0.0564],
                                     [-1,  0,  0,  0.1257],
                                     [0,  0, -1, -0.0219],
                                     [0,  0,  0,  1.0]])

        self.stag_id = 7

        # Subscriber
        self.stag_sub = rp.Subscriber(
            '/stag_ros/markers', STagMarkerArray, self.stag_callback, queue_size=1)

        # Publisher
        self.pose_pub = rp.Publisher(
            '/mavros/vision_pose/pose', PoseStamped, queue_size=1)

        rp.spin()

    def stag_callback(self, msg):
        if (len(msg.stag_array) > 0):
            for i in range(len(msg.stag_array)):
                if msg.stag_array[i].id.data == self.stag_id:
                    H_cam_marker = quaternion_matrix([msg.stag_array[i].pose.orientation.x,
                                                      msg.stag_array[i].pose.orientation.y,
                                                      msg.stag_array[i].pose.orientation.z,
                                                      msg.stag_array[i].pose.orientation.w])
                    H_cam_marker[0, 3] = msg.stag_array[i].pose.position.x
                    H_cam_marker[1, 3] = msg.stag_array[i].pose.position.y
                    H_cam_marker[2, 3] = msg.stag_array[i].pose.position.z

                    H_marker_cam = np.linalg.inv(H_cam_marker)

                    H_marker_drone = np.matmul(H_marker_cam, self.H_cam_drone)
                    q_drone = quaternion_from_matrix(H_marker_drone)

                    drone_pose_msg = PoseStamped()
                    drone_pose_msg.header = msg.stag_array[i].header
                    drone_pose_msg.pose.position.x = H_marker_drone[0, 3]
                    drone_pose_msg.pose.position.y = H_marker_drone[1, 3]
                    drone_pose_msg.pose.position.z = H_marker_drone[2, 3]
                    drone_pose_msg.pose.orientation.w = q_drone[3]
                    drone_pose_msg.pose.orientation.x = q_drone[0]
                    drone_pose_msg.pose.orientation.y = q_drone[1]
                    drone_pose_msg.pose.orientation.z = q_drone[2]

                    self.pose_pub.publish(drone_pose_msg)


if __name__ == '__main__':
    STagAsMoCap()
