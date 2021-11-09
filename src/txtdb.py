from ctypes import *
import os, sys
from ulid import ULID

import libtxtdb

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

class TxtRecordMeta:
    def __init__(self):
        self.version = None

class TxtRecord:
    def __init__(self):
        self.id = None # nanoid.generate()
        self.data = {}
        self.slone = None
        self.meta = TxtRecordMeta()

    def __getitem__(self, field_name):
        if isinstance(field_name, str):
            if field_name in self.data:
                return self.data[field_name]
        return Nothing


class TxtTable:
    def __init__(self, db_ref, table_name):
        self.db_ref = db_ref
        self.table_dir = table_name

    def _fulldir(self):
        return os.path.join(self.db_ref.db_base_dir, self.table_dir)

    def create(self, record):
        result = TxtRecord()
        result.id = libtxtdb.create_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            record.encode("utf8")
        )
        return result

    def read(self, record_id):
        result = TxtRecord()
        result.id = record_id
        doc_str = libtxtdb.read_record(
            self.db_ref.db_base_dir.encode("utf8"), 
            self.table_dir.encode("utf8"), 
            str(record_id).encode("utf8")
        )
        if doc_str == "":
            return None
        return result


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

