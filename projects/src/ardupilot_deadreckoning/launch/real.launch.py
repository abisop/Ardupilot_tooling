import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition as IfConditionType

def generate_launch_description():
    """
    Comprehensive ROS2 launch file for building ArduPilot firmware.
    
    Supports:
    - Multiple vehicle types (copter, heli, plane, rover, sub, antennatracker, AP_Periph)
    - Multiple boards (Pixhawk, Cube, SITL, Linux-based, etc.)
    - Build options (debug, static, parallel jobs)
    - Compiler selection (gcc, clang)
    - Submodule management
    - Firmware upload and installation
    - Specific target building
    
    Reference: BUILD.md in ArduPilot root directory
    """
    
    # ============ CORE BUILD ARGUMENTS ============
    ardupilot_dir_arg = DeclareLaunchArgument(
        'ardupilot_dir',
        default_value=os.path.expanduser('~/Ardupilot_tooling/dev/ardupilot'),
        description='Absolute path to the ardupilot root directory'
    )
    
    board_arg = DeclareLaunchArgument(
        'board',
        default_value='CubeOrange',
        description='Target board: CubeOrange, CubeBlack, Pixhawk1, Pixhawk4, Pixhawk6, Pixracer, navio2, sitl, etc.'
    )
    
    vehicle_type_arg = DeclareLaunchArgument(
        'vehicle_type',
        default_value='copter',
        description='Vehicle type: copter, heli, plane, rover, sub, antennatracker, AP_Periph'
    )
    
    jobs_arg = DeclareLaunchArgument(
        'jobs',
        default_value=str(os.cpu_count() or 4),
        description='Number of parallel build jobs (default: CPU core count)'
    )
    
    # ============ BUILD OPTIONS ============
    debug_arg = DeclareLaunchArgument(
        'debug',
        default_value='false',
        description='Build with debug symbols (useful for SITL debugging)'
    )
    
    static_arg = DeclareLaunchArgument(
        'static',
        default_value='false',
        description='Build statically (required for Bebop/Bebop2)'
    )
    
    compiler_arg = DeclareLaunchArgument(
        'compiler',
        default_value='gcc',
        description='C++ compiler to use: gcc or clang'
    )
    
    # ============ CLEANING OPTIONS ============
    clean_arg = DeclareLaunchArgument(
        'clean',
        default_value='false',
        description='Run clean before build (keeps configure info, current board only)'
    )
    
    distclean_arg = DeclareLaunchArgument(
        'distclean',
        default_value='false',
        description='Run distclean before build (removes ALL build artifacts and configure info)'
    )
    
    submodule_sync_arg = DeclareLaunchArgument(
        'submodule_sync',
        default_value='false',
        description='Resync submodules (useful when switching branches)'
    )
    
    submodule_force_clean_arg = DeclareLaunchArgument(
        'submodule_force_clean',
        default_value='false',
        description='Force clean all submodules and resync (removes all submodules first)'
    )
    
    # ============ UPLOAD/INSTALL OPTIONS ============
    upload_arg = DeclareLaunchArgument(
        'upload',
        default_value='false',
        description='Upload firmware to connected board after build'
    )
    
    install_arg = DeclareLaunchArgument(
        'install',
        default_value='false',
        description='Install firmware to specified DESTDIR (for package building)'
    )
    
    destdir_arg = DeclareLaunchArgument(
        'destdir',
        default_value='/tmp/ardupilot_install',
        description='Installation directory for install command (Linux boards)'
    )
    
    rsync_dest_arg = DeclareLaunchArgument(
        'rsync_dest',
        default_value='',
        description='Rsync destination for Linux boards (e.g., root@192.168.1.2:/)'
    )
    
    # ============ SPECIFIC TARGET OPTIONS ============
    build_target_arg = DeclareLaunchArgument(
        'build_target',
        default_value='',
        description='Specific build target (e.g., bin/arducopter, tests/test_math). If set, overrides vehicle_type'
    )
    
    list_targets_arg = DeclareLaunchArgument(
        'list_targets',
        default_value='false',
        description='List all available build targets and exit'
    )
    
    # ============ INFO OPTIONS ============
    list_boards_arg = DeclareLaunchArgument(
        'list_boards',
        default_value='false',
        description='List all supported boards and exit'
    )
    
    help_arg = DeclareLaunchArgument(
        'help',
        default_value='false',
        description='Show WAF help and exit'
    )
    
    # ============ PROCESS DEFINITIONS ============
    
    # 1. List boards
    list_boards_process = ExecuteProcess(
        cmd=['./waf', 'list_boards'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='list_boards',
        condition=IfConditionType(LaunchConfiguration('list_boards'))
    )
    
    # 2. List all targets
    list_targets_process = ExecuteProcess(
        cmd=['./waf', 'list'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='list_targets',
        condition=IfConditionType(LaunchConfiguration('list_targets'))
    )
    
    # 3. WAF help
    help_process = ExecuteProcess(
        cmd=['./waf', '--help'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='waf_help',
        condition=IfConditionType(LaunchConfiguration('help'))
    )
    
    # 4. Submodule force clean
    submodule_force_clean_process = ExecuteProcess(
        cmd=['./waf', 'submodule_force_clean'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='submodule_force_clean',
        condition=IfConditionType(LaunchConfiguration('submodule_force_clean'))
    )
    
    # 5. Submodule sync
    submodule_sync_process = ExecuteProcess(
        cmd=['./waf', 'submodulesync'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='submodule_sync',
        condition=IfConditionType(LaunchConfiguration('submodule_sync'))
    )
    
    # 6. Distclean
    distclean_process = ExecuteProcess(
        cmd=['./waf', 'distclean'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='distclean',
        condition=IfConditionType(LaunchConfiguration('distclean'))
    )
    
    # 7. Clean
    clean_process = ExecuteProcess(
        cmd=['./waf', 'clean'],
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='clean',
        condition=IfConditionType(LaunchConfiguration('clean'))
    )
    
    # 8. Configure - handles debug, static, compiler, and rsync options
    configure_cmd = [
        'bash', '-c',
        'BOARD=$1; DEBUG=$2; STATIC=$3; COMPILER=$4; RSYNC=$5; '
        'CMD="./waf configure --board $BOARD"; '
        '[[ "$DEBUG" == "true" ]] && CMD="$CMD --debug"; '
        '[[ "$STATIC" == "true" ]] && CMD="$CMD --static"; '
        '[[ "$COMPILER" == "clang" ]] && CMD="CXX=clang++ CC=clang $CMD"; '
        '[[ -n "$RSYNC" ]] && CMD="$CMD --rsync-dest $RSYNC"; '
        'exec $CMD',
        'bash',
        LaunchConfiguration('board'),
        LaunchConfiguration('debug'),
        LaunchConfiguration('static'),
        LaunchConfiguration('compiler'),
        LaunchConfiguration('rsync_dest'),
    ]
    
    configure_process = ExecuteProcess(
        cmd=configure_cmd,
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='configure'
    )
    
    # 9. Build vehicle type or specific target
    build_cmd = [
        'bash', '-c',
        'VEHICLE=$1; TARGET=$2; JOBS=$3; '
        'if [[ -n "$TARGET" ]]; then '
        '  exec ./waf --targets "$TARGET" -j"$JOBS"; '
        'else '
        '  exec ./waf "$VEHICLE" -j"$JOBS"; '
        'fi',
        'bash',
        LaunchConfiguration('vehicle_type'),
        LaunchConfiguration('build_target'),
        LaunchConfiguration('jobs'),
    ]
    
    build_process = ExecuteProcess(
        cmd=build_cmd,
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='build'
    )
    
    # 10. Upload
    upload_cmd = [
        'bash', '-c',
        'VEHICLE=$1; TARGET=$2; '
        'if [[ -n "$TARGET" ]]; then '
        '  exec ./waf --targets "$TARGET" --upload; '
        'else '
        '  exec ./waf "$VEHICLE" --upload; '
        'fi',
        'bash',
        LaunchConfiguration('vehicle_type'),
        LaunchConfiguration('build_target'),
    ]
    
    upload_process = ExecuteProcess(
        cmd=upload_cmd,
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='upload',
        condition=IfConditionType(LaunchConfiguration('upload'))
    )
    
    # 11. Install
    install_cmd = [
        'bash', '-c',
        'DESTDIR=$1; VEHICLE=$2; TARGET=$3; '
        'mkdir -p "$DESTDIR"; '
        'if [[ -n "$TARGET" ]]; then '
        '  DESTDIR="$DESTDIR" ./waf --targets "$TARGET" install; '
        'else '
        '  DESTDIR="$DESTDIR" ./waf "$VEHICLE" install; '
        'fi',
        'bash',
        LaunchConfiguration('destdir'),
        LaunchConfiguration('vehicle_type'),
        LaunchConfiguration('build_target'),
    ]
    
    install_process = ExecuteProcess(
        cmd=install_cmd,
        cwd=LaunchConfiguration('ardupilot_dir'),
        output='screen',
        name='install',
        condition=IfConditionType(LaunchConfiguration('install'))
    )
    
    return LaunchDescription([
        # Core arguments
        ardupilot_dir_arg,
        board_arg,
        vehicle_type_arg,
        jobs_arg,
        
        # Build options
        debug_arg,
        static_arg,
        compiler_arg,
        
        # Clean/submodule options
        clean_arg,
        distclean_arg,
        submodule_sync_arg,
        submodule_force_clean_arg,
        
        # Upload/Install options
        upload_arg,
        install_arg,
        destdir_arg,
        rsync_dest_arg,
        
        # Target options
        build_target_arg,
        list_targets_arg,
        
        # Info options
        list_boards_arg,
        help_arg,
        
        # Processes
        list_boards_process,
        list_targets_process,
        help_process,
        submodule_force_clean_process,
        submodule_sync_process,
        distclean_process,
        clean_process,
        configure_process,
        build_process,
        upload_process,
        install_process,
    ])
