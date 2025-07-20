from pio_DEPRECATED import PIO
from read_machine_code_DEPRECATED import MachineCodeReader

"""
Decision was made to treat all binary values (OpCodes) as strings of "0" and "1" characters instead of real binary numbers.
The focus for this emulator is simplicity, readability, and understanding all the operations, not performance.
"""

codeReader = MachineCodeReader("study/pythonEmulator/DEPRECATED/pio0_code.txt")
program = codeReader.get_instructions()

pio = PIO()
pio.set_program(program)

sm0 = pio.get_state_machine(0)
sm0.init(freq=10000000)


sm1 = pio.get_state_machine(1)
sm1.init()


sm0.start()
#sm1.start()
for _ in range(100):  # Simulate 5 instruction cycles
    pio.tick()