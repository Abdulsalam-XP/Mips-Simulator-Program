# Abdullah
class MipsMemory:
    def __init__(self):
       # memory storage: address -> value
        self.storage = {}

    def load_program(self, start_address, instructions): 
        # load instructions into memory
        current_address = start_address
        for instr in instructions:
            self.storage[current_address] = instr
            current_address += 4   # load instructions into memory

    def load_initial_data(self, address, value):  
         # store data in memory before execution
        self.storage[address] = value

    def read(self, address):
        # read value from memory (used by lw)
        # if address not found, return 0
        return self.storage.get(address, 0)

    def write(self, address, value):
       # write value to memory (used by sw)
        self.storage[address] = value

    def get_all_data(self):   
        # return all memory content 
        return self.storage