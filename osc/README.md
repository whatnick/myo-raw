# myo_raw_osc

- Added OSC built-in compatibility to the myo raw data
- Orientation angles accurately computed 
- Optimal usage with myo-firmware-0.8.18-revd

# Usage: 
- python myo_raw_osc -v <verbose> -s <send> -a <[dest IP,dest port]> -a <...> ... 
    -v --verbose: 0 or 1 \t print the messages. Default to 1
    -s --send: 0 or 1 \t send the data over OSC. Default to 0
    -a --address: [ip,port]  add an OSC client to where send the data
        ip 0 will expand to localhost 127.0.0.1
        multiple clients might be registered by reusing the -a option
        
# OSC messages:
- [/myo/emg, (8 values with raw EMG data)]
- [/myo/imu, yaw(azimuth), roll, pitch(elevation), accX, accY, accZ]


# Examples:
- print the data without sending
python myo_raw_osc.py -v 1')
- send to localhost port 57120 and remote ip 127.0.0.4 port 1235
python myo_raw_osc.py -v 0 -s 1 -a [0,57120] -a [127.0.0.4,12345]
        
  
# Extra external dependencies
  - osc 
  - transforms3d
  
Andrés Pérez López ---> www.andresperezlopez.com

------------------------------------------------------------------------------

# myo_raw_osc_gui