import re
import struct

asm_file_name = input("Please input the asm file name: ")

asm_file = open(asm_file_name, "r")

asm_lines = asm_file.readlines()

# hex_file_name = input("Please input the hex file name: ")

hex_file_name = "out.hex"

hex_file = open(hex_file_name, "w")

# print(asm_lines)

def dec_to_bin_imm(imm):
	if(imm < 0):
		imm = imm + 4
	bin_imm = str(bin(imm))
	print("binary value passed to function: " + bin_imm)
	if(bin_imm[0] == "-"):
		bin_imm = bin_imm[3:]
		bin_imm_flip = ""
		#swap all bits
		print(bin_imm)
		for c in range(0, len(bin_imm)):
			if(bin_imm[c] == "0"):
				# bin_imm = bin_imm[0:c] + "1" + bin_imm[c:len(bin_imm) - 1]
				bin_imm_flip = bin_imm_flip + "1"
			elif(bin_imm[c] == "1"):
				# bin_imm = bin_imm[0:c] + "0" + bin_imm[c:len(bin_imm) - 1]
				bin_imm_flip = bin_imm_flip + "0"
			print(bin_imm_flip)
		#need to figure out how to add 1 as well
		if(bin_imm_flip[-1] == "0"):
			bin_imm_flip = bin_imm_flip[:-1] + "1"
		else:
			#this is simply not yet correct
			p = -1
			while p > -1 * (len(bin_imm_flip) + 1):
				print("p index: " + str(p))
				print(bin_imm_flip[p])
				if(bin_imm_flip[p] == "0"):
					bin_imm_flip = bin_imm_flip[:p] + "1"
					
					while p < -1:
						bin_imm_flip = bin_imm_flip + "0"
						p = p + 1
					p = -1 * len(bin_imm_flip)
				else:
					p = p - 1
		while(len(bin_imm_flip) < 32):
			bin_imm_flip = "1" + bin_imm_flip
		bin_imm = bin_imm_flip
	else:
		bin_imm = bin_imm[2:]
		while(len(bin_imm) < 32):
			bin_imm = "0" + bin_imm
	print(str(bin_imm))
	return bin_imm

#TODO:
# branch instructions
# lw/sw instructions
# figure out wtf is happening with some of these instructions that are different

address = 0
label_address = 0

labels = dict()
print(len(asm_lines))
#need to identify all labels and create a table for their addresses
for l in range(0, len(asm_lines)):
	print("label_address: " + str(label_address))
	print("l: " + str(l))
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
		# print(re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i]))
		value = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", label_line)[-1][-1]).group(0), base) >> 2
		label_address = value

	# need to remember what the hell this was all about - load immediates which require 2 instrs to operate
	elif(re.search(r"(?<!s[rl])li ", label_line)):
		base = 10
		if(re.search(r"0x", label_line)):
			base = 16
		imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", label_line)[-1][-1]).group(0), base)
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
		print("blank line at index " + str(i))
		continue
	if(re.search(r"#", asm_lines[i])):
		print("This line is a comment " + str(i))
		blocks = asm_lines[i].split("#")
		if(blocks[0].strip() != ""):
			asm_lines[i] = blocks[0]
		else:
			continue
	if(re.search(r":", asm_lines[i])):
		continue
	if(re.search(r"org", asm_lines[i])):
		# print("org instruction")
		base = 10
		if(re.search(r"0x", asm_lines[i])):
			base = 16
		# print(re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i]))
		address = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base) >> 2
		continue
	else:
		if(re.search(r"cfw", asm_lines[i])):
			# print(asm_lines[i])
			if(re.search(r"\"", asm_lines[i])):
				print("a string")
				string = asm_lines[i].strip(" \" ")
				string = string[3:].strip("\" ")
				print(string)
				data = ""
				for i in range(0, len(string)):
					# print(hex(ord(string[i]))[2:])
					data_add = hex(ord(string[i]))[2:]
					if(i%4 != 0 or i == 0):
						while(len(data_add) < 2):
							data_add = "0" + data_add
						data = data + data_add
					else:
						print(data)
						#need to increment addr and print to file
						hex_line = hex_addr + data + "\n"
						hex_file.write(hex_line)
						address = address + 1
						hex_addr = hex(address)
						data = hex(ord(string[i]))[2:]
				if(data != ""):
					print(data)
					while(len(data) < 8):
						data = "0" + data
					hex_line = hex_addr + data + "\n"
			elif(re.search(r".", asm_lines[i])):
				fp = float(re.search(r"-?[0-9]+.[0-9]*", asm_lines[i]).group(0))
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
			rs1 = int(re.search(r"[0-9]*", re.findall(r"\(x([0-9]*)\)", asm_lines[i])[0]).group(0))
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r"(0x)?([0-9a-fA-F]*)\(", asm_lines[i])[0][-1]).group(0), base)
			imm_str = dec_to_bin_imm(imm)
			imm_pt1 = int(imm_str[-12:-1], 2)
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"jal", asm_lines[i])):
			opcode = 111
			rd = 1 #not constant, but at least something
			if(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				imm = (labels[(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			print(imm)
			# need to take into account bit swizzling lowkey dont wanna do that rn
			bin_imm = dec_to_bin_imm(imm)
			print("immediate value (for jal): " + bin_imm)
			print(len(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12]))
			imm_val = int(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12], 2)
			print("bit-swizzled imm val: " + str(hex(imm_val)))
			command = hex((imm_val << 12) + (rd << 7) + opcode)[2:]
			print(command)
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"jr", asm_lines[i])):
			opcode = 103
			f3 = 0
			rs1 = int(re.search(r"[0-9]*", re.findall(r"\(?x([0-9]*)\)?", asm_lines[i])[0]).group(0))
			rd = 0
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = re.search(r"[0-9a-fA-F]*", re.findall(r"(0x)?([0-9a-fA-F]*)\(?", asm_lines[i])[0][-1]).group(0)
			if(imm != ''):
				imm_str = dec_to_bin_imm(int(imm, base))
				imm_pt1 = int(imm_str[-12:-1], 2)
			else:
				imm_pt1 = 0
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"j", asm_lines[i])):
			opcode = 111
			rd = 0
			if(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				imm = (labels[(re.findall(r"([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			imm = imm + (int(hex_addr, 16) << 2)
			print(imm)
			# need to take into account bit swizzling lowkey dont wanna do that rn
			bin_imm = dec_to_bin_imm(imm)
			print("immediate value (for jal): " + bin_imm)
			print(len(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12]))
			imm_val = int(bin_imm[-21] + bin_imm[-11:-1] + bin_imm[-12] + bin_imm[-20:-12], 2)
			print("bit-swizzled imm val: " + str(hex(imm_val)))
			command = hex((imm_val << 12) + (rd << 7) + opcode)[2:]
			print(command)
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"beq", asm_lines[i])):
			opcode = 99
			f3 = 0
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bne", asm_lines[i])):
			opcode = 99
			f3 = 1
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bltu", asm_lines[i])):
			opcode = 99
			f3 = 6
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bgeu", asm_lines[i])):
			opcode = 99
			f3 = 7
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"blt", asm_lines[i])):
			opcode = 99
			f3 = 4
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"bge", asm_lines[i])):
			opcode = 99
			f3 = 5
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])):
				print(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i]))
				imm = (labels[(re.findall(r", ([a-zA-Z]([a-zA-Z_0-9]|<?!x[0-9])+)", asm_lines[i])[-1][0])] - ((address + 1) << 2))
				print("imm val from label: " + str(imm))
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			bin_imm = dec_to_bin_imm(imm)
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
			rd = int(re.search(r"[0-9]*", re.findall(r"f([0-9]*),", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]*", re.findall(r"\(x([0-9]*)\)", asm_lines[i])[0]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			command = hex((imm << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"fadd.[sd]", asm_lines[i])):
			opcode = 83
			if(re.search(r"fadd.s", asm_lines[i])):
				f7 = 0
			else:
				f7 = 1
			f3 = 0
			rd = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[1]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"fsub.[sd]", asm_lines[i])):
			opcode = 83
			if(re.search(r"fsub.s", asm_lines[i])):
				f7 = 4
			else:
				f7 = 5
			f3 = 0
			rd = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[1]).group(0))
			rs2 = int(re.search(r"[0-9]+", re.findall(r"f([0-9]+)", asm_lines[i])[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"slli", asm_lines[i])):
			opcode = 19
			f3 = 1
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"-?[0-9a-fA-F]*", re.findall(r", -?(0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
				print("addi search", re.findall(r", -?([0-9a-fA-F]*)", asm_lines[i])[-1][-1])
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
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
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
		elif(re.search(r"add", asm_lines[i])):
			#store everything as integers and bit shift as needed
			opcode = 51
			f3 = 0
			f7 = 0
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"sub", asm_lines[i])):
			#store everything as integers and bit shift as needed
			opcode = 51
			f3 = 0
			f7 = 32
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
		elif(re.search(r"slt", asm_lines[i])):
			opcode = 51
			f3 = 2
			f7 = 0
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"sltu", asm_lines[i])):
			opcode = 51
			f3 = 3
			f7 = 0
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			rs1 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[1]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[2]).group(0))
			command = hex((f7 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"lui", asm_lines[i])):
			opcode = 55
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]+)", asm_lines[i])[0]).group(0))
			if(re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.search(r", ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i]).group(1)]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r", (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			command = hex((int)(imm << 12) + (rd << 7) + opcode)[2:]
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
		elif(re.search(r"s[whb]", asm_lines[i])):
			opcode = 35
			if(re.search(r"sw", asm_lines[i])):
				f3 = 2
			elif(re.search(r"sh", asm_lines[i])):
				f3 = 1
			elif(re.search(r"sb", asm_lines[i])):
				f3 = 0
			rs1 = int(re.search(r"[0-9]*", re.findall(r"\(x([0-9]*)\)", asm_lines[i])[0]).group(0))
			rs2 = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r"(0x)?([0-9a-fA-F]*)\(", asm_lines[i])[0][-1]).group(0), base)
			imm_str = dec_to_bin_imm(imm)
			imm_pt1 = int(imm_str[-12:-6], 2)
			imm_pt2 = int(imm_str[-5:-1], 2)
			command = hex((imm_pt1 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt2 << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"l[whb]", asm_lines[i])):
			opcode = 3
			if(re.search(r"lw", asm_lines[i])):
				f3 = 2
			elif(re.search(r"lh", asm_lines[i])):
				f3 = 1
			elif(re.search(r"lb", asm_lines[i])):
				f3 = 0
			rs1 = int(re.search(r"[0-9]*", re.findall(r"\(x([0-9]*)\)", asm_lines[i])[0]).group(0))
			rd = int(re.search(r"[0-9]*", re.findall(r"x([0-9]*)", asm_lines[i])[0]).group(0))
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r"(0x)?([0-9a-fA-F]*)\(", asm_lines[i])[0][-1]).group(0), base)
			imm_str = dec_to_bin_imm(imm)
			imm_pt1 = int(imm_str[-12:-1], 2)
			command = hex((imm_pt1 << 20) + (rs1 << 15) + (f3 << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"halt", asm_lines[i])):
			hex_line = hex_addr + "ffffffff\n"
		hex_file.write(hex_line)
		address = address + 1
