.PHONY: tf-plan tf-fmt tf-apply format

tf-plan:
	@terraform -chdir=terraform plan

tf-apply:
	@terraform -chdir=terraform apply

tf-fmt:
	@terraform -chdir=terraform fmt

format:
	@$(MAKE) tf-fmt
	@ruff format lambda
