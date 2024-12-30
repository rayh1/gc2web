import sys
from antlr4 import *
from GedcomLexer import GedcomLexer
from GedcomParser import GedcomParser
from GedcomListener import GedcomListener
from GedcomLineListener import GedcomLineListener

class InfoPrinter(GedcomListener):
    def exitTag(self, ctx):
        print("Oh, a key!: "
              + ctx.getText()) 
        
    def exitValue(self, ctx):
        print("Oh, a value!: "
              + ctx.getText())    
 
def main(argv):
    input_stream = FileStream(argv[1])
    lexer = GedcomLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = GedcomParser(stream)
    tree = parser.gedcom()
    listener = GedcomLineListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    for line in listener.lines:
        print(line)

 
if __name__ == '__main__':
    main(sys.argv)