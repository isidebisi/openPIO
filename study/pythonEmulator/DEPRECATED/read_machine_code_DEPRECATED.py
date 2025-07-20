"""
Each read file can not have more than 32 lines of code.
Each line of code must have 16 bits.
Spaces are automatically removed. Bitstrings can have spaces wherever you want.
Empty lines are counted as NOP.
Comments are removed after Bitstrings.
Lines, that exclusively contain comments, are not counted as empty lines.
All characters of the opcode must be 0 or 1.
"""


class MachineCodeReader:
    NOP_OPCODE = "1010000001000010"
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.instructions = [self.NOP_OPCODE] * 32  # Default NOP operation
        self.read_machine_code()

    def read_machine_code(self):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()
            print(len(lines))
            code_lines = []
            for line_number, line in enumerate(lines):
                # Remove comments
                if line[0] == '#' or line[0] == ';' or line[0:1] == '//':
                    continue
                line = line.split(';')[0].split('#')[0].split('//')[0].strip()
                cleaned_line = line.replace(" ", "")
                if not all(c in '01' for c in cleaned_line):
                    raise ValueError(f"Error: Invalid character in line: {line}")
                if cleaned_line == "":
                    cleaned_line = self.NOP_OPCODE
                if len(cleaned_line) != 16:
                    raise ValueError("Error: Each instruction must be 16 bits in a line.")
                code_lines.append(cleaned_line)
                
                print("Line =",line_number+1, "OP_code: ", cleaned_line)
            
            print("original code length: ", len(code_lines))
            if len(code_lines) > 32:
                raise ValueError("Error: More than 32 lines of pure code.")
            elif len(code_lines) < 32:
                code_lines += [self.NOP_OPCODE] * (32 - len(code_lines))
            
            print("Adjusted code length (should be 32): ",len(code_lines))

            for i, bitstring in enumerate(code_lines[:32]):
                self.instructions[i] = bitstring

        

    def get_instructions(self):
        return self.instructions
