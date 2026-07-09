.include "lib_screen_write.asm"

.type main, @function
main:
    la x10, hello_world
    li x11, 0
    li x12, 0
    jal x1, write_string_loc
    ebreak


.data
    .asciz hello_world: "Hello World!"