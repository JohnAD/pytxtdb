import txtdb

db = txtdb.open_database("./testdb")
person_table = db["person_table"]

person_c = """SLONE 1.0
"name" = "JoeJoe"
"age" = "22"
"city" = "New York"
"sizes" = {
  _ = "4"
  _ = "8" 
}
"""

result = person_table.create(person_c)

assert result.id != None

print("id generated = ", result.id)
