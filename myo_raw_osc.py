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
verbose = 1
send = 1
ip = "127.0.0.1"
port = 7110 # myo_raw_osc_gui.py default port
receiveIp = "127.0.0.1"
receivePort = 7111

addressList = []
clientList = []

### get command-line options
try:
    opts, args = getopt.getopt(sys.argv[1:],"hv:s:d:r:",
        ["verbose=","send=","destination=","receive="])
except getopt.GetoptError:
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('\n')
        print ('myo_raw_osc.py: send myo raw data over osc ')
        print('Usage: -v <verbose> -s <send> -d <[dest IP,dest port]> -d <...> ... -r <[receive IP,receive port]>')
        print('-v --verbose: 0 or 1 \t print the messages. Default to 1')
        print('-s --send: 0 or 1 \t send the data over OSC. Default to 1')
        print('-d --destination: [ip,port]  add an OSC client to where send the data')
        print('\t \t \t ip 0 will expand to localhost 127.0.0.1')
        print('\t \t \t multiple clients might be registered by reusing the -a option')    
        print('\t \t \t Default address set to "127.0.0.1",7110')      
        print('-r --receive: [ip,port]  IP address and port where to receive OSC incoming messages (vibration)')
        print('\t \t \t ip 0 will expand to localhost 127.0.0.1')
        print('\n')
        
        print('Output OSC messages:')
        print('[/myo/emg, (8 values with raw EMG data)]')
        print('[/myo/imu, yaw(azimuth), roll, pitch(elevation), accX, accY, accZ]')
        print('\n')
        
        print('Input OSC messages:')
        print('[/myo/vib, {integer between 1 (shorter) and 3 (longer)}]')
        print('\n')

        print('Examples:')
        print('//print the data without sending')
        print('python myo_raw_osc.py -v 1')
        print('//send to localhost port 57120 and remote ip 127.0.0.4 port 1235')
        print('python myo_raw_osc.py -v 0 -s 1 -d [0,57120] -d [127.0.0.4,12345]')
        print('\n')
        sys.exit()
    elif opt in ("-v", "--verbose"):
        verbose = int(arg)
    elif opt in ("-s", "--send"):
        send = int(arg)
    elif opt in ("-d", "--destination"):
        print('DESTINATION')
        args = arg.split(",")
        ip = args[0].split("[")[1]         #remove initial [
        if ip == "0":
            ip="127.0.0.1"
        port = int(args[1].split("]")[0])  #remove final ] and cast to int
        address = {'ip':ip, 'port':port}
        addressList.append(address)
    elif opt in ("-r", "--receive"):
        args = arg.split(",")
        receiveIp = args[0].split("[")[1]         #remove initial [
        if receiveIp == "0":
            receiveIp="127.0.0.1"
        receivePort = int(args[1].split("]")[0])  #remove final ] and cast to int
    
      
### init
m = MyoRaw()
orientation=[]

# instanciate osc clients
if len(addressList)==0:
    addressList.append({'ip':ip,'port':port}) #dafult values
for address in addressList:
    client = OSC.OSCClient()
    client.connect( (address['ip'],address['port']) )
    clientList.append(client)
    
# instanciate osc server
server = OSC.OSCServer( (receiveIp, receivePort) )
server.timeout = 0
    
def user_callback_vib(path, tags, args, source):
    m.vibrate(args[0])
    
server.addMsgHandler( "/myo/vib", user_callback_vib )


### define handlers

###### orientation transform
def proc_imu_transform(quat, gyro, acc):
    global orientation
     # orientation : [yaw/azimuth, roll, pitch/elevation]
    orientation = transforms3d.taitbryan.quat2euler(quat)

###### verbose
def proc_emg_verb(emg,moving):
    # len: (8,1)
    print(emg,moving)
def proc_imu_verb(quat, gyro, acc): # acc and gyro values were changed
    # gyro : [pitch/elevation, roll, yaw/azimuth]
    # orientation : [yaw/azimuth, roll, pitch/elevation]
    # len: (3,3)
    print(orientation,acc)
    
###### OSC
def proc_emg_osc(emg, moving):
    msg = OSC.OSCMessage()
    msg.setAddress("/myo/emg")
    emgFloat = []
    for v in emg:
        emgFloat.append(float(v))  
    msg.append(emgFloat)
    sendOSC(msg)
def proc_imu_osc(quat, gyro, acc):
    msg = OSC.OSCMessage()
    msg.setAddress("/myo/imu")
    msg.append(orientation)
    msg.append(acc)
    sendOSC(msg)
    
def sendOSC(msg):
    for client in clientList:
        try:
            client.send(msg)
        except OSC.OSCClientError:
            print('ERROR: Client %s %i does not exist' % (client.address()[0], client.address()[1]))
#            sys.exit()
            
            
### main process
m.connect()

m.add_imu_handler(proc_imu_transform)
if verbose:
    m.add_emg_handler(proc_emg_verb)
    m.add_imu_handler(proc_imu_verb)
if send:
    m.add_emg_handler(proc_emg_osc)
    m.add_imu_handler(proc_imu_osc)
     
# m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
# m.add_pose_handler(lambda p: print('pose', p))

try:
    while True:
        m.run(1)
        server.handle_request()
finally:
    m.disconnect()
    print()
