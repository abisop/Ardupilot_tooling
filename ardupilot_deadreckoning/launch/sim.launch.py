import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

def generate_launch_description():
    # Declare launch arguments
    ardupilot_dir_arg = DeclareLaunchArgument(
        'ardupilot_dir',
        default_value=os.path.expanduser('~/drone/ardupilot'),
        description='Absolute path to the ardupilot root directory'
    )
    
    gazebo_world_arg = DeclareLaunchArgument(
        'gazebo_world',
        default_value='iris_runway.sdf',
        description='Gazebo SDF world file to load'
    )

    layout_file_arg = DeclareLaunchArgument(
        'layout_file',
        default_value=os.path.expanduser('~/drone/simulations/ros2_ws/src/Ardupilot/Flight_Analysis/Ardupilot/plotjuggler/copter.xml'),
        description='Absolute path to PlotJuggler XML layout file'
    )

    bin_file_arg = DeclareLaunchArgument(
        'bin_file',
        default_value=os.path.expanduser('~/drone/simulations/ros2_ws/src/Ardupilot/Flight_Analysis/Ardupilot/logs/00000001.BIN'),
        description='Absolute path to the binary log/data file'
    )

    # 1. Launch Gazebo (gz sim)
    gazebo_process = ExecuteProcess(
        cmd=['gz', 'sim', '-v4', '-r', LaunchConfiguration('gazebo_world')],
        output='screen',
        name='gazebo_sim'
    )

    # 2. Launch ArduPilot SITL (sim_vehicle.py) in gnome-terminal
    ardupilot_process = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--',
            PathJoinSubstitution([LaunchConfiguration('ardupilot_dir'), 'Tools', 'autotest', 'sim_vehicle.py']),
            '-v', 'ArduCopter',
            '-f', 'gazebo-iris',
            '--model', 'JSON',
            '--map',
            '--console'
        ],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='ardupilot_sitl'
    )

    # 3. Launch PlotJuggler with layout (.xml) and data (.bin)
    plotjuggler_process = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'plotjuggler', 'plotjuggler',
            '-l', LaunchConfiguration('layout_file'),
            '-d', LaunchConfiguration('bin_file')
        ],
        output='screen',
        name='plotjuggler'
    )

    return LaunchDescription([
        ardupilot_dir_arg,
        gazebo_world_arg,
        layout_file_arg,
        bin_file_arg,
        #gazebo_process,
        ardupilot_process,
        plotjuggler_process
    ])