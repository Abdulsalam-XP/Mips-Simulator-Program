# Abdulsalam And Abdullah
class MipsMemory:
    def __init__(self):
        # We use a dictionary to store memory values. 
        # The key is the address and the value is the 32-bit word.
        self.storage = {}

    def load_program(self, start_address, instructions): 
        # Loads the user's assembly program into memory.
        # Instructions should be passed as a list of integers.
        current_address = start_address
        for instr in instructions:
            self.storage[current_address] = instr
            current_address += 4 

    def load_initial_data(self, address, value):  
        # Loads specific data items into memory before simulation starts.
        self.storage[address] = value

    def read(self, address):
        
        # Reads a word from memory. Used by instruction fetch and 'lw'.
        # If address doesn't exist, we return 0 as a default.
        return self.storage.get(address, 0)

    def write(self, address, value):
        # Writes a word to memory. Used by the 'sw'.
        self.storage[address] = value

    def get_all_data(self):   
        # Returns the full memory dictionary. 
        return self.storage