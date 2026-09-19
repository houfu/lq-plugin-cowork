# Thin wrappers around `uv run --project tools lqcowork ...`.
#
#   make setup          install the build tooling
#   make package        build + validate + zip + archives + trigger tests + report
#   make archives       upload-ready dist/skills/<name>.skill from a build
#   make drift          report what moved upstream, without moving the pin
#   make fmt-check      black --check, the formatting gate CI runs
#   make release-check  does TAG agree with cowork.yaml, CHANGELOG.md and dist/?
#   make release        check TAG, tag this commit, push the tag; CI publishes
#
# Optional variables:
#   BUNDLE=legalquants-litigation-cowork   restrict build/validate/package/archives/triggers
#   TO=origin/main                         the ref bump/drift resolve
#   SKILL=wiki                             restrict anchor
#   REPORT=dist/upstream-drift.md          where drift/bump write the report
#
# Required by release-check and release:
#   TAG=v0.1.0                             the release tag (docs/RELEASING.md)

UV ?= uv
LQ := $(UV) run --project tools lqcowork
PYTEST := $(UV) run --project tools pytest
BLACK := $(UV) run --project tools black

BUNDLE ?=
TO ?= origin/main
SKILL ?=
REPORT ?=
TAG ?=

BUNDLE_ARG := $(if $(BUNDLE),--bundle $(BUNDLE),)
SKILL_ARG := $(if $(SKILL),--skill $(SKILL),)
REPORT_ARG := $(if $(REPORT),--report $(REPORT),)

.PHONY: setup build validate package archives triggers drift bump anchor test \
        fmt fmt-check release-check release clean help

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

archives:
	$(LQ) archives $(BUNDLE_ARG)

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

fmt-check:
	$(BLACK) --check tools

release-check:
	@test -n "$(TAG)" || { \
	  echo "make release-check TAG=vX.Y.Z  (the tag to check)" >&2; exit 1; }
	$(LQ) release-check --tag $(TAG)

# Everything a release needs before the tag exists: a clean tree, a tag nobody
# has used, and a tag the tree agrees with. Pushing the tag is the whole
# release trigger — .github/workflows/release.yml does the rest.
release:
	@set -eu; \
	tag='$(TAG)'; \
	test -n "$$tag" || { \
	  echo "make release TAG=vX.Y.Z  (the tag to publish)" >&2; exit 1; }; \
	dirty="$$(git status --porcelain)"; \
	if [ -n "$$dirty" ]; then \
	  echo "refusing to release: the working tree is not clean" >&2; \
	  echo "$$dirty" >&2; \
	  exit 1; \
	fi; \
	if git rev-parse -q --verify "refs/tags/$$tag" >/dev/null; then \
	  echo "refusing to release: tag $$tag already exists here" >&2; \
	  echo "to re-publish it, run the release workflow from the Actions tab" >&2; \
	  exit 1; \
	fi; \
	if [ -n "$$(git ls-remote --tags origin "refs/tags/$$tag")" ]; then \
	  echo "refusing to release: tag $$tag already exists on origin" >&2; \
	  echo "to re-publish it, run the release workflow from the Actions tab" >&2; \
	  exit 1; \
	fi; \
	$(MAKE) --no-print-directory release-check TAG="$$tag"; \
	git tag -a "$$tag" -m "$$tag"; \
	git push origin "refs/tags/$$tag"; \
	echo "pushed $$tag; the release workflow builds and publishes the assets"

clean:
	rm -rf dist
