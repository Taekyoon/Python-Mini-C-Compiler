import argparse
import re

r_space = r"^[\s|\t|\n]+"
r_comment = r"^(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|^(//.*)"
r_tident = r"^[A-Z|a-z|_]+[A-Z|a-z|0-9|_]*"
r_tnumber = r"^[0-9]+"

r_tnot = r'^!'; r_tnotequ = r"^!="; r_tmod = r"^%"; r_tmodAssign = r"^%="
r_tand = r"^&"; r_tlparen = r"^\("; r_trparen = r"^\)"; r_tmul = r"^\*"
r_tmulAssign = r"^\*="; r_tplus = r"^\+"; r_tinc = r"^\+\+"; r_taddAssign = r"^\+="
r_tcomma = r"^,"; r_tminus = r"^-"; r_tdec = r"^--"; r_tsubAssign = r"^-="
r_tdiv = r"^/"; r_tdivAssign = r"^/="; r_tsemicolon = r"^;"; r_tless = r"^<"
r_tlesse = r"^<="; r_tassign = r"^="; r_tequal = r"^=="; r_tgreat = r"^>"
r_tgreate = r"^>="; r_tlbracket = r"^\["; r_trbracket = r"^\]"; r_teof = None
r_tlbrace = r"^{"; r_tor = r"^\|";  r_trbrace = r"^}"

reserved_words = {"const": "tconst", "else": "telse", "if": "tif",
                  "int": "tint", "return": "treturn", "void": "tvoid",
                  "while": "twhile"}

tsymbol_mark = ["tnull", "tnot", "tnotequ", "tmod", "tmodAssign", "tident", "tnumber",   # 0~5
    "tand", "tlparen", "trparen", "tmul", "tmulAssign", "tplus",    # 6~11
    "tinc", "taddAssign", "tcomma", "tminus", "tdec", "tsubAssign", # 12~17
    "tdiv", "tdivAssign", "tsemicolon", "tless", "tlesse", "tassign",   # 18~23
    "tequal", "tgreat", "tgreate", "tlbracket", "trbracket", "teof",    # 24~29
    "tconst", "telse", "tif", "tint", "treturn", "tvoid", # 30~35
    "twhile", "tlbrace", "tor", "trbrace"] # 36~39

tsymbol_regex = {"tspace": r_space, "tident": r_tident, "tnumber": r_tnumber,
                "tcomment": r_comment, "tnotequ": r_tnotequ, "tnot": r_tnot,
                "tmodAssign": r_tmodAssign, "tmod": r_tmod,
                "tmulAssign": r_tmulAssign, "tmul": r_tmul,
                "tdivAssign": r_tdivAssign, "tdiv": r_tdiv,
                "tdec": r_tdec, "tsubAssign": r_tsubAssign, "tminus": r_tminus,
                "tinc": r_tinc, "taddAssign": r_taddAssign, "tplus": r_tplus,
                "tequal": r_tequal,"tassign": r_tassign,
                "tand": r_tand, "tlparen": r_tlparen, "trparen": r_trparen,
                "tcomma": r_tcomma, "tsemicolon": r_tsemicolon,
                "tlesse": r_tlesse, "tless": r_tless,
                "tgreate": r_tgreate, "tgreat": r_tgreat,
                "tlbracket": r_tlbracket, "trbracket":r_trbracket,
                "tlbrace": r_tlbrace, "tor": r_tor, "trbrace": r_trbrace}

symbol_idx = -1
tsymbol_dict = {}
for mark in tsymbol_mark:
    tsymbol_dict[mark] = symbol_idx
    symbol_idx += 1

class LexScanner(object):
    def __init__(self, strings):
        self.idx = 0
        self.strings = strings
        self.resuerved_words = reserved_words
        self.tsymbol_dict = tsymbol_dict
        self.tsymbol_regex = tsymbol_regex

    def next(self):
        if self.idx == len(self.strings):
            raise StopIteration()

        for patt in self.tsymbol_regex:
            result = re.search(self.tsymbol_regex[patt], self.strings[self.idx:])
            if result:
                if patt == "tcomment" or patt == "tspace":
                    self.move(result.end())
                    return None

                token = result.group(0)
                value = 0
                if patt == "tident":
                    if token in self.resuerved_words:
                        patt = self.resuerved_words[token]
                    else:
                        value = token
                elif patt == "tnumber":
                    value = token

                self.move(result.end())
                return {"token": token,
                        "type": self.tsymbol_dict[patt],
                        "value": value}

        print(self.idx, self.strings[self.idx:])
        raise AssertionError()

    def move(self, steps):
        self.idx += steps

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
    for out in scanner:
        if out:
            print("Token -> {0}\t: ({1}, {2})".format(out["token"], out["type"], out["value"]))

if __name__ == "__main__":
    main()
