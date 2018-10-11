from lex import tsymbol_dict
from expression import *
from code_generate_table import *
from code_generate_utils import *


class CodeGenerator(object):
    def __init__(self, tree):
        self.tree = tree
        self.base, self.offset, self.width = 1, 1, 1
        self.TERMINAL, self.NONTERMINAL = 0, 1
        self.lvalue, self.rvalue = None, None
        self.labelNum = 0

        self.opcodeName = opcodeName

        self.symbolTable = list()
        self.symLevel = 0

        self.ucode_str = ""

    def generate(self):
        ptr = self.tree

        self.initSymbolTable()

        p = ptr.son
        while p:
            if p.token["type"] == nodeNumber.DCL:
                self.processDeclaration(p.son)
            elif p.token["type"] == nodeNumber.FUNC_DEF:
                self.processFuncHeader(p.son)
            else:
                icg_error(3)
            p = p.brother

        globalSize = self.offset - 1

        p = ptr.son
        while p:
            if p.token["type"] == nodeNumber.FUNC_DEF:
                self.processFunction(p)
            p = p.brother

        self.emit1(opcode.bgn, globalSize)
        self.emit0(opcode.ldp)
        self.emitJump(opcode.call, "main")
        self.emit0(opcode.endop)

    def initSymbolTable(self):
        self.symbolTable.clear()

    ### DECLARATION
    def insert(self, name, typeSpecifier, typeQualifier, base, offset, width, initialValue):
        item = {"name": name,
                "typeSpecifier": typeSpecifier,
                "typeQualifier": typeQualifier,
                "base": base,
                "offset": offset,
                "width": width,
                "initialValue": initialValue,
                "level": self.symLevel}
        self.symbolTable.append(item)

    def processDeclaration(self, ptr):
        if not ptr.token["type"] == nodeNumber.DCL_SPEC:
            raise AttributeError("icg_error(4)")

        typeSpecifier = typeEnum.INT_TYPE
        typeQualifier = typeEnum.VAR_TYPE

        p = ptr.son
        while p:
            if p.token["type"] == nodeNumber.INT_NODE:
                typeSpecifier = typeEnum.INT_TYPE
            elif p.token["type"] == nodeNumber.CONST_NODE:
                typeQualifier = typeEnum.CONST_TYPE
            else:
                print("processDeclaration: not yet implemented")
            p = p.brother

        p = ptr.brother
        if not p.token["type"] == nodeNumber.DCL_ITEM:
            raise AttributeError("icg_error")

        switch_case = {nodeNumber.SIMPLE_VAR: self.processSimpleVariable,
                       nodeNumber.ARRAY_VAR: self.processArrayVariable}
        while p:
            q = p.son
            token_number = q.token["type"]
            if token_number in switch_case:
                switch_case[token_number](q, typeSpecifier, typeQualifier)
            else:
                print("error in SIMPLE_VAR or ARRAY_VAR")
            p = p.brother

    def processSimpleVariable(self, ptr, typeSpecifier, typeQualifier):
        p = ptr.son
        q = ptr.brother

        sign = 1

        if not ptr.token["type"] == nodeNumber.SIMPLE_VAR:
            print("error in SIMPLE_VAR")

        if typeQualifier == typeEnum.CONST_TYPE:
            if q is None:
                print(ptr.son.token["value"], " must have a constant value")
                return
            if q.token["type"] == nodeNumber.UNARY_MINUS:
                sign = -1
                q = q.son
            initialValue = sign * q.token["value"]
            stIndex = self.insert(p.token["value"], typeSpecifier, typeQualifier,
                            0, 0, 0, initialValue)
        else:
            size = typeSize(typeSpecifier)
            stIndex = self.insert(p.token["value"], typeSpecifier, typeQualifier,
                            self.base, self.offset, self.width, 0)
            self.offset += size

    def processArrayVariable(self, ptr, typeSpecifier, typeQualifier):
        p = ptr.son

        if not ptr.token["type"] == nodeNumber.ARRAY_VAR:
            print("error in ARRAY_VAR")
            return

        if p.brother is None:
            print("array size must be specified")
        else:
            size = int(p.brother.token["value"])

        size *= typeSize(typeSpecifier)

        stIndex = self.insert(p.token["value"], typeSpecifier, typeQualifier,
                        self.base, self.offset, size, 0)
        self.offset += size

    ### EXPRESSION

    def lookup(self, name):
        for i, item in enumerate(self.symbolTable):
            print(item["name"], self.symLevel, item["level"])
            if item["name"] == name and item["level"] == self.symLevel:
                return i
        return -1

    def emit0(self, opcode):
        self.ucode_str += "           {}\n".format(self.opcodeName[opcode])

    def emit1(self, opcode, operand):
        self.ucode_str += "           {} {}\n".format(self.opcodeName[opcode], operand)

    def emit2(self, opcode, operand1, operand2):
        self.ucode_str += "           {} {} {}\n".format(self.opcodeName[opcode], operand1, operand2)

    def emit3(self, opcode, operand1, operand2, operand3):
        self.ucode_str += "           {} {} {} {}\n".format(self.opcodeName[opcode], operand1, operand2, operand3)

    def emitJump(self, opcode, label):
        self.ucode_str += "           {} {}\n".format(self.opcodeName[opcode], label)

    def rv_emit(self, ptr):
        if ptr.token["type"] == tsymbol_dict["tnumber"]:
            self.emit1(opcode.ldc, ptr.token["value"])
        else:
            stIndex = self.lookup(ptr.token["value"])
            if stIndex == -1:
                return
            if self.symbolTable[stIndex]["typeQualifier"] == typeEnum.CONST_TYPE:
                self.emit1(opcode.ldc, self.symbolTable[stIndex]["initialValue"])
            elif self.symbolTable[stIndex]["width"] > 1:
                self.emit2(opcode.lda, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"])
            else:
                self.emit2(opcode.lod, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"])

    def read_emit(self, ptr):
        if ptr.token["type"] == tsymbol_dict["tnumber"]:
            self.emit1(opcode.ldc, ptr.token["value"])
        else:
            stIndex = self.lookup(ptr.token["value"])
            if stIndex == -1:
                return
            if self.symbolTable[stIndex]["typeQualifier"] == typeEnum.CONST_TYPE:
                self.emit1(opcode.ldc, self.symbolTable[stIndex]["initialValue"])
            else:
                self.emit2(opcode.lda, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"])

    def processOperator(self, ptr):
        token_number = ptr.token["type"]

        if token_number == nodeNumber.ASSIGN_OP:
            lhs, rhs = ptr.son, ptr.son.brother
            if lhs.noderep == self.NONTERMINAL:
                self.lvalue = 1
                self.processOperator(lhs)
                self.lvalue = 0

            if rhs.noderep == self.NONTERMINAL:
                self.processOperator(rhs)
            else:
                self.rv_emit(rhs)

            if lhs.noderep == self.TERMINAL:
                stIndex = self.lookup(lhs.token["value"])
                if stIndex == -1:
                    print("undefined variable : ", lhs.token["value"])
                    return
                self.emit2(opcode._str, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"]) ### Need to fill out
            else:
                self.emit0(opcode.sti) ### Need to fill out

        elif token_number == nodeNumber.ADD_ASSIGN or\
             token_number == nodeNumber.SUB_ASSIGN or\
             token_number == nodeNumber.MUL_ASSIGN or\
             token_number == nodeNumber.DIV_ASSIGN or\
             token_number == nodeNumber.MOD_ASSIGN:

            lhs, rhs = ptr.son, ptr.son.brother
            current_nodeNumber = ptr.token["type"]

            ptr.token["type"] = nodeNumber.ASSIGN_OP

            if lhs.noderep == self.NONTERMINAL:
                self.lvalue = 1
                self.processOperator(lhs)
                self.lvalue = 0

            ptr.token["type"] = current_nodeNumber
            if lhs.noderep == self.NONTERMINAL:
                self.processOperator(lhs)
            else:
                self.rv_emit(lhs)

            if rhs.noderep == self.NONTERMINAL:
                self.processOperator(rhs)
            else:
                self.rv_emit(rhs)

            # step 4
            if token_number == nodeNumber.ADD_ASSIGN: self.emit0(opcode.add)
            elif token_number == nodeNumber.SUB_ASSIGN: self.emit0(opcode.sub)
            elif token_number == nodeNumber.MUL_ASSIGN: self.emit0(opcode.mult)
            elif token_number == nodeNumber.DIV_ASSIGN: self.emit0(opcode.divop)
            elif token_number == nodeNumber.MOD_ASSIGN: self.emit0(opcode.modop)

            # step 5
            if lhs.noderep == self.TERMINAL:
                stIndex = self.lookup(lhs.token["value"])
                if stIndex == -1:
                    print("undefined variable : ", lhs.son.token["value"])
                    return
                self.emit2(opcode._str, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"])
            else:
                self.emit0(opcode.sti)

        elif token_number == nodeNumber.ADD or token_number == nodeNumber.SUB or\
             token_number == nodeNumber.MUL or token_number == nodeNumber.DIV or\
             token_number == nodeNumber.MOD or token_number == nodeNumber.EQ or\
             token_number == nodeNumber.NE or token_number == nodeNumber.GT or\
             token_number == nodeNumber.GE or token_number == nodeNumber.LT or\
             token_number == nodeNumber.LE or\
             token_number == nodeNumber.LOGICAL_AND or\
             token_number == nodeNumber.LOGICAL_OR:

            lhs, rhs = ptr.son, ptr.son.brother

            if lhs.noderep == self.NONTERMINAL:
                self.processOperator(lhs)
            else:
                self.rv_emit(lhs)

            if rhs.noderep == self.NONTERMINAL:
                self.processOperator(rhs)
            else:
                self.rv_emit(rhs)

            # step 3
            if token_number == nodeNumber.ADD: self.emit0(opcode.add)
            elif token_number == nodeNumber.SUB: self.emit0(opcode.sub)
            elif token_number == nodeNumber.MUL: self.emit0(opcode.mult)
            elif token_number == nodeNumber.DIV: self.emit0(opcode.divop)
            elif token_number == nodeNumber.MOD: self.emit0(opcode.modop)
            elif token_number == nodeNumber.EQ: self.emit0(opcode.eq)
            elif token_number == nodeNumber.NE: self.emit0(opcode.ne)
            elif token_number == nodeNumber.GT: self.emit0(opcode.gt)
            elif token_number == nodeNumber.LT: self.emit0(opcode.lt)
            elif token_number == nodeNumber.GE: self.emit0(opcode.ge)
            elif token_number == nodeNumber.LE: self.emit0(opcode.le)
            elif token_number == nodeNumber.LOGICAL_AND: self.emit0(opcode.andop)
            elif token_number == nodeNumber.LOGICAL_OR: self.emit0(opcode.orop)

        elif token_number == nodeNumber.UNARY_MINUS or\
            token_number == nodeNumber.LOGICAL_NOT:
            p = ptr.son

            if p.noderep == self.NONTERMINAL:
                self.processOperator(p)
            else:
                self.rv_emit(p)

            if token_number == nodeNumber.UNARY_MINUS: self.emit0(opcode.neg)
            elif token_number == nodeNumber.LOGICAL_NOT: self.emit0(opcode.notop)

             ## switch something
        elif token_number == nodeNumber.PRE_INC or token_number == nodeNumber.PRE_DEC or\
             token_number == nodeNumber.POST_INC or token_number == nodeNumber.POST_DEC:
            p = ptr.son

            if p.noderep == self.NONTERMINAL:
                self.processOperator(p)
            else:
                self.rv_emit(p)

            q = p

            while not q.noderep == self.TERMINAL:
                q = q.son

            if q is None or not q.token["type"] == tsymbol_dict["tident"]:
                print("increment/decrement operators can not be applied in expression")
                return

            stIndex = self.lookup(q.token["value"])
            if stIndex == -1:
                return

            if token_number == nodeNumber.PRE_INC or token_number == nodeNumber.POST_INC:
                self.emit0(opcode.incop)
            elif token_number == nodeNumber.PRE_DEC or token_number == nodeNumber.POST_DEC:
                self.emit0(opcode.decop)

            if p.noderep == self.TERMINAL:
                stIndex = self.lookup(p.token["value"])
                if stIndex == -1:
                    return
                self.emit2(opcode._str, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"]) # Need to do
            elif p.token["type"] == nodeNumber.INDEX:
                self.lvalue = 1
                self.processOperator(p)
                self.lvalue = 0
                self.emit0(opcode.swp)
                self.emit0(opcode.sti)
            else:
                print("error in increment/decrement operators")

        elif token_number == nodeNumber.INDEX:
            indexExp = ptr.son.brother

            if indexExp.noderep == self.NONTERMINAL:
                self.processOperator(indexExp)
            else:
                self.rv_emit(indexExp)
            stIndex = self.lookup(ptr.son.token["value"])

            if stIndex == -1:
                print("undefined variable: ", ptr.son.token["value"])
                return
            self.emit2(opcode.lda, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"])
            self.emit0(opcode.add)
            if self.lvalue == 0:
                self.emit0(opcode.ldi)

        elif token_number == nodeNumber.CALL:
            p = ptr.son

            if self.checkPredefined(p):
                return

            functionName = p.token["value"]
            print(functionName)
            stIndex = self.lookup(functionName)
            print(stIndex)
            if stIndex == -1:
                return
            noArguments = self.symbolTable[stIndex]["width"]

            self.emit0(opcode.ldp)
            p = p.brother
            while p:
                if p.noderep == self.NONTERMINAL:
                    self.processOperator(p)
                else:
                    self.rv_emit(p)
                noArguments -= 1
                p = p.brother

            if noArguments > 0:
                print(functionName, " : too few actual arguments")
            if noArguments < 0:
                print(functionName, " : too many actual arguments")

            self.emitJump(opcode.call, ptr.son.token["value"])
        else:
            print("processOperator: not yet implemented")

    def checkPredefined(self, ptr):
        p = None
        if ptr.token["value"] == "read":
            self.emit0(opcode.ldp)
            p = ptr.brother
            while p:
                if p.noderep == self.NONTERMINAL:
                    self.processOperator(p)
                else:
                    self.read_emit(p)
                p = p.brother
            self.emitJump(opcode.call, "read")
            return True
        elif ptr.token["value"] == "write":
            self.emit0(opcode.ldp)
            p = ptr.brother
            while p:
                if p.noderep == self.NONTERMINAL:
                    self.processOperator(p)
                else:
                    self.rv_emit(p)
                p = p.brother
            self.emitJump(opcode.call, "write")
            return True
        elif ptr.token["value"] == "lf":
            self.emitJump(opcode.call, "lf")
            return True

        return False

    ### STATEMENT
    def genLabel(self):
        ret_str = "$${}".format(self.labelNum)
        self.labelNum += 1
        return ret_str

    def emitLabel(self, label):
        self.ucode_str += "{:11}{}\n".format(label, "nop")

    def processCondition(self, ptr):
        if ptr.noderep == self.NONTERMINAL:
            self.processOperator(ptr)
        else:
            self.rv_emit(ptr)

    def processStatement(self, ptr):
        token_number = ptr.token["type"]
        if token_number == nodeNumber.COMPOUND_ST:
            p = ptr.son.brother
            p = p.son
            while p:
                self.processStatement(p)
                p = p.brother
        elif token_number == nodeNumber.EXP_ST:
            if ptr.son is not None:
                self.processOperator(ptr.son)
        elif token_number == nodeNumber.RETURN_ST:
            if ptr.son is not None:
                returnWithValue = 1
                p = ptr.son
                if p.noderep == self.NONTERMINAL:
                    self.processOperator(p)
                else:
                    self.rv_emit(p)
                self.emit0(opcode.retv)
            else:
                self.emit0(opcode.ret)
        elif token_number == nodeNumber.IF_ST:
            label = self.genLabel()
            self.processCondition(ptr.son)
            self.emitJump(opcode.fjp, label)
            self.processStatement(ptr.son.brother)
            self.emitLabel(label)
        elif token_number == nodeNumber.IF_ELSE_ST:
            label1, label2 = self.genLabel(), self.genLabel()
            self.processCondition(ptr.son)
            self.emitJump(opcode.fjp, label1)
            self.processStatement(ptr.son.brother)
            self.emitJump(opcode.ujp, label2)
            self.emitLabel(label1)
            self.processStatement(ptr.son.brother.brother)
            self.emitLabel(label2)
        elif token_number == nodeNumber.WHILE_ST:
            label1, label2 = self.genLabel(), self.genLabel()
            self.emitLabel(label1)
            self.processCondition(ptr.son)
            self.emitJump(opcode.fjp, label2)
            self.processStatement(ptr.son.brother)
            self.emitJump(opcode.ujp, label1)
            self.emitLabel(label2)
        else:
            print("processStatement: not yet implemented.")
            print_part_tree(ptr)
            raise AttributeError("Bang!")

    ### FUNCTION
    def processSimpleParamVariable(self, ptr, typeSpecifier, typeQualifier):
        p = ptr.son
        if not ptr.token["type"] == nodeNumber.SIMPLE_VAR:
            print("error in SIMPLE_VAR")

        size = typeSize(typeSpecifier)
        stindex = self.insert(p.token["value"], typeSpecifier, typeQualifier,
                         self.base, self.offset, 0, 0)
        self.offset += size

    def processArrayParamVariable(self, ptr, typeSpecifier, typeQualifier):
        p = ptr.son

        if not ptr.token["type"] == nodeNumber.ARRAY_VAR:
            print("error in ARRAY_VAR")
            return

        size = typeSize(typeSpecifier)
        stIndex = self.insert(p.token["value"], typeSpecifier, typeQualifier,
                              base, offset, width, 0)
        offset += size

    def processParamDeclaration(self, ptr):
        if not ptr.token["type"] == nodeNumber.DCL_SPEC:
            icg_error(4)

        typeSpecifier = typeEnum.INT_TYPE
        typeQualifier = typeEnum.VAR_TYPE
        p = ptr.son
        while p:
            if p.token["type"] == nodeNumber.INT_NODE:
                typeSpecifier = typeEnum.INT_TYPE
            elif p.token["type"] == nodeNumber.CONST_NODE:
                typeQualifier = typeEnum.CONST_TYPE
            else:
                print("processParamDeclaration: not yet implemented")
            p = p.brother

        p = ptr.brother
        token_number = p.token["type"]
        if token_number == nodeNumber.SIMPLE_VAR:
            self.processSimpleParamVariable(p, typeSpecifier, typeQualifier)
        elif token_number == nodeNumber.ARRAY_VAR:
            self.processArrayParamVariable(p, typeSpecifier, typeQualifier)
        else:
            print(token_number, nodeNumber.SIMPLE_VAR, nodeNumber.ARRAY_VAR)
            print("error in SIMPLE_VAR or ARRAY_VAR")

    def emitFunc(self, FuncName, operand1, operand2, operand3):
        self.ucode_str += "{:11}{} {} {} {}\n".format(FuncName, "fun", operand1, operand2, operand3)

    def processFuncHeader(self, ptr):
        if not ptr.token["type"] == nodeNumber.FUNC_HEAD:
            print("error in processFuncHeader")

        p = ptr.son.son
        while p:
            if p.token["type"] == nodeNumber.INT_NODE:
                returnType = typeEnum.INT_TYPE
            elif p.token["type"] == nodeNumber.VOID_NODE:
                returnType = typeEnum.VOID_TYPE
            else:
                print("invalid function return type")
            p = p.brother

        p = ptr.son.brother.brother
        p = p.son

        noArguments = 0
        while p:
            noArguments += 1
            p = p.brother

        stIndex = self.insert(ptr.son.brother.token["value"], returnType,
                         typeEnum.FUNC_TYPE, 1, 0, noArguments, 0)

    def processFunction(self, ptr):
        sizeOfVar, numOfVar = 0, 0

        self.base += 1
        self.offset = 1

        if not ptr.token["type"] == nodeNumber.FUNC_DEF:
            icg_error(4)

        p = ptr.son.son.brother.brother
        p = p.son
        while p:
            if p.token["type"] == nodeNumber.PARAM_DCL:
                self.processParamDeclaration(p.son)
                sizeOfVar += 1
                numOfVar += 1
            p = p.brother

        p = ptr.son.brother.son.son
        while p:
            if p.token["type"] == nodeNumber.DCL:
                self.processDeclaration(p.son)
                q = p.son.brother
                while q:
                    if q.token["type"] == nodeNumber.DCL_ITEM:
                        if q.son.token["type"] == nodeNumber.ARRAY_VAR:
                            sizeOfVar += int(q.son.son.brother.token["value"])
                        else:
                            sizeOfVar += 1

                        numOfVar += 1
                    q = q.brother
            p = p.brother

        p = ptr.son.son.brother
        self.emitFunc(p.token["value"], sizeOfVar, self.base, 2)
        for stIndex in range(len(self.symbolTable)-numOfVar, len(self.symbolTable)):
            self.emit3(opcode.sym, self.symbolTable[stIndex]["base"], self.symbolTable[stIndex]["offset"],
                  self.symbolTable[stIndex]["width"])

        p = ptr.son.brother
        self.processStatement(p)

        p = ptr.son.son
        if p.token["type"] == nodeNumber.DCL_SPEC:
            p = p.son
            if p.token["type"] == nodeNumber.VOID_NODE:
                self.emit0(opcode.ret)
            elif p.token["type"] == nodeNumber.CONST_NODE:
                if p.brother.token["type"] == nodeNumber.VOID_NODE:
                    self.emit0(opcode.ret)

        self.emit0(opcode.endop)
        self.base -= 1
        #self.symLevel += 1

    def write_code_to_file(self, file_name):
        file_name = file_name + ".uco"
        with open(file_name, 'w') as f:
            f.write(self.ucode_str)
