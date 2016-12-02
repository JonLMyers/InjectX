import sys
import win32api
from ctypes import *
kernel32 = win32api.kernel32

#Hardcoded globals used when interacting with the WinAPI.
PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = ( 0x000F0000 | 0x00100000 | 0xFFF )
VIRTUAL_MEM = ( 0x1000 | 0x2000 )

def inject(pid, dllPath):
    dllLen = len(dllPath)

    #Create the handle to our target process.
    hTargetProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, false, int(pid))
    if not hTargetProcess:
        print("Oh boy... I could not create a handle to the process!  Your PID is: %s", PID)
        sys.exit(0)

    #Allocate memory within the process.
    loadPath = kernel32.VirtualAllocEx(hTargetProcess, 0, dllLen, VIRTUAL_MEM, PAGE_READWRITE)

    #Write to the newly created space.
    written = c_int(0)
    kernel32.WriteProcessMemory(hTargetProcess, loadPath, dllPath, dllLen, byref(written))

    hKernel32 = kernel32.GetModuleHandleA("kernel32.dll")
    hLoadlib = kernel32.GetProcAddress(hKernel32,"LoadLibraryA")

    #Create the thread and execute the DLL
    threadId = c_ulong(0)
    if not kernel32.CreateRemoteThread(hTargetProcess, None, 0, hLoadlib, loadPath, 0, byref(threadId)):
        print "Oh no... Failed to inject the DLL!"
        sys.exit(0)

    print ("Victory!  Thread with ID 0x%08x sucessfully created." % threadId.value)

def main():
    pid = input("Enter the process id: ")
    dllPath = input("Enter the path to the DLL: ")
    inject(pid, dllPath)

main()
