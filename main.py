from datapath import MipsDatapath
from memory import MipsMemory

# Mapping for the Assembler
REG_MAP = {
    "$zero": 0, "$0": 0, "$at": 1, "$v0": 2, "$v1": 3, "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7, # Added $0 as alias for $zero as well in the assmebler input 
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11, "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19, "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$t8": 24, "$t9": 25, "$ra": 31
}
REG_FUNCT = {
    # R-type: [Opcode, Funct]
    "R_type": {
        "add":  [0x00, 0x20],
        "sub":  [0x00, 0x22],
        "and":  [0x00, 0x24],
        "or":   [0x00, 0x25],
        "nor":  [0x00, 0x27],
        "slt":  [0x00, 0x2A],
        "sll":  [0x00, 0x00],
        "jr":   [0x00, 0x08]
    },
    
    # I-type: [Opcode]
    "I_type": {
        "addi": [0x08],
        "andi": [0x0C],
        "ori":  [0x0D],
        "lw":   [0x23],
        "sw":   [0x2B],
        "beq":  [0x04]
    }
}


# Bin Thabit
def decode(instruction_sent):
    # 1. Remove the commas first!
    clean_str = instruction_sent.replace(",", "")

    # 2. Split the clean string, not the original 'instruction'
    parts = clean_str.split()
    return parts

# Bin Thabit
def get_type_instruction(parts, REG_FUNCT, REG_MAP):
    s = {}
    instr_name = parts[0]
    
    if instr_name in REG_FUNCT['R_type']:
        # R-type: add $rd, $rs, $rt OR sll $rd, $rt, shamt
        s['op'] = REG_FUNCT['R_type'][instr_name][0]
        s['func'] = REG_FUNCT['R_type'][instr_name][1]
        
        if instr_name == 'sll':  # sll $t1, $t0, 2
            s['rs'] = 0
            s['rt'] = REG_MAP[parts[2]]
            s['rd'] = REG_MAP[parts[1]]
            s['shamt'] = int(parts[3])
        else:  # normal R-type like add, sub
            s['rs'] = REG_MAP[parts[2]]
            s['rt'] = REG_MAP[parts[3]]
            s['rd'] = REG_MAP[parts[1]]
            s['shamt'] = 0

    elif instr_name in REG_FUNCT['I_type']:
        s['op'] = REG_FUNCT['I_type'][instr_name][0]

        if instr_name in ('lw', 'sw'):
            # Format: lw $rt, offset($rs)  e.g. lw $s0, 4($zero)
            # parts[1] = $rt, parts[2] = offset($rs)
            mem_operand = parts[2]                        # e.g. "4($zero)" or "0($zero)"
            offset_str, base = mem_operand.split('(')     # "4", "$zero)"
            base = base.rstrip(')')                       # "$zero"
            s['rt'] = REG_MAP[parts[1]]
            s['rs'] = REG_MAP[base]
            s['constant'] = int(offset_str)
        else:
            # Format: addi $rt, $rs, immediate
            s['rs'] = REG_MAP[parts[2]]
            s['rt'] = REG_MAP[parts[1]]
            s['constant'] = int(parts[3])
    
    return s

# Abdullah
def get_machine_code(s):

    if s['op'] == 0:
        machine_code = (s['op'] << 26) | (s['rs'] << 21) | (s['rt'] << 16) | (s['rd'] << 11) | (s['shamt'] << 6) | s[
            'func']
    elif 'rd' not in s.keys():

        machine_code = (s['op'] << 26) | (s['rs'] << 21) | (s['rt'] << 16) | (s['constant'] & 0xFFFF)
    return machine_code

# Bin Thabit And Abdullah
# 4. START THE SIMULATION
def run_simulation(memory, datapath):
    while datapath.pc in memory.storage:
        print(f"\n--- Cycle at PC: {datapath.pc} ---")
        
        # add $s0, $s1, $s2
        # 1. FETCH (Instruction Memory)
        instruction = memory.read(datapath.pc)
        print(instruction)
        # 2. DECODE (Split the wires)
        opcode = (instruction >> 26) & 0x3F
        rs     = (instruction >> 21) & 0x1F
        rt     = (instruction >> 16) & 0x1F
        rd     = (instruction >> 11) & 0x1F
        shamt  = (instruction >> 6)  & 0x1F
        funct  = instruction & 0x3F
        imm    = instruction & 0xFFFF
        
        
        signals = datapath.control_unit(opcode)
        reg_data1, reg_data2 = datapath.register_file(rs, rt, 0, 0, 0, 0)    
        extended_imm = datapath.sign_extend(imm)

        # MUX
        write_reg = datapath.mux(rt, rd, signals["RegDst"])
        alu_in2 = datapath.mux(reg_data2, extended_imm, signals['ALUSrc'])

        
        alu_ctrl = datapath.alu_control(signals["ALUOp"], funct)
        alu_result, zero_flag = datapath.alu(
            reg_data1, alu_in2, alu_ctrl, shamt
        )

        # MEMORY
        mem_data = 0

        if signals["MemRead"]:
            mem_data = memory.read(alu_result)

        if signals["MemWrite"]:
            memory.write(alu_result, reg_data2)

        print(signals)
        

        # WRITE BACK
        final_write_data = datapath.mux(
            alu_result, mem_data, signals["MemtoReg"]
        )

        datapath.register_file(rs, rt, write_reg, final_write_data, signals["RegWrite"])
        
        datapath.print_registers()
        datapath.pc += 4

if __name__ == "__main__":
    # Initialize the memory and the datapath
    memory = MipsMemory()
    datapath = MipsDatapath(memory)

    instructions = [
        "addi $t0, $zero, 5",
        "addi $t1, $zero, 5",
        "addi $s0, $zero, 100",
    ]

    address = 0
    for i, instr in enumerate(instructions):

        # Step 1: Decode the instruction
        parts = decode(instr)

        # Step 2 Check if it is r or i or j type
        type_instruction = get_type_instruction(parts, REG_FUNCT, REG_MAP)

        # Step 3: get the machine code
        machine_code = get_machine_code(type_instruction)
        memory.load_initial_data(i * 4, machine_code)


    # Run the simulation
    run_simulation(memory, datapath)