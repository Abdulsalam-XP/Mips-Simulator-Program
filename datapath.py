# Everyone works
class MipsDatapath:
    def __init__(self, memory_instance):
        self.memory = memory_instance
        self.registers = [0] * 32
        self.pc = 0
        self.REG_NAME = {
    0: "$zero", 0: "$0", 1: "$at", 2: "$v0", 3: "$v1", # Added $0 as alias for $zero 
    4: "$a0", 5: "$a1", 6: "$a2", 7: "$a3",
    8: "$t0", 9: "$t1", 10: "$t2", 11: "$t3",
    12: "$t4", 13: "$t5", 14: "$t6", 15: "$t7",
    16: "$s0", 17: "$s1", 18: "$s2", 19: "$s3",
    20: "$s4", 21: "$s5", 22: "$s6", 23: "$s7",
    24: "$t8", 25: "$t9", 31: "$ra",
}

    # CONTROL UNIT
    # Abdullah
    def control_unit(self, opcode):
        signals = {
            "RegDst": 0,
            "ALUSrc": 0,
            "MemtoReg": 0,
            "RegWrite": 0,
            "MemRead": 0,
            "MemWrite": 0,
            "Branch": 0,
            "Jump": 0,
            "ALUOp": 0,
            "JAL": 0,
            "JR": 0
        }

        # R-type
        if opcode == 0x00:
            signals["RegDst"] = 1
            signals["RegWrite"] = 1
            signals["ALUOp"] = 2

        # addi
        elif opcode == 0x08:
            signals["ALUSrc"] = 1
            signals["RegWrite"] = 1
            signals["ALUOp"] = 0

        # andi
        elif opcode == 0x0C:
            signals["ALUSrc"] = 1
            signals["RegWrite"] = 1
            signals["ALUOp"] = 3

        # ori
        elif opcode == 0x0D:
            signals["ALUSrc"] = 1
            signals["RegWrite"] = 1
            signals["ALUOp"] = 4

        # lw
        elif opcode == 0x23:
            signals["ALUSrc"] = 1
            signals["MemtoReg"] = 1
            signals["RegWrite"] = 1
            signals["MemRead"] = 1
            signals["ALUOp"] = 0   # address = base + offset

        # sw
        elif opcode == 0x2B:
            signals["ALUSrc"] = 1
            signals["MemWrite"] = 1
            signals["ALUOp"] = 0   # address = base + offset

        # beq
        elif opcode == 0x04:
            signals["Branch"] = 1
            signals["ALUOp"] = 1   # subtraction

         # j
        elif opcode == 0x02:
            signals["Jump"] = 1
 
        # jal
        elif opcode == 0x03:
            signals["Jump"] = 1
            signals["JAL"] = 1
            signals["RegWrite"] = 1 


        return signals

    # ALU CONTROL
    # Bin Thabit
    def alu_control(self, alu_op, funct):

        if alu_op == 0:
            return "add"  # addi, lw, sw

        if alu_op == 1:
            return "sub"  # beq

        if alu_op == 3:
            return "and"

        if alu_op == 4:
            return "or"

        if alu_op == 2:  # R-type
            if funct == 0x20: return "add"
            if funct == 0x22: return "sub"
            if funct == 0x24: return "and"
            if funct == 0x25: return "or"
            if funct == 0x27: return "nor"
            if funct == 0x00: return "sll"
            if funct == 0x2A: return "slt"
            if funct == 0x08: return "jr"

        return "none"

    # ALU
    # Bin Thabit
    def alu(self, val1, val2, control, shamt=0):

        res = 0

        if control == "add":
            res = (val1 + val2) & 0xFFFFFFFF

        elif control == "sub":
            res = (val1 - val2) & 0xFFFFFFFF

        elif control == "and":
            res = val1 & val2

        elif control == "or":
            res = val1 | val2

        elif control == "nor":
            res = ~(val1 | val2) & 0xFFFFFFFF

        elif control == "sll":
            res = (val2 << shamt) & 0xFFFFFFFF

        elif control == "slt":
            res = 1 if val1 < val2 else 0

        return res, (1 if res == 0 else 0)
    
    # REGISTER FILE
    # Abdulsalam
    def register_file(self, rs, rt, dest, write_data, reg_write, is_jal=False):
        read1 = self.registers[rs]
        read2 = self.registers[rt]

        if reg_write:
            target = 31 if is_jal else dest
            if target != 0:
                self.registers[target] = write_data
        return read1, read2

    # SIGN EXTEND
    # Abdulsalam
    def sign_extend(self, imm):
        return imm - 0x10000 if imm & 0x8000 else imm

    # MUX (Hardware Accurate)
    # Alanood
    def mux(self, val1, val2, sel):
        return val2 if sel else val1

    # ADDER
    # Alanood
    def adder(self, a, b):
        return (a + b) & 0xFFFFFFFF
    # Alanood
    def print_registers(self):
        print("\n===== NON-ZERO REGISTERS =====")
        for i in range(32):
            value = self.registers[i]
            if value != 0:
                reg_name = self.REG_NAME.get(i, f"R{i}")
                print(f"{reg_name:>6} : {value}")
        print("==============================\n")