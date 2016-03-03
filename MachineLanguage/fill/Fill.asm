@8192				//int maxPixel = 8192
D=A
@maxPixel
M=D

(LOOP)				//while(true)
@KBD				//int color = KBD
D=M
@color
M=D
@pixel       		//int pixel = 0
M=0
(INNERLOOP)         //while(pixel < maxPixel)
@pixel    			
D=M
@maxPixel
D=D-M
@END
D;JGE

@SCREEN				//int address = SCREEN + pixel
D=A
@pixel
D=D+M
@address
M=D

@color				//if (color > 0)
D=M
@WHITE
D;JLE
D=0					//address = !0x0000
@address
A=M
M=!D
@ENDIF
0;JMP
(WHITE)
@address			//address = 0x0000
A=M
M=0

(ENDIF)
@pixel   			//pixel += 1
M=M+1
@INNERLOOP
0;JMP

(END)
@LOOP
0;JMP