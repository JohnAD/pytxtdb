import txtdb
from txtdb import Null

db = txtdb.open_database("./testdb")
person_table = db["person_table"]

# person_c = """#! SLONE 1.0
# "name" = "JoeJoe"
# "age" = "22"
# "city" = "New York"
# "sizes" = "4,8"
# """

person_c = {}
person_c["name"] = "JoeJoe"
person_c["age"] = 22
person_c["city"] = "New York"
person_c["sizes"] = [4, 8]

print("CREATE:")

new_record = person_table.create(person_c)
print("  created record id `" + new_record.id + "`" + " and a variant of `" + str(new_record.variant) + "`")

assert new_record.id != None
assert new_record.variant != None

print("READ:")

record = person_table.read(new_record.id)
print("  read record `" + record.id + "` which has a `name` of \"" + record["name"] + "\"")

assert record != None
assert record.id == new_record.id
assert record["name"] == "JoeJoe"

print("UPDATE:")

record["name"] = "LarryLarry"
update_result = person_table.update(record)
print("  updated record has a name of " + update_result["name"] + " and a variant of " + str(update_result.variant))

assert update_result != None
assert update_result.id == record.id
assert update_result["name"] == "LarryLarry"

print("DELETE:")

result_bool = person_table.delete(record)

assert result_bool == True
print("  record was deleted")

print("CREATE MANY IN PREP FOR FIND TEST:")

person_c["age"] = 33
testlist = []
lastid = None
for n in range(10):
    person_c["name"] = "Smith" + str(n)
    person_c["spin"] = str(n)
    new_record = person_table.create(person_c)
    testlist.append(new_record.id)
    print("  " + str(n) + ": " + new_record.id)
    lastid = new_record.id


print("FIND ALL 10:")

query = "age = 33"

found_list = person_table.find(query)
print("  result:", found_list)

assert len(found_list) == 10

print("  found " + str(len(found_list)))

print("FIND 'spin' > 4:")

query = "spin>4"

found_list = person_table.find(query)
print("  result:")
for found_id in found_list:
    found_record = person_table.read(found_id)
    print("    "+found_record.id+" has spin="+found_record["spin"])
    if int(found_record["spin"]) > 4:
        print("      (GOOD)")
    else:
        print("      (ERR)")

assert len(found_list) == 5
assert lastid in found_list

print("WIPE ALL TESTS OUT:")

for id in testlist:
  result_bool = person_table.delete(id)
  print("  deleting", id, result_bool)
