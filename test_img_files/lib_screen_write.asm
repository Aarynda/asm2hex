#x10 - address of string to write
#x11 - x cursor position to write to
#x12 - y cursor position to write to
#ret value - 0 on success, -1 on failure
.type write_string_loc, @function
write_string_loc:
    la x6, screen_x_cursor
    la x7, screen_y_cursor
    la x8, screen_data_write
    sw x11, 0(x6)
    sw x12, 0(x7)
    write_loop:
        lbu x5, 0(x10)
        beq x5, x0, write_loop_break
        sb x5, 0(x8)
        addi x10, x10, 1
        jal x0, write_loop
    write_loop_break:
        li x10, 0
        jalr x0, 0(x1)