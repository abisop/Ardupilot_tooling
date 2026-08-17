import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition as IfConditionType

def generate_launch_description():
    """
    Launch file for analyzing ArduPilot log files using PyMAVLink, PlotJuggler, or MAVExplorer.
    
    Supports:
    - Loading BIN (binary) log files directly with PlotJuggler (via ArduPilot BIN plugin)
    - Extracting and analyzing log data using PyMAVLink
    - Visualizing with MAVExplorer (3D visualization)
    
    Log file types:
    - *.BIN: ArduPilot binary logs (from SITL or real hardware)
    """
    
    # ============ LOG FILE ARGUMENTS ============
    log_dir_arg = DeclareLaunchArgument(
        'log_dir',
        default_value=os.path.expanduser('~/Ardupilot_tooling/Flight_Analysis/Ardupilot/logs'),
        description='Directory containing log files'
    )
    
    log_file_arg = DeclareLaunchArgument(
        'log_file',
        default_value='',
        description='Specific log file to analyze (absolute path or relative to log_dir)'
    )
    
    # ============ TOOL SELECTION ============
    tool_arg = DeclareLaunchArgument(
        'tool',
        default_value='plotjuggler',
        description='Analysis tool: plotjuggler, mavexplorer, or pymavlink'
    )
    
    # ============ PLOTJUGGLER OPTIONS ============
    plotjuggler_layout_arg = DeclareLaunchArgument(
        'plotjuggler_layout',
        default_value=os.path.expanduser('~/Ardupilot_tooling/Flight_Analysis/Ardupilot/plotjuggler/copter.xml'),
        description='PlotJuggler XML layout file for dashboard configuration'
    )
    
    # ============ MAVEXPLORER OPTIONS ============
    mavexplorer_arg = DeclareLaunchArgument(
        'mavexplorer',
        default_value='false',
        description='Use MAVExplorer for 3D visualization (default: PlotJuggler)'
    )
    
    # ============ PYMAVLINK ANALYSIS OPTIONS ============
    pymavlink_script_arg = DeclareLaunchArgument(
        'pymavlink_script',
        default_value='',
        description='Python script for custom PyMAVLink analysis'
    )
    
    message_type_arg = DeclareLaunchArgument(
        'message_type',
        default_value='',
        description='Specific message type to extract (e.g., GPS, IMU, ATTITUDE)'
    )
    
    # ============ DATA EXTRACTION OPTIONS ============
    extract_arg = DeclareLaunchArgument(
        'extract',
        default_value='false',
        description='Extract and print message data from log file'
    )
    
    stats_arg = DeclareLaunchArgument(
        'stats',
        default_value='false',
        description='Show log file statistics'
    )
    
    # ============ PROCESS DEFINITIONS ============
    
    # 1. List log files in directory
    list_logs_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_DIR=$1; echo "Log files in $LOG_DIR:"; ls -lh "$LOG_DIR"/*.{BIN,LOG,bin,log,csv} 2>/dev/null | tail -20',
            'bash',
            LaunchConfiguration('log_dir'),
        ],
        output='screen',
        name='list_logs'
    )
    
    # 2. Get log file stats using PyMAVLink
    # Usage: python3 -c "import pymavlink.DFReader as dfr; log = dfr.DFReader_binary(filename); print(log.messages[0], log.messages[1]...)"
    stats_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_FILE=$1; python3 << \'EOF\'\n'
            'import sys\n'
            'sys.path.insert(0, "$ARDUPILOT_DIR/modules/mavlink/pymavlink")\n'
            'try:\n'
            '    from pymavlink import DFReader\n'
            '    log = DFReader.DFReader_binary("$LOG_FILE")\n'
            '    print(f"Log file: {LOG_FILE}")\n'
            '    print(f"Total messages: {log.count_of_type}")\n'
            '    print(f"Available message types: {list(log.count_of_type.keys())[:10]}...")\n'
            'except Exception as e:\n'
            '    print(f"Error: {e}")\n'
            'EOF',
            'bash',
            LaunchConfiguration('log_file'),
        ],
        output='screen',
        name='log_stats',
        condition=IfConditionType(LaunchConfiguration('stats'))
    )
    
    # 3. PlotJuggler with BIN log file and layout
    plotjuggler_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_FILE=$1; LAYOUT=$2; '
            'if [[ -z "$LOG_FILE" ]]; then '
            '  echo "No log file specified, launching PlotJuggler empty..."; '
            '  exec plotjuggler; '
            'elif [[ "$LAYOUT" != "" ]] && [[ -f "$LAYOUT" ]]; then '
            '  echo "Launching PlotJuggler with $LOG_FILE and layout $LAYOUT"; '
            '  exec plotjuggler -l "$LAYOUT" -d "$LOG_FILE"; '
            'else '
            '  echo "Launching PlotJuggler with $LOG_FILE"; '
            '  exec plotjuggler -d "$LOG_FILE"; '
            'fi',
            'bash',
            LaunchConfiguration('log_file'),
            LaunchConfiguration('plotjuggler_layout'),
        ],
        output='screen',
        name='plotjuggler',
        condition=IfConditionType(LaunchConfiguration('tool'), negate=True)  # Will be updated below
    )
    
    # 4. MAVExplorer for 3D visualization
    mavexplorer_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_FILE=$1; '
            'if [[ -z "$LOG_FILE" ]]; then '
            '  echo "No log file specified for MAVExplorer"; '
            '  exit 1; '
            'fi; '
            'echo "Launching MAVExplorer with $LOG_FILE"; '
            'exec MAVExplorer.py "$LOG_FILE"',
            'bash',
            LaunchConfiguration('log_file'),
        ],
        output='screen',
        name='mavexplorer'
    )
    
    # 5. Extract specific message type using PyMAVLink
    extract_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_FILE=$1; MSG_TYPE=$2; python3 << \'EOF\'\n'
            'import sys\n'
            'sys.path.insert(0, "$ARDUPILOT_DIR/modules/mavlink/pymavlink")\n'
            'from pymavlink import DFReader\n'
            'try:\n'
            '    log = DFReader.DFReader_binary("$LOG_FILE")\n'
            '    if "$MSG_TYPE":\n'
            '        print(f"\\nMessages of type: {MSG_TYPE}")\n'
            '        count = 0\n'
            '        for msg in log.messages:\n'
            '            if msg.name == "$MSG_TYPE":\n'
            '                print(msg)\n'
            '                count += 1\n'
            '                if count >= 10:  # Print first 10\n'
            '                    print("...")\n'
            '                    break\n'
            '    else:\n'
            '        print("Available message types:")\n'
            '        for msg_type in log.count_of_type.keys():\n'
            '            count = log.count_of_type[msg_type]\n'
            '            print(f"  {msg_type}: {count} messages")\n'
            'except Exception as e:\n'
            '    print(f"Error: {e}")\n'
            'EOF',
            'bash',
            LaunchConfiguration('log_file'),
            LaunchConfiguration('message_type'),
        ],
        output='screen',
        name='extract_messages',
        condition=IfConditionType(LaunchConfiguration('extract'))
    )
    
    # 6. Custom PyMAVLink analysis script
    pymavlink_analysis_process = ExecuteProcess(
        cmd=[
            'bash', '-c',
            'LOG_FILE=$1; SCRIPT=$2; '
            'if [[ ! -f "$SCRIPT" ]]; then '
            '  echo "Script not found: $SCRIPT"; '
            '  exit 1; '
            'fi; '
            'echo "Running analysis script: $SCRIPT"; '
            'export ARDUPILOT_LOG_FILE="$LOG_FILE"; '
            'python3 "$SCRIPT" "$LOG_FILE"',
            'bash',
            LaunchConfiguration('log_file'),
            LaunchConfiguration('pymavlink_script'),
        ],
        output='screen',
        name='pymavlink_analysis',
        condition=IfConditionType(LaunchConfiguration('pymavlink_script'))
    )
    
    return LaunchDescription([
        # Log file arguments
        log_dir_arg,
        log_file_arg,
        
        # Tool selection
        tool_arg,
        
        # PlotJuggler options
        plotjuggler_layout_arg,
        
        # MAVExplorer options
        mavexplorer_arg,
        
        # PyMAVLink options
        pymavlink_script_arg,
        message_type_arg,
        extract_arg,
        stats_arg,
        
        # Processes
        list_logs_process,
        stats_process,
        plotjuggler_process,
        mavexplorer_process,
        extract_process,
        pymavlink_analysis_process,
    ])
