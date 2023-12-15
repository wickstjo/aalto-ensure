from threading import Thread, Semaphore
import time

semaphore = Semaphore(3)

def foo(nth):
    semaphore.acquire()
    print(f'nth ({nth}) started')
    time.sleep(2)
    print(f'nth ({nth}) finished')
    semaphore.release()


for nth in range(10):
    thread = Thread(target=foo, args=(nth,))
    thread.start()