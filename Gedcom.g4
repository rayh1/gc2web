grammar Gedcom;

// Parser Rules
gedcom: line+ EOF;

line: level (' ' opt_xref_id)? ' ' tag (' ' value)? EOL;

level: DIGIT+;

opt_xref_id: pointer;

tag: alphanum+;

value: lineitem+;

lineitem: pointer | escape | anychar;

escape: '@' '#' escape_text '@' non_at;

non_at: ALPHA | DIGIT | otherchar | '#';

escape_text: anychar+;

pointer: '@' alphanum pointer_string '@';

pointer_string: pointer_char+;

pointer_char: ALPHA | DIGIT | otherchar | '#';

alphanum: ALPHA | DIGIT;

anychar: ALPHA | DIGIT | ' ' | '\t' | otherchar | '#' | '@@';

otherchar: '!' | '"' | '$' | '&' | '\'' | '(' | ')' | '*' | '+' | '-' | ',' | '.' | '/';

// Lexer 

ALPHA: [a-zA-Z_];

DIGIT: [0-9];

EOL: [\r\n]+;
