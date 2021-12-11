# slone.py

import re
import itertools

def parse_parts(line):
    # TODO: handle lots of other forms. This will do for MVP.
    tabSpaceCnt = None
    name = None
    attr = None
    value = None
    two_part = re.findall('("[^"]*"|[_]) = ("[^"]*"|.)', line)
    # print(two_part)
    if len(two_part) == 1:
        core = two_part[0]
        name = core[0]
        value = core[1]
        tabSpaceCnt = sum( 1 for _ in itertools.takewhile(str.isspace, line) )
    return (tabSpaceCnt, name, attr, value)


def deserialize_slone(doc_str):
    result = {}
    lines = doc_str.split("\n")
    ptr = [result]
    for line in lines:
        (tab, name, attr, value) = parse_parts(line)
        new_object = False
        if tab != None:
            level = int(tab/2)
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
                    new_object = True
                else:
                    print("err " + line)
            ptr[level][name] = value
            if new_object:
                if len(ptr) == (level + 1):
                    ptr.append(ptr[level][name])
                else:
                    ptr[level + 1] = ptr[level][name]
    return result


def _serialize(doc, level):
    result = ""
    for key in doc:
        # indent
        result += " " * (level * 2)
        # name
        result += '"' + key + '" '
        # equals
        result += "= "
        # value
        value = doc[key]
        if isinstance(value, dict):
            result += "{\n"
            result += _serialize(value, level + 1)
            result += " " * (level * 2)
            result += "}\n"
        elif value is None:
            result += "?\n"
        else:
            result += '"' + str(value) + '"\n'
    return result


def serialize_slone(doc):
    result = "#! SLONE 1.0\n"
    result += _serialize(doc, 0)
    return result
