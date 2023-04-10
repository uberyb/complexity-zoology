from code import ops

rel_syms = ['<', 'a<', 'x<', 'r<', 't<', 'o<', 'osep', 'xsep', 'asep', 'rsep',
            'tsep', 'sep', '<?', 'a<?','x<?', 'r<?', 't<?', 'o<?', '=']
op_syms = ['p=','z=']

def is_declaration(s):
    '''Determine whether a given string is a declaration.
    '''
    # To be a declaration, there should be either two or three entries with
    # colon separators.
    parsed = s.split(':')
    if len(parsed) != 2 and len(parsed) != 3: return False

    # The class name may not contain whitespace.
    class_name = parsed[0].split()
    if len(class_name)  > 1: return False

    # The class name should also not contain more than one period.
    class_name = parsed[0].split('.')
    if len(class_name) > 1: return False

    # If there are keywords, they should contain no spaces and be separated by
    # commas.
    if len(parsed) == 2: return True
    keywords = parsed[2].strip()
    keywords = keywords.split(',')
    for word in keywords:
        if len(word.split()) > 1: return False

    return True

# A boolean function for determining whether a given string is a proposition.
def is_proposition(s):
    # A proposition should have length 3 when whitespace is the separator.
    parsed = s.split()
    if len(parsed) != 3: return False

    # The middle entry of the proposition should be a valid relation.
    valid_relation = False
    if parsed[1] in rel_syms or parsed[1] in op_syms: valid_relation = True

    if valid_relation == False: return False

    # Finally, colons are invalid characters in class names, because they act as
    # separators in declarations.
    if ':' in parsed[0] or ':' in parsed[2]: return False

    return True

# Removes citations from a string. Citations are text surrounded by square
# brackets.
def remove_citations(s):
    left_index = -1
    right_index = -1

    for i in range(len(s)):
        if s[i] == '[':
            left_index = i
            break

    for i in range(len(s)):
        if s[i] == ']': right_index = i + 1

    if left_index > -1 and right_index > left_index:
        s = s[:left_index] + s[right_index:]

    return s

# Removes comments of both types from a one-line string.
def remove_comments(s):
    s = s.split('#', 1)[0] # removes ordinary comments
    s = remove_citations(s)

    return s

# Read a class name from a declaration d.
def get_class_name(d):
    parsed = d.split(':')

    name = parsed[0]
    name = name.strip()

    return name

# Extract a set of keywords from a declaration d.
def get_keywords(d):
    spaced_keywords = set()

    parsed = d.split(':')
    if len(parsed) < 3: return spaced_keywords

    spaced_keywords = parsed[2].strip()
    spaced_keywords = spaced_keywords.split(',')
    keywords = set()
    for kw in spaced_keywords:
        keyword = kw.strip()
        keywords.add(keyword)

    return keywords

# Check each line of an input file to determine whether it is a valid line of
# input. If it is not, the program prints an error message and halts.
def valid_syntax(f):
    f.seek(0)
    i = 0

    for line in f:
        i += 1
        line = remove_comments(line)
        line = line.strip()

        if line and not is_declaration(line) and not is_proposition(line):
            print('Error: Invalid syntax on line ', i)
            quit()

# Read the declarations from the input file f and record the names in a set.
def read_declarations(f):
    f.seek(0)

    names = set()
    keywords = {}

    for line in f:
        text = remove_comments(line)
        if not is_declaration(text): continue

        name = get_class_name(text)

        names.add(name)
        keywords[name] = get_keywords(text)

    return (names, keywords)

# Read propositions from input file into a dict.
def read_propositions(f, classes):
    f.seek(0)
    props = {}
    for R in rel_syms:
        props[R] = {}
        for x in classes: props[R][x] = set()
    for line in f:
        text = remove_comments(line)
        if not is_proposition(text): continue
        X = text.split()[0].split(',')
        Y = text.split()[2].split(',')
        R = text.split()[1]
        for x in X:
            for y in Y:
                props[R][x].add(y)
    return props

# add classes with operator prefixes to the set of classes
def op_classes(f, classes, operators):
    f.seek(0)
    new_classes = set()
    for line in f:
        text = remove_comments(line)
        if not is_proposition(text): continue
        (X, Y) = (text.split()[0].split(','), text.split()[2].split(','))
        for x in X:
            for y in Y:
                for z in [x, y]:
                    L = z.split('.')
                    base_class = L[len(L)-1]
                    if base_class not in classes:
                        print('Undeclared class:')
                        print(base_class)
                        quit()
                    while len(L) > 1:
                        name = '.'.join(L)
                        new_classes.add(name)
                        w = L.pop(0)
                        if w not in operators:
                            print('Undeclared operator:')
                            print(w)
                            quit()
    classes = classes | new_classes
    return classes

# generate set of quadratic relations for operators
def read_oprules(f, operators, operators_keywords):
    f.seek(0)
    oprules = set()
    n = 0
    for op in operators:
        if 'idempotent' in operators_keywords[op]:
            oprules.add((op, op, op, 'id'))
    for line in f:
        n += 1
        text = remove_comments(line)
        if not is_proposition(text): continue
        rel = text.split()
        (x, y) = (rel[0], rel[2])
        if rel[1] == '=':
            L = []
            for z in [x, y]:
                zlist = z.split('.')
                if len(zlist) > 2:
                    print('Non-quadratic operator relation on line ', n)
                    quit()
                L += zlist
                if len(zlist) == 1: L.append('id')
            oprules.add(tuple(L))
        if rel[1] == 'z=':
            for l, r in [(l, r) for l in x.split(',') for r in y.split(',')]:
                oprules.add((l, r, r, l))
        if rel[1] == 'p=':
            for l, r in [(l, r) for l in x.split(',') for r in y.split(',')]:
                oprules.add((l, r, r, 'id'))
                oprules.add((r, l, r, 'id'))
    for rule in oprules:
        for op in rule:
            if op not in operators:
                print('Undeclared operator:')
                print(op)
                quit()
    return oprules

# read ordering of operators from the input file
def read_oporder(f, operators):
    f.seek(0)
    oporder = {}
    for op in operators: oporder[op] = set()
    for line in f:
        text = remove_comments(line)
        if not is_proposition(text): continue
        rel = text.split()
        if rel[1] != '<': continue
        (X, Y) = (rel[0].split(','), rel[2].split(','))
        for x in X:
            for y in Y:
                for z in [x, y]:
                    if z not in operators:
                        print('Undeclared operator:')
                        print(z)
                        quit()
                oporder[x].add(y)
    return oporder

def remove_ignored(classes, props, classes_keywords, operators_keywords,
                   oprules, operators, oporder):
    '''Remove all data involving classes and operators with the
    ignore keyword.
    '''

    ignored_classes = set()
    ignored_operators = set()

    for x in classes_keywords:
        if 'ignore' in classes_keywords[x]: ignored_classes.add(x)
    for x in operators_keywords:
        if 'ignore' in operators_keywords[x]: ignored_operators.add(x)

    # We want to ignore both classes of the form operator.ignored_class and
    # ignored_operator.class.
    for x in classes:
        for N in range(len(x.split('.'))):
            if N < len(x.split('.'))-1:
                if x.split('.')[N] in ignored_operators: ignored_classes.add(x)
            else:
                if x.split('.')[N] in ignored_classes: ignored_classes.add(x)

    # If A is an ignored class and an operator class only appears in relations
    # involving A, then the operator class should also be ignored.
    for x in classes:
        if len(x.split('.')) < 2: continue
        should_ignore = True
        for R in props:
            if x in props[R]:
                for y in props[R][x]:
                    if y not in ignored_classes: should_ignore = False
            for y in props[R]:
                if y not in ignored_classes and x in props[R][y]:
                    should_ignore = False
        if should_ignore: ignored_classes.add(x)

    # After doing the above, though, we should make sure that co and cocap of every
    # unignored class exists.
    for x in classes:
        if x not in ignored_classes:
            ignored_classes.discard('co.' + x)
            ignored_classes.discard('cocap.' + x)

    # Remove ignored classes.
    for x in ignored_classes:
        classes.remove(x)
        if x in classes_keywords: classes_keywords.pop(x)

    # Remove ignored operators.
    for x in ignored_operators:
        operators.remove(x)
        if x in operators_keywords: operators_keywords.pop(x)

    # Remove propositions involving ignored classes.
    for R in props:
        for x in ignored_classes:
            for y in props[R]:
                if x in props[R][y]: props[R][y].remove(x)
            if x in props[R]: props[R].pop(x)

    # Remove operator rules involving ignored operators.
    ignored_oprules = set()
    for x in oprules:
        for y in x:
            if y in ignored_operators: ignored_oprules.add(x)
    for x in ignored_oprules: oprules.remove(x)

    # Removed ignored operators from the operator partial ordering.
    for x in ignored_operators:
        for y in oporder:
            if x in oporder[y]: oporder[y].remove(x)
        if x in oporder: oporder.pop(x)

    return (classes, operators, props, oprules, oporder)

def parse(classes_file, operators_file):
    '''Parse the input files.'''
    classes_file = open(classes_file)
    operators_file = open(operators_file)

    valid_syntax(classes_file)
    valid_syntax(operators_file)

    (classes, classes_keywords) = read_declarations(classes_file)
    (operators, operators_keywords) = read_declarations(operators_file)
    ops.no_operator_declarations(classes)
    classes = op_classes(classes_file, classes, operators)
    classes = ops.generate_co(classes)

    for x in classes:
        if x not in classes_keywords: classes_keywords[x] = set()

    props = read_propositions(classes_file, classes)
    oprules = read_oprules(operators_file, operators, operators_keywords)
    oporder = read_oporder(operators_file, operators)

    classes_file.close()
    operators_file.close()

    ig = remove_ignored(classes, props, classes_keywords, operators_keywords,
                        oprules, operators, oporder)

    classes = ig[0]
    operators = ig[1]
    props = ig[2]
    oprules = ig[3]
    oporder = ig[4]

    parsed = (classes, classes_keywords, operators, operators_keywords, props,
              oprules, oporder)

    return parsed
