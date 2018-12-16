#!/usr/bin/env python2.7
# --- $cppfile # perl data structure out
# Only gives declaration parsing, doesn't parse bodies

# vim: set fileencoding=utf-8
# OMG to make this work:
# sudo pip install clang==3.4 # (whatever your `clang --version` is!), fix path below
import sys
import clang.cindex
# useful to browse /usr/local/lib/python2.7/dist-packages/clang/cindex.py to figure out ast objects
# e.g. node.result_type.text.__class__.__name__ == Type
import inspect

libclang='/usr/lib/llvm-3.8/lib/libclang.so.1'

def get_children(node):
    # return (c for c in node.get_children() if c.location.file.name == sys.argv[1])
    if str(node.kind) == 'xxCursorKind.COMPOUND_STMT':
        return (c for c in node.get_definition())
    else:
        return (c for c in node.get_children())

def oinspect(a):
    # non _ key/values
    vals = ""
    for key in dir(a):
        if not key.startswith("_"):
            vals += key + ", " 
    return vals

def sinspect(a):
    # system inspect, only _
    vals = ""
    for key in dir(a):
        if key.startswith("_"):
            vals += key + ", "
    return vals

def get_text(node):
    kind = str(node.kind)[str(node.kind).index('.')+1:]

    text = node.spelling
    if not text:
        text = node.displayname
    if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        # nothing obvious gives the actual operator
        pass
    if 0 and not text:
        print "get tokens: {} t:{} {}/ {} ...".format(kind, node.type, text, text.__class__.__name__)
        text = ""
        for x,token in enumerate(node.get_tokens()):
            text += token.spelling + " "
        print "get tokens: ",text
    etc = ''
    # token.kind == cindex.TokenKind.COMMENT:
    # to parse comments, which don't seem to appear in the ast (though...)
    # see https://github.com/jessevdk/cldoc/blob/master/cldoc/comment.py
    # The CommentsDictionary which collects the comment-tokens, and indexes them by real parse nodes
    # Consider: semantics of blank lines, beforeness/afterness
    if kind=='COMPOUND_STMT':
        # unparsed in cindex I guess
        if not text:
            text = " ".join(x.spelling for x in node.get_tokens())
    # we can get more info about the node.type
    canon_type = str(node.type.get_canonical().kind) + ":" + str(node.type.get_canonical().get_size())

    fields = '{{ node => "{}", actual_type => "{}", type => "{}", type_name => "{}", text => "{}", access => "{}", static => {}, line => {}, '
    values = [ kind, node.type.kind, canon_type, node.result_type.spelling, text, node.access_specifier.name, 1 if node.is_static_method() else 0, node.location.line ]

    if kind == 'CXX_METHOD':
        #print("Method:",text, node.access_specifier.name)
        canonical_return = str(node.result_type.get_canonical().kind) + ":" + str(node.result_type.get_canonical().get_size())
        fields += 'return_actual_type => "{}", return_type => "{}", '
        values.extend( [node.result_type.kind, canonical_return] )
    return fields.format(*values)

if len(sys.argv) != 2:
    print("Usage: dump_ast.py [header file name]")
    sys.exit()

clang.cindex.Config.set_library_file(libclang)
index = clang.cindex.Index.create()
# translation_unit = index.parse(sys.argv[1], ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__'])
# attempt to #include ard stuff: causes memory error
# translation_unit = index.parse(sys.argv[1], ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__', '-fparse-all-comments', '-DARDUINO=10607', '-I/mnt/auger/home/awgrover/xod/__packages__/packages/arduino/hardware/avr/1.6.21/cores/arduino' ],None,1)
translation_unit = index.parse(sys.argv[1], ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__', '-fparse-all-comments', '-DARDUINO=10607' ],None,1)
# fixme: put in error detect. the ast will be unfinished if there are errors (especially depthwise)
# e.g. see https://github.com/jessevdk/cldoc/blob/master/cldoc/tree.py .process()
#print(asciitree.LeftAligned(traverse = clang_traverse())(translation_unit.cursor) )

def traverse(depth, cursor):

    pos = -1;
    for node in enumerate(get_children(cursor)):
        # children is these are all clang.cindex.Cursor
        pos, children = node
        if pos==0:
            print "children => ["

        # descend if not-in-a-file (root stuff), or in file-of-interest
        if not children.location.file or children.location.file.name == sys.argv[1]:

            # don't describe nodes that aren't in a file
            if children.location.file:
                print "  " * depth,get_text(children)

            if depth > 30: # arbitrary limit
                exit(1)

            printed = traverse(depth+1, children)

            if printed >= 0:
                print "  " * (depth+1),"]";
                print "  " * depth,;

            if children.location.file:
                print "},"
    return pos

print "{"
traverse(0, translation_unit.cursor)
print "]}"
for diag in translation_unit.diagnostics:
    print >> sys.stderr, 'DIAG ',diag
