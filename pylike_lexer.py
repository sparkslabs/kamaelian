#!/usr/bin/python

import os
import sys
import ply.lex as lex
import atexit

files = []
def cleanup_files():
    for filename in files:
        try:
            os.unlink(filename)
        except:
            print "unlink fail",failname

atexit.register(cleanup_files)

states = (
  ('CODE', 'exclusive'),
  ('BLOCKS', 'exclusive'),
  ('EMITDEDENTS', 'exclusive'),
)

tokens = [
  "NUMBER", "EOL", "PRINT", "STRING", "FOREVER", "COLON",
  "INDENT", "DEDENT", "WS"
]

# t_CODE_INITIAL_EOL = r'\n'
t_CODE_INITIAL_PRINT = r'print'
t_CODE_INITIAL_FOREVER = r'while\sTrue'
t_CODE_INITIAL_COLON = r':'

def t_ANY_EOL(t):
    r'\n+'
    # A new line should always switch the parser to the BLOCKS state. This
    # Allows processing of newlines and leading whitespace to inject
    # indent/dedent tokens

    # Also, reset current indentation level - since we haven't checked the
    # new line's indentation yet.
    lexer.curr_spaces_indent = 0
    t.lexer.lineno += len(t.value)
    if t.lexer.lexstate != 'BLOCKS':
        t.lexer.begin('BLOCKS')
    return t

def t_BLOCKS_WS(t):
    r'[ \t]+'
    # We reach this state only after a new line. The number of spaces on this line
    # is therefore the current number of spaces.
    count = 0
    for char in t.value:
      if char == " ":
          count += 1
      if char == "\t":
          count += 8

    lexer.curr_spaces_indent = count
#    # Probably don't want to return this token.
#    return t

def t_BLOCKS_INDENT(t):
    r'[^ \t\n]'
    # We're checking indent, and have the first non-whitespace character.
    # We probably want to switch to parsing code not whitespace, and figure
    # out whether to emit a dedent or not.
    #
    # Since whitespace checking is look ahead, we jump back one char in the
    # input stream beforehand.
    t.lexer.lexpos -= 1

    # First of all, check out indent level.
    curr_spaces_indent = lexer.curr_spaces_indent
    #print "------------------------------------> WE GET HERE TOO ", curr_spaces_indent

    dedents_needed = 0
    #print "lexer.indentation_stack[-1], curr_spaces_indent", lexer.indentation_stack[-1], curr_spaces_indent
    while lexer.indentation_stack[-1] > curr_spaces_indent:
        lexer.indentation_stack.pop()
        dedents_needed += 1
        #print "DEDENT REQUIRED"

    if dedents_needed > 0:
        t.lexer.dedents_needed = dedents_needed
        t.lexer.begin('EMITDEDENTS')
        return

    # If we get here, then our next step is parsing code, switch to code mode:
    t.lexer.begin('CODE')

    # If we get here, and current indentation is greater than the stack, we're
    # indenting, so we need to add that to the indentation stack and emit an
    # indent token:
    if curr_spaces_indent > lexer.indentation_stack[-1]:
        lexer.indentation_stack.append(lexer.curr_spaces_indent)
        return t

def t_EMITDEDENTS_DEDENT(t):
    r'.'
    # This rule matches any char so it always runs in the EMITDEDENTS state
    # We need to push the char back so it's not skipped during parsing
    #print "We REACHED EMITDEDENTS"
    t.lexer.lexpos -= 1

    # This allows us to emit as many DEDENT tokens as necessary.
    if t.lexer.dedents_needed > 0:
        t.lexer.dedents_needed -= 1
        return t
    t.lexer.begin('CODE')


def t_CODE_INITIAL_NUMBER(t):
    r'[-]?\d+'
    try:
         t.value = int(t.value)
    except ValueError:
         #print "Line %d: Number %s is too large!" % (t.lineno,t.value)
         t.value = 0
    return t

def t_CODE_INITIAL_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_ANY_error(t):
    print "PARSER STATE", t.lexer.lexstate
    print "Illegal character '%s'" % t.value[0]
    t.skip(1)


def t_CODE_INITIAL_WS(t):
  r'[ \t]+'
  v = 0
  for char in t.value:
      if char == " ":
          v += 1
      elif char == "\t":
          v += 8
      else:
          v += 0

  sys.stderr.write( "INDENT " + str(v) + "\n")
  sys.stderr.flush()
  t.lexer.curr_indent = v
  return t

if __name__ == "__main__":
    import sys
    test_data = """\
while True:
    print "hello 1"
    print "world 2"
    print 3
    while True:
        print "hello 4"
        print "world 5"
        print 6
        while True:
            print "hello 7"
            print "world 8"
            print 9

    while True:
        print "hello 10"
        print "world 11"
        print 12

print "wibble 13"
print "wibble 14"
print "wibble 15"
"""
    fname = os.tmpnam()
    files.append(fname)
    x = open(fname, "w")
    x.write(test_data)
    x.close()

    f = open(fname)
    sys.stdin = f

    lexer = lex.lex()
    lexer.curr_spaces_indent = 0

    lexer.indentation_stack = []
    lexer.indentation_stack.append(lexer.curr_spaces_indent)

    lexer.begin('BLOCKS')

    lex.runmain(lexer)


