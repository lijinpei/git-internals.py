from .protocol_base import *
import requests

class GitHttpProtocol(GitProtocolBase):
    def __init__(self, use_smart=True):
        super().__init__()
        self.use_smart = use_smart
        if self.use_smart:
            self.discover_refs = self.discover_refs_smart
        else:
            self.discover_refs = self.discover_refs_dumb

    def discover_refs_dumb(self, url):
        req = requests.get(url + '/info/refs')
        print(req.status_code)
        print(req.text)

    @staticmethod
    def get_pkt_line_itor(text):
        next_pos = 0
        text_len = len(text)
        while next_pos < text_len:
            hex_len_str = text[next_pos:next_pos + 4]
            this_line_len = int(hex_len_str, 16)
            if this_line_len == 0:
                yield ''
                next_pos += 4
            else:
                yield text[next_pos + 4:next_pos + this_line_len - 1]
                next_pos += this_line_len
            if next_pos < text_len and text[next_pos] == '\n':
                next_pos += 1

    @staticmethod
    def parse_capabilities(line):
        result = {}
        for kv in line.split(' '):
            first_blank_pos = kv.find('=')
            if first_blank_pos == -1:
                result[kv] = None
            else:
                result[kv[:first_blank_pos]] = kv[first_blank_pos + 1:]
        return result

    @staticmethod
    def split_refs_line(line):
        first_blank_pos = line.find(' ')
        assert(first_blank_pos != -1)
        sha_id = line[:first_blank_pos]
        ref = line[first_blank_pos + 1:]
        if ref[-1] == '\n':
            ref = ref[:-1]
        return (sha_id, ref)

    def discover_refs_smart(self, url):
        req = requests.get(url + '/info/refs?service=git-upload-pack')
        print(req.text)
        assert(req.status_code == 200 or req.status_code == 304)
        pkt_line_itor = GitHttpProtocol.get_pkt_line_itor(req.text)
        service_line = next(pkt_line_itor)
        assert(next(pkt_line_itor) == '')
        HEAD_line = next(pkt_line_itor)
        nul_pos = HEAD_line.find('\0')
        refs = []
        capabilities = self.parse_capabilities(HEAD_line[nul_pos + 1:])
        refs.append(self.split_refs_line(HEAD_line[:nul_pos]))
        for line in pkt_line_itor:
            if not line:
                break
            refs.append(self.split_refs_line(line))
        print(refs)
        print(capabilities)
        post_data=""
        for (sha, ref) in refs:
            post_data += "0032want " + sha + "\n"
        post_data += "00000009done\n"
        req1 = requests.post(url + '/git-upload-pack', headers={'Content-Type': 'application/x-git-receive-pack-request'}, data=post_data)
        print(req1.status_code)
        with open("/home/lijinpei/tmp.pack", "wb") as pack_file:
            pack_file.write(req1.content)

    def upload_pack(self):
        pass
