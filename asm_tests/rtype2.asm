li x2, 0x1000
li x3, 0xbaddecaf
li x4, 0xdeadbeef
add x5, x3, x4
sub x6, x3, x4
and x7, x3, x4
or x8, x3, x4
xor x9, x3, x4
slt x10, x3, x4
sltu x11, x3, x4
li x4, 4
sll x12, x3, x4
srl x13, x3, x4
sra x14, x3, x4
ebreak      #comment out once sw/lw functional

#writeback - can fail
sw x5, 0(x2)
sw x6, 4(x2)
sw x7, 8(x2)
sw x8, 12(x2)
sw x9, 16(x2)
sw x10, 20(x2)
sw x11, 24(x2)
sw x12, 28(x2)
sw x13, 32(x2)
sw x14, 36(x2)
ebreak