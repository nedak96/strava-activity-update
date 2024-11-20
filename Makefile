.PHONY: tf-plan tf-apply format check get-token requirements-export test

tf-init:
	@terraform -chdir=terraform init

tf-plan:
	@terraform -chdir=terraform plan -var-file=./vars.tfvars

tf-apply:
	@terraform -chdir=terraform apply -var-file=./vars.tfvars

format:
	@terraform -chdir=terraform fmt
	@ruff format src scripts tests
	@ruff check src scripts tests --fix

check:
	@mypy
	@ruff check src scripts tests
	@ruff format src scripts tests --check

get-token:
	@python scripts/get_strava_refresh_token.py

requirements-export:
	pdm export -o requirements.txt -f requirements --without-hashes --prod

test:
	pytest
