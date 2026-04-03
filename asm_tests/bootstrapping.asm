org 0x0000
token_loop:
    li x3, 0x10000
    lw x6, 0(x3)
    li x4, 0xc000
    li x7, 0x35 #marking all tokens as possible (except float bc im not dealing with that rn)
    li x8, 0x10008
    sw x7, 0(x8)
consume_loop:
    add x4, x6, x4
    lb x5, 0(x4)
    addi x6, x6, 1
    sw x6, 0(x3)
    li x9, 0x20
    beq x5, x9, token_check

int_lit_check:
    li x9, 0x30
    blt x5, x9, invalid_int_lit
    li x9, 0x3a
    bge x5, x9, invalid_int_lit
    lw x7, 4(x8) #multiply value at intermediate_val by 10 and restore it
    slli x7, x7, 1
    slli x9, x7, 2
    add x7, x7, x9
    add x7, x7, x5
    sw x7, 0(x8)
    jal binary_op_check

invalid_int_lit:
    lw x7, 0(x8)
    andi x7, x7, 0xFFE
    sw x7, 0(x8)

binary_op_check:
    li x9, 0x2b #+ in ascii


assignment_check:
    li x9, 0x3d #= in ascii
    beq x9, x7, int_keyword_check
invalid_assignment_check:
    lw x7, 0(x8)
    andi x7, x7, 0xFDF
    sw x7, 0(x8)

int_keyword_check: #need to update a little state machine here
    lw x7, 8(x8)
    li x9, 3 #state 3 means int was found, but if this character is not a space, int keyword is invalid
    beq x7, x9, invalid_int_keyword
    li x9, 2
    beq x7, x9, int_keyword_state2
    li x9, 1
    beq x7, x9, int_keyword_state1
    li x9, 0x69
    jal int_keyword_cmp
int_keyword_state2:
    li x9, 0x74
    jal int_keyword_cmp
int_keyword_state1:
    li x9, 0x6e
int_keyword_cmp:
    bne x5, x9, invalid_int_keyword
    addi x7, x7, 1
    sw x7, 8(x8)
    jal consume_loop

invalid_int_keyword:
    lw x7, 0(x8)
    andi x7, x7, 0xFEF
    sw x7, 0(x8)
    jal consume_loop

token_check:
    lw x7, 0(x8)
    beq x7, x0, syntax_error


    jal token_loop

syntax_error:
    li x10, 0x8000
    li x11, 0x20000
    li x13, 0
    li x14, 21
syn_err_loop:
    lb x12, 0(x10)
    sb x12, 0(x11)
    addi x10, x10, 1
    addi x11, x11, 1
    addi x13, x13, 1
    bne x13, x14, syn_err_loop
    li x10, 0x10004
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
token_types:
    cfw 0
intermediate_val_int:
    cfw 0
int_keyword_fsm:
    cfw 0
open_space:
    cfw 0

org 0x20000
output:
    cfw 0