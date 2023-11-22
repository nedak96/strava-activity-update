.PHONY: tf-plan tf-apply format check get-token, requirements-export

tf-init:
	@terraform -chdir=terraform init

tf-plan:
	@terraform -chdir=terraform plan

tf-apply:
	@terraform -chdir=terraform apply

format:
	@terraform -chdir=terraform fmt
	@ruff format lambda scripts tests
	@ruff check lambda scripts tests --fix

check:
	@mypy
	@ruff check lambda scripts tests
	@ruff format lambda scripts tests --check

get-token:
	@python scripts/get_strava_refresh_token.py

requirements-export:
	pdm export -o requirements.txt -f requirements --without-hashes --prod
