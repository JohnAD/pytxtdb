from ctypes import *
import os, sys
from ulid import ULID

# dir = os.path.dirname(sys.modules["libtxtdb"].__file__)
# if sys.platform == "win32":
#     libName = "libtxtdb.dll"
# elif sys.platform == "darwin":
#     libName = "libtxtdb.dylib"
# else:
#     libName = "libtxtdb.so"
# dll = cdll.LoadLibrary(os.path.join(dir, libName))

import libtxtdb

class TxtRecordMeta:
    def __init__(self):
        self.version = None

class TxtRecord:
    def __init__(self):
        self.id = None # nanoid.generate()
        self.data = {}
        self.slone = None
        self.meta = TxtRecordMeta()

class TxtTable:
    def __init__(self, db_ref, table_name):
        self.db_ref = db_ref
        self.table_dir = table_name

    def _fulldir(self):
        return os.path.join(self.db_ref.db_base_dir, self.table_dir)

    def create(self, record):
        result = TxtRecord()
        result.id = libtxtdb.cannonical_create_record(self._fulldir().encode("utf8"), record.encode("utf8"))
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

