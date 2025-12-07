import re

asm_file_name = input("Please input the asm file name: ")

asm_file = open(asm_file_name, "r")

asm_lines = asm_file.readlines()

hex_file_name = input("Please input the hex file name: ")

hex_file = open(hex_file_name, "w")

print(asm_lines)

address = 0

for i in range(0, len(asm_lines)):
    hex_line = "test\n"
    if(re.search(r"org", asm_lines[i])):
        address = 0 # need to fix that 
    else:
        if(re.search(r"addi", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 19
            f3 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            imm = int(re.search(r"[0-9]*", re.findall(r", ([0-9]*)", asm_lines[i])[1]).group(0))
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex(address) + command + "\n"
        if(re.search(r"li", asm_lines[i])):
            #currently assumes that li will always load < 12 bits of data (not always true)
            opcode = 19
            f3 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = 0
            imm = int(re.search(r"[0-9]*", re.findall(r", ([0-9]*)", asm_lines[i])[0]).group(0))
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex(address) + command + "\n"
        elif(re.search(r"halt", asm_lines[i])):
            hex_line = hex(address) + "ffffffff\n"
        hex_file.write(hex_line)
        address = address + 1