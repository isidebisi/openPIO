class ShiftRegister:
    isOSR = False
    size = 32
    data = ["0"] * size
    SHIFTCTRL_isRightShift = True
    shiftCounter = 0
    autoShiftThreshold = 32
    autoShiftEnabled = False


    def __init__(self, isOSR, shiftDir=0, autoShift=False, autoShiftThreshold=32):
        self.SHIFTCTRL_isRightShift = dir
        self.autoShiftEnabled = autoShift
        self.autoShiftThreshold = autoShiftThreshold

    def fill(self, nBits, value):
        # Fill the shift register with a value: PULL for OSR and IN for ISR
        
        # First: check if the number of bits is correct and adjust shiftCounter
        if self.isOSR:
            if nBits != 32 or len(value) != 32:
                raise ValueError("OSR must be filled with 32 bits")
            else:
                self.shiftCounter = 0
        else: #ISR
            if nBits >32 or nBits < 1 or len(value) != nBits:
                raise ValueError("ISR must be filled with 1-32 bits")
            else:
                self.shiftCounter += nBits
                if self.shiftCounter > 32:
                    self.shiftCounter %= 32                

        # Second: Fill the shift register with a value:
        if self.SHIFTCTRL_isRightShift:
            for _ in range(nBits):
                self.data.pop()
                self.data.insert(0, value.pop(0))
        else:
            for _ in range(nBits):
                self.data.pop(0)
                self.data.append(value.pop(0))
            

    def empty(self, nBits):
        # Empty the shift register: OUT for OSR and PUSH for ISR

        # Fist: check if the number of bits is correct and adjust shiftCounter
        if self.isOSR:
            if nBits < 0 or nBits > 32:
                raise ValueError("OSR must be emptied with 1-32 bits")
            else:
                self.shiftCounter += 32
                if self.shiftCounter > 32:
                    self.shiftCounter %= 32
        else: #ISR
            if nBits != 32:
                raise ValueError("ISR must be emptied with 32 bits")
            else:
                self.shiftCounter = 0

        # Second: Empty the shift register
        dataOut = []
        if self.SHIFTCTRL_isRightShift:
            for _ in range(nBits):
                dataOut.insert(0,self.data.pop())
        else:
            for _ in range(nBits):
                dataOut.append(self.data.pop(0))

        return dataOut
    
    def autoShift(self):
        # Shift the shift register automatically
        if self.autoShiftEnabled and self.shiftCounter >= self.autoShiftThreshold:
            self.shift()
            self.shiftCounter = 0
    



    def reset(self):
        self.data = ["0"] * self.size

    def get(self):
        return self.data

    def set(self, value):
        if len(value) != 32:
            raise ValueError("Shift register must be set with 32 bits")
        else:
            self.data = value