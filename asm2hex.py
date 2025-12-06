asm_file_name = input("Please input the asm file name: ")

asm_file = open(asm_file_name, "r")

asm_lines = asm_file.readlines()

hex_file_name = input("Please input the hex file name: ")

hex_file = open(hex_file_name, "w")

print(asm_lines)

for i in range(0, len(asm_lines)):
    hex_line = "test" 

    hex_file.write(hex_line)