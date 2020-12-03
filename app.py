#!/usr/bin/env python3

from aws_cdk import core
from cdk_deploy_example.cdk_deploy_example_stack import CdkDeployExampleStack
from cdk_deploy_example.lambda_stack import LambdaStack

CODECOMMIT_REPO_NAME = "pipeline"

app = core.App()

lambda_stack = LambdaStack(app, "LambdaStack")

CdkDeployExampleStack(
    app,
    "PipelineDeployingLambdaStack",
    lambda_code=lambda_stack.lambda_code,
    repo_name=CODECOMMIT_REPO_NAME
)

app.synth()
