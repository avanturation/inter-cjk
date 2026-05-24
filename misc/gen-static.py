"""Generate static font instances from variable TTF via instancer."""
import sys
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WEIGHTS = [
    ("Thin", 100),
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]


def generate_statics(variable_ttf, prefix, family_name, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    for weight_name, weight_value in WEIGHTS:
        font = TTFont(variable_ttf)
        for tag in ['MVAR', 'HVAR', 'GDEF']:
            if tag in font:
                del font[tag]
        instance = instantiateVariableFont(font, {"wght": weight_value}, inplace=True, overlap=True)

        for tag in ['fvar', 'STAT', 'gvar', 'avar', 'HVAR', 'MVAR']:
            if tag in instance:
                del instance[tag]

        name_table = instance['name']
        subfamily = "Regular" if weight_name == "Regular" else weight_name
        full_name = f"{family_name} {weight_name}" if weight_name != "Regular" else family_name
        ps_name = f"{prefix}-{weight_name}"

        for record in name_table.names:
            try:
                record.toUnicode()
            except:
                continue
            if record.nameID == 1:
                name_table.setName(family_name, record.nameID, record.platformID, record.platEncID, record.langID)
            elif record.nameID == 2:
                name_table.setName(subfamily, record.nameID, record.platformID, record.platEncID, record.langID)
            elif record.nameID == 4:
                name_table.setName(full_name, record.nameID, record.platformID, record.platEncID, record.langID)
            elif record.nameID == 6:
                name_table.setName(ps_name, record.nameID, record.platformID, record.platEncID, record.langID)
            elif record.nameID == 3:
                name_table.setName(f"1.000;{ps_name}", record.nameID, record.platformID, record.platEncID, record.langID)

        instance['OS/2'].usWeightClass = weight_value

        out_path = os.path.join(out_dir, f"{prefix}-{weight_name}.ttf")
        instance.save(out_path)
        size_kb = os.path.getsize(out_path) / 1024
        print(f"  {prefix}-{weight_name}.ttf ({size_kb:.0f} KB)")

        otf_path = os.path.join(out_dir, f"{prefix}-{weight_name}.otf")
        instance.flavor = None
        instance.save(otf_path)


def main():
    text_ttf = sys.argv[1]
    display_ttf = sys.argv[2]
    out_dir = sys.argv[3]

    os.makedirs(out_dir, exist_ok=True)
    print("Generating Inter CJK static instances:")
    generate_statics(text_ttf, "InterCJK", "Inter CJK", out_dir)

    print("\nGenerating Inter CJK Display static instances:")
    generate_statics(display_ttf, "InterCJKDisplay", "Inter CJK Display", out_dir)


if __name__ == "__main__":
    main()
