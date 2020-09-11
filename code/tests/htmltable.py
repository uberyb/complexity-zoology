def eqtable(d):
    '''Create an HTML table from the dict d. It is expected that the keys of d
    are strings (preferred names) and the values are sets of strings (equivalent
    names).
    '''
    table = "<table>\n  <tr>\n    <th>Preferred Name</th>\n    " \
            + "<th>Alternate Names</th>\n  </tr>\n"

    for preferred_name in sorted(d.keys()):
        row = "  <tr>\n    <td>" + preferred_name + "</td>\n"
        alternate_names = ', '.join(sorted(d[preferred_name]))
        row += "    <td>" + alternate_names + "</td>\n  </tr>\n"
        table += row

    table += "</table>"

    return table

testdict = {
    'NAME1': set(['NAME2', 'NAME3']),
    'NAME4': set(['NAME5'])}
t = eqtable(testdict)
print(t)
