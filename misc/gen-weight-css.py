"""Generate per-weight CSS files for static font loading."""
import sys
import os

WEIGHTS = [
    (100, "Thin"), (200, "ExtraLight"), (300, "Light"), (400, "Regular"),
    (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
    (900, "Black"),
]


def generate(out_dir):
    os.makedirs(out_dir, exist_ok=True)

    for prefix, family in [("InterCJK", "Inter CJK"), ("InterCJKDisplay", "Inter CJK Display")]:
        for weight_val, weight_name in WEIGHTS:
            filename = f"{prefix}-{weight_name}.css"
            local_name = f"{family} {weight_name}" if weight_name != "Regular" else family
            css = (
                f"@font-face {{\n"
                f"\tfont-family: '{family}';\n"
                f"\tfont-weight: {weight_val};\n"
                f"\tfont-display: swap;\n"
                f"\tsrc: local('{local_name}'),\n"
                f"\t     url('./{prefix}-{weight_name}.woff2') format('woff2');\n"
                f"}}\n"
            )
            with open(os.path.join(out_dir, filename), 'w') as f:
                f.write(css)

    print(f"  Generated {len(WEIGHTS) * 2} per-weight CSS files")


if __name__ == "__main__":
    generate(sys.argv[1])
