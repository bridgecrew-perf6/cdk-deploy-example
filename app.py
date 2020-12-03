#!/usr/bin/env python3

from aws_cdk import core
from cdk_deploy_example.cdk_deploy_example_stack import CdkDeployExampleStack
from cdk_deploy_example.lambda_stack import LambdaStack

app = core.App()

lambda_stack = LambdaStack(app, "LambdaStack")

CdkDeployExampleStack(
    app,
    "CdkDeployExampleStack",
    lambda_code=lambda_stack.lambda_code
)

app.synth()
