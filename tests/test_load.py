import txtdb
from txtdb import Null

db = txtdb.open_database("./testdb")
person_table = db["person_table"]

person_c = """#! SLONE 1.0
"name" = "JoeJoe"
"age" = "22"
"city" = "New York"
"sizes" = {
  _ = "4"
  _ = "8"
}
"""

print("CREATE:")

result = person_table.create(person_c)
print("  id generated:", result.id)

assert result.id != None

print("READ:")

record = person_table.read(result.id)
print("  record received had name:", record["name"])

assert record != None
assert record.id == result.id
assert record["name"] == "JoeJoe"

# print("UPDATE:")

# print("DELETE:")
