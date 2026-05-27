// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.

// n = 0
@n
M=0
// a = 0
@a
M=0
(LOOP)
// if (n == R1) goto RESULT
@n
D=M
@R1
D=D-M
@RESULT
D;JEQ
// a = a + R0
@a
D=M
@R0
D=D+M
@a
M=D
// n = n + 1
@n
M=M+1
// goto LOOP
@LOOP
0;JMP
(RESULT)
@a
D=M
@R2
M=D
(END)
@END
0;JMP