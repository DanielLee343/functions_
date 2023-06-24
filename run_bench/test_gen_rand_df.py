import ctypes
libc = ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libc.so.6")
libc.rand.restype = ctypes.c_int
random_number = libc.rand()
print(random_number)
# a = 1
# print(a)