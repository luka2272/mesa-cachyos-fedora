.DEFAULT_GOAL=help

# See ~/.config/mock/<CONFIG>.cfg or /etc/mock/<CONFIG>.cfg
# Tweak this to centos-stream-9-x86_64 to build for CentOS
MOCK_CHROOT?=fedora-rawhide-x86_64
MOCK_OPTS?=
MOCK_OPTS_RELEASE?=--no-clean --no-cleanup-after $(MOCK_OPTS)
MOCK_OPTS_SNAPSHOT?=$(MOCK_OPTS_RELEASE) --with snapshot_build $(MOCK_OPTS)
YYYYMMDD=$(shell date +%Y%m%d)
SOURCEDIR=$(shell pwd)
SPEC=llvm.spec
# When nothing is given, this will be determined based on
# release or snapshot builds.
SRPM_PATH?=

######### Get sources

.PHONY: get-sources-snapshot
## Downloads all sources we need for a snapshot build.
get-sources-snapshot:
	YYYYMMDD=$(YYYYMMDD) ./.copr/snapshot-info.sh > $(SOURCEDIR)/version.spec.inc
	spectool -g --define "_sourcedir $(SOURCEDIR)" --define "_with_snapshot_build 1" $(SPEC)

.PHONY: get-sources-release
## Downloads all sources we need for a release build.
get-sources-release:
	spectool -g --define "_sourcedir $(SOURCEDIR)" $(SPEC)

######### Build SRPM

.PHONY: srpm-release
## Builds an SRPM that can be used for a release build.
srpm-release: get-sources-release
	rpmbuild \
		--define "_rpmdir $(SOURCEDIR)" \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SOURCEDIR)" \
		--define "_srcrpmdir $(SOURCEDIR)" \
		--define "_builddir $(SOURCEDIR)" \
		-bs $(SPEC)

.PHONY: srpm-snapshot
## Builds an SRPM that can be used for a snapshot build.
srpm-snapshot: get-sources-snapshot
	rpmbuild \
		--with=snapshot_build \
		--define "_rpmdir $(SOURCEDIR)" \
		--define "_sourcedir $(SOURCEDIR)" \
		--define "_specdir $(SOURCEDIR)" \
		--define "_srcrpmdir $(SOURCEDIR)" \
		--define "_builddir $(SOURCEDIR)" \
		-bs $(SPEC)

######### Scrub mock chroot and cache

.PHONY: scrub-chroot
## Completely remove the fedora chroot and cache.
scrub-chroot:
	mock -r $(MOCK_CHROOT) --scrub all

######### Do a mock build

.PHONY: mockbuild-release
## Start a mock build of the release SRPM.
mockbuild-release: srpm-release get-srpm-release
	mock -r $(MOCK_CHROOT) $(MOCK_OPTS_RELEASE) $(srpm_path)

.PHONY: mockbuild-snapshot
## Start a mock build of the snapshot SRPM.
mockbuild-snapshot: srpm-snapshot get-srpm-snapshot
	mock -r $(MOCK_CHROOT) $(MOCK_OPTS_SNAPSHOT) $(srpm_path)

######### Edit-last-failing-script

.PHONY: get-last-run-script
## Get the file that was last modified in /var/tmp/ within the chroot.
get-last-run-script:
	$(eval last_run_script:=/var/tmp/$(shell ls -t1 /var/lib/mock/$(MOCK_CHROOT)/root/var/tmp | head -n1))
	$(info last_run_script=$(last_run_script))
	@echo > /dev/null

.PHONY: edit-last-failing-script
## Opens the last failing or running script from mock in your editor
## of choice for you to edit it and later re-run it in mock with:
## "make mockbuild-rerun-last-script".
edit-last-failing-script: get-last-run-script
	$$EDITOR /var/lib/mock/$(MOCK_CHROOT)/root$(last_run_script)

######### Re-run the last failing script from mock

.PHONY: mockbuild-rerun-last-script
## Re-runs the last failing or running script of your release/snapshot mock mockbuild.
mockbuild-rerun-last-script: get-last-run-script
	mock --root=$(MOCK_CHROOT) --shell 'sh -e $(last_run_script)'

.PHONY: help
# Based on https://gist.github.com/rcmachado/af3db315e31383502660
## Display this help text.
help:/
	$(info Available targets)
	$(info -----------------)
	@awk '/^[a-zA-Z\-0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		helpCommand = substr($$1, 0, index($$1, ":")-1); \
		if (helpMessage) { \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub(/##/, "\n                                       ", helpMessage); \
		} else { \
			helpMessage = "(No documentation)"; \
		} \
		printf "%-37s - %s\n", helpCommand, helpMessage; \
		lastLine = "" \
	} \
	{ hasComment = match(lastLine, /^## (.*)/); \
          if(hasComment) { \
            lastLine=lastLine$$0; \
	  } \
          else { \
	    lastLine = $$0 \
          } \
        }' $(MAKEFILE_LIST)

######### Deprecated targets

# Map deprecated targets to new targets
.PHONY: snapshot-srpm release-srpm
snapshot-srpm release-srpm:
	$(eval mapped_target:=$(subst snapshot-srpm,srpm-snapshot,$(MAKECMDGOALS)))
	$(eval mapped_target:=$(subst release-srpm,srpm-release,$(mapped_target)))
	$(info WARNING: "$(MAKECMDGOALS)" is deprecated. Instead running "$(mapped_target)")
	$(MAKE) $(mapped_target)

######### Version/Release helper targets to build name of SRPM

.PHONY: get-llvm-version-release
## Determines the LLVM version given in the llvm.spec file.
get-llvm-version-release:
	$(eval llvm_version_release:=$(shell grep -ioP "%global\s+(maj|min|patch)_ver[^0-9]\K[0-9]+" $(SPEC) | paste -sd'.'))
	$(info LLVM Release Version: $(llvm_version_release))
	@echo > /dev/null

.PHONY: get-llvm-version-snapshot
## Determines the LLVM version given in the version.spec.inc file.
get-llvm-version-snapshot:
	$(eval llvm_version_snapshot:=$(shell grep -ioP "%global\s+(maj|min|patch)_ver[^0-9]\K[0-9]+" version.spec.inc | paste -sd'.'))
	$(info LLVM Snapshot Version: $(llvm_version_snapshot))
	@echo > /dev/null

.PHONY: get-spec-file-release
## Parses the spec file for the Release: tag
get-spec-file-release:
	$(eval spec_file_release:=$(shell grep -ioP '^Release:\s*\K[0-9]+' $(SPEC)))
	$(info LLVM Spec file Release: $(spec_file_release))
	@echo > /dev/null

.PHONY: get-srpm-release
## Determines the name of the SRPM used for release builds
## Can be overriden by giving "make ... SRPM_PATH=foo.src.rpm".
get-srpm-release: get-llvm-version-release get-spec-file-release
ifeq ($(SRPM_PATH),)
	$(eval srpm_path:=llvm-$(llvm_version_release)-$(spec_file_release).*.src.rpm)
else
	$(eval srpm_path:=$(SRPM_PATH))
endif
	$(info LLVM SRPM Release: $(srpm_path))
	@echo > /dev/null

.PHONY: get-srpm-snapshot
## Determines the name of the SRPM used for snapshot builds
## Can be overriden by giving "make ... SRPM_PATH=foo.src.rpm".
get-srpm-snapshot: get-llvm-version-snapshot get-spec-file-release
ifeq ($(SRPM_PATH),)
	$(eval yyyymmdd:=$(shell grep -ioP "%global\s+llvm_snapshot_yyyymmdd\s+\K[0-9]+" version.spec.inc))
	$(eval git_short:=$(shell grep -ioP "%global\s+llvm_snapshot_git_revision_short\s+\K[a-zA-Z0-9]+" version.spec.inc))
	$(eval srpm_path:=llvm-$(llvm_version_snapshot)~pre$(yyyymmdd).g$(git_short)-$(spec_file_release).*.src.rpm)
else
	$(eval srpm_path:=$(SRPM_PATH))
endif
	$(info LLVM SRPM Snapshot: $(srpm_path))
	@echo > /dev/null
