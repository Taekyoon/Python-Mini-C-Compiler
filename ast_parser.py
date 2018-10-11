import argparse

from parser_table import *
from expression import *
from lex import LexScanner
from code_generate import CodeGenerator


class LRParser(object):
    def __init__(self, scanner):
        self.FINISH = True
        self.NONE = "NONE"
        self.GOAL_RULE = GOAL_RULE
        self.EOF = "EOF"
        self.TERMINAL, self.NONTERMINAL = 0, 1
        self.tident, self.tnumber = 4, 5

        self.parsing_table = ParsingTable
        self.left_symbol = LeftSymbol
        self.right_length = RightLength
        self.rule_name = ruleName
        self.node_name = nodeName

        self.scanner = scanner

        self.tokens = []
        self.stack = []
        self.token = None
        self.builded_tree = None

        self.tree_print = ""

        self.error_count = 0

    def next(self):
        current_state = self.stack[-1]["state"]
        entry = self.parsing_table[current_state][self.token["type"]]

        if entry > 0:
            item = {"symbol": self.token["type"], "state": entry}
            item["value"] = self.buildNode(self.token) if self.meaningfulToken(self.token) else None
            self.stack.append(item)
            self.token = self.scan()
        elif entry < 0:
            rule_number = -entry
            if rule_number == self.GOAL_RULE:
                if self.error_count == 0:
                    print("*** valid source ***")
                else:
                    print("*** error in source : ", self.error_count)
                self.builded_tree = self.stack[-2]['value']
                return self.FINISH

            #self.semantic(rule_number)
            tree = self.buildTree(self.rule_name[rule_number], self.right_length[rule_number])

            for _ in range(self.right_length[rule_number]):
                self.stack.pop()

            lhs = self.left_symbol[rule_number]
            current_state = self.parsing_table[self.stack[-1]["state"]][lhs]
            self.stack.append({"symbol": lhs, "state": current_state, "value": tree})
        else:
            print("error")

    def meaningfulToken(self, token):
        if token["type"] == self.tident or token["type"] == self.tnumber:
            return True
        else:
            return False

    def buildNode(self, token):
        node = TreeNode(token, self.TERMINAL)
        return node

    def buildTree(self, node_number, rhs_length):
        stack_pointer = len(self.stack) - 1
        i = stack_pointer - rhs_length + 1
        while i <= stack_pointer and self.stack[i]["value"] is None:
            i += 1
        if (node_number == 0) and (i > stack_pointer):
            return None

        start = i
        while i <= stack_pointer - 1:
            j = i + 1
            while j <= stack_pointer and self.stack[j]["value"] is None:
                j += 1
            if j <= stack_pointer:
                ptr = self.stack[i]["value"]
                while ptr.brother:
                    ptr = ptr.brother
                ptr.brother = self.stack[j]["value"]
            i = j

        first = None if start > stack_pointer else self.stack[start]["value"]

        if node_number > 0:
            token = {"token": None,
                     "type": node_number,
                     "value": None}
            ptr = TreeNode(token, self.NONTERMINAL)
            ptr.son, ptr.brother = first, None

            return ptr
        else:
            return first

    def parse(self):
        self.prepare_scan()
        self.token = self.scan()
        self.stack.append({"symbol": self.NONE, "state": 0, "value": None})
        for out in self:
            if out:
                break

    def prepare_scan(self):
        for token in self.scanner:
            if token:
                self.tokens.append(token)
        self.tokens.append({"token": self.EOF, "type": 29, "value": 0})
        self.tokens.reverse()

    def scan(self):
        if not self.token:
            return self.tokens.pop()
        return self.tokens.pop() if self.token["token"] != self.EOF\
                                 else self.token

    def start_print_tree(self, indent=1):
        self.tree_print = ""
        self.print_tree(self.builded_tree, indent=indent)

    def print_tree(self, pt, indent=1):
        p = pt
        while p:
            self.tree_print += self.print_node(p, indent)
            if p.noderep == self.NONTERMINAL:
                self.print_tree(p.son, indent=indent+5)
            p = p.brother

    def print_node(self, node, indent=1):
        pt = node
        output = " " * indent

        if pt.noderep == self.TERMINAL:
            if pt.token["type"] == self.tident:
                output += " Terminal: " + pt.token["value"]
            elif pt.token["type"] == self.tnumber:
                output += " Terminal: " + pt.token["value"]
        else:
            i = pt.token["type"]
            output += " Nonterminal: " + self.node_name[i]

        output += "\n"
        return output

    def semantic(self, rule_number):
        print("reduced rule number= ", rule_number)

    def get_ast_tree(self):
        return self.builded_tree

    def write_tree_to_file(self, file_name):
        self.start_print_tree()
        file_name = file_name + ".ast"
        with open(file_name, 'w') as f:
            f.write(self.tree_print)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

class TreeNode(object):
    def __init__(self, token, terminal):
        self.token = token
        self.noderep = terminal
        self.son, self.brother = None, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="input file path")
    args = parser.parse_args()

    file = open(args.path)
    lines = file.readlines()
    file.close()
    strings = ""
    for i in lines:
        strings += i

    scanner = LexScanner(strings)
    parser = LRParser(scanner)
    parser.parse()
    parser.start_print_tree()
    tree = parser.get_ast_tree()

    generator = CodeGenerator(tree)
    generator.generate()

    print(generator.ucode_str)

if __name__ == "__main__":
    main()
