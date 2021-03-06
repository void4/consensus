from time import time

# Object which is true once after <interval> seconds
# For Python2, use the __nonzero__ method
class Every:
    def __init__(self, interval):
        self.interval = interval
        self.lasttime = time()

    def __bool__(self):
        current = time()
        if current-self.lasttime>=self.interval:
            self.lasttime = current
            return True
        return False
