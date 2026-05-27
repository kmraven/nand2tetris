// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/BLACK.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.

// screen_size = 8192
@8192
D=A
@screen_size
M=D
// status = 0
@status
M=0
// if (KBD == 0) goto INIT_DONE
@KBD
D=M
@INIT_DONE
D;JEQ
// status = -1
@status
M=-1
(INIT_DONE)

(LOOP)
    // if (KBD != 0) goto BLACK
    @KBD
    D=M
    @BLACK
    D;JNE
    // else goto WHITE
    @WHITE
    0;JMP

    (BLACK)
        // if (status != 0) goto CHECKED
        @status
        D=M
        @CHECKED
        D;JNE
        // status = -1
        @status
        M=-1
        // FILL(status)
        @n
        M=0
        @FILL
        0;JMP
    (WHITE)
        // if (status == 0) goto CHECKED
        @status
        D=M
        @CHECKED
        D;JEQ
        // status = 0
        @status
        M=0
        // FILL(status)
        @n
        M=0
        @FILL
        0;JMP
    (FILL)
        // if (n == screen_size) goto CHECKED
        @n
        D=M
        @screen_size
        D=D-M
        @CHECKED
        D;JEQ
        // RAM[SCREEN+n] = -1
        @SCREEN
        D=A
        @n
        D=D+M
        @now_addr
        M=D
        @status
        D=M
        @now_addr
        A=M
        M=D
        // n = n + 1
        @n
        M=M+1
        // goto FILL
        @FILL
        0;JMP
    (CHECKED)
        @LOOP
        0;JMP