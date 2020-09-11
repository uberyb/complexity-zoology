color = {}
color['proven'] = '#00b712'
color['disproven'] = '#ff0000'
color['open'] = '#b2ac00'
color['unknown'] = '#848484'
color['unknown_provable'] = '#528452'
color['unknown_disprovable'] = '#845252'
color['selected'] = '#0076ff'
color['error'] = 'ff7b00'

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

    gradient_file = open('./gradients/gradients-' + world + '.txt', 'w')
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

worlds = ('A', 'E', 'AE', 'AA', 'R', 'T', 'E')
for W in worlds: make_svg_gradients(W)
