# Compiler Design Project

This Python script generates C code based on the input provided through the ANTLR grammar. The generated C code implements a simple interpreter for a custom programming language with basic functionalities. Here's an overview of the script's functionalities:

## Code Generation Process

1. The script takes an input ANTLR grammar file as a command-line argument.
2. It generates C code by parsing the input grammar file using ANTLR4.
3. The generated C code implements an interpreter for the custom programming language.
4. The interpreter supports functions, expressions, assignments, declarations, conditionals, and basic I/O operations.

## Pre-generated Code

The generated C code includes pre-generated code that provides the foundation for the interpreter. The pre-generated code includes:

- Standard C library includes and macros.
- Built-in functions for printing integers, doubles, and strings, as well as reading integers and doubles from input.
- A data structure for managing function calls and variable storage.
- Main function and function prototypes.

## First Pass - Semantic Analysis

The first pass of the code generation process performs semantic analysis on the input ANTLR parse tree. It gathers information about functions, local variables, and conditions. The collected information is used in the second pass for code generation.

## Second Pass - Code Generation

The second pass generates the actual C code based on the information collected during the first pass. It translates the ANTLR parse tree into C code that implements the interpreter for the custom programming language. The generated C code supports:

- Function definitions and calls.
- Expressions involving numeric constants, boolean constants, unary and binary operations.
- Variable assignments and declarations.
- Basic control flow structures, such as the 'if' statement.
- Built-in functions for printing and reading values.

## Usage

To use the script, provide the input ANTLR grammar file as a command-line argument. The script will generate C code based on the grammar and write it to an output file. The generated C code can then be compiled using a C compiler (such as GCC) to create an executable interpreter for the custom programming language.

For example, to generate and compile the interpreter from an input grammar file named "MyLanguage.g4":

```shell
python generate_code.py MyLanguage.g4
gcc -Og -g MyLanguage.c -o MyLanguageInterpreter
