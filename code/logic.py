from random import shuffle

def main(names, classes, props, oporder, op, q, operators, opinv):
    # initialize knowledge table, Hasse relation, and transitive closure
    knowledge = {}
    Hasse = {}
    tclosure = {}
    for x in names:
        Hasse[x] = set()
        tclosure[x] = set()
        for y in names:
            for R in ['A', 'AA', 'EA', 'R', 'T', 'E']:
                for c in ['p', 'd', '-p', '-d']:
                    knowledge[(c, R, x, y)] = False

    redundancies = []
    # redundancies = pickle.load(open('redundant.p', 'rb'))
    todo = []
    relation_tuples = [
        ('A', '<', 'osep', '<?'), ('AA', 'a<', 'xsep', 'a<?'),
        ('EA', 'x<', 'asep', 'x<?'), ('R', 'r<', 'rsep', 'r<?'),
        ('T', 't<', 'tsep', 't<?'), ('E', 'o<', 'sep', 'o<?')]

    for x in classes:
        for (Rel, pos, neg, opn) in relation_tuples:
            for y in props[pos][x]:
                if q[x] == q[y]:
                    print('Non-strict inclusion in input:', x, pos, y)
                    quit()
                todo.append(('p', Rel, q[x], q[y], 0))
            for y in props[neg][x]:
                if q[x] == q[y]:
                    print('Oracle separation of equal classes:', x, neg, y)
                    quit()
                todo.append(('d', Rel, q[x], q[y], 0))
            for y in props[opn][x]:
                todo.append(('-p', Rel, q[x], q[y], 0))
                todo.append(('-d', Rel, q[x], q[y], 0))

    shuffle(todo)
    for st in redundancies:
        still_input = False
        for (s, Rel, x, y, flag) in todo:
            if str((s, Rel, x, y)) ==  st: still_input = True
        if not still_input: redundancies.remove(st)

    for f in oporder:
        for g in oporder[f]:
            for x in names:
                if op[f][x] and op[g][x] and op[f][x] != op[g][x]:
                    todo.append(('p', 'A', op[f][x], op[g][x]))

    world_ordering = set([
        ('A','AA'), ('A','R'), ('AA','T'), ('AA', 'EA'), ('EA', 'E'), ('R','E'),
        ('T','E')
        ])

    transitivity_rules = set([
        ('A', 'A', 'A'), ('E', 'A', 'E'), ('A', 'E', 'E'), ('AA', 'AA', 'AA'),
        ('EA', 'AA', 'EA'), ('AA', 'EA', 'EA'), ('R', 'R', 'R'), ('T', 'T', 'T')
        ])

    print('Deducing...')
    while todo:
        formula = todo.pop()
        initial = False
        if len(formula) > 4:
            initial = True
            formula = (formula[0], formula[1], formula[2], formula[3])
        (c, Rel, x, y) = formula
        if knowledge[formula]:
            if initial and str(formula) not in redundancies:
                redundancies.append(str(formula))
            continue
        knowledge[formula] = True
        is_contradiction = False
        if knowledge[('-p', Rel, x, y)] and knowledge[('p', Rel, x, y)]:
            is_contradiction = True
        if knowledge[('d', Rel, x, y)] and knowledge[('-d', Rel, x, y)]:
            is_contradiction = True
        if knowledge[('d', Rel, x, y)] and knowledge[('p', Rel, x, y)]:
            is_contradiction = True
        if is_contradiction:
            print('Contradiction!')
            print((c, Rel, x, y))
            quit()
        if c == 'p' and Rel == 'A' and y not in tclosure[x]:
            if x in tclosure[y]:
                print('Equality learned from inclusion:')
                print(x, '=', y)
                quit()
            Hasse[x].add(y)
            for v in names:
                for w in names:
                    removeHasse = False
                    if x in tclosure[v] and w in tclosure[y]: removeHasse = True
                    if x in tclosure[v] and y == w: removeHasse = True
                    if v == x and w in tclosure[y]: removeHasse = True
                    if removeHasse and w in Hasse[v]: Hasse[v].remove(w)
            tclosure[x].add(y)
            for v in names:
                if v in tclosure[y]: tclosure[x].add(v)
                if x in tclosure[v]: tclosure[v].add(y)
                for w in names:
                    if x in tclosure[v] and w in tclosure[y]: tclosure[v].add(w)
        # 0-ary rules
        if c == 'p': todo.append(('-d', Rel, x, y))
        if c == 'd': todo.append(('-p', Rel, x, y))
        # unary rules
        for (V, W) in world_ordering:
            if (c == 'p' or c == '-d') and Rel == V: todo.append((c, W, x, y))
            if (c == 'd' or c == '-p') and Rel == W: todo.append((c, V, x, y))
        # transitivity rules
        for z in names:
            for (U, V, W) in transitivity_rules:
                if c == 'p' and Rel == U:
                    if knowledge[('p', V, y, z)]: todo.append(('p', W, x, z))
                    if knowledge[('-p', W, x, z)]: todo.append(('-p', V, y, z))
                    if knowledge[('d', W, x, z)]: todo.append(('d', V, y, z))
                    if knowledge[('-d', V, y, z)]: todo.append(('-d', W, x, z))
                if c == 'p' and Rel == V:
                    if knowledge[('p', U, z, x)]: todo.append(('p', W, z, y))
                    if knowledge[('-p', W, z, y)]: todo.append(('-p', U, z, x))
                    if knowledge[('d', W, z, y)]: todo.append(('d', U, z, x))
                    if knowledge[('-d', U, z, x)]: todo.append(('-d', W, z, y))
                if c == 'd' and Rel == W:
                    if knowledge[('p', U, x, z)]: todo.append(('d', V, z, y))
                    if knowledge[('p', V, z, y)]: todo.append(('d', U, x, z))
                    if knowledge[('-d', V, z, y)]: todo.append(('-p', U, x, z))
                    if knowledge[('-d', U, x, z)]: todo.append(('-p', V, z, y))
                if c == '-d' and Rel == U:
                    if knowledge[('p', V, y, z)]: todo.append(('-d', W, x, z))
                    if knowledge[('d', W, x, z)]: todo.append(('-p', V, y, z))
                if c == '-d' and Rel == V:
                    if knowledge[('p', U, z, x)]: todo.append(('-d', W, z, y))
                    if knowledge[('d', W, z, y)]: todo.append(('-p', U, z, x))
                if c == '-p' and Rel == W:
                    if knowledge[('p', U, x, z)]: todo.append(('-p', V, z, y))
                    if knowledge[('p', V, z, y)]: todo.append(('-p', U, x, z))
        # operator rules
        for f in operators:
            if c == 'p' or c == '-d':
                if op[f][x] and op[f][y] and op[f][x] != op[f][y]:
                    todo.append((c, Rel, op[f][x], op[f][y]))
            if c == '-p' or c == 'd':
                for v in opinv[f][x]:
                    for w in opinv[f][y]: todo.append((c, Rel, v, w))
        # cocap.A is the meet of A and cocap.A
        if c == 'p' and Rel in ['A', 'AA', 'R', 'T']:
            if knowledge[('p', Rel, x, op['co'][y])] and x != op['cocap'][y]:
                todo.append(('p', Rel, x, op['cocap'][y]))
            if knowledge[('-p', Rel, x, op['cocap'][y])] and x != op['co'][y]:
                todo.append(('-p', Rel, x, op['co'][y]))
            if knowledge[('d', Rel, x, op['cocap'][y])] and x != op['co'][y]:
                todo.append(('d', Rel, x, op['co'][y]))
            if knowledge[('-d', Rel, x, op['co'][y])] and x != op['cocap'][y]:
                todo.append(('-d', Rel, x, op['cocap'][y]))
        if c == '-p' and Rel in ['A', 'AA', 'R', 'T']:
            for z in opinv['cocap'][y]:
                if knowledge[('p', Rel, x, z)] and x != op['co'][z]:
                    todo.append(('-p', Rel, x, op['co'][z]))
        if c == '-d' and Rel in ['A', 'AA', 'R', 'T'] and x != op['cocap'][y]:
            if knowledge[('p', Rel, x, op['co'][y])]:
                todo.append(('-d', Rel, x, op['cocap'][y]))
        if c == '-d' and Rel in ['A', 'AA', 'R', 'T'] and x != op['co'][y]:
            if knowledge[('d', Rel, x, op['cocap'][y])]:
                todo.append(('-p', Rel, x, op['co'][y]))
        if c == 'd' and Rel in ['A', 'AA', 'R', 'T']:
            for z in opinv['cocap'][y]:
                if x != op['co'][z]:
                    if knowledge[('p', Rel, x, z)]:
                        todo.append(('d', Rel, x, op['co'][z]))
                    if knowledge[('-d', Rel, x, z)]:
                        todo.append(('-p', Rel, x, op['co'][z]))
    return (knowledge, redundancies, Hasse, tclosure)
