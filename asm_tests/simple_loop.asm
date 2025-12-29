li x3, 0
li x4, 10
loop:
	beq x3, x4, loop_end
	addi x3, x3, 1
	jal loop
loop_end:
	halt
