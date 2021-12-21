import txtdb
from txtdb import Null

from datetime import datetime

db = txtdb.open_database("./testdb")
persons = db["persons"]
messages = db["messages"]
like_counter = db["like_counter"]

person_c = {}
person_c["name"] = "JoeJoe"
person_c["age"] = 22

print("CREATE TABLES:")

result = persons.create_table()
assert result
result = persons.upsert_column("name", str, False, None)
assert result
result = persons.upsert_column("age", int, True, None)
assert result
result = persons.upsert_column("spin", int, False, None)
assert result

result = messages.create_table()
assert result
result = messages.upsert_column("when", date, False, None)
assert result
result = messages.upsert_column("content", str, False, None)
assert result

result = like_counter.create_table()
assert result
result = like_counter.upsert_column("count", int, False, 0)
assert result

result = persons.one_to_many(messages) # persons table gets a 'messages' column; messages table gets a 'persons' column.
# result = messages.many_to_one(persons)
assert result
result = like_counter.one_to_one(messages)
assert result

print("CREATE RECORD:")

new_record = persons.create(person_c)
print("  created record id `" + new_record.id + "` with a variant of `" + str(new_record.variant) + "`")

assert new_record.id != None
assert new_record.variant != None

print("READ:")

record = persons.read(new_record.id)
print("  read record `" + record.id + "` which has a `name` of \"" + record["name"] + "\"")

assert record != None
assert record.id == new_record.id
assert record["name"] == "JoeJoe"

print("UPDATE:")

record["name"] = "LarryLarry"
update_result = persons.update(record)
print("  updated record has a name of " + update_result["name"] + " and a variant of " + str(update_result.variant))

assert update_result != None
assert update_result.id == record.id
assert update_result["name"] == "LarryLarry"

print("DELETE:")

result_bool = persons.delete(record)

assert result_bool == True
print("  record was deleted")

print("CREATE MANY IN PREP FOR FIND TEST:")

person_c["age"] = 33
testlist = []
lastid = None
for n in range(10):
    person_c["name"] = "Smith" + str(n)
    person_c["spin"] = str(n)
    new_record = persons.create(person_c)
    testlist.append(new_record.id)
    print("  " + str(n) + ": " + new_record.id)
    lastid = new_record.id


print("FIND ALL 10:")

query = "age = 33"

found_list = persons.find(query)
print("  result:", found_list)

assert len(found_list) == 10

print("  found " + str(len(found_list)))

print("FIND 'spin' > 4:")

query = "spin>4"

found_list = persons.find(query)
print("  result:")
for found_id in found_list:
    found_record = persons.read(found_id)
    print("    "+found_record.id+" has spin="+found_record["spin"])
    if int(found_record["spin"]) > 4:
        print("      (GOOD)")
    else:
        print("      (ERR)")

assert len(found_list) == 5
assert lastid in found_list

print("DELETE TABLES:")

result = persons.delete_table()
assert result
result = messages.delete_table()
assert result
