import hashlib
from .pack_reader import PackReaderBase
import zlib

OBJ_INVALID = 0
OBJ_COMMIT = 1
OBJ_TREE = 2
OBJ_BLOB = 3
OBJ_TAG = 4
OBJ_RESERVED = 5
OBJ_OFS_DELTA = 6
OBJ_REF_DELTA = 7


class GitPackObjectRaw:
    def __init__(self, type_id, size, raw_content):
        self.type_id = type_id
        self.size = size
        self.raw_content = raw_content


class GitPackReader(PackReaderBase):
    def __init__(self, file_like):
        super().__init__(file_like)

    def read_raw_object_entry(self):
        print('read object')
        size_part = self.read(1)[0]
        type_id = (size_part >> 4) & 0x7
        if type_id == OBJ_INVALID:
            raise ValueError("Git pack object type invalid.")
        if type_id == OBJ_RESERVED:
            raise ValueError("Git pack object type reserved.")
        size = size_part & 0xf
        shift = 4;
        while size_part & 0x80:
            size_part = self.read(1)[0]
            size |= (size_part & 0x7f) << shift
            shift += 7
        print(type_id, size)
        if type_id == OBJ_REF_DELTA:
            base_obj_name = self.read(20)
        elif type_id == OBJ_OFS_DELTA:
            encode_byte = self.read(1)[0]
            offset = encode_byte & 0x7f
            offset_shift = 7
            while encode_byte & 0x80:
                encode_byte = self.read(1)[0]
                offset |= (encode_byte & 0x7f) << offset_shift
                offset_shift += 7
        decomp = zlib.decompressobj()
        result = b''
        target_size = size
        comp_len = 0
        while target_size != 0 or not decomp.eof:
            new_content = decomp.decompress(self.read(1), target_size)
            comp_len += 1
            target_size -= len(new_content)
            result += new_content
        assert(len(result) == size)
        assert(len(decomp.unused_data) == 0)
        assert(len(decomp.unconsumed_tail) == 0)
        if type_id == OBJ_BLOB:
            print(result.decode('utf8'))
        return GitPackObjectRaw(type_id, size, result)


class GitPack:
    MAGIC = b"PACK"

    def __init__(self, version, raw_objects):
        self.version = version
        self.raw_objects = raw_objects

    @classmethod
    def read_from_file(cls, file_like):
        reader = GitPackReader(file_like)
        magic = reader.read(4)
        if magic != cls.MAGIC:
            raise ValueError("Git Pack file magic wrong.")
        ver = reader.read_i32()
        if ver != 2 and ver != 3:
            raise ValueError("Git Pack file version number wrong.")
        num_objs = reader.read_i32()
        print('num_objs: ', num_objs)
        raw_objects = [reader.read_raw_object_entry() for _ in range(num_objs)]
        chk_sum = reader.read_no_chksum(20)
        if chk_sum != reader.get_chksum():
            raise ValueError("Git Pack file chksum mismatch")
        return GitPack(ver, raw_objects)
