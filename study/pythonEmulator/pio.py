from state_machine import StateMachine

class PIO:
    SHIFT_LEFT = 0
    SHIFT_RIGHT = 1

    JOIN_NONE = 0
    JOIN_TX = 1
    JOIN_RX = 2
    JOIN_BOTH = 3

    IN_LOW = 0
    IN_HIGH = 1
    OUT_LOW = 2
    OUT_HIGH = 3

    IRQ_SM0 = 0x100
    IRQ_SM1 = 0x200
    IRQ_SM2 = 0x400
    IRQ_SM3 = 0x800

    out_init=None,
    set_init=None,
    sideset_init=None,
    in_shiftdir=0,
    out_shiftdir=0,
    autopush=False,
    autopull=False,
    push_thresh=32,
    pull_thresh=32,
    fifo_join=JOIN_NONE,

    def __init__(self, out_init=None, set_init=None, sideset_init=None, in_shiftdir=0, out_shiftdir=0, autopush=False, autopull=False, push_thresh=32, pull_thresh=32):
        """
        Represents the PIO hardware block, which contains multiple state machines.
        """
        self.out_init = out_init
        self.set_init = set_init
        self.sideset_init = sideset_init
        self.in_shiftdir = in_shiftdir
        self.out_shiftdir = out_shiftdir
        self.autopush = autopush
        self.autopull = autopull
        self.push_thresh = push_thresh
        self.pull_thresh = pull_thresh

        self.state_machines = [StateMachine(i) for i in range(4)]  # 4 state machines in RP2040
        self.clock_cycle = 0
        self.program_memory = [None] * 32  # 32 instructions in RP2040


    def get_state_machine(self, id):
        """Returns a specific state machine by ID."""
        if 0 <= id < len(self.state_machines):
            return self.state_machines[id]
        else:
            raise ValueError("Invalid StateMachine ID")
        
    def set_program(self, instructions):
        #Gets full program and loads it into pio program memory and state machines
        self.program_memory = instructions
        self.load_program(instructions)

    def load_program(self, instructions):
        """Loads a list of instructions into the shared program memory."""
        self.program_memory = instructions
        for i in range(4):
            self.state_machines[i].load_program(self.program_memory)
    
    def load_instruction(self, index, instruction):
        """Loads a single instruction into the shared program memory."""
        self.program_memory[index] = instruction
        for i in range(4):
            self.state_machines[i].load_program(self.program_memory)

    def tick(self):
        """Executes one clock cycle for all state machines."""
        self.clock_cycle += 1
        for sm in self.state_machines:
            sm.tick()


