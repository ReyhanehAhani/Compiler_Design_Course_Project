grammar CLike;
// Parser rules

program: functions;

functions: function+;

function: type name=Identifier '(' arguments? ')' block;

statements: statement statements |;

statement:
	';'
	| block
	| declartion
	| assignment
	| variable=Identifier '++'
	| variable=Identifier '--'
	| return
	| if
	| while
	| expression;

assignment: variable=Identifier '=' expression;
declartion: type variable=Identifier ('=' expression)?;
while: While '(' condition=expression ')' statement;
if: If '(' condition=expression ')' statement else?;
else: 'else' statement;
return: Return expression?;

block: '{' (statement+)? '}';

arguments: argument (',' argument)*;
argument: type name=Identifier;

type: 'int' | 'double' | 'boolean' | 'void';

parameters: expression (',' expression)*;

functionCall: Identifier '(' parameters? ')';

expression:
	functionCall
	| numericConstant
	| boolean=booleanConstant
	| string=StringConstant
	| variable=Identifier
	| '(' expression ')'
	| operation=('-' | '!') unlhs=expression
	| rhs=expression operation=('*' | '/' | '%') lhs=expression
	| rhs=expression operation=('+' | '-') lhs=expression
	| rhs=expression operation=('<' | '>' | '<=' | '>=') lhs=expression
	| rhs=expression operation=('==' | '!=') lhs=expression
	| rhs=expression operation='&&' lhs=expression
	| rhs=expression operation='||' lhs=expression;

numericConstant: (DoubleConstant | IntegerConstant);
booleanConstant: 'true' | 'false';


// Lexer rules
While: 'while';
If: 'if';
Else: 'else';
Return: 'return';

StringConstant: '"' ~('\r' | '\n' | '"' | '\\')* '"';
IntegerConstant: ([1-9] [0-9]*) | '0';
DoubleConstant:
	IntegerConstant '.' IntegerConstant; // TODO: FIX Doube for scientific notation
Identifier: [a-zA-Z_] ([a-zA-Z_] | [0-9])*;

Whitespace: [ \t]+ -> skip;
Newline: ( '\r' '\n'? | '\n') -> skip;
BlockComment: '/*' (BlockComment | .)*? '*/' -> skip;
LineComment: '//' ~[\r\n]* -> skip;