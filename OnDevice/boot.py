import storage
import supervisor
import deviceCode

if  supervisor.runtime.serial_connected:
    storage.remount("/", False)

else: 
    deviceCode.main()