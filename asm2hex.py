import re

asm_file_name = input("Please input the asm file name: ")

asm_file = open(asm_file_name, "r")

asm_lines = asm_file.readlines()

# hex_file_name = input("Please input the hex file name: ")

hex_file_name = "out.hex"

hex_file = open(hex_file_name, "w")

# print(asm_lines)

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
		labels[label[:-1]] = label_address << 2
#		 label_address = label_address + 1
	elif(re.search(r"org", label_line)):
		base = 10
		if(re.search(r"0x", label_line)):
			base = 16
		# print(re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i]))
		value = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", label_line)[-1][-1]).group(0), base) >> 2
		label_address = value

	# need to remember what the hell this was all about
	elif(re.search(r"(?<!s[rl])li", label_line)):
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
	hex_line = "test\n"
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
		if(blocks[0] != ""):
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
			base = 10
			if(re.search(r"0x", asm_lines[i])):
				base = 16
			# print("int found: " + str(re.findall(r"(0x)?([0-9a-fA-F]+)", asm_lines[i])))
			imm = int(re.search(r"[0-9a-fA-F]+", re.findall(r"(0x)?([0-9a-fA-F]+)", asm_lines[i])[-1][-1]).group(0), base)
			imm_str = str(hex(imm)[2:])
			while(len(imm_str) < 8):
				imm_str = "0" + imm_str
			hex_line = hex_addr + imm_str + "\n"
		elif(re.search(r"jal", asm_lines[i])):
			opcode = 103
			rd = 1 #not constant, but at least something
			if(re.search(r" ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])):
				imm = labels[re.findall(r" ([a-zA-Z]([a-zA-Z_]|<?!x[0-9])+)", asm_lines[i])[-1][0]]
			else:
				base = 10
				if(re.search(r"0x", asm_lines[i])):
					base = 16
				imm = int(re.search(r"[0-9a-fA-F]*", re.findall(r" (0x)?([0-9a-fA-F]*)", asm_lines[i])[-1][-1]).group(0), base)
			# need to take into account bit swizzling lowkey dont wanna do that rn
			command = hex((imm << 12) + (rd << 7) + opcode)[2:]
			while(len(command) < 8):
				command = "0" + command
			hex_line = hex_addr + command + "\n"
		elif(re.search(r"beq", asm_lines[i])):
			#TODO: current point to do
			opcode = 99
			f3 = 0
			# need rs1, rs2, imm
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
			# this part has to be fucking weird - i cant just bit slice
			# fuck i have to do weird int to hex str conversion and concetenation :(
			bin_imm = str(bin(imm))
			print("immediate val: " + str(imm))

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
					p = -2
					while p > -1 * len(bin_imm_flip):
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
			
			print(bin_imm)
			print(str(int(bin_imm, 2)))
			# 34 chars long
			# 1000_0001_1110
			imm_pt1 = int(bin_imm[-5:-1] + bin_imm[-12], 2)
			# print(imm_pt1)
			# 1_0111_1110_0000
			imm_pt2 = int(bin_imm[-13] + bin_imm[-11:-6], 2)
			command = hex((imm_pt2 << 25) + (rs2 << 20) + (rs1 << 15) + (f3 << 12) + (imm_pt1 << 7) + opcode)[2:]
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
