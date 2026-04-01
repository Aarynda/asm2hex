  lw    x5, 0(x2)
 m_1:
  bne   x13, x0, m_3
 m_2:
  bne   x15, x0, m_3
   j     m_end
m_3:
  beq   x15, x0, m_4
   beq   x13, x0, m_5
   lw    x6, 0(x12) #why is it inserting a line here?
   lw    x7, 0(x14)
   slt   x4, x6, x7
   beq   x4, x0, m_3a
   sw    x6, 0(x5)
   addi x5, x5, 4
   addi x12, x12, 4
   addi x13, x13, -1
   j     m_1
m_3a:
  sw    x7, 0(x5)
   addi x5, x5, 4
   addi x14, x14, 4
   addi x15, x15, -1
   j     m_1
m_4:  #left copy
  lw    x6, 0(x12)
   sw    x6, 0(x5)
   addi x5, x5, 4
   addi x13, x13, -1
   addi x12, x12, 4
   beq   x13, x0, m_end
   j     m_4
m_5:  # right copy
  lw    x7, 0(x14)
   sw    x7, 0(x5)
   addi x5, x5, 4
   addi x15, x15, -1
   addi x14, x14, 4
   beq   x15, x0, m_end
   j     m_5
m_end:
  jr    x1