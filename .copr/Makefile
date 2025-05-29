NAME = mesa
SPEC = mesa.spec
VERSION := $(shell grep ^Version: $(SPEC) | awk '{print $$2}')
SRPMDIR := .

all:
	rpmbuild -bs .copr/$(SPEC) --define \"_sourcedir $(PWD)/sources\" --define \"_srcrpmdir $(SRPMDIR)\"

