import antlr4

from CLike.CLikeLexer import CLikeLexer
from CLike.CLikeParser import CLikeParser
from CLike.CLikeListener import CLikeListener

import sys
import os
import subprocess

pre_generated_code = """
#include<stdio.h>

#define MAX_STACK 1000000
#define printInt(k) printf("%d\\n", (k))
#define printDouble(x) printf("%f\\n", (x))
#define printString(t) printf("%s\\n", (t))

int readInt() {
    int x;
    scanf("%d", &x);
    return x;
}

double readDouble() {
    double x;
    scanf("%lf", &x);
    return x;
}
union cell {
    int i;
    double d;
    void *l;
};
union cell m[MAX_STACK];
int top = 0;

int main() {
"""

FUNCTION_SIZE = 1000
BUILTINS_ARG = {'printInt': 'i', 'printDouble': 'd', 'printString': 'STR'}
BUILTINS_RET =  {'readInt': 'i', 'readDouble': 'd'}
BUILTINS = dict(BUILTINS_ARG, **BUILTINS_RET)

class CLikeFirstPass(CLikeListener):
    def __init__(self) -> None:
        super().__init__()
        self.statement_counter = 0
        self.function_counter = 0

        self.local_variable = {}
        self.local_variable_map = {}

        self.expression_stack = []
        self.declartion_stack = []

        self.function_map = {}
        self.current_function = "main"

        self.condition_stack = []
        self.condition_counter = 0

    def expressionToStack(self, ctx):
        stack = self.expression_stack if self.expression_stack else self.declartion_stack
        if stack:
            if ctx.numericConstant():
                type_ = "i" if ctx.numericConstant().IntegerConstant() else "d"
                stack.append(
                    {"value": ctx.numericConstant().getText(), "type": type_}
                )
            elif ctx.booleanConstant():
                boolean = "1" if ctx.booleanConstant().getText() == "true" else "0"
                stack.append({"value": boolean, "type": "i"})
            elif ctx.unlhs:
                type_ = stack[-1]["type"]
                stack.append(
                    {"operation": ctx.operation.text, "unary": True, "type": type_}
                )
            elif ctx.rhs and ctx.lhs:
                type_ = stack[-1]["type"]
                stack.append(
                    {"operation": ctx.operation.text, "unary": False, "type": type_}
                )
            elif ctx.functionCall():
                pass

    def rExpressionToStack(self, ctx: CLikeParser.ExpressionContext):
        self.expressionToStack(ctx)

        expression = ctx.expression()
        if expression:
            self.rExpressionToStack(expression[0])
            self.rExpressionToStack(expression[1])

    def expressionCodeGen(self, output=True):
        print(self.expression_stack)
        for item in reversed(self.expression_stack):
            type_ = item["type"]
            type_ = "i" if type_ in ["boolean", "int", "i"] else "d"

            if "value" in item:
                if output:
                    self.output.write(
                        f"m[top + {self.local_variable[self.current_function]}].{type_} = {item['value']};\n"
                    )
                self.local_variable[self.current_function] += 1
            elif "operation" in item:
                if output:
                    if item["unary"]:
                        self.output.write(
                            f"m[top + {self.local_variable[self.current_function]}].{type_} = {item['operation']} m[top + {self.local_variable[self.current_function] - 1}].{type_};\n"
                        )
                    else:
                        self.output.write(
                            f"m[top + {self.local_variable[self.current_function]}].{type_} = m[top + {self.local_variable[self.current_function] - 1}].{type_} {item['operation']} m[top + {self.local_variable[self.current_function] - 2}].{type_};\n"
                        )

                self.local_variable[self.current_function] += 1
            elif "address" in item:
                if output:
                    self.output.write(
                        f"m[{item['top'] * FUNCTION_SIZE} + {item['address']}].{type_} = m[top + {self.local_variable[self.current_function] - 1}].{type_};\n"
                    )
                    self.output.write(f"top = {item['top'] * FUNCTION_SIZE};\n")
            elif "builtin" in item:
                pass
            elif "function" in item:
                if output:
                    self.output.write(
                        f"m[top + {self.local_variable[self.current_function]}].{type_} = m[{item['top'] * FUNCTION_SIZE} + 1].{type_}; \n"
                    )
                self.local_variable[self.current_function] += 1

            elif "type" in item:
                variable = self.local_variable_map[self.current_function][item["name"]][
                    0
                ]
                if output:
                    self.output.write(
                        f"m[top + {variable}].{type_} = m[top + {self.local_variable[self.current_function] - 1}].{type_};\n"
                    )

        self.expression_stack = []

    def declartionCodeGen(self, output=True):
        '''if len(self.expression_stack) == 1:
            type_ = self.expression_stack[-1]["type"]
            self.expression_stack.append({"value": "0", "type": type_})
        '''

        for item in reversed(self.declartion_stack):
            type_ = item["type"]
            type_ = "i" if (type_ in ["boolean", "int", "i"]) else type_
            type_ = "d" if (type_ in ["double"]) else type_

            if "value" in item:
                if output:
                    self.output.write(
                        f"m[top + {self.local_variable[self.current_function]}].{type_} = {item['value']};\n"
                    )
                self.local_variable[self.current_function] += 1
            elif "operation" in item:
                if output:
                    if item["unary"]:
                        self.output.write(
                            f"m[top + {self.local_variable[self.current_function]}].{type_} = {item['operation']} m[top + {self.local_variable[self.current_function] - 1}].{type_};\n"
                        )
                    else:
                        self.output.write(
                            f"m[top + {self.local_variable[self.current_function]}].{type_} = m[top + {self.local_variable[self.current_function] - 1}].{type_} {item['operation']} m[top + {self.local_variable[self.current_function] - 2}].{type_};\n"
                        )

                self.local_variable[self.current_function] += 1
            elif "builtin" in item:
                pass
            elif "function" in item:
                if output:
                    self.output.write(
                        f"m[top + {self.local_variable[self.current_function]}].{type_} = m[{item['top'] * FUNCTION_SIZE} + 1].{type_}; \n"
                    )
                self.local_variable[self.current_function] += 1

            elif "type" in item:
                if output:
                    self.output.write(
                        f"m[top + {self.local_variable[self.current_function]}].{type_} = m[top + {self.local_variable[self.current_function] - 1}].{type_};\n"
                    )
                self.local_variable_map[self.current_function][item["name"]] = (
                    self.local_variable[self.current_function],
                    type_,
                )
                self.local_variable[self.current_function] += 1

                return self.local_variable[self.current_function] - 1

        self.declartion_stack = []

    def enterFunction(self, ctx: CLikeParser.FunctionContext):
        self.function_counter += 1
        self.statement_counter += 1

        self.current_function = ctx.Identifier().getText()

        self.function_map[ctx.Identifier().getText()] = {
            "start": f"statement_{self.function_counter}_{self.statement_counter - 1}",
            "top": self.function_counter,
            "type": ctx.type_().getText()
        }

        self.local_variable[self.current_function] = 0
        self.local_variable_map[self.current_function] = {}

        self.local_variable[self.current_function] += 1  # Return address
        self.local_variable[self.current_function] += 1  # Return value

    def enterArgument(self, ctx: CLikeParser.ArgumentContext):
        identifier = ctx.Identifier().getText()
        type_ = ctx.type_().getText()
        type_ = "i" if ctx.type_().getText() in ["boolean", "int", "i"] else "d"

        self.local_variable_map[self.current_function][identifier] = (
            self.local_variable[self.current_function],
            type_,
        )
        self.local_variable[self.current_function] += 1
    
    def exitFunction(self, ctx: CLikeParser.FunctionContext):
        self.function_map[ctx.Identifier().getText()].update(
            {"end": f"statement_{self.function_counter}_{self.statement_counter - 1}"}
        )
    
    def enterIf(self, ctx: CLikeParser.IfContext):
        pass

    def enterStatement(self, ctx: CLikeParser.StatementContext):
        self.statement_counter += 1

    
    def exitFunctionCall(self, ctx: CLikeParser.FunctionCallContext):
        name = ctx.Identifier().getText()

        if name in BUILTINS:
            return

        self.statement_counter += 1


    def exitIf(self, ctx: CLikeParser.IfContext):
        '''condition = self.condition_stack.pop()
        condition.update({"if_end": self.statement_counter})
        self.condition_stack.insert(0, condition)'''



class CLikeCodeGen(CLikeFirstPass):
    def __init__(self, output, first_pass: CLikeFirstPass) -> None:
        super().__init__()
        self.output = output
        self.first_pass = first_pass

        self.statement_counter = 0
        self.function_counter = 0

        self.local_variable = first_pass.local_variable
        self.local_variable_map = first_pass.local_variable_map

        self.expression_stack = []

        self.function_map = first_pass.function_map

        self.current_function = "main"

        self.condition_stack = first_pass.condition_stack
        self.condition_counter = 0

        self.last_statement = first_pass.statement_counter - 1
        self.last_function = first_pass.function_counter


    def enterProgram(self, ctx: CLikeParser.ProgramContext):
        self.output.write(pre_generated_code.lstrip())

        self.output.write(f"goto {self.function_map['main']['start']};\n")

    def enterFunction(self, ctx: CLikeParser.FunctionContext):
        self.function_counter += 1
        self.output.write(
            f"statement_{self.function_counter}_{self.statement_counter}:\n"
        )
        self.statement_counter += 1

        self.current_function = ctx.Identifier().getText()

        self.output.write(f"top = {self.function_counter * FUNCTION_SIZE};\n")
        '''
        self.function_map[ctx.Identifier().getText()] = {
            "start": f"statement_{self.function_counter}_{self.statement_counter - 1}",
            "top": self.function_counter,
        }
        '''

        self.local_variable[self.current_function] = 0
        self.local_variable_map[self.current_function] = {}

        self.local_variable[self.current_function] += 1  # Return address
        self.local_variable[self.current_function] += 1  # Return value

    def enterArgument(self, ctx: CLikeParser.ArgumentContext):
        identifier = ctx.Identifier().getText()
        type_ = ctx.type_().getText()
        type_ = "i" if ctx.type_().getText() in ["boolean", "int"] else "d"

        self.local_variable_map[self.current_function][identifier] = (
            self.local_variable[self.current_function],
            type_,
        )
        self.local_variable[self.current_function] += 1

    def exitFunction(self, ctx: CLikeParser.FunctionContext):
        '''
        self.function_map[ctx.Identifier().getText()].update(
            {"end": f"statement_{self.function_counter}_{self.statement_counter - 1}"}
        )
        '''

    def exitProgram(self, ctx: CLikeParser.ProgramContext):
        self.output.write(";\n}\n")
        print("*"*100)

        import pprint
        pprint.pprint(vars(self))
    
    def enterStatement(self, ctx: CLikeParser.StatementContext):
        self.output.write(
            f"statement_{self.function_counter}_{self.statement_counter}:\n"
        )
        self.statement_counter += 1

    def exitReturn(self, ctx: CLikeParser.ReturnContext):
        function_ctx = ctx.parentCtx

        while not isinstance(function_ctx, CLikeParser.FunctionContext):
            function_ctx = function_ctx.parentCtx

        type_ = function_ctx.type_().getText()
        name = function_ctx.Identifier().getText()
        top = self.function_map[name]["top"]

        if type_ == "void" and ctx.expression():
            raise Exception("can't return value from void function")
        
        if name == "main":
            self.output.write(f"goto statement_{self.last_function}_{self.last_statement};\n")
            return

        if ctx.expression():
            self.expression_stack.append({"type": type_, "address": 1, "top": top})
            self.rExpressionToStack(ctx.expression())
            self.expressionCodeGen()
            self.expression_stack = []

        self.output.write(f"goto *(m[top + 0].l);\n")

    def enterExpression(self, ctx: CLikeParser.ExpressionContext):
        self.expressionToStack(ctx)

    def exitParameters(self, ctx: CLikeParser.ParametersContext):
        name = ctx.parentCtx.Identifier().getText()

        if name in BUILTINS:
            if name in BUILTINS_ARG:
                expression = tuple(ctx.getChildren())[0]

                type_ = BUILTINS_ARG[name]

                if expression.string and name == "printString":
                    self.output.write(f"printString({expression.StringConstant().getText()});\n")
                
                elif name in ("printInt", "printDouble"):
                    self.expression_stack.append({"type": type_, "builtin": True})

                    self.rExpressionToStack(expression)
                    self.expressionCodeGen()
                    self.expression_stack = []

                    if type_ == 'i':
                        self.output.write(f"printInt(m[top + {self.local_variable[self.current_function] - 1}].{type_});\n")
                    else: 
                        self.output.write(f"printDouble(m[top + {self.local_variable[self.current_function] - 1}].{type_});\n")
            
            return

        argument = tuple(self.local_variable_map[name].items())

        i = 0
        for expression in ctx.getChildren():
            if expression.getText() == ",":
                continue

            address = argument[i][1][0]
            top = self.function_map[name]["top"]
            type_ = "i" if argument[i][1][1] in ["boolean", "int", 'i'] else "d"

            self.expression_stack.append(
                {"type": type_, "address": address, "top": top}
            )
            self.rExpressionToStack(expression)
            self.expressionCodeGen()
            self.expression_stack = []

            i += 1

    def exitFunctionCall(self, ctx: CLikeParser.FunctionCallContext):
        name = ctx.Identifier().getText()

        if name in BUILTINS:
            return

        self.output.write(f"top = {self.function_map[name]['top'] * FUNCTION_SIZE};\n")

        self.output.write(
            f"m[top + 0].l = &&statement_{self.function_counter}_{self.statement_counter};\n"
        )

        self.output.write(f"goto {self.function_map[name]['start']};\n")


        self.output.write(
            f"statement_{self.function_counter}_{self.statement_counter}:\n"
        )
        self.statement_counter += 1
        self.output.write(f"top = {self.function_counter * FUNCTION_SIZE};\n")

        name = ctx.Identifier().getText()
        type_ = self.function_map[name]['type']
        print(type_)

        if name in BUILTINS:
            if name in BUILTINS_RET:
                self.output.write(f"m[top + {self.local_variable[self.current_function] - 1}].{type_} = {name}();\n")
            return

        top = self.function_map[name]['top']
        self.expression_stack.append(
            {"function": name, "top": top, "type": type_}
        )

        '''if ctx.parentCtx:
            if ctx.parentCtx.parentCtx:
                assign: CLikeParser.AssignmentContext = ctx.parentCtx.parentCtx

                assignee = assign.Identifier().getText()                

                function_top = self.function_map[name]['top']
                variable = self.local_variable_map[self.current_function][assignee]
                print(variable)

                self.output.write(
                    f"m[top + {variable[0]}].{variable[1]} = m[{function_top * FUNCTION_SIZE} + 1].{variable[1]};\n"
                )'''


    def enterAssignment(self, ctx: CLikeParser.AssignmentContext):
        identifier = ctx.Identifier().getText()
        type_ = self.local_variable_map[self.current_function][identifier][1]
        type_ = "i" if type_ in ["boolean", "int", "i"] else "d"


        self.expression_stack.append({"type": type_, "name": identifier})

    def exitAssignment(self, ctx: CLikeParser.AssignmentContext):
        self.expressionCodeGen()
        self.expression_stack = []

    def enterDeclartion(self, ctx: CLikeParser.DeclartionContext):
        function_ctx = ctx.parentCtx

        while not isinstance(function_ctx, CLikeParser.FunctionContext):
            function_ctx = function_ctx.parentCtx

        # Global decleration
        if not isinstance(function_ctx, CLikeParser.FunctionContext):
            raise Exception("Global variable not allowed")

        if ctx.type_().getText() == "void":
            raise Exception("Void variable type not allowed")

        identifier = ctx.Identifier().getText()
        type_ = "i" if ctx.type_().getText() in ["boolean", "int"] else "d"

    
        self.declartion_stack.append({"type": type_, "name": identifier, "declartion": True})

    def exitDeclartion(self, ctx: CLikeParser.DeclartionContext):
        self.declartionCodeGen()
        self.declartion_stack = []

    def enterIf(self, ctx: CLikeParser.IfContext):
        #TODO: Impl IF
        pass

if __name__ == "__main__":
    InputName = sys.argv[1]
    OutputName = f'{InputName}.c'
    
    with open(OutputName, 'w') as OutputFile: 
        input = antlr4.FileStream(InputName)
        lexer = CLikeLexer(input)
        stream = antlr4.CommonTokenStream(lexer)
        parser = CLikeParser(stream)
        walker = antlr4.ParseTreeWalker()
        tree = parser.program()

        first_pass = CLikeFirstPass()
        walker.walk(first_pass, tree)

        code_gen = CLikeCodeGen(OutputFile, first_pass)
        walker.walk(code_gen, tree)

    subprocess.run(['gcc', '-Og', '-g', OutputName])
