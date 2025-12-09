import re

asm_file_name = input("Please input the asm file name: ")

asm_file = open(asm_file_name, "r")

asm_lines = asm_file.readlines()

# hex_file_name = input("Please input the hex file name: ")

hex_file_name = "out.hex"

hex_file = open(hex_file_name, "w")

print(asm_lines)

address = 0

for i in range(0, len(asm_lines)):
    hex_line = "test\n"
    hex_addr = hex(address)
    while(len(hex_addr) < 6):
        hex_addr = "0x0" + hex_addr[2:]
    hex_addr_1 = hex(address + 1)
    while(len(hex_addr_1) < 6):
        hex_addr_1 = "0x0" + hex_addr_1[2:]
    if(re.search(r"org", asm_lines[i])):
        address = 0 # need to fix that 
    else:
        if(re.search(r"slli", asm_lines[i])):
            opcode = 19
            f3 = 1
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"srli", asm_lines[i])):
            opcode = 19
            f3 = 5
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"srai", asm_lines[i])):
            opcode = 19
            f3 = 5
            f7 = 32
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((f7 << 25) + (imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"xori", asm_lines[i])):
            opcode = 19
            f3 = 4
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"ori", asm_lines[i])):
            opcode = 19
            f3 = 6
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"addi", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 19
            f3 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"andi", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 19
            f3 = 7
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
            command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"sll", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 1
            f7 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"srl", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 5
            f7 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"sra", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 5
            f7 = 32
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"xor", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 4
            f7 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"or", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 6
            f7 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"and", asm_lines[i])):
            #store everything as integers and bit shift as needed
            opcode = 51
            f3 = 7
            f7 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
            rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
            rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
            command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
            while(len(command) < 8):
                command = "0" + command
            hex_line = hex_addr + command + "\n"
        elif(re.search(r"li", asm_lines[i])):
            #currently assumes that li will always load < 12 bits of data (not always true)
            opcode = 19
            f3 = 0
            rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
            rs1 = 0
            base = 10
            if(re.search(r"0x", asm_lines[i])):
                base = 16
            imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[0][-1]).group(0), base)
            if(imm < 2048):
                command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
                while(len(command) < 8):
                    command = "0" + command
                hex_line = hex_addr + command + "\n"
            else:
                if(imm%4096 > 2048):
                    command = hex((imm%4096 << 20) + (rd << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
                    while(len(command) < 8):
                        command = "0" + command
                    hex_line = hex_addr_1 + command + "\n"
                    command2 = hex((int(imm/4096 + 1) << 12) + (rd << 7) + 55)[2:]
                    while(len(command2) < 8):
                        command2 = "0" + command2
                    hex_file.write(hex_addr + command2 + "\n")
                    address = address + 1
                elif(imm%4096 < 2048 and imm%4096 >= -2047):
                    command = hex((imm%4096 << 20) + (rd << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
                    while(len(command) < 8):
                        command = "0" + command
                    hex_line = hex_addr_1 + command + "\n"
                    command2 = hex((int(imm/4096) << 12) + (rd << 7) + 55)[2:]
                    while(len(command2) < 8):
                        command2 = "0" + command2
                    hex_file.write(hex_addr + command2 + "\n")
                    address = address + 1
                else:
                    command = hex((imm%4096 << 20) + (rd << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
                    while(len(command) < 8):
                        command = "0" + command
                    hex_line = hex_addr_1 + command + "\n"
                    command2 = hex((int(imm/4096 + 1) << 12) + (rd << 7) + 55)[2:]
                    while(len(command2) < 8):
                        command2 = "0" + command2
                    hex_file.write(hex_addr + command2 + "\n")
                    address = address + 1
        elif(re.search(r"halt", asm_lines[i])):
            hex_line = hex_addr + "ffffffff\n"
        hex_file.write(hex_line)
        address = address + 1