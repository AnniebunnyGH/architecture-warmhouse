import os
import sys
import zlib
import urllib.request

def encode6bit(b):
    if b < 10:
        return chr(48 + b)
    b -= 10
    if b < 26:
        return chr(65 + b)
    b -= 26
    if b < 26:
        return chr(97 + b)
    b -= 26
    if b == 0:
        return '-'
    if b == 1:
        return '_'
    return '?'

def encode(data):
    r = ""
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]
        if len(chunk) == 3:
            r += encode6bit((chunk[0] & 0xFC) >> 2)
            r += encode6bit(((chunk[0] & 0x03) << 4) | ((chunk[1] & 0xF0) >> 4))
            r += encode6bit(((chunk[1] & 0x0F) << 2) | ((chunk[2] & 0xC0) >> 6))
            r += encode6bit(chunk[2] & 0x3F)
        elif len(chunk) == 2:
            r += encode6bit((chunk[0] & 0xFC) >> 2)
            r += encode6bit(((chunk[0] & 0x03) << 4) | ((chunk[1] & 0xF0) >> 4))
            r += encode6bit((chunk[1] & 0x0F) << 2)
        elif len(chunk) == 1:
            r += encode6bit((chunk[0] & 0xFC) >> 2)
            r += encode6bit((chunk[0] & 0x03) << 4)
    return r

def plantuml_encode(text):
    compressor = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
    compressed = compressor.compress(text.encode('utf-8')) + compressor.flush()
    return encode(compressed)

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_puml.py <file.puml>")
        sys.exit(1)
    
    puml_path = sys.argv[1]
    if not os.path.exists(puml_path):
        print(f"File {puml_path} not found.")
        sys.exit(1)
        
    with open(puml_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    encoded = plantuml_encode(text)
    url = f"http://www.plantuml.com/plantuml/png/{encoded}"
    
    # Ensure output directory is images/ next to the diagrams/ parent folder
    # i.e., if puml is in <root>/diagrams/name.puml, we save to <root>/images/name.png
    puml_abs = os.path.abspath(puml_path)
    parent_dir = os.path.dirname(puml_abs)
    grandparent_dir = os.path.dirname(parent_dir)
    out_dir = os.path.join(grandparent_dir, 'images')
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    base = os.path.splitext(os.path.basename(puml_path))[0]
    out_path = os.path.join(out_dir, f"{base}.png")
    
    print(f"Fetching diagram from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(out_path, 'wb') as out_f:
                out_f.write(response.read())
        print(f"Saved rendered image to {out_path}")
    except Exception as e:
        print(f"Error rendering: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
