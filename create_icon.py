"""Gera o ícone do app (icon.ico) com um monitor estilizado."""
import struct
import zlib
import os


def create_ico(path: str):
    """Cria um .ico 32x32 com um ícone de monitor/conexão em tons de indigo."""
    size = 32
    pixels = [[0] * size for _ in range(size)]

    # Cores BGRA
    BG = (0, 0, 0, 0)  # transparente
    INDIGO = (0xf1, 0x66, 0x63, 0xFF)  # #6366f1 em BGRA
    LIGHT = (0xf8, 0x8c, 0x81, 0xFF)   # #818cf8 em BGRA
    WHITE = (0xF0, 0xE4, 0xE2, 0xFF)   # #e2e4f0 em BGRA

    # Desenha monitor (retângulo 6..25 x 6..20)
    for y in range(6, 21):
        for x in range(6, 26):
            if y == 6 or y == 20 or x == 6 or x == 25:
                pixels[y][x] = INDIGO  # borda
            else:
                pixels[y][x] = (0x1e, 0x16, 0x16, 0xFF)  # tela escura

    # Base do monitor
    for x in range(13, 19):
        pixels[21][x] = INDIGO
        pixels[22][x] = INDIGO
    for x in range(11, 21):
        pixels[23][x] = INDIGO

    # Seta de conexão na tela (play/connect)
    for dy, width in enumerate(range(1, 8)):
        if dy < 7:
            for dx in range(width):
                px = 12 + dx
                py = 10 + dy
                if 7 <= px <= 24 and 7 <= py <= 19:
                    pixels[py][px] = LIGHT
    # Espelhar para fazer triângulo
    for dy, width in enumerate(range(6, 0, -1)):
        for dx in range(width):
            px = 12 + dx
            py = 17 + dy - 6 + 7
            if 7 <= px <= 24 and 7 <= py <= 19:
                if pixels[py][px] == (0x1e, 0x16, 0x16, 0xFF):
                    pixels[py][px] = LIGHT

    # Converter para BMP
    row_size = size * 4
    pixel_data = b""
    for y in range(size - 1, -1, -1):  # BMP é bottom-up
        for x in range(size):
            c = pixels[y][x] if isinstance(pixels[y][x], tuple) and len(pixels[y][x]) == 4 else BG
            pixel_data += struct.pack("BBBB", c[0], c[1], c[2], c[3])

    # AND mask (transparência — 1 bit por pixel, cada row padded a 4 bytes)
    and_mask = b""
    for y in range(size - 1, -1, -1):
        row_bits = 0
        row_bytes = b""
        for x in range(size):
            c = pixels[y][x] if isinstance(pixels[y][x], tuple) and len(pixels[y][x]) == 4 else BG
            bit = 1 if c[3] == 0 else 0
            row_bits = (row_bits << 1) | bit
            if (x + 1) % 8 == 0:
                row_bytes += struct.pack("B", row_bits)
                row_bits = 0
        # Pad to 4 bytes
        while len(row_bytes) % 4 != 0:
            row_bytes += b"\x00"
        and_mask += row_bytes

    # BITMAPINFOHEADER
    bih = struct.pack("<IiiHHIIiiII",
                      40,        # biSize
                      size,      # biWidth
                      size * 2,  # biHeight (doubled for AND mask)
                      1,         # biPlanes
                      32,        # biBitCount
                      0,         # biCompression
                      len(pixel_data) + len(and_mask),
                      0, 0, 0, 0)

    image_data = bih + pixel_data + and_mask

    # ICO header
    ico_header = struct.pack("<HHH", 0, 1, 1)  # reserved, type=ICO, count=1

    # ICO directory entry
    ico_entry = struct.pack("<BBBBHHII",
                            size,   # width
                            size,   # height
                            0,      # color palette
                            0,      # reserved
                            1,      # color planes
                            32,     # bits per pixel
                            len(image_data),
                            6 + 16)  # offset (header=6 + entry=16)

    with open(path, "wb") as f:
        f.write(ico_header + ico_entry + image_data)


if __name__ == "__main__":
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    create_ico(ico_path)
    print(f"Ícone criado: {ico_path}")
