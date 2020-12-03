
# class CdkDeployExampleStack(core.Stack):
#
#     def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)
#
#         # The code that defines your stack goes here



from aws_cdk import (
    core,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_lambda as lambda_,
    aws_s3 as s3
)


class CdkDeployExampleStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, repo_name: str = None,
                 lambda_code: lambda_.CfnParametersCode = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        code = codecommit.Repository.from_repository_name(
            self,
            "ImportedRepo",
            repo_name
        )

        cdk_build = codebuild.PipelineProject(
            self,
            "CdkBuild",
            build_spec=codebuild.BuildSpec.from_object(
                dict(
                    version="0.2",
                    phases=dict(
                        install=dict(
                            commands=[
                                "npm install aws-cdk",
                                "npm update",
                                "python -m pip install -r requirements/deploy.txt"
                            ]),
                        build=dict(commands=[
                            "npx cdk synth -o dist"]
                        )
                    ),
                    artifacts={
                        "base-directory": "dist",
                        "files": ["LambdaStack.template.json"]
                    },
                    environment=dict(buildImage=codebuild.LinuxBuildImage.STANDARD_2_0)
                )
            )
        )

        lambda_build = codebuild.PipelineProject(
            self,
            'LambdaBuild',
            build_spec=codebuild.BuildSpec.from_object(
                dict(
                    version="0.2",
                    phases=dict(
                        install=dict(
                            commands=[
                                "python -m pip install -r requirements/test.txt"
                            ]),
                        build=dict(commands=["python -m pytest"])),
                    artifacts={
                        "base-directory": "lambdas",
                        "files": ["lambda_handler.py"]
                    },
                    environment=dict(buildImage=codebuild.LinuxBuildImage.STANDARD_2_0)
                )
            )
        )

        source_output = codepipeline.Artifact()
        cdk_build_output = codepipeline.Artifact("CdkBuildOutput")
        lambda_build_output = codepipeline.Artifact("LambdaBuildOutput")

        lambda_location = lambda_build_output.s3_location

        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub",
            output=source_output,
            oauth_token=core.SecretValue.secrets_manager("github-token"),
            trigger=codepipeline_actions.GitHubTrigger.POLL,
            # Replace these with your actual GitHub project info
            owner="wowzoo",
            repo="cdk-deploy-example"
        )

        codepipeline.Pipeline(
            self,
            "Pipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Lambda_Build",
                            project=lambda_build,
                            input=source_output,
                            outputs=[lambda_build_output]),
                        codepipeline_actions.CodeBuildAction(
                            action_name="CDK_Build",
                            project=cdk_build,
                            input=source_output,
                            outputs=[cdk_build_output])
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[
                        codepipeline_actions.CloudFormationCreateUpdateStackAction(
                            action_name="Lambda_CFN_Deploy",
                            template_path=cdk_build_output.at_path(
                                "LambdaStack.template.json"),
                            stack_name="LambdaDeploymentStack",
                            admin_permissions=True,
                            parameter_overrides=dict(
                                lambda_code.assign(
                                    bucket_name=lambda_location.bucket_name,
                                    object_key=lambda_location.object_key,
                                    object_version=lambda_location.object_version)),
                            extra_inputs=[lambda_build_output])
                    ]
                )
            ]
        )
