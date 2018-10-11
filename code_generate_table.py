from utils import enum

opcode = enum("notop",	"neg",	"incop",	"decop",	"dup",
    "add",	"sub",	"mult",	"divop",	"modop",	"swp",
    "andop",	"orop",	"gt",	"lt",	"ge",	"le",	"eq",	"ne",
    "lod",	"_str",	"ldc",	"lda",
    "ujp",	"tjp",	"fjp",
    "chkh",	"chkl",
    "ldi",	"sti",
    "call",	"ret",	"retv",	"ldp",	"proc",	"endop",
    "nop",	"bgn",	"sym"
)

opcodeName = [
    "notop",    "neg",	"inc",	"dec",	"dup",
    "add",	"sub",	"mult",	"div",	"mod",	"swp",
    "and",	"or",	"gt",	"lt",	"ge",	"le",	"eq",	"ne",
    "lod",	"str",	"ldc",	"lda",
    "ujp",	"tjp",	"fjp",
    "chkh",	"chkl",
    "ldi",	"sti",
    "call",	"ret",	"retv",	"ldp",	"proc",	"end",
    "nop",	"bgn",	"sym"
]

typeEnum = enum(
    "INT_TYPE",	"VOID_TYPE",	"VAR_TYPE",	"CONST_TYPE",	"FUNC_TYPE"
)
