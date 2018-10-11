from lex import tsymbol_dict
from code_generate_table import opcode, typeEnum
from parser_table import *
from expression import nodeName

def icg_error(errno):
    print("ICG_ERROR: ", errno)

def typeSize(typeSpecifier):
    if typeSpecifier == typeEnum.INT_TYPE:
        return 1
    else:
        print("not yet implemented")
        return 1

NONTERMINAL, TERMINAL = 1, 0
tident, tnumber = 4, 5
node_name = nodeName
tree_print = ""

def print_part_tree(pt):
    print_tree(pt, 1)

def print_tree(pt, indent=1):
    global tree_print
    p = pt
    while p:
        tree_print += print_node(p, indent)
        if p.noderep == NONTERMINAL:
            print_tree(p.son, indent=indent+5)
        p = p.brother

def print_node(node, indent=1):
    pt = node
    output = " " * indent

    if pt.noderep == TERMINAL:
        if pt.token["type"] == tident:
            output += " Terminal: " + pt.token["value"]
        elif pt.token["type"] == tnumber:
            output += " Terminal: " + pt.token["value"]
    else:
        i = pt.token["type"]
        output += " Nonterminal: " + node_name[i]

    print(output)
    return output
