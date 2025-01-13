# FILE: gc2web/GedcomLineListener.py
from GedcomListener import GedcomListener
from GedcomParser import GedcomParser
from GedcomLine import GedcomLine

class GedcomLineListener(GedcomListener):
    def __init__(self):
        self.lines = []

    def exitLine(self, ctx: GedcomParser.LineContext):
        level = ctx.level().getText()
        opt_xref_id = ctx.opt_xref_id().getText() if ctx.opt_xref_id() else None
        tag = ctx.tag().getText()
        value = None
        pointervalue = None

        if ctx.value():
            for item in ctx.value().lineitem():
                if item.pointer():
                    pointervalue = item.pointer().getText()
                elif item.anychar():
                    value = item.getText()

        gedcom_line = GedcomLine(level, opt_xref_id, tag, value, pointervalue)
        self.lines.append(gedcom_line)