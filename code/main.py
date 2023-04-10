import shutil, subprocess
from code import equalities, logic, ops, output, parser

def main():

    # < Most of this code comes from parser.py and is documented in
    # input-syntax.pdf
    print('Reading input...')
    parsed = parser.parse('./data/classes.txt', './data/operators.txt')
    classes = parsed[0]
    classes_keywords = parsed[1]
    operators = parsed[2]
    operators_keywords = parsed[3]
    props = parsed[4] # Organized as a dictionary {'relation (or op)': 'some class' : {set of classes under this relation}}
    oprules = parsed[5] # These are rules defined in data/operators.txt. Comes at a tuple (op1, op2, op3, op4) which I think means op1.op2 = op3.op4
    oporder = parsed[6] # Not sure why oporder is important or how exactly it's specified yet
    # >


    # < There is a preference hierarchy outlined in input-syntax.pdf which is an
    # ordering of the prefered name of a class. Not really important to
    # understand how this fnc works
    prefs = generate_preference_hierarchy(classes_keywords)
    # >

    (props, q, names) = equalities.main(classes_keywords, props, operators, classes, prefs)

    (op, opinv) = ops.opcompute(names, classes, operators, q, oprules)

    (knowledge, redundancies, Hasse, tclosure) = logic.main(names, classes,
                                                            props, oporder,
                                                            op, q, operators,
                                                            opinv)
    print('Postprocessing...')
    knowledge_graph = make_knowledge_graph(knowledge)
    relation_pairs = [('A', 'A'), ('AA', 'AA'), ('EA', 'AA'), ('R', 'R'),
                      ('T', 'T'), ('E', 'A')]
    colored_graph = {}
    gradient_list = {}
    table_names = {}
    extremal_unknowns = {}
    hidden_names = set()
    status_table = {}
    for x in classes_keywords:
        if 'hidden' in classes_keywords[x]: hidden_names.add(x)
    for (Rel, Dual) in relation_pairs:
        (colored_graph[Rel], table_names[Rel]) = make_colored_graph(knowledge_graph, Dual, prefs, hidden_names, op)
        gradient_list[Rel] = make_gradient_list(knowledge_graph, Rel, prefs,
                                                hidden_names, op, knowledge,
                                                colored_graph)
        extremal_unknowns[Rel] = get_extremal_unknowns(knowledge_graph,
                                                       knowledge, Rel, Dual,
                                                       prefs)
        status_table[Rel] = get_status_table(names, knowledge, prefs, Rel, Dual)

    output.generate_progress_report(extremal_unknowns, status_table)

    output.main(classes_keywords, knowledge, q, redundancies, names, op,
                classes, tclosure, props, Hasse, colored_graph, gradient_list,
                table_names)

def get_status_table(names, knowledge, prefs, Rel, Dual):
    eq_graph = {}
    for x in names:
        eq_graph[x] = set()
        for y in names:
            is_equal = False
            if knowledge[('p', Dual, x, y)]:
                if knowledge[('p', Dual, y, x)]: is_equal = True
            if is_equal: eq_graph[x].add(y)
    (Rel_q, Rel_names) = equalities.union_find(eq_graph, prefs)
    P_count = 0
    D_count = 0
    O_count = 0
    up_count = 0
    ud_count = 0
    uu_count = 0
    for x in Rel_names:
        for y in Rel_names:
            if x == y: continue
            if knowledge[('p', Rel, x, y)]: P_count += 1
            if knowledge[('d', Rel, x, y)]: D_count += 1
            if knowledge[('-p', Rel, x, y)]:
                if knowledge[('-d', Rel, x, y)]: O_count += 1
            if not knowledge[('-p', Rel, x, y)]:
                if not knowledge[('p', Rel, x, y)]:
                    if knowledge[('-d', Rel, x, y)]: up_count += 1
            if knowledge[('-p', Rel, x, y)]:
                if not knowledge[('-d', Rel, x, y)]:
                    if not knowledge[('d', Rel, x, y)]: ud_count += 1
            if not knowledge[('-p', Rel, x, y)]:
                if not knowledge[('-d', Rel, x, y)]: uu_count += 1
    status_table = {'P' : P_count, 'D' : D_count, 'O' : O_count,
                    '?p' : up_count, '?d' : ud_count, '??' : uu_count}

    return status_table


def get_extremal_unknowns(knowledge_graph, knowledge, Rel, Dual, prefs):
    test_flag = True
    eq_graph = {}
    for x in knowledge_graph[Dual]:
        eq_graph[x] = set()
        for y in knowledge_graph[Dual]:
            if x == y: continue
            if x in knowledge_graph[Dual][y]:
                if y in knowledge_graph[Dual][x]:
                    eq_graph[x].add(y)
    (q, names) = equalities.union_find(eq_graph, prefs)
    unknowns = {}
    likely_unknowns = []
    unlikely_unknowns = []
    for x in names:
        unknowns[x] = set()
        for y in names:
            if x == y: continue
            is_unknown = True
            for c in ['p','d']:
                if knowledge[(c, Rel, x, y)]: is_unknown = False
            if knowledge[('-p', Rel, x, y)] and knowledge[('-d', Rel, x, y)]:
                is_unknown = False
            if is_unknown: unknowns[x].add(y)
    for x in unknowns:
        for y in unknowns[x]:
            is_likely = True
            is_unlikely = True
            for z in names:
                if x == z or y == z: continue
                if z in unknowns[x]:
                    if knowledge[('p', Dual, y, z)]: is_likely = False
                    if knowledge[('p', Dual, z, y)]: is_unlikely = False
                if y in unknowns[z]:
                    if knowledge[('p', Dual, z, x)]: is_likely = False
                    if knowledge[('p', Dual, x, z)]: is_unlikely = False
            if is_likely:
                if knowledge[('-d', Rel, x, y)]: state = 'provable'
                elif knowledge[('-p', Rel, x, y)]: state = 'disprovable'
                else: state = 'blank'
                likely_unknowns.append((x, y, state))
            if is_unlikely:
                if knowledge[('-d', Rel, x, y)]: state = 'provable'
                elif knowledge[('-p', Rel, x, y)]: state = 'disprovable'
                else: state = 'blank'
                unlikely_unknowns.append((x, y, state))
        likely_unknowns.sort()
        unlikely_unknowns.sort()
        extremal_unknowns = {'likely' : likely_unknowns,
                             'unlikely' : unlikely_unknowns}
    return extremal_unknowns

def generate_preference_hierarchy(classes_keywords):
    def is_prefnum_keyword(s):
        if s[0:10] != 'preferred(': return False
        if not str.isdigit(s[10:len(keyword)-1]): return False
        if s[len(keyword)-1] != ')': return False
        return True

    prefs = {}
    for x in classes_keywords:
        keyword_count = 0
        for keyword in classes_keywords[x]:
            if keyword == 'preferred':
                prefs[x] = 1
                keyword_count += 1
            if is_prefnum_keyword(keyword):
                prefs[x] = int(keyword[10:len(keyword)-1])
                keyword_count += 1
    pref_max = 0
    for x in prefs:
        if prefs[x] > pref_max: pref_max = prefs[x]
    for x in classes_keywords:
        if x not in prefs:
            operator_count = len(x.split('.'))-1
            if x.split('.')[operator_count] in prefs:
                base_pref = prefs[x.split('.')[operator_count]]
            else:
                base_pref = pref_max+1
            prefs[x] = operator_count*(pref_max+1)+base_pref

    return prefs

def make_knowledge_graph(knowledge):
    knowledge_graph = {}
    for (c, Rel, x, y) in knowledge:
        if c != 'p': continue
        if Rel not in knowledge_graph: knowledge_graph[Rel] = {}
        if x not in knowledge_graph[Rel]: knowledge_graph[Rel][x] = set()
        if knowledge[(c, Rel, x, y)]: knowledge_graph[Rel][x].add(y)
    return knowledge_graph

def make_colored_graph(knowledge_graph, Rel, prefs, hidden_names, op):
    eq_graph = {}
    for x in knowledge_graph[Rel]:
        eq_graph[x] = set()
        for y in knowledge_graph[Rel]:
            if x == y: continue
            if x in knowledge_graph[Rel][y]:
                if y in knowledge_graph[Rel][x]:
                    eq_graph[x].add(y)
    (q, names) = equalities.union_find(eq_graph, prefs)
    pure_names = get_pure_names(names, hidden_names)
    table_names = get_pure_names(names, hidden_names)
    cocap_names = set()
    for x in pure_names:
        for y in pure_names:
            if x == y: continue
            if x == q[op['cocap'][y]]: cocap_names.add(x)
    for x in cocap_names: pure_names.remove(x)
    colored_graph = {}
    for x in pure_names:
        colored_graph[x] = {}
        for color in ['black', 'blue', 'green', 'red']:
            colored_graph[x][color] = set()
    for x in pure_names:
        for y in pure_names:
            if x == y: continue
            draw_edge = True
            if y not in knowledge_graph[Rel][op['cocap'][x]]: draw_edge = False
            for z in pure_names:
                if z == x or z == y: continue
                if z in knowledge_graph[Rel][op['cocap'][x]]:
                    if y in knowledge_graph[Rel][op['cocap'][z]]:
                        draw_edge = False
                if y in knowledge_graph[Rel][x]:
                    if z in knowledge_graph[Rel][x]:
                        if y in knowledge_graph[Rel][z]:
                            draw_edge = False
                    if z in knowledge_graph[Rel][op['co'][x]]:
                        if op['co'][y] in knowledge_graph[Rel][z]:
                            draw_edge = False
                elif op['co'][y] in knowledge_graph[Rel][x]:
                    if z in knowledge_graph[Rel][op['co'][x]]:
                        if y in knowledge_graph[Rel][z]:
                            draw_edge = False
                    if z in knowledge_graph[Rel][x]:
                        if op['co'][y] in knowledge_graph[Rel][z]:
                            draw_edge = False
            if draw_edge:
                if y in knowledge_graph[Rel][x]:
                    if y in knowledge_graph[Rel][op['co'][x]]:
                        edge_color = 'black'
                    else:
                        edge_color = 'blue'
                elif y in knowledge_graph[Rel][op['co'][x]]:
                    edge_color = 'red'
                else:
                    edge_color = 'green'
                colored_graph[x][edge_color].add(y)
    return (colored_graph, table_names)

def make_gradient_list(knowledge_graph, Rel, prefs, hidden_names, op,
                       knowledge, colored_graph):
    names_list = sorted(colored_graph[Rel].keys())
    gradient_list = []
    for i in range(len(names_list)):
        gradient_list.append([])
        for j in range(len(names_list)):
            clicked_name = names_list[i]
            colored_name = names_list[j]
            gradient = output.get_gradient(clicked_name, colored_name, Rel,
                                           knowledge, op)
            gradient_list[i].append(gradient)
    return gradient_list


def get_pure_names(names, hidden_names):
    '''Get the pure names from a set of names; that is, names which are not in
    the set of hidden names and that do not involve the use of operators.
    '''
    pure_names = set()
    for x in names:
        if x in hidden_names: continue
        if len(x.split('.')) > 1: continue
        pure_names.add(x)
    return pure_names

main()
