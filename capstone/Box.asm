// Box.asm for K = 99 (Roll No: 2501730499)
// Start row = 99 -> base address = 16384 + 32*99 = 19552
// Height = 20 rows (rows 99..118)
// Width = 16 * ((99 mod 4) + 1) = 64 pixels = 4 words per row (offsets 0..3)
// Draws black (-1) while any key is pressed (KBD != 0), clears (0) when released.

(MAIN_LOOP)
    // Check keyboard at RAM[24576]
    @KBD
    D=M
    @SET_CLEAR
    D;JEQ         // If KBD == 0 (no key pressed), color = 0

    // Key is pressed: color = -1 (all 16 bits black)
    @color
    M=-1
    @DRAW_INIT
    0;JMP

(SET_CLEAR)
    // No key pressed: color = 0 (clear pixels)
    @color
    M=0

(DRAW_INIT)
    // rowAddr = 19552 (SCREEN + 32 * 99)
    @19552
    D=A
    @rowAddr
    M=D

    // rowsRemaining = 20
    @20
    D=A
    @rowsRemaining
    M=D

(ROW_LOOP)
    // If rowsRemaining == 0, finish pass and return to MAIN_LOOP
    @rowsRemaining
    D=M
    @MAIN_LOOP
    D;JEQ

    // wordAddr = rowAddr, colsRemaining = 4
    @rowAddr
    D=M
    @wordAddr
    M=D

    @4
    D=A
    @colsRemaining
    M=D

(COL_LOOP)
    // If colsRemaining == 0, advance to next row
    @colsRemaining
    D=M
    @NEXT_ROW
    D;JEQ

    // Load color into D and write to RAM[wordAddr]
    @color
    D=M
    @wordAddr
    A=M
    M=D

    // wordAddr++
    @wordAddr
    M=M+1

    // colsRemaining--
    @colsRemaining
    M=M-1

    @COL_LOOP
    0;JMP

(NEXT_ROW)
    // rowAddr += 32 (one screen row)
    @32
    D=A
    @rowAddr
    M=D+M

    // rowsRemaining--
    @rowsRemaining
    M=M-1

    @ROW_LOOP
    0;JMP
