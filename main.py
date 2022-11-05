from absl import app
from absl import flags
from git.pack_idx_v2 import *
from git.pack import GitPack


def main(argv):
    with open(argv[1], "rb") as pack_idx_file:
        pack_idx = GitPack.read_from_file(pack_idx_file)
        print(pack_idx)


if __name__ == "__main__":
    app.run(main)
