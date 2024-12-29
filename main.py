import sys
from antlr4 import *
from GedcomLexer import GedcomLexer
from GedcomParser import GedcomParser
from GedcomListener import GedcomListener

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
    printer = InfoPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
 
if __name__ == '__main__':
    main(sys.argv)