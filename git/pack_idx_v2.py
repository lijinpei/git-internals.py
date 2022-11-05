from collections import namedtuple
import hashlib


class PackIdxV2:
    def __init__(
        self,
        fanout_table,
        object_names,
        object_crc32s,
        object_offset_values,
        object_offset_entries,
        packfile_chksum,
        idxfile_chksum,
    ):
        self.fanout_table = fanout_table
        self.object_names = object_names
        self.object_crc32s = object_crc32s
        self.object_offset_values = object_offset_values
        self.object_offset_entries = object_offset_entries
        self.packfile_chksum = packfile_chksum
        self.idxfile_chksum = idxfile_chksum

    def __str__(self):
        return (
            "{fanout_table}\n{object_names}\n{object_crc32s}\n{object_offset_values}\n{object_offset_entries}\n".format(
                **self.__dict__
            )
            + self.packfile_chksum.hex()
            + "\n"
            + self.idxfile_chksum.hex()
            + "\n"
        )

    @classmethod
    def read_from_file(cls, file_like, has_offset_entries=False):
        idxfile_chksum_verify = hashlib.sha1()

        def read_and_chksum(n):
            content = file_like.read(n)
            idxfile_chksum_verify.update(content)
            return content

        if read_and_chksum(4) != b"\xfftOc":
            raise ValueError("Git Pack Index V2 magic number wrong.")

        def read_network_order_i32():
            content = read_and_chksum(4)
            return int.from_bytes(content, "big")

        def read_network_order_i64():
            content = read_and_chksum(8)
            return int.from_bytes(content, "big")

        if read_network_order_i32() != 2:
            raise ValueError("Git Pack Index V2 version number wrong.")
        fanout_table = [read_network_order_i32() for _ in range(256)]
        object_count = fanout_table[255]
        print("object_count: ", object_count)
        object_names = [read_and_chksum(20) for _ in range(object_count)]
        object_crc32s = [read_and_chksum(4) for _ in range(object_count)]
        object_offset_values = [read_network_order_i32() for _ in range(object_count)]
        if has_offset_entries:
            object_offset_entries = [
                read_network_order_i64() for _ in range(object_count)
            ]
        else:
            object_offset_entries = None
        packfile_chksum = read_and_chksum(20)
        idxfile_chksum = file_like.read(20)
        if idxfile_chksum_verify.digest() != idxfile_chksum:
            raise ValueError("Git Pack Index V2 idxfile checksum mismatch.")
        return PackIdxV2(
            fanout_table,
            object_names,
            object_crc32s,
            object_offset_values,
            object_offset_entries,
            packfile_chksum,
            idxfile_chksum,
        )
