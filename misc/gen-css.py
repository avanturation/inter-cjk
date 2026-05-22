"""Generate CSS for Inter CJK web fonts."""
import os
import sys

def main():
    webdir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    css = []
    
    # Variable font
    css.append("""/* Inter CJK Variable */
@font-face {
  font-family: 'Inter CJK Variable';
  font-style: normal;
  font-display: swap;
  font-weight: 100 900;
  src: url('InterCJKVariable.woff2') format('woff2');
}

/* Inter CJK Display Variable (opsz=32) */
@font-face {
  font-family: 'Inter CJK Display Variable';
  font-style: normal;
  font-display: swap;
  font-weight: 100 900;
  font-variation-settings: 'opsz' 32;
  src: url('InterCJKVariable.woff2') format('woff2');
}
""")
    
    # Static fonts
    weights = {
        "Thin": 100,
        "ExtraLight": 200,
        "Light": 300,
        "Regular": 400,
        "Medium": 500,
        "SemiBold": 600,
        "Bold": 700,
        "ExtraBold": 800,
        "Black": 900,
    }
    
    css.append("/* Inter CJK Static */")
    for name, weight in weights.items():
        filename = f"InterCJK-{name}.woff2"
        if os.path.exists(os.path.join(webdir, filename)):
            css.append(f"""@font-face {{
  font-family: 'Inter CJK';
  font-style: normal;
  font-display: swap;
  font-weight: {weight};
  src: url('{filename}') format('woff2');
}}
""")
    
    css.append("/* Inter CJK Display Static */")
    for name, weight in weights.items():
        filename = f"InterCJKDisplay-{name}.woff2"
        if os.path.exists(os.path.join(webdir, filename)):
            css.append(f"""@font-face {{
  font-family: 'Inter CJK Display';
  font-style: normal;
  font-display: swap;
  font-weight: {weight};
  src: url('{filename}') format('woff2');
}}
""")
    
    print('\n'.join(css))

if __name__ == "__main__":
    main()
