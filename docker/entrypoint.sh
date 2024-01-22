#!/bin/bash
set -e

# setup ros environment
source "/opt/ros/$ROS_DISTRO/setup.bash" --

cp -r /opt/ros/$ROS_DISTRO/lib/python3/dist-packages/* /home/mushroom/catkin_ws/dist-packages/

exec "$@"
