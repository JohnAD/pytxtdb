# slone.py

import re
import itertools

def parse_parts(line):
    tabSpaceCnt = None
    name = None
    attr = None
    value = None
    two_part = re.findall('("[^"]*"|[_]) = ("[^"]*"|.)', line)
    print(two_part)
    if len(two_part) == 1:
        core = two_part[0]
        name = core[0]
        value = core[1]
        tabSpaceCnt = sum( 1 for _ in itertools.takewhile(str.isspace, line) )
    return (tabSpaceCnt, name, attr, value)


def deserialize_slone(doc_str):
    result = {}
    lines = doc_str.split("\n")
    for line in lines:
        (tabs, name, attr, value) = parse_parts(line)
        if tabs != None:
            if name.startswith('"'):
                name = name.strip('"')
            else:
                if name == "_":
                    name = None
                else:
                    print("err " + line)
            if value.startswith('"'):
                value = value.strip('"')
            else:
                if value == "?":
                    value = None
                elif value == "{":
                    value = {}
                else:
                    print("err " + line)
            result[name] = value
    return result