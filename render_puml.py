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

def resolve_includes(file_path, processed_files=None):
    if processed_files is None:
        processed_files = set()
        
    abs_path = os.path.abspath(file_path)
    if abs_path in processed_files:
        return "" # Prevent circular inclusion
    processed_files.add(abs_path)
    
    if not os.path.exists(abs_path):
        print(f"Warning: include file {abs_path} not found.")
        return f"' Error: include {file_path} not found\n"
        
    dir_name = os.path.dirname(abs_path)
    resolved_lines = []
    
    with open(abs_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            is_include = False
            inc_path = None
            if stripped.startswith("!include ") or stripped.startswith("!includeurl "):
                parts = stripped.split(None, 1)
                if len(parts) == 2:
                    path_val = parts[1].strip().strip('"').strip("'")
                    if not path_val.startswith("http://") and not path_val.startswith("https://"):
                        is_include = True
                        inc_path = path_val
            
            if is_include:
                if "c4/" in inc_path or inc_path.startswith("C4"):
                    c4_file = os.path.basename(inc_path)
                    remote_path = f"https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/v2.5.0/{c4_file}"
                    resolved_lines.append(f"!include {remote_path}\n")
                else:
                    target_path = os.path.join(dir_name, inc_path)
                    resolved_content = resolve_includes(target_path, processed_files)
                    resolved_lines.append(resolved_content)
            else:
                resolved_lines.append(line)
                
    return "".join(resolved_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python render_puml.py <file.puml>")
        sys.exit(1)
    
    puml_path = sys.argv[1]
    if not os.path.exists(puml_path):
        print(f"File {puml_path} not found.")
        sys.exit(1)
        
    # Resolve all local includes to generate a self-contained PUML string
    print(f"Resolving local includes in {puml_path}...")
    self_contained_text = resolve_includes(puml_path)
    
    puml_abs = os.path.abspath(puml_path)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, 'images')
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    # Build unique image filename based on subdirectory if present, e.g. device_registry_components.png
    parts = os.path.splitext(os.path.relpath(puml_abs, os.path.join(script_dir, 'diagrams')))[0].split(os.sep)
    base = "_".join(parts)
    out_path = os.path.join(out_dir, f"{base}.png")
    
    print(f"Rendering diagram via Kroki POST to {out_path}...")
    try:
        req = urllib.request.Request(
            'https://kroki.io/plantuml/png',
            data=self_contained_text.encode('utf-8'),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Content-Type': 'text/plain; charset=utf-8'
            }
        )
        with urllib.request.urlopen(req) as response:
            with open(out_path, 'wb') as f:
                f.write(response.read())
        print(f"Saved rendered image to {out_path}")
    except Exception as e:
        print(f"Error rendering: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
