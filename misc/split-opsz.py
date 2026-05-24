"""Split opsz+wght variable font into two wght-only files using instancer."""
import sys
import os
import copy
from multiprocessing import Pool
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

WEIGHT_MAP = {
    100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular",
    500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black",
}


def _split_one(args):
    src_path, out_dir, opsz_val, family_name, ps_prefix, filename = args

    font = TTFont(src_path)
    instantiateVariableFont(font, {"opsz": opsz_val}, inplace=True, overlap=True)

    font['fvar'].axes = [a for a in font['fvar'].axes if a.axisTag != 'opsz']

    new_instances = []
    for inst in font['fvar'].instances:
        coords = dict(inst.coordinates)
        if abs(coords.get('opsz', opsz_val) - opsz_val) < 0.1:
            coords.pop('opsz', None)
            inst.coordinates = coords
            wght = int(coords.get('wght', 400))
            font['name'].setName(WEIGHT_MAP.get(wght, "Regular"),
                                 inst.subfamilyNameID, 3, 1, 0x0409)
            font['name'].setName(WEIGHT_MAP.get(wght, "Regular"),
                                 inst.subfamilyNameID, 1, 0, 0)
            new_instances.append(inst)
    font['fvar'].instances = new_instances

    if 'STAT' in font:
        stat = font['STAT'].table
        if stat.DesignAxisRecord:
            stat.DesignAxisRecord.Axis = [a for a in stat.DesignAxisRecord.Axis if a.AxisTag != 'opsz']
            stat.DesignAxisCount = len(stat.DesignAxisRecord.Axis)
        if hasattr(stat, 'AxisValueArray') and stat.AxisValueArray:
            new_values = []
            for av in stat.AxisValueArray.AxisValue:
                if hasattr(av, 'AxisIndex'):
                    if av.AxisIndex == 0:
                        continue
                    av.AxisIndex -= 1
                new_values.append(av)
            stat.AxisValueArray.AxisValue = new_values

    name_table = font['name']
    for record in name_table.names:
        try:
            record.toUnicode()
        except:
            continue
        if record.nameID == 1:
            name_table.setName(family_name, record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 4:
            name_table.setName(family_name, record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 6:
            name_table.setName(f"{ps_prefix}-Variable", record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 3:
            name_table.setName(f"1.000;{ps_prefix}-Variable", record.nameID, record.platformID, record.platEncID, record.langID)

    out_path = os.path.join(out_dir, filename)
    font.save(out_path)
    return f"{filename}: {os.path.getsize(out_path)/1024/1024:.1f} MB"


def split(src_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    jobs = [
        (src_path, out_dir, 14.0, "Inter CJK Variable", "InterCJK", "InterCJKVariable.ttf"),
        (src_path, out_dir, 32.0, "Inter CJK Display Variable", "InterCJKDisplay", "InterCJKDisplayVariable.ttf"),
    ]

    with Pool(2) as pool:
        for result in pool.imap_unordered(_split_one, jobs):
            print(f"  {result}")


if __name__ == "__main__":
    print("Splitting opsz axis via instancer (parallel):")
    split(sys.argv[1], sys.argv[2])
