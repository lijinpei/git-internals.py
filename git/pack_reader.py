import hashlib

class PackReaderBase:
    def __init__(self, file_like):
        self.file_like = file_like
        self.chksum_verifier = hashlib.sha1()

    def read(self, n):
        content = self.file_like.read(n)
        self.chksum_verifier.update(content)
        return content

    def read_no_chksum(self, n):
        return self.file_like.read(n)

    def read_i32(self):
        content = self.read(4)
        return int.from_bytes(content, 'big')

    def read_i64(self):
        content = self.read(8)
        return int.from_bytes(content, 'big')

    def get_chksum(self):
        return self.chksum_verifier.digest()
