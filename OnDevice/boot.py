import storage
import supervisor
import deviceCode

storage.remount("/", False)

if  supervisor.runtime.serial_connected:
    print("entering debugging mode")

else: 
    deviceCode.main()