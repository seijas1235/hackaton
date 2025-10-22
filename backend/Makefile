SHELL := powershell.exe

.PHONY: build deploy validate package clean

build:
	 sam build

# Guided deploy to configure stack name, region, and parameters (JwtIssuer, JwtAudience, AgentId, AgentAliasId)
deploy:
	 sam deploy --guided

validate:
	 sam validate --lint

package:
	 sam package --s3-bucket $$env:S3_BUCKET --output-template-file .aws-sam\packaged.yaml

clean:
	 if (Test-Path .aws-sam) { Remove-Item -Recurse -Force .aws-sam }
