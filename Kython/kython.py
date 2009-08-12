#!/usr/bin/python

def parse(originalfile ,dict={}):
    lines = originalfile.split("\n")
    indent = 0
    code = ''
    in_string = False
    quote_string = None
    indent_tokens = []
    for line in lines:
        if not in_string:
            triple_quote = line.find("'''")
            triple_doublequote = line.find('"""')
            if triple_quote != triple_doublequote: # (both -1 == not start of string
                in_string = True
                if triple_quote == -1:
                    quote_string = '"""'
                elif triple_doublequote == -1:
                    quote_string = "'''"
                else:
                    if triple_quote < triple_doublequote:
                        quote_string = "'''"
                    else:
                        quote_string = '"""'
                Q = line.find(quote_string)
                the_string = line[Q:]+"\n"
                line = line[:Q]
                code += ('    '*indent)+line.lstrip()
                continue
            if line.strip() == '':
                code += ('    '*indent)+line+"\n"
                continue
            if line.strip() == 'end':
                indent -= 1
                code += ('    '*indent)+"# "+line.lstrip()+" "+ indent_tokens.pop(-1)+"\n"
                continue
            code += ('    '*indent)+line.lstrip()+"\n"
            if line.rstrip()[-1] == ':':
                indent += 1
                indent_tokens.append( line.lstrip().split()[0])
        else:
            Q = line.find(quote_string)
            if Q != -1:
                the_string += line[:Q+3]
                line = line[Q+3:]
                code += the_string
                code += line + "\n"
                in_string = False
            else:
                the_string += line+"\n"
    return code

originalfile = open("hello.kpy").read()
code = parse(originalfile)
print "---------------"

if False: # show code
    i = 1
    for line in code.split("\n"):
        print i,"\t\t|", line
        i += 1
    print "---------------"

try:
    exec code
except SyntaxError, e:
    print "---------------"
    print "SYNTAX ERROR - here"
    i = 1
    context = 5
    for line in originalfile.split("\n"):
        if e.lineno - context < i < e.lineno +context:
            if i != e.lineno:
                print i,"\t\t|", line
            else:
                print i,"here --->\t|", line
        i += 1
    raise
