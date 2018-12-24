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
import json
import platform
import os
import re
import glob
import subprocess
from pprint import pprint

def libclang():
    # path to libclang for cindex
    # Make an effort to be cross-os (ha)

    rez = False

    # first, .config obviously
    if os.path.isfile('.config'):
        config = json.load( open('.config', 'r') )
        if 'path' in config:
            if 'libclang' in config['path']:
                rez = config['path']['libclang']
                #print "# config " + rez
    
    if not rez:
        # clang -print-search-dirs might know
        try:
            paths = subprocess.check_output("clang -print-search-dirs", shell=True).split("\n")
            paths = filter(lambda p: p != '', paths)
        except subprocess.CalledProcessError as e:
            paths = []
        paths = filter(lambda p: re.search(r'^libraries:',p), paths)
        if len(paths) > 0:
            paths = paths[0]
            paths = re.sub( r'^libraries: =', '', paths)
            paths = paths.split(':')
            #print "#cl  "; pprint(list(paths))
            paths = list(glob.glob(p + "/libclang*.so*" ) for p in paths)
            paths = [item for sublist in paths for item in sublist] # flatten
            paths = list( os.path.realpath(p) for p in paths) # lots of relative .. typically
            # use 1st that is found
            #print "#  "; pprint(list(paths))
            if len(paths) > 0:
                rez = paths[0]
                #print "# clang"

    if not rez:
        # llvm-config might know
        try:
            paths = subprocess.check_output("llvm-config --libdir", shell=True).split("\n")
            paths = filter(lambda p: p != '', paths)
        except subprocess.CalledProcessError as e:
            paths = []
        if (not rez) and len(paths) > 0:
            paths = list(glob.glob(p + "/libclang*.so*" ) for p in paths)
            paths = [item for sublist in paths for item in sublist]
            paths.sort( key = lambda p: len(p.split("/"))) # shortest "depth"
            #print "#  "; pprint(list(paths))
            if len(paths) > 0:
                rez = paths[0]
                #print "# llvm-config"

    # FIXME: put finding for windows  here

    if (not rez) and platform.system() in ('Linux', 'Darwin', 'FreeBSD', 'posix'): # unixy things
        if os.system("which dpkg-query >/dev/stderr"):
            paths = os.popen("dpkg-query -S 'libclang*.so*' | awk '{print $2}'").read().split("\n")
            paths = filter(lambda p: p != '', paths)
            #print "#  "; pprint(paths)
            # not a link is probably better
            better_paths = filter(lambda p: not os.path.islink(p), paths)
            if better_paths == 0:
                # nothing that is not a link? oh well
                better_paths = paths
            # less deep is probably better
            paths.sort( key = lambda p: len(p.split("/"))) # shortest "depth"
            if len(paths) > 0:
                rez = paths[0]
            #print "# from dkpkg"

        if not rez:
            # try `locate`
            paths = os.popen("locate -b 'libclang.so*'").read().split("\n")
            paths = filter(lambda p: p != '', paths)
            if len(paths) > 0:
                # /usr/lib is likely better on linux anyway
                better_paths = filter(lambda p: re.search(r'^/usr/lib', p), paths)
                if better_paths == 0:
                    # no /usr/lib? oh well
                    better_paths = paths
                # less deep is probably better
                paths.sort( key = lambda p: len(p.split("/"))) # shortest "depth"
                if len(paths) > 0:
                    rez = paths[0]
                #print "# from locate"
        
    if not rez:
        raise Exception('Couldn\'t find a libclang library, add "path" : { "libclang" : "some/where" } to .config file')
    print >> sys.stderr, "Using libclang "+rez
    return rez

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
        # was testing if not text, maybe tokens
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

    elements = {
        'node' : kind,
        'actual_type' : node.type.kind.__str__(),
        'type' : canon_type,
        'type_name' : node.type.get_canonical().spelling,
        'text' : text, 
        'access' : node.access_specifier.name,
        'static' : 1 if node.is_static_method() else 0, 
        'line' : node.location.line
        }

    #print "# .canaon.kind " + node.type.get_canonical().kind.__str__()
    if node.type.get_canonical().kind.__str__() == 'TypeKind.ENUM':
        elements['type_name'] = node.type.get_canonical().spelling # the enum name
        # .type : <clang.cindex.Type object
        # .type.kind : TypeKind.TYPEDEF
        #print "    # try .type.get_canonical() " + node.type.get_canonical().__str__()
        #print "    # try .type.get_canonical().spell " + node.type.get_canonical().spelling
        #print "    # try .type.get_canonical().kind " + node.type.get_canonical().kind.__str__()
        #print "    # try .type.get_canonical().kind " + node.type.get_canonical().kind.spelling
        #print "    # try .type.kind " + node.type.kind.__str__()
        #print "    # try .type.kind " + node.type.kind.spelling

    if kind == 'CXX_METHOD':
        #print("Method:",text, node.access_specifier.name)
        canonical_return = str(node.result_type.get_canonical().kind) + ":" + str(node.result_type.get_canonical().get_size())
        elements['return_actual_type'] = node.result_type.kind.__str__()
        elements['return_type'] = canonical_return.__str__()
        elements['type_name'] = node.result_type.spelling 
    return '{ ' + ", ".join( ("\"{}\" : {}".format(x,json.dumps(y)) for x, y in elements.items()) )

if len(sys.argv) != 2:
    print >> sys.stderr, ("Usage: dump_ast.py [header file name]")
    sys.exit()

clang.cindex.Config.set_library_file(libclang())
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
    child_printed_ct = 0
    for node in enumerate(get_children(cursor)):
        # children is these are all clang.cindex.Cursor
        pos, children = node
        if pos==0:
            print (',' if depth !=0 else ''),'"children" : ['

        # descend if not-in-a-file (root stuff), or in file-of-interest
        if not children.location.file or children.location.file.name == sys.argv[1]:

            # don't describe nodes that aren't in a file
            if children.location.file:
                print "  " * depth, (',' if child_printed_ct > 0 else ''),get_text(children)
                child_printed_ct += 1

            if depth > 30: # arbitrary limit
                exit(1)

            printed = traverse(depth+1, children)

            if printed >= 0:
                print "  " * (depth+1),']';
                print "  " * depth,;

            if children.location.file:
                print '}'
    return pos

print '{'
traverse(0, translation_unit.cursor)
print ']}'
for diag in translation_unit.diagnostics:
    print >> sys.stderr, 'DIAG ',diag
