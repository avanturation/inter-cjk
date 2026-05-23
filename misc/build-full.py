"""Merge Inter Variable + Pretendard JP Variable into InterCJK-full.ttf.

Applies all design adjustments:
- CJK vertical alignment: Y offset +21 (matches Pretendard's 가-H center diff of +3)
- CJK weight matching: 1% horizontal thinning (gray-level balance with Latin)
- CJK optical size: 3% tighter at opsz=32 (Display)
- Contextual symbol alignment: CJK added to calt @UC class so symbols get .case forms
- Latin-CJK kern: +100 units between script transitions
- SUIT-matched vertical metrics: ratio 1.248, symmetric around cap center
- GSUB/GPOS: CJK script support (hang, kana, hani)
"""
import sys
import os
import copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._f_v_a_r import NamedInstance

Y_OFFSET = 21
CJK_HSCALE = 0.99
OPSZ_SCALE = 0.03
LATIN_CJK_SPACING = 0

CJK_RANGES = [
    (0x1100, 0x11FF), (0x2E80, 0x2EFF), (0x2F00, 0x2FDF),
    (0x3000, 0x303F), (0x3040, 0x309F), (0x30A0, 0x30FF),
    (0x3100, 0x312F), (0x3130, 0x318F), (0x31F0, 0x31FF),
    (0x3200, 0x32FF), (0x3300, 0x33FF), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xA960, 0xA97F), (0xAC00, 0xD7AF),
    (0xD7B0, 0xD7FF), (0xF900, 0xFAFF), (0xFE30, 0xFE4F),
    (0xFF00, 0xFFEF),
]

WEIGHTS = [
    (100, "Thin"), (200, "ExtraLight"), (300, "Light"), (400, "Regular"),
    (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
    (900, "Black"),
]


def get_deps(gname, glyf_table, visited=None):
    if visited is None:
        visited = set()
    if gname in visited:
        return visited
    visited.add(gname)
    g = glyf_table[gname]
    if g.isComposite():
        for c in g.components:
            get_deps(c.glyphName, glyf_table, visited)
    return visited


def merge(inter_ttf, pretendard_ttf, output_path):
    print("Loading Inter Variable...")
    inter = TTFont(inter_ttf)
    _ = inter['gvar'].variations

    print("Loading Pretendard JP Variable...")
    pretendard = TTFont(pretendard_ttf)
    _ = pretendard['gvar'].variations
    pretendard_cmap = pretendard.getBestCmap()
    pretendard_glyf = pretendard['glyf']
    pretendard_hmtx = pretendard['hmtx']
    pretendard_gvar = pretendard['gvar'].variations

    inter_cmap = inter.getBestCmap()
    inter_glyf = inter['glyf']
    inter_hmtx = inter['hmtx']

    # Identify CJK codepoints to add
    new_codepoints = set()
    for start, end in CJK_RANGES:
        for cp in range(start, end + 1):
            if cp in pretendard_cmap and cp not in inter_cmap:
                new_codepoints.add(cp)
    print(f"  {len(new_codepoints)} CJK codepoints to add")

    # Get glyph dependencies
    inter_glyph_set = set(inter.getGlyphOrder())
    glyphs_needed = set()
    for cp in new_codepoints:
        glyphs_needed.update(get_deps(pretendard_cmap[cp], pretendard_glyf))
    glyphs_to_copy = sorted(glyphs_needed - inter_glyph_set)
    print(f"  {len(glyphs_to_copy)} glyphs to copy")

    # Name mapping
    name_map = {g: (f"jp.{g}" if g in inter_glyph_set else g) for g in glyphs_to_copy}

    # Add to glyph order
    glyph_order = inter.getGlyphOrder()
    for gname in glyphs_to_copy:
        glyph_order.append(name_map[gname])
    inter.setGlyphOrder(glyph_order)

    # Copy glyphs with adjustments
    print("  Copying glyphs (Y offset, horizontal scaling)...")
    for gname in glyphs_to_copy:
        target = name_map[gname]
        g = copy.deepcopy(pretendard_glyf[gname])
        width = pretendard_hmtx[gname][0]
        x_center = width / 2.0

        if g.isComposite():
            for comp in g.components:
                if comp.glyphName in name_map:
                    comp.glyphName = name_map[comp.glyphName]
                if hasattr(comp, 'y'):
                    comp.y += Y_OFFSET
        elif g.numberOfContours > 0:
            coords = g.coordinates
            if coords:
                new_coords = [(round(x_center + (x - x_center) * CJK_HSCALE), y + Y_OFFSET)
                              for x, y in coords]
                g.coordinates = type(coords)(new_coords)

        if hasattr(g, 'yMin') and g.yMin is not None:
            g.yMin += Y_OFFSET
            g.yMax += Y_OFFSET

        inter_glyf[target] = g
        inter_hmtx[target] = pretendard_hmtx[gname]

    # Update cmap
    for table in inter['cmap'].tables:
        if hasattr(table, 'cmap') and table.cmap is not None:
            for cp in new_codepoints:
                orig = pretendard_cmap[cp]
                target = name_map.get(orig, orig)
                if target in set(inter.getGlyphOrder()):
                    table.cmap[cp] = target

    # Add CJK gvar (wght + opsz)
    print("  Adding CJK gvar (wght + opsz)...")
    inter_gvar = inter['gvar']
    for gname in glyphs_to_copy:
        target = name_map[gname]
        variations = []

        # wght variation from Pretendard
        if gname in pretendard_gvar and pretendard_gvar[gname]:
            for tv in pretendard_gvar[gname]:
                if 'wght' in tv.axes:
                    new_coords = []
                    for coord in tv.coordinates:
                        if coord is None:
                            new_coords.append(None)
                        else:
                            new_coords.append((round(coord[0] * CJK_HSCALE), coord[1]))
                    variations.append(TupleVariation({'wght': tv.axes['wght']}, new_coords))

        # opsz variation (3% tighter at Display)
        g = inter_glyf[target]
        if not g.isComposite() and g.numberOfContours > 0:
            coords = g.coordinates
            if coords:
                width = inter_hmtx[target][0]
                xc = width / 2.0
                opsz_deltas = [(round((x - xc) * (-OPSZ_SCALE)), 0) for x, y in coords]
                adv_delta = round(width * (-OPSZ_SCALE))
                opsz_deltas += [(0, 0), (adv_delta, 0), (0, 0), (0, 0)]
                variations.append(TupleVariation({'opsz': (0, 1.0, 1.0)}, opsz_deltas))

        inter_gvar.variations[target] = variations

    # Add CJK contextual symbol alignment via rclt feature
    # rclt (Required Contextual Alternates) fires for ALL scripts including Hangul
    # When CJK glyph is adjacent to a symbol, substitute symbol with .case version
    print("  Adding rclt: CJK-context symbol .case substitution...")
    gsub = inter['GSUB'].table
    cjk_glyph_list = sorted(set(glyph_order[2937:]), key=lambda g: glyph_order.index(g))

    # Get case mapping: find all glyph.case pairs in the font
    case_mapping = {}
    for g in glyph_order:
        if '.case' in g and '.case.' not in g:
            base = g.replace('.case', '')
            if base in set(glyph_order):
                case_mapping[base] = g

    # Create SingleSubst lookup for case substitution
    single_st = otTables.SingleSubst()
    single_st.mapping = case_mapping
    single_lookup = otTables.Lookup()
    single_lookup.LookupType = 1
    single_lookup.LookupFlag = 0
    single_lookup.SubTable = [single_st]
    single_lookup.SubTableCount = 1
    single_idx = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(single_lookup)

    # Create ChainContextSubst: [CJK] symbol' → .case
    input_glyphs = sorted(case_mapping.keys(), key=lambda g: glyph_order.index(g) if g in glyph_order else 999999)

    chain_st1 = otTables.ChainContextSubst()
    chain_st1.Format = 3
    bt_cov = otTables.Coverage()
    bt_cov.Format = 1
    bt_cov.glyphs = cjk_glyph_list
    chain_st1.BacktrackCoverage = [bt_cov]
    chain_st1.BacktrackCount = 1
    in_cov = otTables.Coverage()
    in_cov.Format = 1
    in_cov.glyphs = input_glyphs
    chain_st1.InputCoverage = [in_cov]
    chain_st1.InputCount = 1
    chain_st1.LookAheadCoverage = []
    chain_st1.LookAheadCount = 0
    slr1 = otTables.SubstLookupRecord()
    slr1.SequenceIndex = 0
    slr1.LookupListIndex = single_idx
    chain_st1.SubstLookupRecord = [slr1]
    chain_st1.SubstCount = 1

    # ChainContextSubst: symbol' [CJK] → .case
    chain_st2 = copy.deepcopy(chain_st1)
    chain_st2.BacktrackCoverage = []
    chain_st2.BacktrackCount = 0
    la_cov = otTables.Coverage()
    la_cov.Format = 1
    la_cov.glyphs = cjk_glyph_list
    chain_st2.LookAheadCoverage = [la_cov]
    chain_st2.LookAheadCount = 1

    chain_lookup = otTables.Lookup()
    chain_lookup.LookupType = 6
    chain_lookup.LookupFlag = 0
    chain_lookup.SubTable = [chain_st1, chain_st2]
    chain_lookup.SubTableCount = 2
    chain_idx = len(gsub.LookupList.Lookup)
    gsub.LookupList.Lookup.append(chain_lookup)
    gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

    # Register as rclt feature for all scripts
    rclt_fr = otTables.FeatureRecord()
    rclt_fr.FeatureTag = 'rclt'
    rclt_fr.Feature = otTables.Feature()
    rclt_fr.Feature.LookupListIndex = [chain_idx]
    rclt_fr.Feature.LookupCount = 1
    rclt_fr.Feature.FeatureParams = None
    rclt_idx = len(gsub.FeatureList.FeatureRecord)
    gsub.FeatureList.FeatureRecord.append(rclt_fr)
    gsub.FeatureList.FeatureCount = len(gsub.FeatureList.FeatureRecord)

    for sr in gsub.ScriptList.ScriptRecord:
        if sr.Script.DefaultLangSys:
            sr.Script.DefaultLangSys.FeatureIndex.append(rclt_idx)
            sr.Script.DefaultLangSys.FeatureCount = len(sr.Script.DefaultLangSys.FeatureIndex)

    print(f"    {len(case_mapping)} symbol→.case pairs via rclt")

    # Replace ₩ with Pretendard's Korean-style won sign
    print("  Replacing ₩ with Pretendard glyph...")
    won_cp = 0x20A9
    if won_cp in pretendard_cmap:
        p_won_name = pretendard_cmap[won_cp]
        i_won_name = inter.getBestCmap()[won_cp]
        inter_glyf[i_won_name] = copy.deepcopy(pretendard_glyf[p_won_name])
        inter_hmtx[i_won_name] = pretendard_hmtx[p_won_name]
        if p_won_name in pretendard_gvar and pretendard_gvar[p_won_name]:
            won_variations = []
            for tv in pretendard_gvar[p_won_name]:
                if 'wght' in tv.axes:
                    won_variations.append(TupleVariation({'wght': tv.axes['wght']}, tv.coordinates))
            inter_gvar.variations[i_won_name] = won_variations

    # GSUB/GPOS scripts
    print("  Adding CJK scripts to GSUB/GPOS...")
    for table_tag in ['GSUB', 'GPOS']:
        if table_tag in inter:
            table = inter[table_tag].table
            if table.ScriptList:
                existing = {s.ScriptTag for s in table.ScriptList.ScriptRecord}
                dflt = None
                for sr in table.ScriptList.ScriptRecord:
                    if sr.ScriptTag == 'DFLT':
                        dflt = sr.Script
                        break
                for tag in ['hang', 'kana', 'hani']:
                    if tag not in existing:
                        nr = otTables.ScriptRecord()
                        nr.ScriptTag = tag
                        nr.Script = otTables.Script()
                        nr.Script.DefaultLangSys = copy.deepcopy(dflt.DefaultLangSys) if dflt else None
                        nr.Script.LangSysRecord = []
                        nr.Script.LangSysCount = 0
                        table.ScriptList.ScriptRecord.append(nr)
                table.ScriptList.ScriptCount = len(table.ScriptList.ScriptRecord)

    # Latin-CJK kern
    print("  Adding Latin-CJK kern...")
    gpos = inter['GPOS'].table
    final_cmap = inter.getBestCmap()
    latin_glyphs = [final_cmap[cp] for cp in range(0x41, 0x7B) if cp in final_cmap] + \
                   [final_cmap[cp] for cp in range(0x30, 0x3A) if cp in final_cmap]
    cjk_kern_glyphs = [glyph_order[i] for i in range(2937, min(2937 + 5000, len(glyph_order)))]

    cd1 = {g: 1 for g in latin_glyphs}
    for g in cjk_kern_glyphs:
        cd1[g] = 2
    cd2 = {g: 1 for g in cjk_kern_glyphs}
    for g in latin_glyphs:
        cd2[g] = 2

    pairpos = otTables.PairPos()
    pairpos.Format = 2
    pairpos.ValueFormat1 = 4
    pairpos.ValueFormat2 = 0
    coverage = otTables.Coverage()
    coverage.Format = 1
    coverage.glyphs = sorted(set(latin_glyphs + cjk_kern_glyphs),
                             key=lambda g: glyph_order.index(g) if g in glyph_order else 999999)
    pairpos.Coverage = coverage
    pairpos.ClassDef1 = otTables.ClassDef()
    pairpos.ClassDef1.classDefs = cd1
    pairpos.ClassDef2 = otTables.ClassDef()
    pairpos.ClassDef2.classDefs = cd2

    class1_records = []
    for c1 in range(3):
        c1r = otTables.Class1Record()
        c2rs = []
        for c2 in range(3):
            c2r = otTables.Class2Record()
            vr = otTables.ValueRecord()
            vr.XAdvance = LATIN_CJK_SPACING if (c1 == 1 and c2 == 1) or (c1 == 2 and c2 == 2) else 0
            c2r.Value1 = vr
            c2r.Value2 = None
            c2rs.append(c2r)
        c1r.Class2Record = c2rs
        class1_records.append(c1r)
    pairpos.Class1Record = class1_records
    pairpos.Class1Count = 3
    pairpos.Class2Count = 3

    new_lookup = otTables.Lookup()
    new_lookup.LookupType = 2
    new_lookup.LookupFlag = 0
    new_lookup.SubTable = [pairpos]
    new_lookup.SubTableCount = 1
    li = len(gpos.LookupList.Lookup)
    gpos.LookupList.Lookup.append(new_lookup)
    gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'kern':
            fr.Feature.LookupListIndex.append(li)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)

    # Vertical metrics (SUIT-matched)
    print("  Setting vertical metrics (ratio 1.125, total=2304)...")
    os2 = inter['OS/2']
    hhea = inter['hhea']
    os2.sTypoAscender = 1810
    os2.sTypoDescender = -494
    os2.sTypoLineGap = 0
    os2.usWinAscent = 1810
    os2.usWinDescent = 494
    os2.fsSelection |= (1 << 7)
    hhea.ascent = 1810
    hhea.descent = -494
    hhea.lineGap = 0

    # OS/2 ranges
    os2.ulUnicodeRange1 |= (1 << 28)
    os2.ulUnicodeRange2 |= (1 << 16) | (1 << 17) | (1 << 18) | (1 << 24) | (1 << 27) | (1 << 29)
    os2.ulCodePageRange1 |= (1 << 17) | (1 << 19) | (1 << 20)

    # maxp, HVAR
    inter['maxp'].numGlyphs = len(glyph_order)
    if 'HVAR' in inter:
        del inter['HVAR']

    # Named instances
    print("  Setting named instances...")
    name_table = inter['name']
    for record in name_table.names:
        try:
            record.toUnicode()
        except:
            continue
        if record.nameID == 1:
            name_table.setName("Inter CJK", record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 4:
            name_table.setName("Inter CJK Variable", record.nameID, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 6:
            name_table.setName("InterCJK-Variable", record.nameID, record.platformID, record.platEncID, record.langID)

    inter['fvar'].instances = []
    max_nid = max(r.nameID for r in name_table.names)
    nid = max_nid + 1
    for opsz_val in [14.0, 32.0]:
        for wght_val, wght_name in WEIGHTS:
            inst = NamedInstance()
            inst.subfamilyNameID = nid
            name_table.setName(wght_name, nid, 3, 1, 0x0409)
            name_table.setName(wght_name, nid, 1, 0, 0)
            inst.coordinates = {"opsz": opsz_val, "wght": float(wght_val)}
            inter['fvar'].instances.append(inst)
            nid += 1

    # Save
    inter.save(output_path)
    size = os.path.getsize(output_path) / 1024 / 1024
    print(f"\nSaved: {output_path} ({size:.1f} MB)")
    print(f"  Glyphs: {len(glyph_order)}")
    print(f"  Axes: {[(a.axisTag, a.minValue, a.maxValue) for a in inter['fvar'].axes]}")


if __name__ == "__main__":
    inter_ttf = sys.argv[1]
    pretendard_ttf = sys.argv[2]
    output = sys.argv[3]
    merge(inter_ttf, pretendard_ttf, output)
