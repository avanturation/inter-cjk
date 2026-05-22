SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
VERSION  := $(shell cat version.txt)
DISTDIR  := build/InterCJK-$(VERSION)

default: all

all: variable static web

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
# Static fonts (from variable via instancer)

static: $(DISTDIR)/extras/ttf/.ok

$(DISTDIR)/extras/ttf/.ok: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf | $(DISTDIR)/extras/ttf
	python3 misc/gen-static.py \
		$(DISTDIR)/InterCJKVariable.ttf \
		$(DISTDIR)/InterCJKDisplayVariable.ttf \
		$(DISTDIR)/extras/ttf
	touch $@

# ---------------------------------------------------------------------------------
# Web fonts (WOFF2 variable + static)

web: $(DISTDIR)/web/.ok

$(DISTDIR)/web/.ok: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf $(DISTDIR)/extras/ttf/.ok | $(DISTDIR)/web
	fonttools ttLib.woff2 compress $(DISTDIR)/InterCJKVariable.ttf \
		-o $(DISTDIR)/web/InterCJKVariable.woff2
	fonttools ttLib.woff2 compress $(DISTDIR)/InterCJKDisplayVariable.ttf \
		-o $(DISTDIR)/web/InterCJKDisplayVariable.woff2
	@for f in $(DISTDIR)/extras/ttf/*.ttf; do \
		name=$$(basename "$$f" .ttf); \
		fonttools ttLib.woff2 compress "$$f" -o "$(DISTDIR)/web/$$name.woff2"; \
	done
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

$(DISTDIR)/web:
	mkdir -p $@

# ---------------------------------------------------------------------------------
# Clean

clean:
	rm -rf build

.PHONY: default all variable static web package clean
