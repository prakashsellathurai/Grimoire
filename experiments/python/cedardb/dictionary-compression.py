from typing import List, Tuple, Optional
import struct
import array


class DictionaryCompressor:
    def __init__(self, values: List[str]):
        self.dict_values: List[str] = sorted(set(values))
        self.offsets: List[int] = []
        self._build_offsets()
        self.key_bytes: int = self._pick_key_width()
        self.keys: List[int] = [self._key_for(v) for v in values]

    def _build_offsets(self) -> None:
        offset = 0
        for s in self.dict_values:
            self.offsets.append(offset)
            offset += len(s.encode("utf-8"))
        self._total_str_len = offset

    def _pick_key_width(self) -> int:
        n = len(self.dict_values)
        if n <= 2**8:
            return 1
        elif n <= 2**16:
            return 2
        else:
            return 4

    def _key_for(self, value: str) -> int:
        lo, hi = 0, len(self.dict_values) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.dict_values[mid] == value:
                return mid
            elif self.dict_values[mid] < value:
                lo = mid + 1
            else:
                hi = mid - 1
        raise ValueError(f"value not in dictionary: {value}")

    def compress(self) -> bytes:
        n = len(self.dict_values)
        buf = bytearray()
        buf += struct.pack("<I", n)
        buf += struct.pack("<I", self._total_str_len)
        off_arr = array.array("I", self.offsets)
        buf += off_arr.tobytes()
        for s in self.dict_values:
            buf += s.encode("utf-8")
        key_fmt = {1: "B", 2: "H", 4: "I"}[self.key_bytes]
        k_arr = array.array(key_fmt, self.keys)
        buf += k_arr.tobytes()
        return bytes(buf)

    def get_original(self, index: int) -> str:
        return self.dict_values[self.keys[index]]

    @staticmethod
    def decompress(compressed: bytes) -> List[str]:
        offset = 0
        num_values = struct.unpack_from("<I", compressed, offset)[0]
        offset += 4
        total_str_len = struct.unpack_from("<I", compressed, offset)[0]
        offset += 4
        raw_offsets = struct.unpack_from(f"<{num_values}I", compressed, offset)
        offset += num_values * 4
        str_data_offset = offset
        dict_values = []
        for i in range(num_values):
            start = raw_offsets[i]
            if i + 1 < num_values:
                end = raw_offsets[i + 1]
            else:
                end = total_str_len
            length = end - start
            s = compressed[str_data_offset + start : str_data_offset + end].decode("utf-8")
            dict_values.append(s)
        offset += total_str_len
        remaining = compressed[offset:]
        key_count = num_values
        key_width = len(remaining) // key_count
        key_fmt = {1: "B", 2: "H", 4: "I"}[key_width]
        keys = list(array.array(key_fmt, remaining))
        return [dict_values[k] for k in keys]


if __name__ == "__main__":
    data = ["banana", "apple", "cherry", "banana", "date", "apple", "elderberry"]
    dc = DictionaryCompressor(data)
    compressed = dc.compress()
    decompressed = DictionaryCompressor.decompress(compressed)
    print(f"Original ({len(data)}): {data}")
    print(f"Keys ({dc.key_bytes} byte(s) each): {dc.keys}")
    print(f"Dictionary: {dc.dict_values}")
    print(f"Offsets: {dc.offsets}")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Naive size: {sum(len(v.encode('utf-8')) for v in data)} bytes")
    print(f"Decompressed: {decompressed}")
    assert data == decompressed, f"round-trip failed!\n  orig: {data}\n  got:  {decompressed}"
    print("Round-trip OK")
