"""Add Pretendard-style ss05, ss06, ss10-ss16 features to Inter CJK.

Copies variant glyphs (.hang, .medium, .large, .small, PUA) from Pretendard
and adds GSUB lookups for stylistic sets.
"""
import copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables


def add_pretendard_ss_features(inter, pretendard_font, glyph_order):
    pretendard_glyf = pretendard_font['glyf']
    pretendard_hmtx = pretendard_font['hmtx']
    pretendard_gvar = pretendard_font['gvar'].variations
    pretendard_gsub = pretendard_font['GSUB'].table
    inter_glyf = inter['glyf']
    inter_hmtx = inter['hmtx']
    inter_gvar = inter['gvar']
    inter_glyph_set = set(glyph_order)

    # Collect all variant glyphs needed from Pretendard
    needed_glyphs = set()
    pret_go = pretendard_font.getGlyphOrder()

    for g in pret_go:
        if any(x in g for x in ['.medium', '.large', '.small', '.hang']):
            if g not in inter_glyph_set:
                needed_glyphs.add(g)

    # PUA glyphs from ss06 and all other ss features
    for fr in pretendard_gsub.FeatureList.FeatureRecord:
        if fr.FeatureTag.startswith('ss'):
            for li in fr.Feature.LookupListIndex:
                lookup = pretendard_gsub.LookupList.Lookup[li]
                for st in lookup.SubTable:
                    if hasattr(st, 'mapping'):
                        for src, dst in st.mapping.items():
                            if dst not in inter_glyph_set:
                                needed_glyphs.add(dst)
                            if src not in inter_glyph_set:
                                needed_glyphs.add(src)

    print(f"    Copying {len(needed_glyphs)} variant glyphs from Pretendard...")

    # Also collect component dependencies
    def get_deps(gname, glyf_table, visited=None):
        if visited is None:
            visited = set()
        if gname in visited or gname not in glyf_table.glyphs:
            return visited
        visited.add(gname)
        g = glyf_table[gname]
        if g.isComposite():
            for c in g.components:
                get_deps(c.glyphName, glyf_table, visited)
        return visited

    all_needed = set()
    for gname in needed_glyphs:
        if gname in pretendard_glyf.glyphs:
            all_needed.update(get_deps(gname, pretendard_glyf))
    all_needed = {g for g in all_needed if g not in inter_glyph_set}

    # Copy glyphs
    for gname in sorted(all_needed):
        if gname not in pretendard_glyf.glyphs:
            continue
        glyph_order.append(gname)
        inter_glyf[gname] = copy.deepcopy(pretendard_glyf[gname])
        inter_hmtx[gname] = pretendard_hmtx[gname]
        if gname in pretendard_gvar and pretendard_gvar[gname]:
            from fontTools.ttLib.tables.TupleVariation import TupleVariation
            new_vars = []
            for tv in pretendard_gvar[gname]:
                if 'wght' in tv.axes:
                    new_vars.append(TupleVariation({'wght': tv.axes['wght']}, tv.coordinates))
            inter_gvar.variations[gname] = new_vars
        else:
            inter_gvar.variations[gname] = []

    inter.setGlyphOrder(glyph_order)
    inter['maxp'].numGlyphs = len(glyph_order)

    # Build ss lookup mappings from Pretendard
    gsub = inter['GSUB'].table
    inter_glyph_set = set(glyph_order)
    inter_glyph_set = set(glyph_order)

    ss_configs = []
    for tag in ['ss05', 'ss06', 'ss10', 'ss11', 'ss12', 'ss13', 'ss14', 'ss15', 'ss16']:
        for fr in pretendard_gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag == tag:
                mapping = {}
                for li in fr.Feature.LookupListIndex:
                    lookup = pretendard_gsub.LookupList.Lookup[li]
                    for st in lookup.SubTable:
                        if hasattr(st, 'mapping'):
                            for src, dst in st.mapping.items():
                                if src in inter_glyph_set and dst in inter_glyph_set:
                                    mapping[src] = dst
                if mapping:
                    ss_configs.append((tag, mapping))
                break

    # Add lookups to GSUB
    for tag, mapping in ss_configs:
        single_st = otTables.SingleSubst()
        single_st.mapping = mapping

        new_lookup = otTables.Lookup()
        new_lookup.LookupType = 1
        new_lookup.LookupFlag = 0
        new_lookup.SubTable = [single_st]
        new_lookup.SubTableCount = 1

        lookup_idx = len(gsub.LookupList.Lookup)
        gsub.LookupList.Lookup.append(new_lookup)
        gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

        # Check if feature already exists
        existing = None
        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag == tag:
                existing = fr
                break

        if existing:
            existing.Feature.LookupListIndex.append(lookup_idx)
            existing.Feature.LookupCount = len(existing.Feature.LookupListIndex)
        else:
            new_fr = otTables.FeatureRecord()
            new_fr.FeatureTag = tag
            new_fr.Feature = otTables.Feature()
            new_fr.Feature.LookupListIndex = [lookup_idx]
            new_fr.Feature.LookupCount = 1
            new_fr.Feature.FeatureParams = None

            feat_idx = len(gsub.FeatureList.FeatureRecord)
            gsub.FeatureList.FeatureRecord.append(new_fr)
            gsub.FeatureList.FeatureCount = len(gsub.FeatureList.FeatureRecord)

            for sr in gsub.ScriptList.ScriptRecord:
                if sr.Script.DefaultLangSys:
                    sr.Script.DefaultLangSys.FeatureIndex.append(feat_idx)
                    sr.Script.DefaultLangSys.FeatureCount = len(sr.Script.DefaultLangSys.FeatureIndex)

        print(f"    {tag}: {len(mapping)} substitution pairs")
