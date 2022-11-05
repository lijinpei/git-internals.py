from collections import namedtuple


class PackIdxV1:
    PackIdxObject = namedtuple("PackIdxObject", "offset, name")

    def __init__(self, fanout_table, objects, packfile_chksum, idxfile_chksum):
        self.fanout_table = fanout_table
        self.objects = objects
        self.packfile_chksum = packfile_chksum
        self.idxfile_chksum = idxfile_chksum

    def __str__(self):
        return "{}\n{}\n{}\n{}\n".format(
            self.fanout_table,
            self.objects,
            self.packfile_chksum.hex(),
            self.idxfile_chksum.hex(),
        )

    @classmethod
    def read_from_file(cls, file_like):
        def read_network_order_i32():
            content = file_like.read(4)
            return int.from_bytes(content, "big")

        fanout_table = [read_network_order_i32() for _ in range(256)]
        object_count = fanout_table[255]
        print("object_count: ", object_count)

        def read_object():
            offset = read_network_order_i32()
            name = file_like.read(20)
            return cls.PackIdxObject(offset, name)

        objects = [read_object() for _ in range(object_count)]
        packfile_chksum = file_like.read(20)
        idxfile_chksum = file_like.read(20)
        return PackIdxV1(fanout_table, objects, packfile_chksum, idxfile_chksum)
