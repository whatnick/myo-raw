# # Usage
#   python myo_raw_osc.py -i/--ip -p/--port -s/--send -e/--emgOn -u/--imuOn
#   - -i: IP destination address. Default to 127.0.0.1
#   - -p: UDP destination port. Default to 57120 (sclang)
#   - -s: Send (1) or not (0) data through OSC. Default to 1.
#   - -e: Get (1) or not (0) EMG data
#   - -u: Get (1) or not (0) IMU data
#
# # OSC messages:
#   - [/myo/emg, (8 values with raw EMG data)]
#   - [/myo/imu, yaw(azimuth), roll, pitch(elevation), accX, accY, accZ]

from __future__ import print_function

import sys

from common import *
from myo_raw import *

import OSC
import transforms3d
import getopt


######################################################################
######################################################################

## default settings
send = 0
ip = "127.0.0.1"
port = 57120 # supercollider language
emgOn = 1
imuOn = 1


### get command-line options
try:
    opts, args = getopt.getopt(sys.argv[1:],"s:hi:p:e:u:",
        ["send=","ip=","port=","emgOn=","imuOn"])
except getopt.GetoptError:
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('myo_raw_osc.py -s <sendOn> -i <dest IP> -p <dest port> -e <emgOn> -u <imuOn>')
        sys.exit()
    elif opt in ("-s", "--send"):
        send = int(arg)
    elif opt in ("-i", "--ip"):
        ip = arg
    elif opt in ("-p", "--port"):
        port = int(arg)
    elif opt in ("-e", "--emgOn"):
        emgOn = int(arg)
    elif opt in ("-u", "--imuOn"):
        imuOn = int(arg)


### init
m = MyoRaw()
client = OSC.OSCClient()
client.connect( (ip, port) )

### define handlers
def proc_emg(emg, moving):
    print(emg,moving)
    if send:
        try:
            msg = OSC.OSCMessage()
            msg.setAddress("/myo/emg")
            msg.append(emg)
            client.send(msg)
        except OSC.OSCClientError:
            print('ERROR: Client %s %i does not exist' % (ip, port))
            sys.exit()

def proc_imu(quat, gyro, acc): # acc and gyro values were changed
    # gyro : [pitch/elevation, roll, yaw/azimuth]

    orientation = transforms3d.taitbryan.quat2euler(quat)
    # orientation : [yaw/azimuth, roll, pitch/elevation]
    print(orientation,acc)
    if send:
        try:
            msg = OSC.OSCMessage()
            msg.setAddress("/myo/imu")
            msg.append(orientation)
            msg.append(acc)
            client.send(msg)
        except OSC.OSCClientError:
            print('ERROR: Client %s %i does not exist' % (ip, port))
            sys.exit()



### main process
m.connect()
if emgOn:
    m.add_emg_handler(proc_emg)
if imuOn:
    m.add_imu_handler(proc_imu)

# m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
# m.add_pose_handler(lambda p: print('pose', p))

try:
    while True:
        m.run(1)
finally:
    m.disconnect()
    print()
