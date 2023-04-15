from time import sleep
import _thread
 
def core0():
    global lock
    global previous
    global now
    
    print("Core 0 got there first..!")
    
    while True:
        lock.acquire()
        
        print("This is core 0 running :)")
        
        newFib = previous + now
        previous = now
        now = newFib
         
        print("Next fib number:", now)
        sleep(1)
        
        lock.release()
 
     
def core1():
    global lock
    global previous
    global now
    
    print("Core 1 got there first..!")
    
    while True:
        lock.acquire()
        
        print("This is core 1 running :0")
        
        newFib = previous + now
        previous = now
        now = newFib
        
        print("Next fib number:", now)
        sleep(1)
         
        lock.release()
        
        
previous = 0
now = 1        
lock = _thread.allocate_lock()
# core1 or core1()? 
second_thread = _thread.start_new_thread(core1, ())
core0()
