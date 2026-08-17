import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    # Expand '~' to full home directory path
    appimage_path = os.path.expanduser('~/QGroundControl-x86_64.AppImage')

    qgc_process = ExecuteProcess(
        cmd=[appimage_path],
        output='screen',
    )

    return LaunchDescription([
        qgc_process
        ])