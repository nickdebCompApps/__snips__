from threading import Timer
from time import sleep
from word2number import w2n

class Timers():
    
    def __init__(self, time, units):
        self.timer = None
        self.units = units
        self.time = time
    
    def isInt(self):
        try:
            num = float(self.time)
        except ValueError:
            return False
        return True
    
    def convertSeconds(self):
        if self.isInt():
            if self.units == 'seconds' or self.units == 'second':
                self.time = self.time
            elif self.units == 'minutes' or self.units == 'minute':
                self.time = int(self.time) * 60
            elif self.units == 'hours' or self.units == 'hour':
                self.time = int(self.time) * 3600
            elif self.units == 'days' or self.units == 'day':
                self.time = int(self.time) * 216000
            elif self.units == 'months' or self.units == 'month':
                self.time = int(self.time) * 12960000
            else:
                self.time = 10
        else:
            self.time = w2n.word_to_num(self.time)
            self.convertSeconds()
            
            
             
    def start(self):
        self.convertSeconds()
        self.timer = Timer(self.time, self.finished)
        self.timer.start() 
        
    def finished(self):
        print('done')
        return True
    
    def cancel(self):
        self.timer.cancel()
