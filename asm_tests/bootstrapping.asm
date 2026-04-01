org 0x0000
li x3, 0x10000
li x4, 0x80000
lw x5, 0(x4)
add x4, x5, x4
lb x5, 0(x4)


syntax_error:
    li x10, 0x8000
    li x11, 0x100000
    li x13, 0
    li x14, 21
syn_err_loop:
    lb x12, 0(x10)
    sb x12, 0(x11)
    addi x10, x10, 1
    addi x11, x11, 1
    addi x13, x13, 1
    bne x13, x14, syn_err_loop
    li x10, 0x80004
    lb x12, 0(x10)
    sb x12, 0(x11)
    halt


org 0x8000
syn_err_data:
    cfw "syntax error at line "

org 0xc000
data:
    cfw "int a = 5;"


org 0x10000
index:
    cfw 0
line_num:
    cfw 0
open_space:
    cfw 0

org 0x20000
output:
    cfw 0