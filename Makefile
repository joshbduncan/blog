.DEFAULT_GOAL := help
.PHONY: help
##@ General
help: ## Display this help section
	@echo $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development
imgspecs: imgspecs.sh ## get all static image file dimensions
	find app/static/images -type f -name "[^.]*" | sort | ./imgspecs.sh

server: ## startup the dev server
	uv run flask run

shell: ## startup the flask shell
	uv run flask shell

test-freeze: # freeze the blog and start up dev server on static files
	uv run python blog.py --run

##@ Build
build: ## freeze the blog for deployment
	uv run python blog.py --build
	esbuild build/static/css/styles.css --target=chrome90 --outfile=build/static/css/styles.css --allow-overwrite

render: ## freeze the blog for deployment on render
	uv run python blog.py --build
	npm install esbuild
	esbuild build/static/css/styles.css --target=chrome90 --outfile=build/static/css/styles.css --allow-overwrite
