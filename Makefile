SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
VERSION  := $(shell cat version.txt)
DISTDIR  := build/InterCJK-$(VERSION)

INTER_SRC     := src/inter/src/Inter-Roman.glyphspackage
PRETENDARD_SRC := src/pretendard/src/PretendardJP.glyphspackage

default: all

all: variable static web dynamic-subset

# ---------------------------------------------------------------------------------
# Source variable fonts (built from submodule sources)

build/inter-variable.ttf: $(INTER_SRC) | build
	cd src/inter && python3 -m fontmake -g src/Inter-Roman.glyphspackage \
		-o variable \
		--output-path ../../$@ \
		--verbose WARNING

build/pretendard-variable.ttf: | build
	curl -L -o build/pretendard-jp.zip \
		"https://github.com/orioncactus/pretendard/releases/download/v1.3.9/PretendardJP-1.3.9.zip"
	unzip -o build/pretendard-jp.zip "public/variable/PretendardJPVariable.ttf" -d build/
	mv build/public/variable/PretendardJPVariable.ttf $@
	rm -rf build/pretendard-jp.zip build/public

# ---------------------------------------------------------------------------------
# Merged full variable (opsz + wght)

build/InterCJK-full.ttf: build/inter-variable.ttf build/pretendard-variable.ttf misc/build-full.py
	python3 misc/build-full.py $< build/pretendard-variable.ttf $@

# ---------------------------------------------------------------------------------
# Split into Text + Display (pins opsz via instancer)

variable: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf

$(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf: build/InterCJK-full.ttf misc/split-opsz.py | $(DISTDIR)
	python3 misc/split-opsz.py $< $(DISTDIR)

# ---------------------------------------------------------------------------------
# Static fonts (instancer per weight)

static: $(DISTDIR)/extras/ttf/.ok

$(DISTDIR)/extras/ttf/.ok: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf misc/gen-static.py | $(DISTDIR)/extras/ttf
	python3 misc/gen-static.py \
		$(DISTDIR)/InterCJKVariable.ttf \
		$(DISTDIR)/InterCJKDisplayVariable.ttf \
		$(DISTDIR)/extras/ttf
	touch $@

# ---------------------------------------------------------------------------------
# Web fonts (WOFF2)

web: $(DISTDIR)/web/.ok

$(DISTDIR)/web/.ok: $(DISTDIR)/InterCJKVariable.ttf $(DISTDIR)/InterCJKDisplayVariable.ttf $(DISTDIR)/extras/ttf/.ok | $(DISTDIR)/web
	python3 -m fontTools ttLib.woff2 compress $(DISTDIR)/InterCJKVariable.ttf \
		-o $(DISTDIR)/web/InterCJKVariable.woff2
	python3 -m fontTools ttLib.woff2 compress $(DISTDIR)/InterCJKDisplayVariable.ttf \
		-o $(DISTDIR)/web/InterCJKDisplayVariable.woff2
	@for f in $(DISTDIR)/extras/ttf/*.ttf; do \
		name=$$(basename "$$f" .ttf); \
		python3 -m fontTools ttLib.woff2 compress "$$f" -o "$(DISTDIR)/web/$$name.woff2"; \
	done
	cp misc/inter-cjk.css $(DISTDIR)/web/inter-cjk.css
	touch $@

# ---------------------------------------------------------------------------------
# Dynamic subset (unicode-range split for fast web loading)

PRETENDARD_CSS := src/pretendard/dist/web/variable/pretendardvariable-jp-dynamic-subset.css

dynamic-subset: $(DISTDIR)/web/dynamic-subset/.ok $(DISTDIR)/web/dynamic-subset-display/.ok

$(DISTDIR)/web/dynamic-subset/.ok: $(DISTDIR)/InterCJKVariable.ttf misc/gen-dynamic-subset.py | $(DISTDIR)/web/dynamic-subset
	python3 misc/gen-dynamic-subset.py \
		$(DISTDIR)/InterCJKVariable.ttf \
		$(PRETENDARD_CSS) \
		$(DISTDIR)/web/dynamic-subset \
		"Inter CJK Variable" \
		"inter-cjk-variable-dynamic-subset.css"
	touch $@

$(DISTDIR)/web/dynamic-subset-display/.ok: $(DISTDIR)/InterCJKDisplayVariable.ttf misc/gen-dynamic-subset.py | $(DISTDIR)/web/dynamic-subset-display
	python3 misc/gen-dynamic-subset.py \
		$(DISTDIR)/InterCJKDisplayVariable.ttf \
		$(PRETENDARD_CSS) \
		$(DISTDIR)/web/dynamic-subset-display \
		"Inter CJK Display Variable" \
		"inter-cjk-display-variable-dynamic-subset.css"
	touch $@

$(DISTDIR)/web/dynamic-subset:
	mkdir -p $@

$(DISTDIR)/web/dynamic-subset-display:
	mkdir -p $@

# ---------------------------------------------------------------------------------
# Package

package: all $(DISTDIR)/LICENSE.txt $(DISTDIR)/help.txt
	cd build && zip -r InterCJK-$(VERSION).zip InterCJK-$(VERSION)/

$(DISTDIR)/LICENSE.txt: LICENSE.txt | $(DISTDIR)
	cp $< $@

$(DISTDIR)/help.txt: misc/help.txt | $(DISTDIR)
	cp $< $@

# ---------------------------------------------------------------------------------
# Setup

setup:
	git submodule update --init --depth 1
	pip install -r requirements.txt

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

.PHONY: default all variable static web package setup clean
