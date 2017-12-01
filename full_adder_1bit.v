module full_adder_1bit (A, B, Cin, S, Cout);
//-------------Input Ports Declarations-----------------------------
input A, B, Cin;
//-------------Output Ports Declarations-----------------------------
output S, Cout;
//-------------Logic-----------------------------------------------
assign S = A ^ B ^ Cin ;
assign Cout = (A & B) | (Cin & (A ^ B));
endmodule