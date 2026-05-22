SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
VERSION  := $(shell cat version.txt)
DISTDIR  := build/InterCJK-$(VERSION)

default: all

all: variable web

# ---------------------------------------------------------------------------------
# Variable fonts (split opsz into 2 files)

variable: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf

build/InterCJK-full.ttf: src/InterCJK.glyphspackage src/features/*.fea | build
	fontmake -g src/InterCJK.glyphspackage \
		-o variable \
		--output-path $@ \
		--verbose WARNING

$(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf: build/InterCJK-full.ttf | $(DISTDIR)
	python3 misc/split-opsz.py $< $(DISTDIR)

# ---------------------------------------------------------------------------------
# Static fonts (instances)

static: static-ttf static-otf

static-ttf: $(DISTDIR)/extras/ttf/.ok

$(DISTDIR)/extras/ttf/.ok: src/InterCJK.glyphspackage src/features/*.fea | $(DISTDIR)/extras/ttf
	fontmake -g src/InterCJK.glyphspackage \
		-o ttf \
		--output-dir $(DISTDIR)/extras/ttf \
		--verbose WARNING
	touch $@

static-otf: $(DISTDIR)/extras/otf/.ok

$(DISTDIR)/extras/otf/.ok: src/InterCJK.glyphspackage src/features/*.fea | $(DISTDIR)/extras/otf
	fontmake -g src/InterCJK.glyphspackage \
		-o otf \
		--output-dir $(DISTDIR)/extras/otf \
		--verbose WARNING
	touch $@

# ---------------------------------------------------------------------------------
# Web fonts (WOFF2)

web: $(DISTDIR)/web/.ok

$(DISTDIR)/web/.ok: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf | $(DISTDIR)/web
	fonttools ttLib.woff2 compress $(DISTDIR)/InterCJKVariable.ttf \
		-o $(DISTDIR)/web/InterCJKVariable.woff2
	fonttools ttLib.woff2 compress $(DISTDIR)/InterCJKDisplayVariable.ttf \
		-o $(DISTDIR)/web/InterCJKDisplayVariable.woff2
	cp misc/inter-cjk.css $(DISTDIR)/web/inter-cjk.css
	touch $@

# ---------------------------------------------------------------------------------
# Package (zip for release)

package: all $(DISTDIR)/LICENSE.txt $(DISTDIR)/help.txt
	cd build && zip -r InterCJK-$(VERSION).zip InterCJK-$(VERSION)/

$(DISTDIR)/LICENSE.txt: LICENSE.txt | $(DISTDIR)
	cp $< $@

$(DISTDIR)/help.txt: misc/help.txt | $(DISTDIR)
	cp $< $@

# ---------------------------------------------------------------------------------
# Directories

build:
	mkdir -p $@

$(DISTDIR):
	mkdir -p $@

$(DISTDIR)/extras/ttf:
	mkdir -p $@

$(DISTDIR)/extras/otf:
	mkdir -p $@

$(DISTDIR)/web:
	mkdir -p $@

# ---------------------------------------------------------------------------------
# Clean

clean:
	rm -rf build

.PHONY: default all variable static static-ttf static-otf web package clean
