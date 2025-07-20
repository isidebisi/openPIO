import side_set_delay

OPCODES = {
    "000": "JMP",
    "001": "WAIT",
    "010": "IN",
    "011": "OUT",
    "100": "PUSHPULL",
    "101": "MOV",
    "110": "IRQ",
    "111": "SET",
    "1010000001000010": "NOP",
    "100 1": "PULL",
    "100 0": "PUSH"
}
OPCODES_REVERSE = {v: k for k, v in OPCODES.items()}  # Reverse lookup


class StateMachine:
    MACHINE_FREQUENCY = 125000000  # 125 MHz
    
    def __init__(self, id, clock_div=1.0):
        """
        Represents a single PIO state machine.

        :param id: Unique ID of the state machine (0-3 in RP2040).
        """

        self.id = id
        self.clock_cycle = 0
        self.clock_div_int = int(clock_div)  # Integer part
        self.clock_div_frac = int((clock_div - self.clock_div_int) * 256)  # 8-bit fractional part
        self.fractional_accum = 0  # Accumulator for delta-sigma algorithm
        self.program = [OPCODES_REVERSE["NOP"]] *32  # Stores loaded PIO program (list of instructions)
        self.running = False  # Tracks execution state
        self.cycles_until_next_exec = self.clock_div_int  # Start with integer delay
        self.programCounter = 0
        self.opDelayCount = 0 # Delay counter for current operation

        self.in_base = 0
        self.out_base = 0
        self.set_base = 0
        self.jmp_pin = 0
        self.sideset_base = 0

        self.ISR = None  # Input shift register
        self.ISR_shift_counter = 0
        self.ISR_shift_dir = 0
        self.OSR = None  # Output shift register
        self.OSR_shift_counter = 0
        self.OSR_shift_dir = 0
        self.autopush = False
        self.autopull = False
        self.push_thresh = 32
        self.pull_thresh = 32
        self.tx_fifo = []
        self.rx_fifo = []
        self.scratchX = 0
        self.scratchY = 0



    def init(
        self, 
        freq=-1,
        in_base=None,
        out_base=None,
        set_base=None,
        jmp_pin=None,
        sideset_base=None,
        in_shiftdir=None,
        out_shiftdir=None,
        autopush=None,
        autopull=None,
        push_thresh=None,
        pull_thresh=None,):

        if in_base is not None:
            self.in_base = in_base
        if out_base is not None:
            self.out_base = out_base
        if set_base is not None:
            self.set_base = set_base
        if jmp_pin is not None:
            self.jmp_pin = jmp_pin
        if sideset_base is not None:
            self.sideset_base = sideset_base
        if in_shiftdir is not None:
            self.ISR_shift_dir = in_shiftdir
        if out_shiftdir is not None:
            self.OSR_shift_dir = out_shiftdir
        if autopush is not None:
            self.autopush = autopush
        if autopull is not None:
            self.autopull = autopull
        if push_thresh is not None:
            self.push_thresh = push_thresh
        if pull_thresh is not None:
            self.pull_thresh = pull_thresh


        """Sets the clock divider for timing control."""
        
        if freq <= self.MACHINE_FREQUENCY:
            if freq > 0:
                self.clock_div = self.MACHINE_FREQUENCY / freq
                self.clock_div_int = int(self.clock_div)
                self.clock_div_frac = int((self.clock_div - self.clock_div_int) * 256)
                self.fractional_accum = 0
            else:
                self.clock_div = 1.0
                self.clock_div_int = 1
                self.clock_div_frac = 0
                self.fractional_accum = 0
        else:
            raise ValueError("Invalid frequency value (too high)")


    def load_program(self, instructions):
        """Loads a list of instructions into the state machine."""
        self.program = instructions

    def start(self):
        """Starts the state machine execution."""
        if self.program:
            self.running = True
            print(f"StateMachine {self.id} started.")
        else:
            print(f"StateMachine {self.id} has no program loaded.")

    def stop(self):
        """Stops the state machine execution."""
        self.running = False
        print(f"StateMachine {self.id} stopped.")

    def execute_instruction(self):
        """Executes the next instruction if enough cycles have passed."""
        if self.running and self.program:
            if self.cycles_until_next_exec <= 0:
                opcode = self.program[self.programCounter]
                instr = self.decode_instruction(opcode)
                print(f"StateMachine {self.id} at ClockCycle: {self.clock_cycle} executing: {instr}")

                if self.opDelayCount > 0:   #only execute next instruction if delay count is 0
                    self.execute_DELAY()
                else:
                    self.dispatch_instruction(instr, opcode)

                self.programCounter = (self.programCounter + 1) % 32  # Wrap around at 32
                
                # Update cycles based on delta-sigma algorithm
                self.update_cycle_counter()

    def decode_instruction(self, opcode):
        """Decodes an instruction opcode to determine the operation."""
        if opcode in OPCODES:   #if NOP
            return OPCODES[opcode]
        
        instr = OPCODES.get(opcode[:3], "UNKNOWN")
        if instr == "UNKNOWN":
            raise ValueError(f"Unknown opcode: {opcode}")
        
        if instr == "PUSHPULL":
            return OPCODES["100 1"] if opcode[8] == '1' else OPCODES["100 0"]

        return instr

    def dispatch_instruction(self, instruction, opcode):
        """Routes instruction execution to the correct function."""
        instruction_map = {
            "JMP":  lambda: self.execute_JMP(opcode),
            "WAIT": lambda: self.execute_WAIT(opcode),
            "IN":   lambda: self.execute_IN(opcode),
            "OUT":  lambda: self.execute_OUT(opcode),
            "PULL": lambda: self.execute_PULL(opcode),
            "PUSH": lambda: self.execute_PUSH(opcode),
            "MOV":  lambda: self.execute_MOV(opcode),
            "IRQ":  lambda: self.execute_IRQ(opcode),
            "SET":  lambda: self.execute_SET(opcode),
            "NOP":  lambda: self.execute_NOP(opcode),
        }

        execute_func = instruction_map.get(instruction, lambda: self.execute_UNKNOWN(opcode))
        execute_func()  # Call the corresponding function

    def update_cycle_counter(self):
        """
        Implements first-order delta-sigma modulation for clock division.
        Determines how many system cycles should pass before the next instruction.
        """
        self.fractional_accum += self.clock_div_frac

        # If accumulated fraction overflows past 256 (1.0 in 8-bit fraction)
        if self.fractional_accum >= 256:
            self.fractional_accum -= 256
            self.cycles_until_next_exec = self.clock_div_int + 1  # Extra cycle
        else:
            self.cycles_until_next_exec = self.clock_div_int  # Normal cycle

    def tick(self):
        """Simulates system clock cycles until the next execution."""
        if self.running:
            self.clock_cycle += 1
            self.cycles_until_next_exec -= 1
            self.execute_instruction()

    def execute_JMP(self, opcode):
        print(f"SM{self.id}: Executing JMP")

    def execute_WAIT(self, opcode):
        print(f"SM{self.id}: Executing WAIT")

    def execute_IN(self, opcode):
        print(f"SM{self.id}: Executing IN")

    def execute_OUT(self, opcode):
        print(f"SM{self.id}: Executing OUT")

    def execute_PULL(self, opcode):
        print(f"SM{self.id}: Executing PULL")

    def execute_PUSH(self, opcode):
        print(f"SM{self.id}: Executing PUSH")

    def execute_MOV(self, opcode):
        print(f"SM{self.id}: Executing MOV")

    def execute_IRQ(self, opcode):
        print(f"SM{self.id}: Executing IRQ")

    def execute_SET(self, opcode):
        print(f"SM{self.id}: Executing SET")

    def execute_NOP(self, opcode):
        print(f"SM{self.id}: Executing NOP")

    def execute_DELAY(self):
        if self.opDelayCount > 0:
            self.opDelayCount -= 1
            print(f"SM{self.id}: Executing DELAY")
        else:
            ValueError(f"SM{self.id}: DELAY opcode encountered without delay count!")

    def execute_UNKNOWN(self, opcode):
        print(f"SM{self.id}: Unknown instruction encountered!")