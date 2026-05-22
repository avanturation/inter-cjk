SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
FONTDIR  := build/fonts
UFODIR   := build/ufo
VERSION  := $(shell cat version.txt)

default: variable

# ---------------------------------------------------------------------------------
# Variable fonts

variable: $(FONTDIR)/InterCJK-Variable.ttf

$(FONTDIR)/InterCJK-Variable.ttf: src/InterCJK.glyphspackage src/features/*.fea | $(FONTDIR)
	fontmake -g src/InterCJK.glyphspackage \
		-o variable \
		--output-path $@ \
		--verbose WARNING

# ---------------------------------------------------------------------------------
# Static fonts (instances)

static: static-ttf

static-ttf: $(FONTDIR)/static/ttf/.ok

$(FONTDIR)/static/ttf/.ok: src/InterCJK.glyphspackage src/features/*.fea | $(FONTDIR)/static/ttf
	fontmake -g src/InterCJK.glyphspackage \
		-o ttf \
		--output-dir $(FONTDIR)/static/ttf \
		--verbose WARNING
	touch $@

# ---------------------------------------------------------------------------------
# Directories

$(FONTDIR):
	mkdir -p $@

$(FONTDIR)/static/ttf:
	mkdir -p $@

# ---------------------------------------------------------------------------------
# Clean

clean:
	rm -rf build

.PHONY: default variable static static-ttf clean
