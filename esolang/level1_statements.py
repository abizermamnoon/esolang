'''

The following tests show example strings in the language.
There are no meaningful commands at this point,
only a block structure.

>>> tree = parser.parse("")
>>> tree = parser.parse(";")
>>> tree = parser.parse(";;;;")
>>> tree = parser.parse("{{}}")
>>> tree = parser.parse(";{};{;;}")
>>> tree = parser.parse(";{{}{{}}};{;{}{;};}")

The following tests check that unbalanced blocks correctly raise exceptions.

>>> tree = parser.parse("{") # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
lark.exceptions.UnexpectedEOF:

>>> tree = parser.parse("{{}{}{{{}}") # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
lark.exceptions.UnexpectedEOF:

>>> tree = parser.parse("{;;;}}") # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
lark.exceptions.UnexpectedCharacters:
    
The following checks test that comments work.

>>> tree = parser.parse(";{};#")
>>> tree = parser.parse(";{};#{")
>>> tree = parser.parse(";{#}") # doctest: +IGNORE_EXCEPTION_DETAIL
Traceback (most recent call last):
    ...
lark.exceptions.UnexpectedEOF:

'''
import lark
import esolang.level0_arithmetic

# Define the extended grammar
grammar = esolang.level0_arithmetic.grammar + r"""
    %extend start: start (";" start)*
        | assign_var
        | block
        | /#.*/                -> comment
        | if_statement
    if_statement: "if" condition ":" block "else" false_output

    condition: "(" start ")"

    false_output: start

    block: "{" start* "}"

    assign_var: NAME "=" start

    NAME: /[_a-zA-Z][_a-zA-Z0-9]*/

    %extend atom: NAME -> access_var
"""

parser = lark.Lark(grammar)

class Interpreter(esolang.level0_arithmetic.Interpreter):
    '''
    This interpreter supports variable assignment, conditionals, and blocks.
   
    >>> interpreter = Interpreter()
    >>> interpreter.visit(parser.parse("a = 2"))
    2
    >>> interpreter.visit(parser.parse("a + 2"))
    4
    >>> interpreter.visit(parser.parse("a = a + 3"))
    5
    >>> interpreter.visit(parser.parse("b = 3"))
    3
    >>> interpreter.visit(parser.parse("a * b"))
    15
    >>> interpreter.visit(parser.parse("a = 3; {a+5}"))
    8
    >>> interpreter.visit(parser.parse("a = 3; {a=5; a+5}"))
    10
    >>> interpreter.visit(parser.parse("a = 3; {a=5}; a+5"))
    10
    >>> interpreter.visit(parser.parse("a = 3; {c=5}; c+5")) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: Variable c undefined
    >>> interpreter.visit(parser.parse("if (1): { 2 } else 3"))
    2
    >>> interpreter.visit(parser.parse("if (1): { 10 } else 5"))
    10
    >>> interpreter.visit(parser.parse("a = 10; if (a): { 10 } else 0"))
    10
    >>> interpreter.visit(parser.parse("a = 1; if (a): { 10 } else 100"))
    10
    
    '''

    def __init__(self):
        self.stack = [{}]

    def _get_from_stack(self, name):
        """Retrieve a variable value from the current scope stack."""
        for d in reversed(self.stack):
            if name in d:
                return d[name]
        raise ValueError(f"Variable '{name}' is undefined")

    def _assign_to_stack(self, name, value):
        """Assign a value to a variable in the current scope stack."""
        for d in reversed(self.stack):
            if name in d:
                d[name] = value
                return value
        self.stack[-1][name] = value
        return value

    def assign_var(self, tree):
        """Handle variable assignment."""
        name = tree.children[0].value
        value = self.visit(tree.children[1])
        self._assign_to_stack(name, value)
        return value

    def access_var(self, tree):
        """Handle variable access."""
        name = tree.children[0].value
        return self._get_from_stack(name)

    def block(self, tree):
        """Handle block statements with a new scope."""
        self.stack.append({})
        result = None
        for child in tree.children:
            result = self.visit(child)
        self.stack.pop()
        return result

    def if_statement(self, tree):
        """Handle if-else statements."""
        condition_result = self.visit(tree.children[0])
        true_block = tree.children[1]
        false_output = tree.children[2]
        if condition_result != 0:
            return self.visit(true_block)
        else:
            return self.visit(false_output)

    def condition(self, tree):
        """Evaluate a condition to either True or False (non-zero or zero)."""
        return self.visit(tree.children[0])
