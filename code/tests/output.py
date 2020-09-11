# Given a graph G, the Hasse relation H of its quotient graph, and the quotient
# map q, find the relations in G that are not Hasse in the quotient.
def redundancies(G, H, q):
    R = {}

    for v in G:
        R[v] = set()
        for w in G[v]:
            if q[w] in H[q[v]] or q[v] == q[w]: continue
            R[v].add(w)
    return R

# Record the results of the computation as a text file. f is the already loaded
# output file, G is the initial input graph, S is the set of preferred and
# standalone classes, q is the quotient map, and C is the transitive closure.
def write_results(outfile, G, S, q, C):
    for i in range(len(G)):
        for v in S:
            if q[v] != i: continue

            # write a header for the current class
            outfile.write('-'*(len(v)+1) + '\n')
            outfile.write(v + '\n')
            outfile.write('-'*(len(v)+1) + '\n')
            outfile.write('\n')

            # print equal classes for v
            equal_list = []
            equal_classes = False
            for w in G:
                if q[v] == q[w] and v != w:
                    equal_classes = True
                    equal_list.append(w)
            equal_string = v + ' = ' + ','.join(equal_list) + '\n'
            if equal_classes == True: outfile.write(equal_string)

            # print classes contained in v
            greater_than_list = []
            greater_than_classes = False
            for w in G:
                if q[v] in C[q[w]]:
                    greater_than_classes = True
                    greater_than_list.append(w)
            greater_than_string = v + ' > ' + ','.join(greater_than_list) + '\n'
            if greater_than_classes == True: outfile.write(greater_than_string)

            # print classes containing  v
            less_than_list = []
            less_than_classes = False
            for w in G:
                if q[w] in C[q[v]]:
                    less_than_classes = True
                    less_than_list.append(w)
            less_than_string = v + ' < ' + ','.join(less_than_list) + '\n'
            if less_than_classes == True: outfile.write(less_than_string)

            outfile.write('\n')

# Write out all redundant input. outfile is the output file, and R is the graph
# of redundant input.
def write_redundancies(outfile, R):
    existredundancies = False
    for v in R:
        for w in R[v]:
            if existredundancies == False:
                outfile.write('================\n')
                outfile.write('REDUNDANT INPUT:\n')
                outfile.write('================\n\n')
                existredundancies = True
            outfile.write(v + ' < ' + w + '\n')

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
def add_num_attribute(s, t):
    if s[0:2] != '<g': return s
    right_index = 0
    for i in range(len(s)):
        if s[i] == '>':
            right_index = i
            break
    if right_index == 0: return s
    new_string = s[0:right_index] + ' num="' + t + '"'  + s[right_index:len(s)]
    return new_string

# Return 'P' if x < y is proven, 'D' if it is disproven, and 'O' if it is open.
# Otherwise, return U.
def get_status_character(x, y, knowledge):
    if x == y: return 'P'
    if knowledge[('p', 'A', x, y)]: return 'P'
    if knowledge[('d', 'A', x, y)]: return 'D'
    if knowledge[('-p', 'A', x, y)] and knowledge[('-d', 'A', x, y)]:
        return 'O'
    return 'U'

# Pick the correct gradient name for the y bubble, given that x has been
# clicked.
def get_gradient(x, y, knowledge, op):
    if x == y: return "Sel"

    a = get_status_character(x, y, knowledge)
    b = get_status_character(op['cocap'][x], y, knowledge)
    c = get_status_character(op['co'][x], y, knowledge)
    s = a + b + c

    possibilities = ['PPP', 'PPD', 'PPO', 'PPU', 'DPP', 'DPD', 'DDD', 'DOD',
                     'DUD', 'DPO', 'DOO', 'DUO', 'DPU', 'DOU', 'DUU', 'OPP',
                     'OPD', 'OOD', 'OUD', 'OPO', 'OOO', 'OUO', 'OPU', 'OOU',
                     'OUU', 'UPP', 'UPD', 'UOD', 'UUD', 'UPO', 'UOO', 'UUO',
                     'UPU', 'UOU', 'UUU']

    if s not in possibilities: return "Err"

    return s

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
    while ctr < 3:
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
