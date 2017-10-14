import time

class TCLabClockError(RuntimeError):
    def __init__(self, message):
        RuntimeError.__init__(self, message)

def clock(tfinal, tstep=1, strict=False):
    start_time = time.time()
    prev_time = start_time
    fuzz = 0.005
    k = 0
    while (prev_time-start_time) <= tfinal  + fuzz:
        if strict and ((prev_time - start_time) > (k*tstep + fuzz)):
                raise TCLabClockError("TCLab failed to keep up with real time.")
        yield round(prev_time - start_time,2)
        if strict:
            tsleep = (k+1)*tstep - (time.time() - start_time) - fuzz
        else:
            tsleep = tstep - (time.time() - prev_time) - fuzz
        try:
            if tsleep >= fuzz:
                time.sleep(tsleep)
            prev_time = time.time()
            k += 1
        except:
            self.stop()