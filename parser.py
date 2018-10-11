import argparse

from parser_table import *
from lex import LexScanner


class LRParser(object):
    def __init__(self, scanner):
        self.FINISH = True
        self.NONE = "NONE"
        self.GOAL_RULE = GOAL_RULE
        self.EOF = "EOF"

        self.parsing_table = ParsingTable
        self.left_symbol = LeftSymbol
        self.right_length = RightLength
        self.scanner = scanner

        self.tokens = []
        self.stack = []
        self.token = None

        self.error_count = 0

    def next(self):
        current_state = self.stack[-1]["state"]
        entry = self.parsing_table[current_state][self.token["type"]]

        if entry > 0:
            self.stack.append({"symbol": self.token["type"], "state": entry})
            self.token = self.scan()
        elif entry < 0:
            rule_number = -entry
            if rule_number == self.GOAL_RULE:
                if self.error_count == 0:
                    print("*** valid source ***")
                else:
                    print("*** error in source : ", self.error_count)
                return self.FINISH

            self.semantic(rule_number)

            for _ in range(self.right_length[rule_number]):
                self.stack.pop()

            lhs = self.left_symbol[rule_number]
            current_state = self.parsing_table[self.stack[-1]["state"]][lhs]
            self.stack.append({"symbol": lhs, "state": current_state})
        else:
            pass

    def parse(self):
        print("Start Parse")
        self.prepare_scan()
        self.token = self.scan()
        self.stack.append({"symbol": self.NONE, "state": 0})
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

    def semantic(self, rule_number):
        print("reduced rule number= ", rule_number)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


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

if __name__ == "__main__":
    main()
