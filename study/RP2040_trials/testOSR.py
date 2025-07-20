import rp2
import machine
import time

# Define a 32-bit test value.
# Example: 32'b01001100011100001111000001111100 = 0x4C70F07C
TEST_VALUE = 0b01001100011100001111000001111100

#-------------------------------------------------------------
# PIO program using OUT with a 17-bit left shift.
# This program:
#   - Pulls a 32-bit word into OSR.
#   - Shifts out 17 bits from OSR into X (using left shift).
#   - Moves X to ISR and pushes it to the RX FIFO.
# Expected: The value in X will contain the 17 MSBs of TEST_VALUE in its upper bits,
# and the lower 15 bits will be zeros.
@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def pio_out_test():
    pull()               # Load OSR with a 32-bit word from the TX FIFO.
    out(x, 17)           # Shift out 17 bits from OSR into X (left shift).
    mov(isr, x)         # Copy X into the ISR.
    push(block)         # Push the ISR value into the RX FIFO.

#-------------------------------------------------------------
# PIO program using MOV (normal transfer) to move OSR to X.
@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_LEFT)
def pio_mov_test_normal():
    pull()               # Load OSR with a 32-bit word.
    mov(x, osr)         # Move OSR to X normally.
    mov(isr, x)         # Copy X into ISR.
    push(block)

#-------------------------------------------------------------
# PIO program using MOV with reverse bit order.
# This assumes that 'reverse()' is defined in rp2 (as in the official module)
# to reverse the bit order during the MOV.
@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_LEFT)
def pio_mov_test_reverse():
    pull()                # Load OSR with a 32-bit word.
    mov(x, reverse(osr))  # Move OSR to X with bit reversal.
    mov(isr, x)
    push(block)

#-------------------------------------------------------------
# Instantiate state machines for each test.
# Use arbitrary GPIO assignments if you don't need real pin I/O.
# In these examples, we focus only on FIFO operations.
sm_out       = rp2.StateMachine(0, pio_out_test, freq=2000000)
sm_mov_norm  = rp2.StateMachine(1, pio_mov_test_normal, freq=2000000)
sm_mov_rev   = rp2.StateMachine(2, pio_mov_test_reverse, freq=2000000)

# Activate the state machines.
sm_out.active(1)
sm_mov_norm.active(1)
sm_mov_rev.active(1)

# Allow some time for initialization.
time.sleep(0.1)

# Write the test value to each state's TX FIFO.
sm_out.put(TEST_VALUE)
sm_mov_norm.put(TEST_VALUE)
sm_mov_rev.put(TEST_VALUE)

# Allow some time for the PIO programs to execute.
time.sleep(0.1)

# Read back the results from the RX FIFO.
result_out      = sm_out.get()       # From OUT test with 17-bit left shift.
result_mov_norm = sm_mov_norm.get()  # From MOV test (normal).
result_mov_rev  = sm_mov_rev.get()   # From MOV test (reverse).

print("Test OUT (17-bit left shift) result:")
print(f'{result_out:032b}')

print("Test MOV (normal) result:")
print(f'{result_mov_norm:032b}')

print("Test MOV (reversed) result:")
print(f'{result_mov_rev:032b}')