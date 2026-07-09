import re
import struct
import sys
import argparse
import pathlib
import yaml
import io
import string

colors = {"RED": "\033[31m", "RESET": "\033[0m"}

debugger = False
no_addresses = False
verbose = False
image_file = None
mem_map = {}
user_data_files = []
kernel_files = {}
user_program_files = []
io_mapping = {}
kernel_file_stack = []

def print_debug(debug_string):
	if(debugger):
		print("Debug: " + debug_string)
          
def print_verbose(message):
    if(verbose or debugger):
        print("Info: "  + message)

def print_error(message):
    print(colors["RED"] + "Error: " + message + colors["RESET"])
    sys.exit(1)

def formatted_dict(dictionary):
    formatting = []
    for key, item in dictionary.items():
        formatting.append(f"\t{str(key)}: {str(item)}")
    return "\n".join(formatting)
    
def formatted_list(print_list):
    if(print_list == [] or print_list == None):
        return "\tNone"
    formatting = []
    for item in print_list:
        formatting.append(f"\t{str(item)}")
    return "\n".join(formatting)

def word(value: int):
    value_string = hex(value)[2:]
    while(len(value_string) < 8):
        value_string = "0" + value_string
    return value_string

class FileStruct:
    def __init__(self, filename, data):
        self.filename = filename
        self.hex_filename = convert_text_file(io.TextIOWrapper(io.BytesIO(filename.encode("utf-8"))))
        self.data = data
        self.data_size = len(data) * 4 #assumes that data will always be word-aligned hex
        self.name_addr = None
        self.data_addr = None

    def set_name_addr(self, name_addr):
        self.name_addr = name_addr

    def set_data_addr(self, data_addr):
        self.data_addr = data_addr

    def __str__(self):
        return f"filename: {self.filename}, size: {self.data_size} B\n\tname_addr: {hex(self.name_addr) if type(self.name_addr) == int else self.name_addr}, data_addr: {hex(self.data_addr) if type(self.data_addr) == int else self.data_addr}"

opcode_lookup = {
    #RV32I
    "lb"    : 0x3,
    "lh"    : 0x3,
    "lw"    : 0x3,
    "lbu"   : 0x3,
    "lhu"   : 0x3,
    "fence" : 0xF,
    "fence.i"   : 0xF,
    "addi"  : 0x13,
    "slli"  : 0x13,
    "slti"  : 0x13,
    "sltiu" : 0x13,
    "xori"  : 0x13,
    "srli"  : 0x13,
    "srai"  : 0x13,
    "ori"   : 0x13,
    "andi"  : 0x13,
    "auipc" : 0x17,
    "sb"    : 0x23,
    "sh"    : 0x23,
    "sw"    : 0x23,
    "add"   : 0x33,
    "sub"   : 0x33,
    "sll"   : 0x33,
    "slt"   : 0x33,
    "sltu"  : 0x33,
    "xor"   : 0x33,
    "srl"   : 0x33,
    "sra"   : 0x33,
    "or"    : 0x33,
    "and"   : 0x33,
    "lui"   : 0x37,
    "beq"   : 0x63,
    "bne"   : 0x63,
    "blt"   : 0x63,
    "bge"   : 0x63,
    "bltu"  : 0x63,
    "bgeu"  : 0x63,
    "jalr"  : 0x67,
    "jal"   : 0x6F,
    "ecall" : 0x73,
    "ebreak"    : 0x73,
    "CSRRW" : 0x73,
    "CSRRS" : 0x73,
    "CSRRC" : 0x73,
    "CSRRWI"    : 0x73,
    "CSRRSI"    : 0x73,
    "CSRRCI"    : 0x73
}

pseudo_instr = ["beqz", "bnez", "la", "li", "j", "jr", "mv", "neg", "nop", "not", "ret", "seqz", "snez"]

itype_opcodes = {0x03, 0x0F, 0x13, 0x67, 0x73}
utype_opcodes = {0x17, 0x37}
stype_opcodes = {0x23}
rtype_opcodes = {0x33}
sbtype_opcodes = {0x63}
ujtype_opcodes = {0x6F}

class InstructionStruct:
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.opcode = opcode_lookup[mnemonic]
        self.f3 = 0
        self.f7 = 0

    def set_rd(self, rd):
        self.rd = rd

    def set_rs1(self, rs1):
        self.rs1 = rs1

    def set_rs2(self, rs2):
        self.rs2 = rs2

    def set_imm(self, imm):
        self.imm = imm

    def set_f3(self, f3):
        self.f3 = f3

    def set_f7(self, f7):
        self.f7 = f7

    def convert_to_hex(self):
        if(self.opcode in itype_opcodes):
            if(self.f3 != None and self.rd != None and self.rs1 != None and self.imm != 'null'):
                return hex((self.imm << 20) + (self.rs1 << 15) + (self.f3 << 12) + (self.rd << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete I-Type Instruction struct")
        elif(self.opcode in utype_opcodes):
            if(self.imm != 'null' and self.rd != None):
                return hex((self.imm << 12) + (self.rd << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete U-Type Instruction struct")
        elif(self.opcode in stype_opcodes):
            if(self.imm != 'null' and self.rs1 != None and self.rs2 != None and self.f3 != None):
                return hex((int(self.imm/32) << 25) + (self.rs2 << 20) + (self.rs1 << 15) + ((self.imm%32) << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete S-Type Instruction struct")
        elif(self.opcode in rtype_opcodes):
            if(self.f7 != None and self.f3 != None and self.rs1 != None and self.rs2 != None and self.rd != None):
                return hex((self.f7 << 25) + (self.rs2 << 20) + (self.rs1 << 15) + (self.f3 << 12) + (self.rd << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete R-Type Instruction struct")
        elif(self.opcode in sbtype_opcodes):
            if(self.f3 != None and self.rs1 != None and self.rs2 != None):
                return hex((((int(self.imm) >> 12)%2) << 31) + (((int(self.imm) >> 5)%64) << 25) + (self.rs2 << 20) + (self.rs1 << 15) + (self.f3 << 12) + (((int(self.imm) >> 1)%16) << 8) + (((int(self.imm) >> 11)%2) << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete SB-Type Instruction struct")
        elif(self.opcode in ujtype_opcodes):
            if(self.rd != None and self.imm != 'null'):
                return hex((((int(self.imm) >> 20)%2) << 31) + (((int(self.imm) >> 1)%1024) << 21) + (((int(self.imm) >> 11)%2) << 20) + (((int(self.imm) >> 12)%256) << 12) + (self.rd << 7) + self.opcode)[2:]
            else:
                print_error("Incomplete UJ-Type Instruction struct")
        else:
            return "00000000"

    def __str__(self):
        if(self.opcode in rtype_opcodes):
            return f"{self.mnemonic} x{self.rd}, x{self.rs1}, x{self.rs2}"
        elif(self.opcode in itype_opcodes):
            return f"{self.mnemonic} x{self.rd}, x{self.rs1}, {self.imm}"
        elif(self.opcode in (stype_opcodes|sbtype_opcodes)):
            return f"{self.mnemonic} x{self.rs1}, x{self.rs2}, {self.imm}"
        elif(self.opcode in (utype_opcodes|ujtype_opcodes)):
            return f"{self.mnemonic} x{self.rd}, {self.imm}"
        else:
            return f"{self.mnemonic}"
            


#take in a text file stream and convert it to the raw binary ascii values
def convert_text_file(file_stream: io.TextIOWrapper):
    mem_block = []
    character = file_stream.read(1)
    i = 0
    while(character):
        hex_character = hex(ord(character))[2:]
        if(len(hex_character) < 2):
            hex_character = "0" + hex_character
        if i%4 == 0:
            mem_block.append(hex_character)
        else:
            mem_block[-1] = mem_block[-1] + hex_character
        character = file_stream.read(1)
        i = i + 1
    if(i%4 == 0):
        mem_block.append("00")
    else:
        mem_block[-1] = mem_block[-1] + "00"
    return mem_block

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_image_file", default="null")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--no_addr", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    global debugger, no_addresses, image_file, verbose
    debugger = args.debug
    no_addresses = args.no_addr
    verbose = args.verbose
    if(args.build_image_file != "null"):
        if(pathlib.Path(args.build_image_file).is_file()):
            image_file = open(args.build_image_file, "r")
        else:
            print_error(f"build-image-file {args.build_image_file} not found!")
             

def parse_build_file_yml():
    data = yaml.load(image_file, yaml.SafeLoader)
    global mem_map
    mem_map = data["memory_map"]
    print_verbose("Memory mapping: \n" + formatted_dict(mem_map))
    global user_data_files, kernel_files, user_program_files, io_mapping
    user_data_files = data.get("user_data", [])
    print_verbose("User data files: \n" + formatted_list(user_data_files))
    user_program_files = data.get("user_programs", [])
    print_verbose("User program files: \n" + formatted_list(user_program_files))
    kernel_file_names = data.get("kernel_files", [])
    for file in kernel_file_names:
        kernel_files[file] = ["Unparsed", -1, {}, []]
    print_verbose("Kernel files: \n" + formatted_list(kernel_files))
    io_mapping = data.get("io_map", {})
    print_verbose("IO Mapping: \n" + formatted_dict(io_mapping))
    image_file.close()


def parse_user_data():
    if(user_data_files == []):
        print_verbose("No user data files provided")
        return
    file_list = []
    for user_file in user_data_files:
        if(pathlib.Path(user_file).is_file()):
            print_verbose(f"Parsing user data file {user_file}")
            user_stream = open(user_file, "r")
            file_ext = user_file.split(".")[-1]
            print_debug(f"File extension: {file_ext}")
            match file_ext:
                case "txt":
                    mem_block = convert_text_file(user_stream)
                case _:
                    print_error("Unknown file type!")
            user_stream.close()
            output_file = open("output/" + user_file.split(".")[0] + ".bin", "w")
            output_file.write(formatted_list(mem_block))
            output_file.close()
            filename = user_file.split("/")[-1]
            file_list.append(FileStruct(filename, mem_block))
        else:
            print_error(f"user data file {user_file} not found!")
    return file_list

def create_file_system(user_data_files: list):
    user_data_start = mem_map.get("user_data", None)
    if(user_data_start == None):
        print_error("User data files provided, but no space allocated")
    else:
        user_data_end = user_data_start[1]
        user_data_start = user_data_start[0]

    user_file_system_start = mem_map.get("user_file_system", None)
    if(user_file_system_start == None):
        print_error("User data files provided, but no file system space allocated")
    else:
        user_file_system_end = user_file_system_start[1]
        user_file_system_start = user_file_system_start[0]

    user_data_file_headers = []
    user_data_files_data = []
    for file in user_data_files:

        file.set_name_addr(user_data_start)
        user_data_file_headers.append(word(file.name_addr))
        user_data_files_data.extend(file.hex_filename)
        user_data_start += len(file.hex_filename) * 4

        file.set_data_addr(user_data_start)
        user_data_file_headers.append(word(file.data_addr))
        user_data_files_data.extend(file.data)
        user_data_start += len(file.data) * 4

        user_data_file_headers.append(word(file.data_size))
        user_data_file_headers.append("00000000") #permissions bits - not verified yet, will just be wtv
    print_verbose(formatted_list(user_data_files))
    print_verbose(formatted_list(user_data_file_headers))
    print_verbose(formatted_list(user_data_files_data))

def pass_1_vars(file: io.TextIOWrapper):
    local_vars = {}
    line = file.readline()
    while line:
        if(re.search(r":", line) and not re.search(r"#.*:", line)):
            label_name = re.search(r"(\S+):", line).group(1)
            local_vars[label_name] = "null"
        line = file.readline()
    
    print_debug("Local variable table: \n" + formatted_dict(local_vars))
    return local_vars

def pass_2_convert(file: io.TextIOWrapper):
    hex_structs = []
    line = file.readline()
    i = 0
    while line:
        i += 1
        line_mnemonic = ""
        first_m_loc = len(line)
        for mnemonic in opcode_lookup.keys():
            if(line.find(mnemonic + " ") != -1 and (line.find(mnemonic + " ") < first_m_loc or (line.find(mnemonic + " ") == first_m_loc and len(mnemonic + " ") > len(line_mnemonic + " ")))):
                line_mnemonic = mnemonic
                first_m_loc = line.find(mnemonic)

        reg_regex = r"[ ,(](x[0-9a-f]{1,2})"
        imm_regex = r"((, (([0-9]+)|(0x[0-9a-fA-F]+)|([0-9a-zA-Z_-]+\n)))|(([0-9]+)|(0x[0-9a-fA-F]+)|([0-9a-zA-Z_-]+))\()"
        #regular instructions
        if(line_mnemonic != "" and ("#" not in line or (line.find(line_mnemonic) < line.find("#")))):
            inst = InstructionStruct(line_mnemonic)
            regs = re.findall(reg_regex, line)
            for reg in regs:
                if(reg[0] == "," or reg[0] == "("):
                    reg = reg[1:]
            imm = re.search(imm_regex, line)
            if(imm):
                imm = imm.group(1)
            if(inst.opcode in itype_opcodes):
                if(len(regs) < 2 and line_mnemonic not in ["ebreak", "ecall", "fence", "fence.i"]):
                    print_debug(formatted_list(regs))
                    print_error(f"Insufficient number of registers provided for i-type instruction {line_mnemonic} on line {i}")
                if(imm == None):
                    print_error(f"Immediate value not found for i-type instruction {line_mnemonic} at line {i}")
                inst.set_rd(int(regs[0][1:]))
                inst.set_rs1(int(regs[1][1:]))
                inst.set_imm(imm[2:].strip())
                match line_mnemonic:
                    case "lb": inst.set_f3(0)
                    case "lh": inst.set_f3(1)
                    case "lw": inst.set_f3(2)
                    case "lbu": inst.set_f3(4)
                    case "lhu": inst.set_f3(5)
                    case "fence": inst.set_f3(0)
                    case "fence.i": inst.set_f3(1)
                    case "addi": inst.set_f3(0)
                    case "slli": inst.set_f3(1)
                    case "slti": inst.set_f3(2)
                    case "sltiu": inst.set_f3(3)
                    case "xori": inst.set_f3(4)
                    case "srli": inst.set_f3(5)
                    case "srai": 
                        inst.set_f3(5)
                        inst.set_f7(0x20)
                    case "ori": inst.set_f3(6)
                    case "andi": inst.set_f3(7)
                    case "ebreak": inst.set_imm(1)

            elif(inst.opcode in rtype_opcodes):
                if(len(regs) < 3):
                    print_debug(formatted_list(regs))
                    print_error(f"Insufficient number of registers provided for r-type instruction {line_mnemonic} on line {i}")
                inst.set_rd(int(regs[0][1:]))
                inst.set_rs1(int(regs[1][1:]))
                inst.set_rs2(int(regs[2][1:]))

            elif(inst.opcode in (stype_opcodes | sbtype_opcodes)):
                if(len(regs) < 2):
                    print_debug(formatted_list(regs))
                    print_error(f"Insufficient number of registers provided for s-type instruction {line_mnemonic} on line {i}")
                inst.set_rs1(int(regs[1][1:]))
                inst.set_rs2(int(regs[0][1:]))
                inst.set_imm(imm[2:].strip())

                match line_mnemonic:
                    case "sb": inst.set_f3(0)
                    case "sh": inst.set_f3(1)
                    case "sw": inst.set_f3(2)
                    case "beq": inst.set_f3(0)
                    case "bne": inst.set_f3(1)
                    case "blt": inst.set_f3(4)
                    case "bge": inst.set_f3(5)
                    case "bltu": inst.set_f3(6)
                    case "bgeu": inst.set_f3(7)

            elif(inst.opcode in (utype_opcodes|ujtype_opcodes)):
                if(len(regs) < 1):
                    print_debug(formatted_list(regs))
                    print_error(f"Insufficient number of registers provided for u-type instruction {line_mnemonic} on line {i}")
                inst.set_rd(int(regs[0][1:]))
                inst.set_imm(imm[2:].strip())


            hex_structs.append(inst)

        #labels
        elif(line_mnemonic == "" and ":" in line):
            hex_structs.append(line.strip())

        #pseudo-instructions
        elif(line_mnemonic == ""):
            line_instr = ""
            first_p_loc = len(line)
            for instr in pseudo_instr:
                if(line.find(instr + " ") != -1 and (line.find(instr + " ") < first_p_loc or (line.find(instr + " ") == first_p_loc and len(instr + " ") > len(line_instr + " ")))):
                    line_instr = instr
                    first_p_loc = line.find(instr)

            if(line_instr != ""):
                match line_instr:
                    case "li":
                        inst = InstructionStruct("addi")
                        reg = re.search(reg_regex, line).group(0)
                        imm = re.search(imm_regex, line).group(0)
                        inst.set_rd(int(reg[2:]))
                        inst.set_rs1(0)
                        inst.set_imm(imm[2:].strip())
                        hex_structs.append(inst)
                    case "la":
                        inst = InstructionStruct("addi")
                        reg = re.search(reg_regex, line).group(0)
                        imm = re.search(imm_regex, line).group(0)
                        inst.set_rd(int(reg[2:]))
                        inst.set_rs1(0)
                        inst.set_imm(imm[2:].strip())
                        inst_lui = InstructionStruct("lui")
                        inst_lui.set_rd(int(reg[2:]))
                        inst_lui.set_imm(0xF)
                        hex_structs.append(inst_lui)
                        hex_structs.append(inst)


        print(f"{line[:-1]}: {line_mnemonic}")

        line = file.readline()

    print_debug("Hex conversion structs: \n" + formatted_list(hex_structs))
    return hex_structs

def pass_3_clarify_vars(hex_structs: list, local_vars: dict):
    print_debug(formatted_list(hex_structs))
    if(local_vars):
        last_item_addr = 0
        last_item_index = 0
        for item in hex_structs:
            if type(item) == str:
                #have to find name + resolve sizes
                if(re.search(r"\.", item)):
                    print_debug("Variable found")
                    var_type = re.search(r"\.(\S+)", item).group(1)
                    var_data = re.search(r": (.+)", item).group(1)
                    print_debug(var_type + ", " + var_data)
                    match var_type:
                        case "asciz":
                            var_data = var_data[1:-1]
                            var_data = convert_text_file(io.TextIOWrapper(io.BytesIO(var_data.encode("utf-8"))))
                            print_debug(formatted_list(var_data))
                            var_size = 4 * len(var_data)
                            hex_structs.insert(hex_structs.index(item) + 1, var_data)
                        case _:
                            print_error(f"Unknown variable directive {var_type}")
                else:
                    print_debug("Label found")
                    var_size = 0
                label_name = re.search(r"(\S+):", item).group(1)
                local_vars[label_name] = 4 * (hex_structs.index(item) - last_item_index) + (last_item_addr)
                last_item_addr = local_vars[label_name] + var_size
                last_item_index = hex_structs.index(item)
                hex_structs.pop(hex_structs.index(item))
        for item in hex_structs:
            if(type(item) == list):
                index = hex_structs.index(item)
                hex_structs.pop(index)
                for i in range(0, len(item)):
                    hex_structs.insert(index + i, item[i])
        print_debug(formatted_list(hex_structs))
        print_debug(formatted_dict(local_vars))
    else:
        print_debug("No local vars found")

def pass_4_resolve_vars(hex_structs: list, local_vars: dict, include_vars: dict, base_addr: int):
    i = 0
    for item in hex_structs:
        if(type(item) == InstructionStruct):
            if(item.opcode not in rtype_opcodes):
                if(type(item.imm) == str):
                    if(re.search(r"[0-9]*", item.imm) != None and re.search(r"[0-9]*", item.imm).group(0) == item.imm):
                        item.imm = int(item.imm)
                    elif(item.imm in local_vars.keys()):
                        item.imm = local_vars[item.imm]
                        item.imm = item.imm + (base_addr)
                    elif(item.imm in include_vars.keys()):
                        item.imm = include_vars[item.imm]
                    elif(item.imm in io_mapping.keys()):
                        item.imm = io_mapping[item.imm]
                    else:
                        print_error(f"Immediate variable {item.imm} found outside of scope")
                if(item.opcode in sbtype_opcodes|ujtype_opcodes):
                    print_debug(f"Initial immediate: {item.imm}, base_addr: {base_addr}, i: {i}")
                    item.imm = (((item.imm - base_addr)) - i)
                    print_debug(f"new imm: {item.imm}")
            i += 4
    print_debug(formatted_list(hex_structs))
    

def pass_5_convert(hex_structs: list):
    for i in range(0, len(hex_structs)):
        if(type(hex_structs[i]) == InstructionStruct):
            hex_structs[i] = hex_structs[i].convert_to_hex()
            print_debug(hex_structs[i])
    
    print_debug(formatted_list(hex_structs))
        
def write_asm_file(asm_file: io.TextIOWrapper, asm_lines: list):
    for i in range(0, len(asm_lines)):
    # for line in asm_lines:
        while(len(asm_lines[i]) < 8):
            asm_lines[i] = "0" + asm_lines[i]
        asm_file.write(asm_lines[i] + "\n")

def include_dictionary(main_dict: dict, add_dict: dict, address: int):
    for item in add_dict.keys():
        main_dict[item] = add_dict[item] + address

def parse_asm_file_part1(kernel_file_name: string):
    kernel_file = open(kernel_file_name, "r")
    #handle includes - need to push file names onto a stack so that I can recursively get the right things
    print_verbose("Parsing kernel file " + kernel_file_name)
    global kernel_file_stack
    #searching for include files and traversing the tree
    line = kernel_file.readline()
    include_vars_dict = {}
    while line:
        #including a file
        if(re.search(r"\.include \"[A-Za-z0-9._-]+\"", line)):
            include_file_name = re.search(r"\.include \"([A-Za-z0-9\._-]+)\"", line).group(1)
            print_verbose("Including file " + include_file_name)
            #absolute filename path if "/", else relative path
            if(include_file_name[0] != '/'):
                include_file_name = "/".join(kernel_file_name.split("/")[:-1]) + "/" + include_file_name
            if(include_file_name in kernel_file_stack):
                print_error(f"Circular dependencies found in assembly base: \n{include_file_name} and {kernel_file_name}")
            
            #identify whether include file was already parsed or not
            include_parsed = False
            if(kernel_files[include_file_name][0] == "Separately parsed"):
                print_verbose("Include file already parsed, importing data")
                include_parsed = True
            
            if(not include_parsed):
                kernel_file_stack.append(kernel_file_name)
                parse_asm_file_part1(include_file_name)

            include_vars_dict.update(kernel_files[include_file_name][2])

        line = kernel_file.readline()

    #finished including files (mostly) - need to do first pass here and identify variables
    kernel_file.seek(0)
    local_vars_dict = pass_1_vars(kernel_file)
    # local_vars_dict.update(include_vars_dict)

    #second pass - generate structs for each instruction, store as list of instruction objects
    kernel_file.seek(0)
    kernel_files[kernel_file_name][2] = local_vars_dict
    kernel_files[kernel_file_name][3] = pass_2_convert(kernel_file)

    kernel_files[kernel_file_name][0] = "Separately parsed"
    kernel_file.close()


def parse_asm_file_part2(kernel_file_name: string):
    hex_file = kernel_files[kernel_file_name][3]
    local_vars_dict = kernel_files[kernel_file_name][2]
    kernel_file = open(kernel_file_name, "r")
    line = kernel_file.readline()
    include_vars_dict = {}
    while line:
        #including a file
        if(re.search(r"\.include \"[A-Za-z0-9._-]+\"", line)):
            include_file_name = re.search(r"\.include \"([A-Za-z0-9\._-]+)\"", line).group(1)
            print_verbose("Including file " + include_file_name)
            #absolute filename path if "/", else relative path
            if(include_file_name[0] != '/'):
                include_file_name = "/".join(kernel_file_name.split("/")[:-1]) + "/" + include_file_name
            if(include_file_name in kernel_file_stack):
                print_error(f"Circular dependencies found in assembly base: \n{include_file_name} and {kernel_file_name}")
            
            #identify whether include file was already parsed or not
            include_parsed = False
            if(kernel_files[include_file_name][0] == "Fully parsed"):
                print_verbose("Include file already parsed, importing data")
                include_parsed = True
            
            if(not include_parsed):
                kernel_file_stack.append(kernel_file_name)
                parse_asm_file_part2(include_file_name)

            # local_vars_dict.update(kernel_files[include_file_name][2])
            include_dictionary(include_vars_dict, kernel_files[include_file_name][2], kernel_files[include_file_name][1])
            print_debug(formatted_dict(kernel_files[include_file_name][2]))
            print_debug(formatted_dict(include_vars_dict))

        line = kernel_file.readline()

    pass_3_clarify_vars(hex_file, local_vars_dict)
    # include_dictionary(local_vars_dict, local_vars_dict, kernel_files[kernel_file_name][1])

    pass_4_resolve_vars(hex_file, local_vars_dict, include_vars_dict, kernel_files[kernel_file_name][1])

    pass_5_convert(hex_file)

    kernel_files[kernel_file_name][2] = local_vars_dict
    kernel_files[kernel_file_name][0] = "Fully parsed"
    print_verbose("Completely parsed file " + kernel_file_name)
    kernel_output_file = open("output/" + kernel_file_name[:-4] + ".bin", "w")
    write_asm_file(kernel_output_file, hex_file)
    kernel_output_file.close()
    kernel_file.close()

def assign_file_addresses():
    kernel_addr_start = mem_map["kernel_code"][0]
    
    for filename in kernel_files.keys():
        if(kernel_files[filename][1] == -1):
            kernel_files[filename][1] = kernel_addr_start
            kernel_addr_start += len(kernel_files[filename][3])
            kernel_addr_start = ((kernel_addr_start >> 6) + 1) << 6
            print_verbose(f"Filename: {filename}, address: {kernel_files[filename][1]}, file size: {len(kernel_files[filename][3])}")

def parse_kernel_programs():
    #first pass - identify all variables
    global kernel_files
    for filename in kernel_files.keys():
        if(kernel_files[filename][0] != "Separately parsed"):
            parse_asm_file_part1(filename)

    assign_file_addresses()

    for filename in kernel_files.keys():
        if(kernel_files[filename][0] != "Fully parsed"):
            parse_asm_file_part2(filename)
    return 0

def write_output_file():
    ordered_list_of_filenames = []
    list_of_filenames = kernel_files.keys()# + user_data_files
    
    for i in range(0, len(list_of_filenames)):
        min_address = 0xFFFF
        min_item = ""
        for item in list_of_filenames:
            if item in ordered_list_of_filenames:
                continue
            elif item in kernel_files.keys():
                if kernel_files[item][1] < min_address:
                    min_address = kernel_files[item][1] >> 2
                    min_item = item
            #elif item in user_data_files:

        ordered_list_of_filenames.append(min_item)

    print_debug("Order of files: \n" + formatted_list(ordered_list_of_filenames))

    curr_addr = 0x0000
    img_out_file = open("output/out.hex", "w")

    #used if no bootloader provided
    if(r".+boot\.asm" not in list_of_filenames):
        img_out_file.write("0x0000f0b7\n")
        img_out_file.write("0x000080e7\n")
        curr_addr = 2

    for item in ordered_list_of_filenames:
        if item in kernel_files.keys():
            while(curr_addr < kernel_files[item][1] >> 2):
                img_out_file.write("0x00000000\n")
                curr_addr += 1
            for hex_line in kernel_files[item][3]:
                img_out_file.write("0x" + hex_line + "\n")
                curr_addr += 1
    
    img_out_file.close()

def main():
    parse_cli()
    print("Debug output enabled: ", debugger)
    print("Verbose output enabled: ", verbose or debugger)
    parse_build_file_yml()
    user_data_filesystem = parse_user_data()
    create_file_system(user_data_filesystem)

    parse_kernel_programs()
    write_output_file()
    

if __name__ == "__main__":
    main()