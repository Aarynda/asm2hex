#testing branch instructions - using labels for immediate values
li x3, 0
#this value should be 4
beq x0, x3, test
halt

test:
halt
