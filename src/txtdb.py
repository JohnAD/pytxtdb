from ctypes import *
import os, sys
from ulid import ULID

import libtxtdb

from slone import deserialize_slone, serialize_slone

class __Null:
    def __str__(self):
        return "?"
    def __repr__(self):
        return "__Null"

Null = __Null()

class __Nothing:
    def __str__(self):
        return "_"
    def __repr__(self):
        return "__Nothing"

Nothing = __Nothing()

def interpret_dict_name(name):
    if name is None:
        return None
    elif isinstance(name, __Null):
        raise ValueError("A item name cannot be Null (aka 'unknown'). Technically, one cannot hash a value that isn't known yet. Perhaps v3.0 will import from a time-travel library.")
    elif isinstance(name, __Nothing):
        return None
    else:
        return str(name)

def interpret_dict_value(value):
    if value is None:
        return None
    elif isinstance(value, __Null):
        return None
    elif isinstance(value, __Nothing):
        return None # TODO: turn this into a `del x[name]` deletion
    elif isinstance(value, dict):
        return value
    else:
        return str(value) 

class TxtRecord:
    def __init__(self):
        self.id = None     # nanoid.generate()
        self.data = {}     # data is the source-of-truth, not slone
        self._slone = None
        self.variant = None

    def __getitem__(self, name):
        if isinstance(name, str):
            if name in self.data:
                return self.data[name]
        return Nothing

    def __setitem__(self, name, value):
        final_name = interpret_dict_name(name)
        final_value = interpret_dict_value(value)
        self.data[final_name] = final_value


class TxtTable:
    def __init__(self, db_ref, table_name):
        self.db_ref = db_ref
        self.table_dir = table_name

    def _fulldir(self):
        return os.path.join(self.db_ref.db_base_dir, self.table_dir)

    def _interpret_field_type(self, field_type):
        field_expression = None
        if isinstance(field_type, str):
            text_field_expression = field_type
        elif hasattr(field_type, "__name__"):
            type_name = field_type.__name__
            if type_name == 'int':
                field_expression = "INTEGER"
            elif type_name == 'str':
                field_expression = "TEXT"
            elif type_name == 'decimal':
                field_expression = "DECIMAL"
            elif type_name == 'datetime':
                field_expression = "DATETIME"
            elif type_name == 'bool':
                field_expression = "BOOLEAN"
        return field_expression

    def apply_table(self):
        result = libtxtdb.apply_table(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8")
        )
        record = deserialize_slone(result)

    def apply_column(self, column_name, column_type):
        field_expression = self._interpret_field_type(column_type)
        if field_expression == None:
            raise ValueError(f"The 'apply_column' function does not support that column_type ({column_type}).")
        result = libtxtdb.apply_column(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"),
            column_name.encode('utf8'),
            field_expression.encode('utf8')
        )
        record = deserialize_slone(result)

    def apply_joined_column(self, other_table):
        if not isinstance(other_table, TxtTable):
            raise ValueError("The 'apply_join' function only accepts other TxtTable for 'other_table'.")
        if self.db_ref != other_table.db_ref:
            raise ValueError("The other TxtTable must be part of the same database.")
        result = libtxtdb.apply_joined_column(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"),
            other_table.table_dir.encode("utf8")
        )
        record = deserialize_slone(result)

    def apply_index(self, index_name, field_name):
        result = libtxtdb.apply_index(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"),
            index_name.encode("utf8"),
            field_name.encode("utf8")
        )

    def create(self, record_data, record_id = None):
        slone = None
        if isinstance(record_data, str):
            record = deserialize_slone(record_data)
            if record_id:
                record["header"] = {}
                record["header"]["id"] = str(record_id)
            slone = serialize_slone(record)
        elif isinstance(record_data, dict):
            record = {}
            record["content"] = record_data
            record["header"] = {}
            if record_id:
                record["header"]["id"] = str(record_id)
            slone = serialize_slone(record)
        elif isinstance(record_data, TxtRecord):
            record = {}
            record["content"] = record_data.data
            record["header"] = {}
            if record_data.id:
                record["header"]["id"] = str(record_data.id)
            if record_id:
                record["header"]["id"] = str(record_id)
            slone = serialize_slone(record)
        else:
            raise ValueError("The 'create' function only accepts dictionaries, SLONE-formatted strings, or TxtRecord objects.")
        #
        doc_str = libtxtdb.create_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            slone.encode("utf8")
        )
        #
        if doc_str.startswith("ERR"):
            raise IOError(doc_str)
        record = deserialize_slone(doc_str)
        result = TxtRecord()
        result.id = record["header"]["id"]
        result.variant = record["header"]["variant"]
        result._slone = doc_str
        result.data = record["content"]
        return result

    def read(self, record):
        recordid = None
        if isinstance(record, TxtRecord):
            recordid = record.id
        elif isinstance(record, str):
            recordid = record
        else:
            raise ValueError("The 'update' function only accepts TxtRecord objects or recordid strings.")
        #
        doc_str = libtxtdb.read_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            str(recordid).encode("utf8")
        )
        #
        if doc_str.startswith("ERR"):
            raise IOError(doc_str)
        record = deserialize_slone(doc_str)
        result = TxtRecord()
        result.id = record["header"]["id"]
        result.variant = record["header"]["variant"]
        result._slone = doc_str
        result.data = record["content"]
        return result

    def update(self, record):
        result = TxtRecord()
        if isinstance(record, TxtRecord):
            result.data = record.data
            temp = {}
            temp["header"] = {}
            temp["header"]["id"] = record.id
            temp["content"] = record.data
            result._slone = serialize_slone(temp)
        else:
            raise ValueError("The 'update' function only accepts TxtRecord objects.")
        #
        doc_str = libtxtdb.update_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            result._slone.encode("utf8")
        )
        #
        if doc_str.startswith("ERR"):
            raise IOError(doc_str)
        temp = deserialize_slone(doc_str)
        result.id = temp["header"]["id"]
        result.variant = temp["header"]["variant"]
        result._slone = doc_str
        result.data = temp["content"]
        return result

    def delete(self, record):
        recordid = None
        if isinstance(record, TxtRecord):
            recordid = record.id
        elif isinstance(record, str):
            recordid = record
        else:
            raise ValueError("The 'update' function only accepts TxtRecord objects or recordid strings.")
        #
        doc_str = libtxtdb.delete_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            recordid.encode("utf8")
        )
        if doc_str.startswith("ERR"):
            raise IOError(doc_str)
        if doc_str == "true":
            return True
        return False

    def find(self, query, order=None, limit=100):
        queryString = None
        orderString = None
        limitInt = None
        if isinstance(query, str):
            queryString = query
        else:
            raise ValueError("The 'find' function only accepts strings for the query.")
        if isinstance(order, str):
            orderString = order
        elif order is None:
            orderString = ""
        else:
            raise ValueError("The 'find' function only accepts strings (or None) for the order.")
        if isinstance(limit, int):
            limitInt = limit
        else:
            raise ValueError("The 'find' function only accept integers for the limit.")
        #
        found_ids_str = libtxtdb.find_records(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            queryString.encode("utf8"),
            orderString.encode("utf8"),
            limit
        )
        if found_ids_str.startswith("ERR"):
            raise IOError(found_ids_str)
        found_ids = found_ids_str.split() # split by whitespace
        return found_ids


class TxtDB:
    def __init__(self, db_base_dir=None):
        if db_base_dir == None:
            self.db_base_dir = "."
        else:
            self.db_base_dir = db_base_dir
            if not os.path.exists(self.db_base_dir):
                os.makedirs(self.db_base_dir)

    def __getitem__(self, table_name):
        new_table = TxtTable(self, table_name)
        needed_path = new_table._fulldir()
        if not os.path.exists(needed_path):
            os.makedirs(needed_path)
        return new_table

def open_database(db_base_dir=None):
    return TxtDB(db_base_dir)

