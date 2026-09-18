# Thin wrappers around `uv run --project tools lqcowork ...`.
#
#   make setup      install the build tooling
#   make package    build + validate + zip + trigger tests + report
#   make drift      report what moved upstream, without moving the pin
#
# Optional variables:
#   BUNDLE=legalquants-litigation-cowork   restrict build/validate/package/triggers
#   TO=origin/main                         the ref bump/drift resolve
#   SKILL=wiki                             restrict anchor
#   REPORT=dist/upstream-drift.md          where drift/bump write the report

UV ?= uv
LQ := $(UV) run --project tools lqcowork
PYTEST := $(UV) run --project tools pytest
BLACK := $(UV) run --project tools black

BUNDLE ?=
TO ?= origin/main
SKILL ?=
REPORT ?=

BUNDLE_ARG := $(if $(BUNDLE),--bundle $(BUNDLE),)
SKILL_ARG := $(if $(SKILL),--skill $(SKILL),)
REPORT_ARG := $(if $(REPORT),--report $(REPORT),)

.PHONY: setup build validate package triggers drift bump anchor test fmt clean help

help:
	@grep -E '^[a-z-]+:' Makefile | cut -d: -f1 | grep -v '^help$$' | sort

setup:
	$(UV) sync --project tools

build:
	$(LQ) build $(BUNDLE_ARG)

validate:
	$(LQ) validate $(BUNDLE_ARG)

package:
	$(LQ) package $(BUNDLE_ARG)

triggers:
	$(LQ) triggers $(BUNDLE_ARG)

drift:
	$(LQ) bump-upstream --dry-run --to $(TO) $(REPORT_ARG)

bump:
	$(LQ) bump-upstream --to $(TO) $(REPORT_ARG)

anchor:
	$(LQ) anchor $(SKILL_ARG)

test:
	$(PYTEST) tools/tests

fmt:
	$(BLACK) tools

clean:
	rm -rf dist
