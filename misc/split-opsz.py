"""Split a variable font with opsz+wght into two wght-only files."""
import sys
import os
from fontTools.ttLib import TTFont


def make_single_axis_font(src_path, keep_opsz, family_name, ps_prefix, out_path):
    font = TTFont(src_path)
    _ = font['gvar'].variations

    for gname in font['gvar'].variations:
        new_tvs = []
        for tv in font['gvar'].variations[gname]:
            if 'opsz' in tv.axes:
                del tv.axes['opsz']
            if tv.axes:
                new_tvs.append(tv)
        font['gvar'].variations[gname] = new_tvs

    font['fvar'].axes = [a for a in font['fvar'].axes if a.axisTag != 'opsz']

    new_instances = []
    for inst in font['fvar'].instances:
        coords = dict(inst.coordinates)
        if coords.get('opsz', 14.0) == keep_opsz:
            coords.pop('opsz', None)
            inst.coordinates = coords
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

    if 'avar' in font:
        if hasattr(font['avar'], 'segments') and 'opsz' in font['avar'].segments:
            del font['avar'].segments['opsz']

    name_table = font['name']
    for record in name_table.names:
        try:
            t = record.toUnicode()
        except:
            continue
        if record.nameID == 1:
            name_table.setName(family_name, record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 4:
            name_table.setName(f"{family_name} Variable", record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 6:
            name_table.setName(f"{ps_prefix}-Variable", record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 3:
            name_table.setName(f"1.000;{ps_prefix}-Variable", record.nameID, record.platformID, record.platEncID, record.langID)

    font.save(out_path)
    print(f"  {os.path.basename(out_path)}: {os.path.getsize(out_path)/1024/1024:.1f} MB")


def main():
    src = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    print("Splitting opsz axis into separate files:")
    make_single_axis_font(src, 14.0, "Inter CJK", "InterCJK",
                          os.path.join(out_dir, "InterCJKVariable.ttf"))
    make_single_axis_font(src, 32.0, "Inter CJK Display", "InterCJKDisplay",
                          os.path.join(out_dir, "InterCJKDisplayVariable.ttf"))


if __name__ == "__main__":
    main()
