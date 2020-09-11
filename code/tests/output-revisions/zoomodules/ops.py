# Detect whether a string s has the form p.[text].
def has_prefix(p, s):
    L = s.split('.')
    if len(L) < 2: return False
    if L[0] != p: return False
    return True

# Check whether any of the class names in S have operator prefixes. If so,
# print an error and halt.
def no_operator_declarations(S):
    for s in S:
        if len(s.split('.')) > 1:
            print('Invalid declared class:')
            print(s)
            print('Declared classes cannot contain operators.')
            quit()

# Add co.name and cocap.name to S for each name in S.
def generate_co(S):
    C = set()
    for name in S:
        if (not has_prefix('co', name)) and (not has_prefix('cocap', name)):
            C.add('co' + '.' + name)
            C.add('cocap' + '.' + name)
    S = S | C
    return S

# operator computations
def opcompute(names, classes, operators, q, oprules):
    print('Computing operators...')
    todo = []
    op = {}
    for f in operators:
        op[f] = {}
        for name in names:
            op[f][name] = ''
    for name in names:
        op['id'][name] = name
    for x in classes:
        for f in operators:
            if has_prefix(f, x):
                todo.append((f, q[x.split('.', 1)[1]], q[x]))
    names_squared = set()
    for x in names:
        for y in names:
            names_squared.add((x,y))
    for (F, X, Y) in todo:
        if op[F][X] == Y: continue
        if op[F][X] and op[F][X] != Y:
            print('Undeclared non-transitive equality:')
            print(op[F][X])
            print(Y)
            quit()
        op[F][X] = Y
        for (f, g, h, k) in oprules:
            if F == f:
                for x in names:
                    if op[g][x] == X:
                        for y in names:
                            if op[k][x] == y:
                                todo.append((h, y, Y))
            if F == g:
                for (x, y) in names_squared:
                    if op[f][Y] == x and op[k][X] == y: todo.append((h, y, x))
                    if op[h][x] == y and op[k][X] == x: todo.append((f, Y, y))
            if F == h:
                for (x,y) in names_squared:
                    if op[g][x] == y and op[k][x] == X: todo.append((f, y, Y))
            if F == k:
                for (x,y) in names_squared:
                    if op[f][x] == y and op[g][X] == x: todo.append((h, Y, y))
                    if op[g][X] == x and op[h][Y] == y: todo.append((f, x, y))

    # compute operator inverses
    opinv = {}
    for f in operators:
        opinv[f] = {}
        for x in names:
            opinv[f][x] = set()
            for y in names:
                if op[f][y] == x: opinv[f][x].add(y)

    return (op, opinv)
