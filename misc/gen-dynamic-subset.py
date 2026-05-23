"""Generate dynamic subset woff2 files and CSS from a variable TTF.

Uses Pretendard JP's unicode-range split as reference, then subsets
the Inter CJK variable font into matching chunks.
"""
import sys
import os
import re
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options


def parse_unicode_ranges(css_path):
    with open(css_path) as f:
        content = f.read()
    return re.findall(r'unicode-range:\s*([^;]+);', content)


def unicode_range_to_codepoints(range_str):
    codepoints = set()
    for part in range_str.split(','):
        part = part.strip().replace('U+', '').replace('u+', '')
        if '-' in part:
            start, end = part.split('-')
            codepoints.update(range(int(start, 16), int(end, 16) + 1))
        else:
            codepoints.add(int(part, 16))
    return codepoints


def subset_font(font_path, codepoints, output_path):
    font = TTFont(font_path)
    options = Options()
    options.flavor = 'woff2'
    options.layout_features = ['*']
    options.glyph_names = False
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
    options.drop_tables = ['DSIG', 'MVAR']

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)
    font.save(output_path)


def generate(font_path, reference_css, output_dir, family_name, css_filename):
    os.makedirs(output_dir, exist_ok=True)

    ranges = parse_unicode_ranges(reference_css)
    font_basename = os.path.splitext(os.path.basename(font_path))[0]

    css_lines = []
    total = len(ranges)

    for i, range_str in enumerate(ranges):
        codepoints = unicode_range_to_codepoints(range_str)
        if not codepoints:
            continue

        subset_filename = f"{font_basename}.subset.{i}.woff2"
        subset_path = os.path.join(output_dir, subset_filename)

        try:
            subset_font(font_path, codepoints, subset_path)
            size_kb = os.path.getsize(subset_path) / 1024
            if size_kb < 0.1:
                os.remove(subset_path)
                continue
        except Exception as e:
            continue

        css_lines.append(f"/* [{i}] */")
        css_lines.append("@font-face {")
        css_lines.append(f"\tfont-family: '{family_name}';")
        css_lines.append(f"\tfont-style: normal;")
        css_lines.append(f"\tfont-display: swap;")
        css_lines.append(f"\tfont-weight: 100 900;")
        css_lines.append(f"\tsrc: url('./{subset_filename}') format('woff2');")
        css_lines.append(f"\tunicode-range: {range_str};")
        css_lines.append("}")

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{total}] subsets generated...")

    css_path = os.path.join(output_dir, css_filename)
    with open(css_path, 'w') as f:
        f.write('\n'.join(css_lines) + '\n')

    subset_count = len([f for f in os.listdir(output_dir) if f.endswith('.woff2')])
    print(f"  Done: {subset_count} subsets, CSS at {css_filename}")


if __name__ == "__main__":
    font_path = sys.argv[1]
    reference_css = sys.argv[2]
    output_dir = sys.argv[3]
    family_name = sys.argv[4] if len(sys.argv) > 4 else "Inter CJK Variable"
    css_filename = sys.argv[5] if len(sys.argv) > 5 else "inter-cjk-dynamic-subset.css"

    print(f"Generating dynamic subsets for {os.path.basename(font_path)}:")
    generate(font_path, reference_css, output_dir, family_name, css_filename)
