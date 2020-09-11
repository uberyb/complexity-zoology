import subprocess, shutil
from code import ops

color = {}
color['proven'] = '#00b712'
color['disproven'] = '#ff0000'
color['open'] = '#b2ac00'
color['unknown'] = '#848484'
color['unknown_provable'] = '#528452'
color['unknown_disprovable'] = '#845252'
color['selected'] = '#0076ff'
color['error'] = '#ff7b00'

def get_possible_gradients():
    possibilities = []
    statuses = ('D', 'P', 'O', 'U', 'V', 'W')

    for L in statuses:
        for M in statuses:
            for R in statuses:
                is_possible = True
                if (L == 'P' or R == 'P') and M != 'P': is_possible = False
                if M == 'D' and (L != 'D' or R != 'D'): is_possible = False
                if L in ('O', 'V') or M in ('O', 'V'):
                    if M not in ('O', 'P', 'V'): is_possible = False
                if M in ('O', 'W'):
                    if L not in ('D', 'O', 'W') or R not in ('D', 'O', 'W'):
                        is_possible = False
                if is_possible: possibilities.append(L+M+R)

    return possibilities

def make_svg_gradients(world):
    global color

    meaning = {'D':'disproven', 'P':'proven', 'O':'open', 'U':'unknown',
               'V':'unknown_provable', 'W':'unknown_disprovable'}
    col = {}
    for A in meaning:
        col[A] = color[meaning[A]]
    
    possibilities = get_possible_gradients()

    gradient_file = open('./code/helpers/gradients-' + world + '.txt', 'w')
    gradient_file.write('<defs>\n')

    gradient = '<linearGradient id="' + world + '_Sel">'
    gradient += '<stop offset="100%" stop-color="' + color['selected'] + '" />'
    gradient += '</linearGradient>\n'
    gradient_file.write(gradient)
    gradient = '<linearGradient id="' + world + '_Err">'
    gradient += '<stop offset="100%" stop-color="' + color['error'] + '" />'
    gradient += '</linearGradient>\n'
    gradient_file.write(gradient)
    
    for triple in possibilities:
        L = triple[0]
        M = triple[1]
        R = triple[2]
        if L == M and M == R:
            gradient = '<linearGradient id="' + world + '_' + L + M + R + '">'
            gradient += '<stop offset="100%" stop-color="' + col[L] + '" />'
            gradient += '</linearGradient>\n'
            gradient_file.write(gradient)
        elif L == 'P' or R == 'P':
            gradient = '<linearGradient id="' + world + '_' + L + M + R + '">'
            gradient += '<stop offset="49%" stop-color="' + col[L] + '" />'
            gradient += '<stop offset="50%" stop-color="' + col[R] + '" />'
            gradient += '<stop offset="51%" stop-color="' + col[R] + '" />'
            gradient += '</linearGradient>\n'
            gradient_file.write(gradient)
        else:
            gradient = '<linearGradient id="' + world + '_' + L + M + R + '">'
            gradient += '<stop offset="33%" stop-color="' + col[L] + '" />'
            gradient += '<stop offset="34%" stop-color="' + col[M] + '" />'
            gradient += '<stop offset="66%" stop-color="' + col[M] + '" />'
            gradient += '<stop offset="67%" stop-color="' + col[R] + '" />'
            gradient += '</linearGradient>\n'
            gradient_file.write(gradient)

    gradient_file.write('</defs>')
    gradient_file.close()

# Remove any text of the form <title>...</title> from the input string. Return
# the new string, along with the contents of the title element.
def extract_title_element(s):
    if len(s) < 15: return (s, '')
    new_string = s
    contents = ''
    left_index = 0
    right_index = 0
    for i in range(len(s)-15):
        if s[i:i+7] == '<title>':
            left_index = i
            break
    for i in range(len(s)-8):
        if s[i:i+8] == '</title>': right_index = i
    if left_index < right_index:
        new_string = s[0:left_index]+s[right_index+8:len(s)]
        contents = s[left_index+7:right_index]
    return (new_string, contents)

# If the string s has the form <g...>..., output a string of the form
# <g... num="t">... . If s does not have this form, then return s.
# def add_num_attribute(s, t):
#     if s[0:2] != '<g': return s
#     right_index = 0
#     for i in range(len(s)):
#         if s[i] == '>':
#             right_index = i
#             break
#     if right_index == 0: return s
#     new_string = s[0:right_index] + ' num="' + t + '"'  + s[right_index:len(s)]
#     return new_string

# Return 'P' if x < y is proven, 'D' if it is disproven, and 'O' if it is open.
# Otherwise, return U.
def get_status_character(x, y, Rel, knowledge):
    if x == y: return 'P'
    if knowledge[('p', Rel, x, y)]: return 'P'
    if knowledge[('d', Rel, x, y)]: return 'D'
    if knowledge[('-p', Rel, x, y)] and knowledge[('-d', Rel, x, y)]:
        return 'O'
    if knowledge[('-d', Rel, x, y)]:
        return 'V'
    if knowledge[('-p', Rel, x, y)]:
        return 'W'
    return 'U'

def get_gradient(x, y, Rel, knowledge, op):
    '''Pick the correct gradient name for the y bubble, given that x has been
    clicked.
    '''
    if x == y: return Rel + "_Sel"

    a = get_status_character(x, y, Rel, knowledge)
    b = get_status_character(op['cocap'][x], y, Rel, knowledge)
    c = get_status_character(op['co'][x], y, Rel, knowledge)
    s = a + b + c

    possibilities = get_possible_gradients()

    if s not in possibilities: return "Err"

    return Rel + "_" + s

def isdimline(s):
    '''Check whether a string has the form <svg width="..." height="..." ...
    '''
    quote_indices=[]
    for i in range(len(s)):
        if s[i] == '"': quote_indices.append(i)
    if len(quote_indices) < 4: return False
    if s[0:quote_indices[0]] != "<svg width=": return False
    if s[quote_indices[1]-2:quote_indices[2]] != "pt\" height=": return False
    if s[quote_indices[3]-2:quote_indices[3]] != "pt": False
    m = s[quote_indices[0]+1:quote_indices[1]-2]
    n = s[quote_indices[2]+1:quote_indices[3]-2]
    if (not str.isdigit(m)) or (not str.isdigit(n)): return False
    return True

def getdimensions(s):
    '''Get the dimensions of the SVG object from the relevant line.
    '''
    q = []
    for ind in range(len(s)):
        if len(q) == 4: break
        if s[ind] == '"': q.append(ind)
    i = q[0]+1
    j = q[1]-2
    k = q[2]+1
    l = q[3]-2
    m = int(s[i:j])
    n = int(s[k:l])
    return (m,n)

def getstrend(s):
    '''Extract the end of the line specifying the dimensions of the SVG file.
    '''
    ctr = 0
    i = 0
    while ctr < 4:
        if s[i] == '"': ctr += 1
        i += 1
    return s[i:len(s)]

def writenewdims(M, N, s):
    '''Returns the line that will specify the dimensions of the SVG object in
    the new SVG file.
    '''
    t = "<svg width=\""
    t += str(M)
    t += "pt\" height=\""
    t += str(N)
    t += "pt\""
    t += s
    return t

def eqtable(d):
    '''Create an HTML table from the dict d. It is expected that the keys of d
    are strings (preferred names) and the values are sets of strings (equivalent
    names).
    '''
    table = "    <table>\n      <tr>\n        <th>Preferred Name</th>\n    " \
            + "    <th>Alternate Names</th>\n      </tr>\n    "

    for preferred_name in sorted(d.keys()):
        row = "  <tr>\n        <td>" + preferred_name + "</td>\n    "
        alternate_names = ', '.join(sorted(d[preferred_name]))
        row += "    <td>" + alternate_names + "</td>\n      </tr>\n    "
        table += row

    table += "</table>"

    return table

def make_world_diagram(classes_keywords, knowledge, q, op, classes, Rel, Dual,
                       colored_graph, table_names):
    '''Create SVG file for the specified world.
    '''

    dot_filename = './code/helpers/output_' + Rel + '.dot'
    svg_filename = './code/helpers/outgraph_' + Rel + '.svg'
    gradient_filename = './code/helpers/gradients-' + Rel + '.txt'
    svg_copy_filename = './code/helpers/outgraph_original_' + Rel + '.svg'

    outfile = open(dot_filename, 'w')
    outfile.write('digraph G {')
    outfile.write('\n    bgcolor=white;')
    outfile.write('\n    rankdir=BT;')
    outfile.write('\n    node [color=black,fontcolor=black];')

    hidden_classes = set()
    for x in classes_keywords:
        if 'hide' in classes_keywords[x]: hidden_classes.add(q[x])

    graph_names = sorted(colored_graph.keys())
    graph_names_index = 1
    graph_numbering = {}
    for x in graph_names:
        s = '\n    ' + str(graph_names_index) + ' [label=\"' + x + '\",id=\"'
        s += Rel +'node' + str(graph_names_index) + '\"];'
        outfile.write(s)
        graph_numbering[x] = graph_names_index
        graph_names_index += 1

    table_dict = {}
    for x in table_names:
        table_dict[x] = set()
        for y in classes:
            if y in hidden_classes or len(y.split('.')) > 1: continue
            if x == y: continue
            if q[x] == q[y]:
                table_dict[x].add(y)
                continue
            if knowledge[('p', Dual, q[x], q[y])]:
                if knowledge[('p', Dual, q[y], q[x])]: table_dict[x].add(y)
    empty_table_entries = set()
    for x in table_dict:
        if not table_dict[x]: empty_table_entries.add(x)
    for x in empty_table_entries:
        table_dict.pop(x)

    for x in colored_graph:
        for color in ['black', 'blue', 'red', 'green']:
            for y in colored_graph[x][color]:
                s = '\n    ' + str(graph_numbering[x]) + ' -> '
                s += str(graph_numbering[y]) + ' [color=' + color + '];'
                outfile.write(s)

    outfile.write('\n}')
    outfile.close()

    subprocess.call(['dot', '-Tsvg', dot_filename, '-o', svg_filename])

    gradient_file = open(gradient_filename)
    gradients = []
    for line in gradient_file: gradients.append(line)
    gradient_file.close()

    svgfile = open(svg_filename)
    newsvg = []

    areafactor = 0.65
    nonewdims = True

    for line in svgfile:
        new_line = line
        if new_line[0:13] == '<g id="graph0':
            line_start = '<g id="graph' + Rel
            line_end = new_line[13:len(new_line)]
            new_line = line_start + line_end
        if nonewdims:
            # rewrite dimensions if needed
            if isdimline(new_line):
                (m,n) = getdimensions(new_line)
                end = getstrend(new_line)
                new_line = writenewdims(m*areafactor, n*areafactor,  end)
                nonewdims = False
        if new_line: newsvg.append(new_line)
        if new_line[0:12] == '<g id="graph': newsvg += gradients

    svgfile.close()

    shutil.copy(svg_filename, svg_copy_filename)
    svgfile = open(svg_filename, 'w')
    svgfile.writelines(newsvg)
    svgfile.close()

    return table_dict

def make_table(a):
    '''Use an array to generate a text-based table. The input array, a, is a
    two-dimensional list of strings with the number of rows equal to the
    number of columns.
    '''
    n = len(a)

    # determine the width of each column
    column_width = []
    for j in range(n):
        max_string_length = 0
        for i in range(n):
            max_string_length = max(max_string_length, len(a[i][j]))
        current_column_width = max(3, max_string_length+2)
        column_width.append(current_column_width)

    # make a new array with spaces on the ends of each string
    b = []
    for i in range(n):
        b.append([])
        for j in range(n):
            if j == 0:
                appended_spaces = column_width[j]-len(a[i][j])
                b_value = a[i][j] + (' '*appended_spaces)
            else:
                initial_spaces = column_width[j]-len(a[i][j])-1
                b_value = (' '*initial_spaces) + a[i][j] + ' '
            b[i].append(b_value)

    rows = []
    for i in range(n): rows.append(''.join(b[i]))
    second_row = ''
    for j in range(n): second_row += '-'*column_width[j]
    second_row = second_row[0:len(second_row)-1] + ' '
    rows.insert(1, second_row)

    table = '\n'.join(rows)

    return table

def generate_progress_report(extremal_unknowns, status_table):
    extr_file = open('./progress.txt', 'w')

    extr_file.write('+'*21)
    extr_file.write(' COMPLEXITY ZOOLOGY - PROGRESS REPORT ')
    extr_file.write('+'*21)
    extr_file.write('\n\n')
    extr_file.write('Knowledge Status Table\n')
    extr_file.write('='*22)
    extr_file.write('\n\n')

    table_array = [['World:', 'P', 'D', 'O', '?p', '?d', '?u']]
    table_array += [['All oracles', str(status_table['A']['P']),
                    str(status_table['A']['D']), str(status_table['A']['O']),
                    str(status_table['A']['?p']), str(status_table['A']['?d']),
                    str(status_table['A']['??'])]]
    table_array += [['All algebraic oracles', str(status_table['AA']['P']),
                     str(status_table['AA']['D']),
                     str(status_table['AA']['O']),
                     str(status_table['AA']['?p']),
                     str(status_table['AA']['?d']),
                     str(status_table['AA']['??'])]]
    table_array += [['Some algebraic oracle', str(status_table['EA']['P']),
                    str(status_table['EA']['D']), str(status_table['EA']['O']),
                    str(status_table['EA']['?p']),
                    str(status_table['EA']['?d']),
                    str(status_table['EA']['??'])]]
    table_array += [['Random oracle', str(status_table['R']['P']),
                     str(status_table['R']['D']), str(status_table['R']['O']),
                     str(status_table['R']['?p']),
                     str(status_table['R']['?d']),
                     str(status_table['R']['??'])]]
    table_array += [['Trivial oracle', str(status_table['T']['P']),
                     str(status_table['T']['D']), str(status_table['T']['O']),
                     str(status_table['T']['?p']),
                     str(status_table['T']['?d']),
                     str(status_table['T']['??'])]]
    table_array += [['Some oracle', str(status_table['E']['P']),
                     str(status_table['E']['D']), str(status_table['E']['O']),
                     str(status_table['E']['?p']),
                     str(status_table['E']['?d']),
                     str(status_table['E']['??'])]]

    table = make_table(table_array)
    extr_file.write(table)

    extr_file.write('\n\nKEY: ')
    extr_file.write('''P - proven
     D - disproven
     O - open
     ?p - unknown (provable)
     ?d - unknown (disprovable)
     ?u - unknown (no data)''')

    extr_file.write('\n\nExtremal Unknowns\n')
    extr_file.write('=================\n\n')

    world_names = [('A', 'all oracles', '<?'),
                   ('AA', 'algebraic oracles', 'a<?'),
                   ('EA', 'some algebraic oracle', 'x<?'),
                   ('R', 'random oracle', 'r<?'),
                   ('T', 'trivial oracle', 't<?'),
                   ('E', 'some oracle', 'o<?')]

    state_abbreviation = {'blank' : 'u', 'provable': 'p', 'disprovable': 'd'}

    for (Rel, world, base_relsym) in world_names:
        heading = 'Most likely - ' + world
        extr_file.write(heading + '\n')
        extr_file.write('-' * len(heading))
        extr_file.write('\n\n')
        for (x, y, state) in extremal_unknowns[Rel]['likely']:
            relsym = base_relsym + state_abbreviation[state]
            extr_file.write(x + ' ' + relsym + ' ' + y + '\n')
        extr_file.write('\n')
        heading = 'Least likely - ' + world
        extr_file.write(heading + '\n')
        extr_file.write('-' * len(heading))
        extr_file.write('\n\n')
        for (x, y, state) in extremal_unknowns[Rel]['unlikely']:
            relsym = base_relsym + state_abbreviation[state]
            extr_file.write(x + ' ' + relsym + ' ' + y + '\n')
        extr_file.write('\n')
    extr_file.close()

def main(classes_keywords, knowledge, q, redundancies, names, op, classes, tclosure, props, Hasse, colored_graph, gradient_list, table_names):

    relation_pairs = [('A', 'A'), ('AA', 'AA'), ('EA', 'AA'), ('R', 'R'),
                      ('T', 'T'), ('E', 'A')]
    table_dict ={}
    table = {}
    for (Rel, Dual) in relation_pairs:
        make_svg_gradients(Rel)
        table_dict[Rel] = make_world_diagram(classes_keywords, knowledge, q,
                                             op, classes, Rel, Dual,
                                             colored_graph[Rel],
                                             table_names[Rel])

        table[Rel] = eqtable(table_dict[Rel])


    redfile = open('./redundancies.txt', 'w')
    redfile.write('Upper bound for redundant inclusions:\n\n')

    for x in props['<']:
        for y in props['<'][x]:
            if q[y] not in Hasse[q[x]]:
                redfile.write(x + ' < ' + y + '\n')

    redfile.write('\nRedundant initial formulas:\n\n')
    redfile.write('\n'.join(redundancies))

    redfile.close()

    htmlfile = open('./outgraph.html', 'w')

    htmlfile.write("""<html>
    <head>
    <style>
    body.dark-mode {
      filter: invert(100%) hue-rotate(180deg);
      background-color: black
    }
    body.light-mode {
      filter: invert(0%);
      background-color: white
    }
    table, th, td {
        border: 2px solid black;
    }
    th {
        text-align: left;
    }
    td {
        border: 1px solid black;
    }

    text {
        cursor: pointer;
    }
    .tabcontent {
        display: none;
    }
    </style>
    <script>

    var coloring_A = [""")

    for i in range(len(gradient_list['A'])):
        htmlfile.write('["' + '", "'.join(gradient_list['A'][i]) + '"]')
        if i != len(gradient_list['A'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')
    htmlfile.write('var coloring_AA = [')
    for i in range(len(gradient_list['AA'])):
        htmlfile.write('["' + '", "'.join(gradient_list['AA'][i]) + '"]')
        if i != len(gradient_list['AA'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')
    htmlfile.write('var coloring_EA = [')
    for i in range(len(gradient_list['EA'])):
        htmlfile.write('["' + '", "'.join(gradient_list['EA'][i]) + '"]')
        if i != len(gradient_list['EA'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')
    htmlfile.write('var coloring_R = [')
    for i in range(len(gradient_list['R'])):
        htmlfile.write('["' + '", "'.join(gradient_list['R'][i]) + '"]')
        if i != len(gradient_list['R'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')
    htmlfile.write('var coloring_T = [')
    for i in range(len(gradient_list['T'])):
        htmlfile.write('["' + '", "'.join(gradient_list['T'][i]) + '"]')
        if i != len(gradient_list['T'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')
    htmlfile.write('var coloring_E = [')
    for i in range(len(gradient_list['E'])):
        htmlfile.write('["' + '", "'.join(gradient_list['E'][i]) + '"]')
        if i != len(gradient_list['E'])-1:
            htmlfile.write(',\n                ')
    htmlfile.write('];\n\n')

    htmlfile.write("""window.onload = init;

    function init() {

        var ellipses = document.getElementsByTagName("ellipse");

        for(var i=0; i < ellipses.length; i++)
            ellipses[i].parentNode.addEventListener("click", colorNode, true);

        }

    function colorNode(event) {

	var current_graph = event.currentTarget.parentNode.id;
	var all_ellipses = document.getElementsByTagName("ellipse");
	var ellipses = [];
	for(var i=0; i < all_ellipses.length; i++) {
	    if(all_ellipses[i].parentNode.parentNode.id == current_graph)
		ellipses[ellipses.length] = all_ellipses[i];
	}
	var coloring;
	if (current_graph == 'graphA') {
	    coloring = coloring_A;
	} else if (current_graph == 'graphAA') {
            coloring = coloring_AA;
        } else if (current_graph == 'graphEA') {
            coloring = coloring_EA;
	} else if (current_graph == 'graphR') {
	    coloring = coloring_R;
	} else if (current_graph == 'graphT') {
	    coloring = coloring_T;
	} else {
            coloring = coloring_E;
        }

        var iA = getNodeNumber(event.currentTarget.getAttribute("id"));

        for(var i=0; i < ellipses.length; i++) {
    	    var iB = getNodeNumber(ellipses[i].parentNode.getAttribute("id"));
            var fillValue = "url(#".concat(coloring[iA-1][iB-1], ")");
            ellipses[i].setAttribute("fill", fillValue)
            }

    }

    function toggleTheme() {
        var x = document.getElementById("docbody");
        if (x.className == "light-mode") {
          x.className = "dark-mode";
        }
        else {
          x.className = "light-mode";
        }
    }

    function openWorld(event, world_name) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i=0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i=0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(world_name).style.display = "block";
        event.currentTarget.className += " active";
    }

    function getNodeNumber(s) {
        var i = -1;
        for (j=0; j<s.length-4 && i==-1; j++) {
            if (s.substring(j,j+4) == "node") {
                i=j+4;
            }
        }
        var number = parseInt(s.substring(i));
        return number;
    }

    </script>

    </head>

    <body id="docbody" class="light-mode">

    <h1>Output Graph</h1>

    <button type="button" name="theme" onclick="toggleTheme()" >Toggle light/dark
    </button>

    <p>The arrows are interpreted as follows:</p>

    <ul style="list-style-type:none">
    <li>A <span style="color:black">&rarr;</span> B: A &sube; B and co(A) &sube; B
    for every oracle.</li>

    <li>A <span style="color:blue">&rarr;</span> B: A &sube; B for every oracle.
    </li>

    <li>A <span style="color:red">&rarr;</span> B: co(A) &sube; B for every oracle.
    </li>

    <li>A <span style="color:green">&rarr;</span> B: cocap(A) &sube; B for every
    oracle.</li>
    </ul>

    <p> Click on a node to compare it to other complexity classes. Clicking a node
    marks it as A, and the coloring of each node shows the status of the
    corresponding class when it is considered as B. The left part of the node shows
    the status of A &sube; B, the right part of the node shows the status of co(A)
    &sube; B, and the middle part of the node shows the status of cocap(A) &sube; B
    (all with respect to every oracle). </p>

    <p> The colors are interpreted as follows: </p>

    <ul>
    <li style="color:""")
    htmlfile.write(color["proven"])
    htmlfile.write("""">Proven</li>
    <li style="color:""")
    htmlfile.write(color["disproven"])
    htmlfile.write("""">Disproven</li>
    <li style="color:""")
    htmlfile.write(color["open"])
    htmlfile.write("""">Open</li>
    <li style="color:""")
    htmlfile.write(color["unknown"])
    htmlfile.write("""">Unknown to the system</li>
    <li style="color:""")
    htmlfile.write(color["unknown_provable"])
    htmlfile.write("""">Unknown to the system (but not disproven)</li>
    <li style="color:""")
    htmlfile.write(color["unknown_disprovable"])
    htmlfile.write("""">Unknown to the system (but not proven)</li>
    <li style="color:""")
    htmlfile.write(color["selected"])
    htmlfile.write("""">Currently selected</li>
    <li style="color:""")
    htmlfile.write(color["error"])
    htmlfile.write("""">Error: the status of this class is logically
    impossible</li>
    </ul>

    <div class="tab">
    <button class="tablinks" onclick="openWorld(event, \'AllOracles\')">
    All Oracles
    </button>
    <button class="tablinks" onclick="openWorld(event, \'AlgebraicOracles\')">
    All Algebraic Oracles
    </button>
    <button class="tablinks" onclick="openWorld(event, \'SomeAlgebraic\')">
    Some Algebraic Oracle
    </button>
    <button class="tablinks" onclick="openWorld(event, \'RandomOracle\')">
    Random Oracle
    </button>
    <button class="tablinks" onclick="openWorld(event, \'TrivialOracle\')">
    Trivial Oracle
    </button>
    <button class="tablinks" onclick="openWorld(event, \'SomeOracle\')">
    Some Oracle
    </button>
    </div>

    """)

    htmlfile.write('<div id="AllOracles" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_A.svg')
    for line in svgfile: htmlfile.write('    ' + line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['A'])
    htmlfile.write('\n</div>\n')

    htmlfile.write('<div id="AlgebraicOracles" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_AA.svg')
    for line in svgfile: htmlfile.write('    ' + line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['AA'])
    htmlfile.write('\n</div>\n')

    htmlfile.write('<div id="SomeAlgebraic" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_EA.svg')
    for line in svgfile: htmlfile.write('    ' + line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['EA'])
    htmlfile.write('\n</div>\n')

    htmlfile.write('<div id="RandomOracle" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_R.svg')
    for line in svgfile: htmlfile.write('    '+ line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['R'])
    htmlfile.write('\n</div>\n')

    htmlfile.write('<div id="TrivialOracle" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_T.svg')
    for line in svgfile: htmlfile.write('    ' + line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['T'])
    htmlfile.write('\n</div>\n')

    htmlfile.write('<div id="SomeOracle" class="tabcontent">\n')
    svgfile = open('./code/helpers/outgraph_E.svg')
    for line in svgfile: htmlfile.write('    ' + line)
    svgfile.close()

    htmlfile.write("\n<br/>\n<br/>\n")
    htmlfile.write(table['E'])
    htmlfile.write('\n</div>\n')

    htmlfile.write("""</body>
    </html>""")

    htmlfile.close()
