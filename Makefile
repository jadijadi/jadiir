# Theme switcher. Themes in trial: archie, papermod, gruvbox.
#   make serve THEME=gruvbox
#   make build THEME=gruvbox
THEME ?= gruvbox
CONFIG = hugo.toml,config-$(THEME).toml

.PHONY: serve build publish

serve:
	hugo server --config $(CONFIG)

build:
	hugo --cleanDestinationDir --gc --config $(CONFIG)

publish: build
	ghp-import public
	git push origin gh-pages
