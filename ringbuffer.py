class Ringbuffer:
    def __init__(self, capacity):
        self.buf = [None for i in range(capacity)]
        self.pos = 0
        self.capacity = capacity

    def push(self, item):
        self.buf[self.pos] = item
        self.pos = (self.pos + 1) % self.capacity

    def list(self):
        return [x for x in self.buf[self.pos:] + self.buf[:self.pos] if x is not None]
