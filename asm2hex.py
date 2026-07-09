import re
import struct
import sys

asm_file_name = sys.argv[1]
# asm_file_name = input("Please input the asm file name: ")
options = sys.argv[2:]

debugger = False

def print_debug(debug_string):
	if(debugger):
		print(debug_string)

if("-debug" in options):
	debugger = True
else:
	debugger = False

if("-no-addr" in options):
	no_addresses = True
else:
	no_addresses = False

asm_file = open(asm_file_name, "r")
asm_lines = asm_file.readlines()

if("-I" in options):
	index = options.index("-I")
	include_file_name = options[index + 1]
	include_file = open(include_file_name, "r")
	include_lines = include_file.readlines()
	asm_lines.extend(include_lines)
	include_file.close()


hex_file_name = "out.hex"

hex_file = open(hex_file_name, "w")

print_debug(asm_lines)

def dec_to_bin_imm(imm, address_calc):
	# if(imm < 0 and address_calc == True):
	# 	imm = imm + 4
	print_debug(address_calc)
	bin_imm = str(bin(imm))
	print_debug("binary value passed to function: " + bin_imm)
	if(bin_imm[0] == "-"):
		bin_imm = bin_imm[3:]
		bin_imm_flip = ""
		#swap all bits
		print_debug(bin_imm)
		for c in range(0, len(bin_imm)):
			if(bin_imm[c] == "0"):
				# bin_imm = bin_imm[0:c] + "1" + bin_imm[c:len(bin_imm) - 1]
				bin_imm_flip = bin_imm_flip + "1"
			elif(bin_imm[c] == "1"):
				# bin_imm = bin_imm[0:c] + "0" + bin_imm[c:len(bin_imm) - 1]
				bin_imm_flip = bin_imm_flip + "0"
			print_debug(bin_imm_flip)
		#need to figure out how to add 1 as well
		if(bin_imm_flip[-1] == "0"):
			bin_imm_flip = bin_imm_flip[:-1] + "1"
		else:
			#this is simply not yet correct
			p = -1
			if(address_calc == True):
				bin_imm_flip2 = ""
			else:
				bin_imm_flip2 = ""
			while(-1 * p < len(bin_imm_flip)):
				if(bin_imm_flip[p] == "1"):
					bin_imm_flip2 = "0" + bin_imm_flip2
					p = p - 1
				else:
					bin_imm_flip2 = "1" + bin_imm_flip2
					bin_imm_flip2 = bin_imm_flip[:p] + bin_imm_flip2
					p = -1 * len(bin_imm_flip)
				print_debug(bin_imm_flip2)
			bin_imm_flip = bin_imm_flip2
		while(len(bin_imm_flip) < 32):
			bin_imm_flip = "1" + bin_imm_flip
		bin_imm = bin_imm_flip
	else:
		bin_imm = bin_imm[2:]
		while(len(bin_imm) < 32):
			bin_imm = "0" + bin_imm
	print_debug(str(bin_imm))
	return bin_imm


address = 0
label_address = 0

labels = dict()
print_debug("number of lines: " + str(len(asm_lines)))
#need to identify all labels and create a table for their addresses
for l in range(0, len(asm_lines)):
	# print_debug("label_address: " + str(label_address))
	# print_debug("l: " + str(l))
	label_line = asm_lines[l]
	if(re.search(r"#", label_line)):
		blocks = label_line.split("#")
		if(blocks[0] != ""):
			label_line = blocks[0]
		else:
			continue
	if(re.search(r"([_a-zA-Z0-9]+):", label_line)):
		label = re.search(r"([_a-zA-Z0-9]+):", label_line).group(0)
		labels[label[:-1]] = (label_address) << 2
#		 label_address = label_address + 1
	elif(re.search(r"org", label_line)):
		base = 10
		if(re.search(r"0x", label_line)):
			base = 16
		# print_debug(re.findall(r" (0x)?([0-9a-fA-F]+)", asm_lines[i]))
		value = int(re.search(r"[0-9a-fA-F]+", re.findall(r" (0x)?([0-9a-fA-F]+)", label_line)[-1][-1]).group(0), base) >> 2
		label_address = value

	# need to remember what the hell this was all about - load immediates which require 2 instrs to operate
	elif(re.search(r"(?<!s[rl])li ", label_line)):
		if(re.findall(r", [A-Za-z0-9_]+", label_line) != None):
			label_address = label_address + 2
		else:
			base = 10
			if(re.search(r"0x", label_line)):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", label_line)[-1][-1]).group(0), base)
			if(imm > 2048):
				label_address = label_address + 2
			else:
				label_address = label_address + 1
	elif(re.search(r"[0-9a-zA-Z]+", label_line)):
		label_address = label_address + 1

print(labels)

for i in range(0, len(asm_lines)):
	to_print = True
	hex_line = "test" + asm_lines[i] + "\n"
	hex_addr = hex(address)
	while(len(hex_addr) < 6):
		hex_addr = "0x0" + hex_addr[2:]
	hex_addr_1 = hex(address + 1)
	while(len(hex_addr_1) < 6):
		hex_addr_1 = "0x0" + hex_addr_1[2:]
	if(asm_lines[i].strip() == ""):
		print_debug("blank line at index " + str(i))
		continue
	if(re.search(r"#", asm_lines[i])):
		print_debug("This line is a comment " + str(i))
		blocks = asm_lines[i].split("#")
		if(blocks[0].strip() != ""):
			asm_lines[i] = blocks[0]
		else:
			continue
	if(re.search(r":", asm_lines[i])):
		continue
	if(re.search(r"org", asm_lines[i])):
		# print_debug("org instruction")
		base = 10
		if(re.search(r"0x", asm_lines[i])):
			base = 16
		# print_debug(re.findall(r" (0x)?([0-9a-fA-F]+)", asm_lines[i]))
		new_address = int(re.search(r"[0-9a-fA-F]+", re.findall(r" (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base) >> 2
		if(no_addresses):
			for j in range(0, new_address - address):
				hex_file.write("00000000\n")
		address = new_address
		continue
	else:
		if(re.search(r"cfw", asm_lines[i])):
			# print_debug(asm_lines[i])
			if(re.search(r"\"", asm_lines[i])):
				print_debug("a string")
				print_debug(asm_lines[i])
				index1 = asm_lines[i].find("\"")
				print_debug(index1)
				string = asm_lines[i][index1 + 1:]
				print_debug(string)
				data = ""
				for i in range(0, len(string)):
					# print_debug(hex(ord(string[i]))[2:])
					data_add = hex(ord(string[i]))[2:]
					if(i%4 != 0 or i == 0):
						while(len(data_add) < 2):
							data_add = "0" + data_add
						data = data + data_add
					else:
						print_debug(data)
						#need to increment addr and print to file
						if(no_addresses):
							hex_line = data + "\n"
						else:
							hex_line = hex_addr + data + "\n"
						hex_file.write(hex_line)
						address = address + 1
						hex_addr = hex(address)
						data = hex(ord(string[i]))[2:]
				if(data != ""):
					print_debug("data printed at end of loop: " + data)
					while(len(data) < 8):
						data = data + "0"
					if(no_addresses):
						hex_line = data + "\n"
					else:
						hex_line = hex_addr + data + "\n"
			elif(re.search(r"\.", asm_lines[i])):
				fp = float(re.search(r"-?[0-9]+.[0-9]+", asm_lines[i]).group(0))
				fp_bin = hex(int(format(struct.unpack('!I', struct.pack('!f', fp))[0], '032b'), 2))[2:]
				hex_line = hex_addr + fp_bin + "\n"
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r"(0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
				imm_str = str(hex(imm)[2:])
				while(len(imm_str) < 8):
					imm_str = "0" + imm_str
				hex_line = hex_addr + imm_str + "\n"
		elif(re.search(r"jalr", asm_lines[i])):
			opcode = 103
			f3 = 0
			rs1 = int(re.search(r"[0-9]+", re.findall(r"\(x([0-9]+)\)", asm_lines[i])[0]).group(0))
			rd = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r"(0x)?([0-9a-fA-F]+)\(", asm_lines[i])[0][-1]).group(0), base)
			imm_str = dec_to_bin_imm(imm, True)
			imm_pt1 = int(imm_str[-12:], 2)
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"jal", asm_lines[i])):
			opcode = 111
			if(re.findall(r"x([0-9]+)", asm_lines[i])):
				rd = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			else:
				rd = 1
			if(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				imm = (labels[(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r" (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			print_debug(imm)
			# need to take into account bit swizzling lowkey dont wanna do that rn
			bin_imm = dec_to_bin_imm(imm, True)
			print_debug("immediate value (for jal): " + bin_imm)
			print_debug(len(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12]))
			imm_val = int(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12], 2)
			print_debug("bit-swizzled imm val: " + str(hex(imm_val)))
			command = hex((imm_val << 12) + (rd << 7) + opcode)[2:]
			print_debug(command)
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"jr ", asm_lines[i])):
			opcode = 103
			f3 = 0
			rs1 = int(re.search(r"[0-9]+", re.findall(r"\(?x([0-9]+)\)?", asm_lines[i])[0]).group(0))
			rd = 0
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = re.search(r"[0-9a-fA-F]+", re.findall(r"(0x)?([0-9a-fA-F]+)\(?", asm_lines[i])[0][-1]).group(0)
			if(imm != ''):
				imm_str = dec_to_bin_imm(int(imm, base), True)
				imm_pt1 = int(imm_str[-12:-1], 2)
			else:
				imm_pt1 = 0
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"j ", asm_lines[i])):
			opcode = 111
			rd = 0
			if(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				imm = (labels[(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r" (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			imm = imm + (int(hex_addr, 16) << 2)
			print_debug(imm)
			# need to take into account bit swizzling lowkey dont wanna do that rn
			bin_imm = dec_to_bin_imm(imm, True)
			print_debug("immediate value (for jal): " + bin_imm)
			print_debug(len(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12]))
			imm_val = int(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12], 2)
			print_debug("bit-swizzled imm val: " + str(hex(imm_val)))
			command = hex((imm_val << 12) + (rd << 7) + opcode)[2:]
			print_debug(command)
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"beq", asm_lines[i])):
			opcode = 99
			f3 = 0
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, False)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-5], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bne", asm_lines[i])):
			opcode = 99
			f3 = 1
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, False)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-5], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bltu", asm_lines[i])):
			opcode = 99
			f3 = 6
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, True)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bgeu", asm_lines[i])):
			opcode = 99
			f3 = 7
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, True)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"blt", asm_lines[i])):
			opcode = 99
			f3 = 4
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, True)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bge", asm_lines[i])):
			opcode = 99
			f3 = 5
			rs1 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print_debug(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print_debug("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm, True)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"fl[wd]", asm_lines[i])):
			opcode = 7
			if(re.search(r"fld", asm_lines[i])):
				f3 = 3
			else:
				f3 = 2
			rd = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+),", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", re.findall(r"\(x([0-9]+)\)", asm_lines[i])[0]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"f(add|sub|mul|div).[sd]", asm_lines[i])):
			opcode = 83
			if(re.search(r"f(add|sub|mul|div).s", asm_lines[i])):
				f7 = 0
			else:
				f7 = 1
			if(re.search(r"sub", asm_lines[i])):
				f7 = f7 + 4
			elif(re.search(r"mul", asm_lines[i])):
				f7 = f7 + 8
			elif(re.search(r"div", asm_lines[i])):
				f7 = f7 + 12
			f3 = 0
			registers = re.findall(r"f([0-9]+)", asm_lines[i])
			if(len(registers) < 3):
				print(f"error - not enough registers listed for floating point r-type instruction at line number {i + 1}")
				print(registers)
			rd = int(re.search(r"[0-9]+", registers[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", registers[1]).group(0))
			rs2 = int(re.search(r"[0-9]+", registers[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"((add|sra|srl|sll|xor|or|and|slt)i )|sltiu", asm_lines[i])):
			#store everything as integers and bit shift as needed
			opcode = 19
			if(re.search(r"(sra|srl)", asm_lines[i])):
				f3 = 5
			elif(re.search(r"(sll)", asm_lines[i])):
				f3 = 1
			elif(re.search(r"xor", asm_lines[i])):
				f3 = 4
			elif(re.search(r"or", asm_lines[i])):
				f3 = 6
			elif(re.search(r"and", asm_lines[i])):
				f3 = 7
			elif(re.search(r"slt", asm_lines[i])):
				f3 = 2
			elif(re.search(r"sltu", asm_lines[i])):
				f3 = 3
			else:
				f3 = 0
			registers = re.findall(r"x([0-9]+)", asm_lines[i])
			if(len(registers) < 2):
				print(f"error - not enough registers listed for i-type instruction at line number {i + 1}")
				print(registers)
				print(re.search(r"(add|sra|srl|sll|xor|or|and|slt|sltu)i ", asm_lines[i]))
			rd = int(re.search(r"[0-9]+", registers[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", registers[1]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)(|-?(0x)?([0-9a-fA-F]+))", asm_lines[i]) == None):
				print(f"error - no immediate value found at line {i + 1}")
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"-?[0-9a-fA-F]+", re.findall(r", -?(0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			if(re.search(r"-", asm_lines[i])):
				imm = int(dec_to_bin_imm(-1 * imm, False),2)
				command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[3:]
			else:
				if(re.search(r"sra", asm_lines[i])):
					imm = imm + (32 * 32)
					print_debug(f"sra immediate: {imm}")
				command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			print_debug(f"i type command: {command}")
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"(add |sub |sra |srl |sll |xor |or |and |slt |sltu )", asm_lines[i])):
			#r type rv32i instructions
			opcode = 51
			if(re.search(r"(sra|srl)", asm_lines[i])):
				f3 = 5
			elif(re.search(r"(sll)", asm_lines[i])):
				f3 = 1
			elif(re.search(r"xor", asm_lines[i])):
				f3 = 4
			elif(re.search(r"or", asm_lines[i])):
				f3 = 6
			elif(re.search(r"and", asm_lines[i])):
				f3 = 7
			elif(re.search(r"slt", asm_lines[i])):
				f3 = 2
			elif(re.search(r"sltu", asm_lines[i])):
				f3 = 3
			else:
				f3 = 0
			if(re.search(r"(sub|sra)", asm_lines[i])):
				f7 = 32
			else:
				f7 = 0
			registers = re.findall(r"x([0-9]+)", asm_lines[i])
			if(len(registers) < 3):
				print(f"error - not enough registers listed for r-type instruction at line number {i + 1}")
				print(registers)
			rd = int(re.search(r"[0-9]+", registers[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", registers[1]).group(0))
			rs2 = int(re.search(r"[0-9]+", registers[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"lui ", asm_lines[i])):
			opcode = 55
			rd = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			command = hex((int)(imm << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"li ", asm_lines[i])):
			opcode = 19
			f3 = 0
			rd = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = 0
			if(re.search(r"[A-Za-z0-9_]+", re.findall(r", [A-Za-z0-9_]+", asm_lines[i])[0]).group(0) in labels.keys()):
				label = re.search(r"[A-Za-z0-9_]+", re.findall(r", [A-Za-z0-9_]+", asm_lines[i])[0]).group(0)
				imm = labels[label]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r", (0x)?([0-9a-fA-F]+)", asm_lines[i])[0][-1]).group(0), base)
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
					if(no_addresses):
						hex_file.write(command2 + "\n")
					else:
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
					if(no_addresses):
						hex_file.write(command2 + "\n")
					else:
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
					if(no_addresses):
						hex_file.write(command2 + "\n")
					else:
						hex_file.write(hex_addr + command2 + "\n")
					address = address + 1
		elif(re.search(r"s[whb]", asm_lines[i])):
			opcode = 35
			if(re.search(r"sw", asm_lines[i])):
				f3 = 2
			elif(re.search(r"sh", asm_lines[i])):
				f3 = 1
			elif(re.search(r"sb", asm_lines[i])):
				f3 = 0
			rs1 = int(re.search(r"[0-9]+", re.findall(r"\(x([0-9]+)\)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r"-?(0x)?([0-9a-fA-F]+)\(", asm_lines[i])[0][-1]).group(0), base)
			imm_str = dec_to_bin_imm(imm, False)
			imm_pt1 = int(imm_str[-12:-5], 2)
			imm_pt2 = int(imm_str[-5:], 2)
			command = hex((imm_pt1 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt2 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"l[whb]u?", asm_lines[i])):
			opcode = 3
			if(re.search(r"lw", asm_lines[i])):
				f3 = 2
			elif(re.search(r"lh", asm_lines[i])):
				f3 = 1
			elif(re.search(r"lb", asm_lines[i])):
				f3 = 0
			if(re.search(r"u", asm_lines[i])):
				f3 = f3 + 4
			rs1 = int(re.search(r"[0-9]+", re.findall(r"\(x([0-9]+)\)", asm_lines[i])[0]).group(0))
			rd = int(re.search(r"[0-9]+", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r"-?(0x)?([0-9a-fA-F]+)\(", asm_lines[i])[0][-1]).group(0), base)
			if(re.search(r"-", asm_lines[i])):
				imm = imm * -1
			imm_str = dec_to_bin_imm(imm, False)
			print_debug(f"imm_str for load instr: {imm_str}")
			imm_pt1 = int(imm_str[-12:], 2)
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"ebreak", asm_lines[i])):
			opcode = 115
			imm = 1
			f3 = 0
			rs1 = 0
			rd = 0
			command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"halt", asm_lines[i])):
			hex_line = hex_addr + "ffffffff\n"
		if(no_addresses and hex_line[0] == '0'):
			hex_line = hex_line[6:]
		# print_debug(f"asm_lines[i]: {asm_lines[i]}, hex_line: {hex_line}")
		hex_file.write(hex_line)
		address = address + 1