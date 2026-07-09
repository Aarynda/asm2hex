org 0x0000
li x2, 0x1000
li x3, 0x2000
flw f1, 0(x2)
flw f2, 4(x2)
fadd.d f3, f1, f2
fsw f3, 0(x3)
fsub.d f4, f1, f2
fsw f4, 4(x3)
fmul.d f5, f1, f2
fsw f5, 8(x3)
fdiv.d f6, f1, f2
fsw f6, 12(x3)


org 0x1000
data:
cfw 35.2
cfw -17.5