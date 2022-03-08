#!/usr/bin/python3

import rospy as rp

import roslaunch
import threading
import time

from nav_msgs.msg import Odometry


class Launcher():

    def __init__(self,):
        rp.init_node('t265_node_launcher')

        # Launch from .launch file
        self.uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(self.uuid)
        self.launch = None
        self.start_node()

        self.odom_sub = rp.Subscriber(
            '/camera/odom/sample', Odometry, self.odom_callback, queue_size=1)

        self.last_time = None

        t = threading.Thread(self.keep_alive())
        t.start()
        rp.spin()

    def start_node(self,):
        rp.loginfo('Starting node')
        self.launch = roslaunch.parent.ROSLaunchParent(self.uuid, ['/home/usrl/git/px4_with_vision/launch/t265.launch'])
        self.launch.start()

    def stop_node(self,):
        rp.loginfo('Killing node')
        self.launch.shutdown()
        self.launch = None

    def odom_callback(self, msg):
        self.last_time = msg.header.stamp

    def keep_alive(self,):
        r = rp.Rate(25)
        while not rp.is_shutdown():
            if self.last_time is not None:
                dt = rp.Time.now() - self.last_time

                if (dt.to_sec() > 0.5):
                    rp.loginfo('Node is not publishing anything. Kill and restart')
                    self.stop_node()
                    time.sleep(1)
                    self.start_node()
                    self.last_time = None

            r.sleep()


if __name__ == '__main__':
    Launcher()
