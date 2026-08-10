import os
import argparse
CHUNK_SIZE = 4096

def tail(path, n):
    """Return the last n lines of a file without loading it fully into memory."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = remaining = f.tell()
        buffer = b""
        newline_count = 0

        while remaining > 0 and newline_count <= n:
            read_size = min(CHUNK_SIZE, remaining)
            remaining -= read_size
            f.seek(remaining)
            chunk = f.read(read_size)
            buffer = chunk + buffer
            newline_count = buffer.count(b"\n")

        lines = buffer.splitlines()
        last_lines = lines[-n:] if n <= len(lines) else lines
        return [line.decode("utf-8", errors="replace") for line in last_lines]

def main():
    parser = argparse.ArgumentParser(description="tail reimplementation")
    parser.add_argument("-n", type=int, default=10, help="number of lines")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    for i, path in enumerate(args.files):
        for line in tail(path, args.n):
            print(line)


if __name__ == "__main__":
    main()
