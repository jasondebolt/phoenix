# Phoenix Microservice
<img src="/Phoenix/images/logo.png" height="70px"/>

## Table of Contents

* [What is Phoenix?](#what-is-phoenix)
* [How do I get started?](#how-do-i-get-started)
* [Phoenix Overview](#phoenix-overview)
* [Prerequisites](#prerequisites)
* [Phoenix Pipelines](#phoenix-pipelines)
* [Initial Phoenix Project Setup](#initial-phoenix-project-setup)
    * [Preparing an AWS account to work with Phoenix](#preparing-an-aws-account-to-work-with-phoenix)
        * [Create a repo in github](#create-a-repo-in-github)
        * [Configure the VPC's](#configure-the-vpcs)
        * [Save the API docs user agent token](#save-the-api-docs-user-agent-token)
        * [AWS CodeBuild GitHub OAuth authorization](#aws-codebuild-github-oauth-authorization)
        * [Create the base docker images for the Phoenix projects in your AWS account](#create-the-base-docker-images-for-the-phoenix-projects-in-your-aws-account)
    * [Creating a Phoenix project](#creating-a-phoenix-project)
        * [Create a repo in github](#create-a-repo-in-github)
        * [Configuring the project config file](#configuring-the-project-config-file)
        * [Initializing the Microservice](#initializing-the-microservice)
* [Why No Nested Stacks](#why-no-nested-stacks)
* [CloudFormation JSON Template Files](#cloudformation-json-template-files)
    * [Account Specific Stacks](#account-specific-stacks)
        * [template-vpc.json](#template-vpcjson)
        * [template-jenkins.json](#template-jenkinsjson)
    * [Project Specific Stacks](#project-specific-stacks)
        * [template-acm-certificates.json](#template-acm-certificatesjson)
        * [template-s3-ecr.json](#template-s3-ecrjson)
        * [template-ssm-globals-macro.json](#template-ssm-globals-macrojson)
        * [template-pipeline.json](#template-pipelinejson)
        * [template-github-webhook.json](#template-github-webhookjson)
        * [template-pull-request-pipeline.json](#template-pull-request-pipelinejson)
        * [template-release-environments-pipeline.json](#template-release-environments-pipelinejson)
        * [template-microservice-cleanup.json](#template-microservice-cleanupjson)
    * [Environment (dev, testing, prod, etc.) Specific Stacks](#environment-specific-stacks)
        * [template-ssm-environments.json](#template-ssm-environmentsjson)
        * [template-database.json](#template-databasejson)
        * [template-ec2.json](#template-ec2json)
        * [template-lambda.json](#template-lambdajson)
        * [template-cognito.json](#template-cognitojson)
        * [template-cognito-internals.json](#template-cognito-internalsjson)
        * [template-api-custom-domain.json](#template-api-custom-domainjson)
        * [template-api-documentation.json](#template-api-documentationjson)
        * [template-api.json](#template-apijson)
        * [template-api-deployment.json](#template-api-deploymentjson)
        * [template-ecs-task.json](#template-ecs-taskjson)
* [CloudFormation JSON Parameter Files](#cloudformation-json-parameter-files)
    * [Environments](#environments)
        * [Dev Environment](#dev-environment)
            * [Developer Specific Environments](#developer-specific-environments)
            * [GitHub Pull Request Specific Environments](#github-pull-request-specific-environments)
            * [Dev Parameter Files](#dev-parameter-files)
            * [Dev Deploy Scripts](#dev-deploy-scripts)
        * [Testing Environment](#testing-environment)
        * [E2E Environment](#e2e-environment)
        * [Prod Environment](#prod-environment)
    * [Adding Environments](#adding-environments)
    * [Removing Environments](#removing-environments)
* [Deployment Shell Scripts](#deployment-shell-scripts)
    * [Account Specific Shell Scripts](#account-specific-shell-scripts)
         * [deploy-vpc.sh](#deploy-vpcsh)
         * [deploy-jenkins.sh](#deploy-jenkinssh)
    * [Project Specific Shell Scripts](#project-specific-shell-scripts)
        * [deploy-acm-certificates.sh](#deploy-acm-certificatessh)
        * [deploy-s3-ecr.sh](#deploy-acm-certificatessh)
        * [deploy-ssm-globals-macro.sh](#deploy-ssm-globals-macrosh)
        * [deploy-pipeline.sh](#deploy-pipelinesh)
        * [deploy-github-access-token.sh](#deploy-github-access-tokensh)
        * [deploy-github-webhook-pull-request.sh](#deploy-github-webhook-pull-requestsh)
        * [deploy-github-webhook-release.sh](#deploy-github-webhook-releasesh)
        * [deploy-microservice-init.sh](#deploy-microservice-initsh)
        * [deploy-microservice-cleanup.sh](#deploy-microservice-cleanupsh)
    * [Developer Environment Specific Shell Scripts](#developer-environment-specific-shell-scripts)
        * [API Dev Deployment Scripts](#api-dev-deployment-scripts)
            * [deploy-dev-api-custom-domain.sh](#deploy-dev-api-custom-domainsh)
            * [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh)
            * [deploy-dev-api-documentation.sh](#deploy-dev-api-documentationsh)
            * [deploy-dev-api.sh](#deploy-dev-apish)
            * [deploy-dev.sh](#deploy-devsh)
        * [Cognito Dev Deployment Scripts](#cognito-dev-deployment-scripts)
            * [deploy-dev-cognito.sh](#deploy-dev-cognitosh)
            * [deploy-dev-cognito-internals.sh](#deploy-dev-cognito-internalssh)
        * [deploy-dev-database.sh](#deploy-dev-databasesh)
        * [deploy-dev-ec2.sh](#deploy-dev-ec2sh)
        * [deploy-dev-ecs-task-main.sh](#deploy-dev-ecs-task-mainsh)
            * [Updating your ECS service](#updating-your-ecs-service)
            * [Viewing your ECS service](#viewing-your-ecs-service)
            * [Multiple Service/Task/Container Scenario](#multiple-taskservicecontainer-scenario)
        * [deploy-dev-lambda.sh](#deploy-dev-lambdash)
        * [deploy-dev-ssm-environments.sh](#deploy-dev-ssm-environmentssh)
* [CodeBuild buildspec.yml Files](#codebuild-buildspecyml-files)
    * [Build Stage CodeBuild jobs](#build-stage-codebuild-jobs)
        * [buildspec.yml](#buildspecyml)
        * [buildspec-unit-test.yml](#buildspec-unit-testyml)
        * [buildspec-lint.yml](#buildspec-lintyml)
    * [Environment Specific CodeBuild jobs](#build-stage-codebuild-jobs)
        * [buildspec-api-documentation.yml](#buildspec-api-documentationyml)
        * [buildspec-integration-test.yml](#buildspec-integration-testyml)
        * [buildspec-rds-migration.yml](#buildspec-rds-migrationyml)
        * [buildspec-post-prod-deploy.yml](#buildspec-post-prod-deployyml)
    * [Manually Invoked CodeBuild jobs](#manually-invoked-codebuild-jobs)
        * [buildspec-destroy-microservice.yml](#buildspec-destroy-microserviceyml)
* [Python Helper Scripts](#python-helper-scripts)
    * [parameters_generator.py](#parameters_generatorpy)
    * [search_and_replace.py](#search_and_replacepy)
    * [generate_environment_params.py](#generate_environment_paramspy)
    * [rename_ssm_parameter.py](#rename_ssm_parameterpy)
    * [cfn_stacks.py](#cfn_stackspy)
    * [generate_dev_params.py](#generate_dev_paramspy)
    * [pull_request_codebuild.py](#pull_request_codebuildpy)
* [Python 3.6 Lambda Functions](#python-36-lambda-functions)
    * [alb_listener_rule](#alb_listener_rule)
    * [api_internals](#api_internals)
    * [cognito_internals](#cognito_internals)
    * [create_pull_request_webhook](#create_pull_request_webhook)
    * [create_release_webhook](#create_release_webhook)
    * [delete_ecr_repos](#delete_ecr_repos)
    * [delete_network_interface](#delete_network_interface)
    * [delete_s3_files](#delete_s3_files)
    * [macro](#macro)
    * [password_generator](#password_generator)
    * [post_pullrequests](#post_pullrequests)
    * [projects](#projects)
    * [proxy](#proxy)
    * [pull_request_webhook](#pull_request_webhook)
    * [release_webhook](#release_webhook)
    * [ssm_secret](#ssm_secret)
    * [vpc_proxy](#vpc_proxy)
* [Non-Python Lambda Functions](#non-python-lambda-functions)
* [Example Dockerfile used for testing/debugging ECS deployments](#example-dockerfile)


## What is Phoenix
It is a <a href="https://aws.amazon.com/microservices/">microservice</a> platform originally created by Jason DeBolt.

It is a subdirectory in which all of your infrastructure code lives, including admin scripts for manipulating
everything from developer clouds, pipelines, releases, and deployments.

It is a collection of tools, templates, and scripts for launching highly available, multi-environment, <a href="https://12factor.net/">Twelve Factor App</a> microservice projects on AWS with advanced support for CI/CD automation.

It ships with multi-environment VPC configuration, complex CI/CD pipeline infrastructure, advanced GitHub webhook integration, central storage and propagation of project parameters/variables, and multiple developer specific cloud environments.

Currently, Phoenix is only supported in the **us-east-1** region. This is mostly due to requirements in some AWS services that ACM certificates be created in the us-east-1 region.

## How do I get started?
1. Clone this repository.
2. Place all of your application source code in the root directory of this repository (above the Phoenix directory).
3. Create a Dockerfile for your application.
   * You will later need to update the "docker build" command in [buildspec.yml](#buildspecyml) with this location.
4. Complete the [Initial Phoenix Project Setup](#initial-phoenix-project-setup) section.

## Phoenix Overview
A Phoenix microservice is a Git repository with a "Phoenix" subdirectory. This Phoenix subdirectory includes the following file types:
1) [CloudFormation JSON Template Files](#cloudformation-json-template-files)
2) [CloudFormation JSON Parameter Files](#cloudformation-json-parameter-files)
3) [Deployment Shell Scripts](#deployment-shell-scripts) (mostly used for developer specific clouds)
4) [CodeBuild buildspec.yml Files](#codebuild-buildspecyml-files) (These are like Jenkins jobs)
5) [Python Helper Scripts](#python-helper-scripts)
6) [Python 3.6 Lambda Functions](#python-36-lambda-functions)
7) [Example Dockerfile used for testing/debugging ECS deployments](#example-dockerfile)

## Prerequisites
Working with Phoenix without strong knowledge of CloudFormation is an exercise in frustration. Take some time to learn it.

1. Introductory CloudFormation
    * <a href="https://aws.amazon.com/cloudformation/getting-started/">AWS CloudFormation Getting Started</a>
    * <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/GettingStarted.html">Getting Started with AWS CloudFormation</a>
2. Advanced CloudFormation (pick one from below)
    * <a href="https://linuxacademy.com/amazon-web-services/training/course/name/aws-cloudformation-deep-dive"> Linux Academy - AWS CloudFormation Deep Dive</a>
    * <a href="https://acloud.guru/learn/aws-advanced-cloudformation">A Cloud Guru - AWS Advanced CloudFormation</a>

## Phoenix Pipelines
A Phoenix microservice includes one or more CI/CD pipelines, some permanent, some ephemeral. Each pipeline has a source stage, which is usually triggered from a Git repository webhook. There is also a build stage, which will build a set of immutable artifacts that will be later deployed to one or more environments. Both source code and artifacts can be scanned for security and/or static analysis. If the build, testing, and linting stages pass, the artifacts (lambda functions, docker images, etc.) are deployed into a testing environment. After the testing environment is deployed to, a set of integration tests and load tests may further test your microservice. All environments contain there own databases, lambda functions, ECS clusters, dynamoDB tables, SSM parameters, and API Gateway deployments. Finally, the artifacts are deployed to a production environment using blue/green deployment strategies for all AWS resources. Optionally, pull request specific ephemeral pipelines can be added if your team requires these.

## Initial Phoenix Project Setup

### Preparing an AWS account to work with Phoenix

#### Configure the VPC's
* These steps are only required once per AWS account (once for all Phoenix projects in an AWS account).
* Add appropriate CIDR ranges in the template-vpc-params-dev.json, template-vpc-params-testing.json, and template-vpc-params-prod.json files.
* Ensure that all CIDR IP ranges are not currently used by any other Phoenix projects or other networks.
* Deploy the VPC's
```
$ cd Phoenix
$ ./deploy-vpc.sh create
```

#### Save the API docs user agent token
* These steps are only required once per AWS account (once for all Phoenix projects in an AWS account).
* This is a secret token used to verify HTTP requests made to API documents served from the S3 bucket.
* This token can be shared by all Phoenix projects in a single AWS account.
* This token can saved in a browser using the Chrome browser plugin to add to the 'user-agent' header in requests.
* Usage of this token in the browser is optional, but it can be useful when accessing API docs from over VPN.

```
From you mac:
$ pwgen 32 -1
```

Save the above generated token in the '/global/api-docs-user-agent' SSM parameter store parameter with
the descripte "UserAgent used to authenticate with S3 static websites for API Documentation." It this key already exists
in SSM parameter store for the AWS account, you don't need to do anything.

#### AWS CodeBuild GitHub OAuth authorization
- The following steps assume use of LastPass and OneLogin for credentials storage and auth.
* These steps are only required once per AWS account (once for all Phoenix projects in an AWS account).
* When using AWS CodeBuild with GitHub webhook integrations, there is a one time setup involving Oauth tokens for new AWS accounts.
* We will need to use a shared admin GitHub account to authorize these tokens rather than use user specific GitHub accounts.
1. Sign out of your GitHub account.
2. Sign out of your OneLogin account.
3. Sign back into OneLogin as the your "user@yourdomain.com" user.
4. Once logged in, click on the GitHub app within OneLogin.
5. At the GitHub login screen, use the username and password specified in LastPass.
6. Verify that you are logged into GitHub as the the user who will issue access tokens.
7. In the new AWS account, open the AWS CodeBuild console as the user who will issue access tokens.
8. Create a simple CodeBuild job using GitHub as the source, and click on the "Connect to GitHub" button.
9. A dialog box will appear where you can authorize "aws-codesuite" to access the GitHub organization.
10. Now you can allow CloudFormation to automatically create GitHub webhooks associated with this AWS account.
11. Log out of the "user@yourdomain.com" GitHub account.
12. Log out of the "user@yourdomain.com" OneLogin account.
13. Log back into your OneLogin and GitHub accounts.

#### Create the base docker images for the Phoenix projects in your AWS account
It's a great idea to <a href="https://12factor.net/dependencies">Explicitly declare and isolate dependencies</a> by using
immutable Docker images for build nodes and application nodes.

Phoenix uses a sister repo called "phoenix-docker" that includes a full CI/CD solution for continuously building and deploying entire Docker image hierarchies.

You can clone the "phoenix-docker" repo here:
https://github.com/solarmosaic/phoenix-docker

The CloudFormation project in the "phoenix-docker" repo does the following:
1. Creates a GitHub webhook.
2. Creates ECR repos for storing families of related docker images.
3. Creates a CodeBuild job for building and pushing the docker images.
4. Creates a CodePipeline for orchestration.
5. Creates IAM roles.

The default Docker image hierarchy provide look like this:
```
                               Ubuntu 14.04
                          /                    \
                   Java/Openjkd-8        NodeJS/10.1.0
                    /
                 Scala
                 /
               ScalaBuild
```

After cloning "phoenix-docker" and following the README, you should have a set of built docker images in ECR that you can used for all Phoenix projects in your AWS account. Your Phoenix projects "template-ssm-globals-macro-params.json" file should know where to find these docker images in ECR:
```
    "CodeBuildDockerImage": "111111111111.dkr.ecr.us-east-1.amazonaws.com/scala-build:0.1.1",
    "NodeJSBuildDockerImage": "111111111111.dkr.ecr.us-east-1.amazonaws.com/nodejs:10.1.0",
```
Where 111111111111 is your AWS account ID.

### Creating a Phoenix project

#### Create a repo in github
1. Create a blank repo in GitHub with an all lowercase repo name.
    * The name of the repo should be short and lowercase with no special characters (dashes are ok).
2. Make sure to add this repo under the correct organization
3. Add the group that includes the GitHub user whose access token is used to create webhooks for your project.
4. Clone the this repo and change the remote path
    * git remote -v
    * git remote remove origin
    * git remote add origin git@github.com:/{your-organization}/{your-repo}.git

#### Configuring the project config file
Make sure you have followed all steps in [Preparing an AWS account to work with Phoenix](#preparing-an-aws-account-to-work-with-phoenix) before continuing these next few sections.

All Phoenix projects have a file called "template-ssm-globals-macro-params.json" used for project wide configuration.
The project wide configuration values include, but aren't limited to, the following:

* Organization name
    * This would typically be the name of the company/organization associated with the repo.
* Project name
    * The name of your project. (Use call lowercase, no dashes or special characters)
* Git repo name
    * The name of your git repository in GitHub.
* Git root project branch
    * The name of the git branch used to deploy to production
* Git current project branch
    * This is a deprecated field that can just be the same as the root project branch.
* GitHub organization
    * The name of your GitHub Organization
* Domain
    * The name of your domain (use "api.your-domain.com" for API's, and "your-domain.com" for applications)
    * You should create a public hosted zone for this domain or subdomain (see the Hosted Zone ID param)
* Hosted Zone ID
    * You **must manually create a public hosted zone** in the AWS Route53 console and enter this ID here.
* Key pair name
    * You must manually create an EC2 SSH key and enter the name of the key here (use "us-east-1-{your-aws-account-id}"
* Notification email
    * An email to send build notification to and other alerts
* IAM Role
    * You must manually create an IAM role with admin permissions which includes secretsmanager.amazonaws.com, cloudformation.amazonaws.com, codepipeline.amazonaws.com, codebuild.amazonaws.com, and lambda.amazonaws.com in the trust policy. This will get you started, but should obviously be changed if strong security is a concern.
* Code Build Docker Image
    * Enter the ID, including the image tag, of the ECR image you are using for your AWS CodeBuild jobs.
    * See [Create the base docker images for the Phoenix projects in your AWS account](#create-the-base-docker-images-for-the-phoenix-projects-in-your-aws-account).
* NodeJS Build Docker Image
    * For build that require NodeJS, enter the ID, including the image tag, of the ECR image you are using. You can also just use the same ID as the code build docker image above.
    * See [Create the base docker images for the Phoenix projects in your AWS account](#create-the-base-docker-images-for-the-phoenix-projects-in-your-aws-account).
* Git URL
    * This can just be "https://github.com"
* Pipeline Environments
    * A comma delimited list of environment names you wish to deploy to in the main pipeline.
* Release Environments
    * A comma delimited list of release environment names you wish to deploy to in all release pipelines.
* Version
    * The VERSION_ID value in this field will usually be replace with a timestamp from one of the deployment shell scripts.

The config should look something like this:
```
  {
  "Parameters": {
    "OrganizationName": "example",
    "ProjectName": "foo",
    "GitRepoName": "foo",
    "GitRootProjectBranch": "master",
    "GitCurrentProjectBranch": "master",
    "GitHubOrganization": "example",
    "Domain": "foo.example.com",
    "HostedZoneId": "Z1Q365PZIUEHGE",
    "KeyPairName": "us-east-1-111111111111",
    "ProjectDescription": "The Example Foo project.",
    "NotificationEmail": "foo-engineering@example.com",
    "IAMRole": "arn:aws:iam::111111111111:role/OriginationsAdmins",
    "CodeBuildDockerImage": "111111111111.dkr.ecr.us-east-1.amazonaws.com/scala-build:0.1.1",
    "NodeJSBuildDockerImage": "111111111111.dkr.ecr.us-east-1.amazonaws.com/nodejs:10.1.0",
    "GitURL": "https://github.com",
    "PipelineEnvironments": "testing, e2e, prod",
    "ReleaseEnvironments": "",
    "Version": "VERSION_ID"
  }
}
```
- Where 111111111111 is your AWS account ID.
- You can keep "VERSION_ID" as is.

#### Initializing the Microservice
Lastly, we need to invoke a single script will will bootstrap our Phoenix microservice.

```
    ./deploy-microservice-init.sh {token}
```

**IMPORTANT**: Immediately after invoking the above script, open the <a href="https://console.aws.amazon.com/acm">AWS ACM console</a> and manually approve the adding of CNAME records for your domain. Click on the little expansion arrows, 2 levels down. **If you forget to do this, the above script will hang on the "./deploy-acm-certificates.sh create" call.**

The above script will call a series of other scripts to create your microserivice. You should monitor the following
consoles while these scripts are running:
1. <a href="https://console.aws.amazon.com/cloudformation">CloudFormation Console</a>
2. <a href="https://console.aws.amazon.com/codepipeline">CodePipeline Console</a>
3. <a href="https://console.aws.amazon.com/acm">AWS Certificate Manager Console</a> --> You must approve the CNAME's.

All of these global stacks are idempotent, so if anything fails you can safely delete, fix, and retry.

After all stacks from the microservice-init script have been created, push to that master branch of the repo
```
$ git push origin master
```

Open the <a href="https://console.aws.amazon.com/codepipeline">CodePipeline Console</a> to view the git revision
propagating down the pipeline.

Additional things to consider:
* Do you want to create any NS records in a different AWS account that point to your subdomain's 4 NS records?
* Do you need to grant other teams access to your GitHub repo?


## Why no Nested Stacks?
At the time Phoenix was first developed, Cloudformation Nested Stacks had several limitations. These limitations included
lack of support for <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/create-reusable-transform-function-snippets-and-add-to-your-template-with-aws-include-transform.html">AWS::Include</a> transforms, Cloudformation
macros and more. Nested stacks can also become difficult to work with for large sets of stacks, sometimes becoming
completely stuck (requiring AWS support to fix). In December 2018, Cloudformation macro support was added to Nested Stacks,
so it may be possible to refactor Phoenix to leverage Nested Stacks in the near future. If this occurs, it would probably be  best to decouple stacksets for the expensive, heavy resources such as RDS instances, API gateway custom domains, and CloudFront distributions from the faster, lightweight resources such as ECS, Lambda, DynamoDB, and API Gateway deployments.

## CloudFormation JSON Template Files
An AWS account may include multiple Phoenix projects, and each Phoenix project may include multiple environments like
"dev" for developer and pull-request resources, "testing" for testing/staging/qa resources, and "prod" for production
resources. Phoenix cloudformation templates are scoped to the account level, project level, and environment level.

The "template-vpc.json" file is an **account specific** as well as an **environment specific** stack. This template may create a dev VPC stack, a testing VPC stack, and a prod VPC stack. These VPC stacks can be shared by multiple Phoenix projects.

The "template-pipeline.json" file is a **project specific** stack. This template is used to create a stack named "{project-name}-pipeline.json". This CI/CD pipeline is shared by all environments, so only one stack instance should be created for this template.

The "template-ec2.json" file is an **environment specific** stack. Stack names may include "{project-name}-ec2-testing" and
"{project-name}-ec2-prod".

### Account Specific Stacks
The following templates are used to create stacks to used across the entire AWS account, possibly hosting several Phoenix projects. The stack name will be {template-name}.

#### template-vpc.json
Approximately 21 AWS resources are created including VPC's, Internet Gateways, NAT gateways, routing tables, private/public subnets configured for high availability, and VPC Elastic IP's. These VPC stacks export values important by many other stacks.

#### template-jenkins.json
While I highly recommend AWS CodeBuild rather than Jenkins for a number of reasons, this template can be used to spin up a single Jenkins node. This template is entirely optional, however.

### Project Specific Stacks
The following templates are scoped to a single Phoenix project. Most of these templates are associated with a single stack.
The stack name will be {project-name}-{template-name}.

#### template-acm-certificates.json
This template creates several different ACM SSL certificates used for things like ECS endpoints, API Gateway endpoints, Cognito Auth endpoints, and S3 website endpoints, all of which are supported by Phoenix.

#### template-s3-ecr.json
This template creates an ECR repository for your projects docker images as well as several S3 buckets. Logging buckets are created for CodePipeline, CodeBuild, and Elastic Load Balancer Logs. Additional buckets are created for source code artifacts like Lambda source bundles and Phoenix CloudFormation templates.

#### template-ssm-globals-macro.json
This template creates a <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html">CloudFormation Macro</a> and a set of global non-environment specific SSM parameters for your Phoenix project. The macro is a Lambda function that pre-processes CloudFormation templates and the SSM parameters are saved into SSM parameter store.

See [macro](#macro) and [deploy-ssm-globals-macro.sh](#deploy-ssm-globals-macrosh) for more information.

#### template-pipeline.json
This template creates a multi-environment AWS CodePipeline, GitHub webhook on the master branch, build/test/lint AWS CodeBuild jobs, and an CloudWatch rule which sends SNS notifications to the project email upon pipeline failure. This is one of the most important CloudFormation stacks of any Phoenix project.

#### template-github-webhook.json
This is neither a global nor environment specific template, but the template can have multiple stack instances. This template deploys a GitHub webhook on GitHub for one or more events, an API Gateawy endpoint, a Lambda webhook handler, a post webhook Lambda handler, and other resources required for launching GitHub webhooks. The API Gateway endpoint sits between GitHub and Lambda and it used to receive the webhook event from GitHub. This is a very powerful template that can potentially be used to created dozens of GitHub webhooks of different types. Currently Phoenix ships with two stacks (parameter files) for this template, one for pull requests (template-github-webhook-pull-request-params.json) and another for release events (template-github-webhook-release-params.json).

#### template-pull-request-pipeline.json
This is a pull request specific template, supporting multiple stack instances. Each stack instance of this template is associated with a GitHub pull request pipeline. This stack(s) associated with this template are created/updated/deleted
from within a Lambda function that listens for pull request events from GitHub.

#### template-release-environments-pipeline.json
Each stack instance of this template is associated with a release into a specific release environment. This stack(s) associated with this template are created/updated/deleted from within a Lambda function that listens for push events from GitHub where the branch matches the regular expression pattern "release-\d{8}$". See the "release_webhook" Lambda function in the lambda folder for details.

#### template-microservice-cleanup.json
This template creates an AWS CodeBuild job that destroys all AWS resources for one or more environments (dev, testing, prod, etc). The "buildspec-destory-microservice.yml" buildspec
deletes CloudFormation stacks in the appropriate order. A project admin can manually kick off this CodeBuild job to completely destory one or more Phoenix environments.

### Environment Specific Stacks
The following templates are scoped to one or more environments (dev, testing, prod, etc) for a single Phoenix project.
There may be several stack instances per template, each scoped to an different environment. The stack name will be
{project-name}-{template-name}-{environment}.

#### template-ssm-environments.json
This template deploys environment specific SSM parameters for your project. Any kind of environment specific project parameters/config can be stored as SSM parameters in this template. Once deployed, these parameters are stored in SSM Parameter Store and made available to all other CloudFormation stacks.

Many teams store project configuration values in source code config files. This is a violation of the Twelve-Factor App
rule of <a href="https://12factor.net/config">store config in the environment, not the source code<a>.

Phoenix has an easy solution for centrally storing project or environment specific configuration values and making them
available to AWS resources (EC2 instances, Lambda functions, ECS containers, CodeBuild jobs, etc.) via IAM policies.
This eliminates differences in dev/test/prod parity, increases visibility of configuration values, enhances security,
and provides a single "source of truth" for your project configuration values. All configuration values are stored in AWS SSM Parameter store, which is currently a free service.

If you look at the "template-ssm-environments.json" template, you'll see a "DescriptionParam" parameter with a key ending with "description". The value associated with this parameter is stored in SSM parameter store can can be accessed in other CloudFormation templates (See the "Description" value in the Outputs section of the "template-lambda.json" for an example of importing these values). Simply add environment specific parameters to the "template-ssm-environments.json" file
and add new config values in all of the "template-ssm-environments-params-{environment}.json" parameter files before
updating these stacks. All stored values will be made available to other authorized AWS resources.

The "PROJECTNAMELambdaMacro" transform at the top section of many CloudFormation templates as well as the "macro" lambda
function in the "Phoenix/lambda" folder make this possible.

#### template-database.json
This template deploys an Aurora MySQL cluster and supports
cluster restores from snapshots. A custom Lambda resource within the template auomatically generates a password for new
database instances, with some support for password rotation as well. There is also a CodeBuild job defined in this template
that can be used for database migrations within the CI/CD CodePipeline.

For further detail on the following:

* Creating a new database stack (without a snapshot)
* Updating a database stack (without a snapshot)
* Creating a database stack (with a snapshot)
* Updating a database stack (with a snapshot)
* Deleting a database instance
* Password rotation
* Finding historical passwords in SSM parameter store
* Testing Plan for the Lambda password generator

See <a href="https://docs.google.com/document/d/16UUY3h-4wU372XF8D0Fs1IQ3ABLrO-Vjn5ao2YkB84M/edit#">Phoenix for Datbase Admins</a>

See [deploy-dev-database.sh](#deploy-dev-databasesh) for more detail.

#### template-ec2.json
This template creates an EC2 launch configuration, auto scaling group, security groups, EC2 instances, load balancers, an other EC2 resources.

#### template-lambda.json
This template contains Lambda functions and all resources required for deploying lambda functions, such as IAM roles
and security groups. Phoenix ships with a VPC proxy lambda function which can proxy HTTP requests from API Gateay to
to private instances in an ECS cluster. A example "Project" Lambda function which handles requests from API Gateway
is also provided. Note that Lambda functions that require access to private EC2 or ECS resources must be placed in
a VPC.

#### template-cognito.json
This template creates AWS Cognito resources such as an AppClient and UserPool. Like all CloudFormation templates, this
template can be extended.

#### template-cognito-internals.json
This template creates AWS Cognito resources that are not fully supported in AWS CloudFormation, such as user pool auth
domains, resource servers, user pool clients, and route53 record sets. Cognito is one of the AWS services that doesn't have all resources covered/provisionable by CloudFormation. This template solves this problem by using an <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html"> AWS Lambda-backed Custom Resource</a> within the template. Within the template, a Lambda function
is created from the "lambda/cognito_internals" Python code, and invokes the code during stack create/update/delete operations.
After the lambda function is invoked, it returns data and control back to the CloudFormation stack.

#### template-api-custom-domain.json
This template deploys a <a href="https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-custom-domains.html">custom domain name</a> for your API Gateway API endpoints. It also create an DNS record set
in Route53 which points to this custom domain. When you deploy an edge-optimized API, API Gateway sets up an Amazon CloudFront distribution and a DNS record to map the API domain name to the CloudFront distribution domain name. Requests for the API are then routed to API Gateway through the mapped CloudFront distribution.

#### template-api-documentation.json
This template deploys AWS resources required to support versioned API documentation. Resources include a static S3 website/bucket, Bucket policy, CloudFront distribution, Web Application Firewall ACL, WAF rules, and WAF predicates for managing API documentation access.

#### template-api.json
This template deploys your API Gateway REST API. This includes all API REST resources and methods, along with API
models, auth types, and any other API Gateway resources specific to an API.

#### template-api-deployment.json
This template deploys that API specified in "template-api.json". Note that the declaration of the API (template-api.json) is
deployed separately from the deployment of the API (template-api-deployment.json). This is because API Gateway deployments are static, immutable "snaphots in time" of a given API. Once an API has been deployed, it cannot be changed, only replaced. This template also contains an <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html"> AWS Lambda-backed Custom Resource</a> from the Python source code in the "lambda/api_internals" folder. The
lambda function updates the API Gateway with a custom method integration that adds custom headers to the request, as well
as altering the request body. I used a custom lambda function here to avoid dozens of identical hard coded Python code
within template-api.json.

#### template-ecs-task.json
This template generates all resources required for a single ECS task service. An ECS task can inlude up to 10 containers
(1 main container and 9 sidecar containers). If more than one service (which may include up to 10 containers) is required for your Phoenix project, you can create a new set of parameter files and create multiple stack instances of this template. There
are no limits to the number of services are containers that can be deployed from a Phoenix project. The only limits are AWS
limits.

This is probably one of the more advanced CloudFormation templates within Phoenix. It can be used to deploy ECS tasks using
either Fargate or EC2. It deploys a CloudWatch logs group, a single task definition, an ECS service, an Application Load
Balancer along with ALB listeners, Auto Scaling rules/alarms/policies based on 500 response errors, security groups, and
a DNS record set that points to the ALB endpoint. There are also some predefined environment variables that are passed
into the ECS task, but these can be removed. The lambda password generator and RDS password retriever are legacy and
can probably also be removed.

Phoenix ships with 4 parameter files for this template (template-ecs-task-**main**-params-{dev,e2e,testing,prod}.json). If your Phoenix project requires, say, a worker service for processing images from an SQS queue, you would create 4 more template files (template-ecs-task-**images**-params-{dev,e2e,testing,prod}.json). Make sure to update all other relevant files
(buildspec.yml, template-pipeline.json, etc.) to ensure this new ECS service is deployed.

## CloudFormation JSON Parameter Files
CloudFormation uses parameter files to deploy a single template to multiple environments. Currently, Phoenix ships with four
different environments (dev, e2e, testing, and prod).

Environments can be added, renamed, or removed entirely.

### Environments

#### Dev Environment
Phoenix supports multiple dev environments. There are 2 basic types of dev environments supported within Phoenix:

1. Developer specific
2. Github pull request specific

##### Developer Specific Environments
Developer Specific environments are environments used only by a given developer to assist in development of not
only application source code, but also infrastructure code (CloudFormation templates). Developers can have their
own SQS queues, lambda functions, ECS clusters, RDS instances, and API Gateway deployments. This makes feedback
loops for infrastructure very fast since it provides developers the confidence that their isolated clouds will
not impact production or any other environment.

These dev environments are complete "developer clouds" that deploy the exact same AWS resources that are deployed
to in production, although they may be less scalable (fewer compute resources, lower limit on cpu and memory, etc.)
to save on costs. Each developer on your team may have their own developer environment.

There is no "single" dev environment within Phoenix. However, there may be shared resources across all dev environments,
such as RDS/Aurora/MySQL database instances. The reason for sharing expensive resources like databases is to save on costs.
However, keep in mind that you may need to scale up shared dev environment resources to handle workloads associated with larger development teams. For example, increasing the instance size of a dev Aurora MySQL instance will allow a larger number of db connections from many different developer environments.

##### GitHub Pull Request Specific Environments
GitHub pull request specific environments are similar to developer specific environments, but instead of being scoped
to the developer, they are scoped to a specific GitHub pull request. Also, whereas developer specific environments
have no pipelines, GitHub pull requests **do** have pipelines. These pipelines are ephemeral and live as long as the pull request is open. Any new git commits that are pushed to the branch associated with the pull request will send revisions down the pull request pipeline, building and optionally deploying new artifacts along the way into a separate, isolated AWS environment. The build/test/lint CodeBuild jobs associated with the pull request pipelines point to the same buildspec.yml files as are used in all other environments, including production.

##### Dev Parameter Files
When a new developer joins your project, they should run "python generate_dev_params.py dev{username}" where "username"
is an all lowercase (no dashes, underscores, or dots) alias for the developer. For example, developer Jane Doe
would run the command "python generate_dev_params.py devjane" to generate her dev CoudFormation parameter files. Since these
files are gitignored, they will show up in your IDE/filesystem but cannot be checked into Git.

All CloudFormation parameter files that end with "*-params-dev.json" are gitignored by default to keep different developer
parameter files from clashing with eachother.

##### Dev Deploy Scripts
A dev deploy script is a shell script within Phoenix that matches the file pattern of "deploy-dev-*.sh". There are currently
13 such scripts, all of which deploy one or more dev environment CloudFormation stacks. All [Environment Specific Stacks](#environment-specific-stacks) have dev deployment scripts.

A developer will execute these scripts locally whenever AWS infrastructure changes are made via CloudFormation templates. For example, if a developer wants to add a new Lambda function to production, they would first add the function to "template-lambda.json" and run "deploy-dev-lambda.sh update" to deploy the lambda function into their dev environment, assuming their dev environment is already up and running. The developer would then test the function in their own isolated dev cloud. Once the developer is satisfied with the lambda function, they will create a new branch, a pull request, and the code will be merged into the master branch. Once the code is merged into the master branch, the lambda function is deployed into testing, e2e, and finally into production.

Note that developers do not have their own AWS CodePipelines within the Phoenix platform. Instead, developers deploy to one
stack at at time using one of the dev deploy scripts. Since pipelines work best when multiple stacks need to be created/updated together in a consistent, orchestrated way, pipelines are overkill for developer workflows.

Phoenix deploys all dev resources into the "dev" VPC provided by "template-vpc.json".

#### Testing Environment
The Testing environment is an isolated environment for deploying AWS resources used for testing before production.
One a testing environment is deployed, a suite of tests can operate on the testing environment. These tests occur after
the testing environment is deployed to. Such tests may include integration tests, browser tests, load tests, and security
related tests on infrastructure. Phoenix deploys all testing resources into the "testing" VPC provided by "template-vpc.json".

#### E2E Environment
E2E stands for "End-to-End". This environment is intended to be used for an additional level of testing between the testing and production environments. The E2E stage may include very expensive or time consuming integration tests that could be decoupled from the main integration tests run in the testing environment. Like all environments shipped this Phoenix, this environment can be removed for most projects. Phoenix deploys all E2E resources into the "testing" VPC provided by "template-vpc.json". There is no need to create a separate VPC just for e2e environments.

#### Prod Environment
The production environment is where all production infrastructure and build artifacts are deployed into. The same source code and build artifacts that are deployed into both testing and e2e environments are deployed into production. Also, the same
CloudFormation templates that are deployed into both testing and e2e environments are deployed into production. The only
difference between testing, e2e, and production environments should be the configuration, which can be found in CloudFormation
parameter files. These configuration values are used to configure AWS infrastructure and are made available to various
execution environments for build artifacts to consume. The execution environments include those supporting Lambda runtimes, ECS container runtimes, AWS CodeBuild runtimes, or virtual machine runtimes on EC2.

In the future, Phoenix may support multiple production environments for blue/green type deployments across entire environments using CNAME switching. Blue/green deployments are already available for some indiviual components within an environment, such
as ECS services and Lambda functions.

Phoenix deploys all prod resources into the "prod" VPC provided by "template-vpc.json".

### Adding Environments
You can add more environments to your Phoenix project by doing the following.
1. Add the environment name "template-ssm-globals-macro-params.json"
    * Add the name of your new environment to the "PipelineEnvironments" comma delimited list.
    * Deploy the updated parameter to SSM with "./deploy-ssm-globals-macro.sh update"
2. Execute the "generate_environment_params.py" helper script to generate the parameter files locally.
    * Execute "python generate_environment_params.py {your-environment-name}"
    * See the docstring of the python generate_environment_params.py script for details.
3. Update the new environment's parameter files with appropriate values.
    * You should see "template-*-params-{your-new-environment}.json" files in your local Phoenix project.
4. Update "template-pipeline.json" with a pipeline stage for your new environment.
   * Copy the entire "DeployToTesting" section, paste to a different area of the template, and rename.
    ```
    {
      "Name": "DeployToTesting",
      "Actions": [
        {
          ...
        }
      ]
     }
    ```
5. Update the pipeline stack with "./deploy-pipeline.sh update"
6. Create a git commit and push your new parameter files to the master branch of your project.

### Removing Environments
You can remove environments from your Phoenix project by doing the following.
1. Remove the environment name "template-ssm-globals-macro-params.json"
    * Remove the name of the environment from the "PipelineEnvironments" comma delimited list.
    * Deploy the updated parameter to SSM with "./deploy-ssm-globals-macro.sh update"
2. Execute the "generate_environment_params.py" helper script to generate the parameter files locally.
    * Execute "python generate_environment_params.py {your-environment-name} **--delete**"
    * See the docstring of the python generate_environment_params.py script for details.
3. Verify that the environment parameter files have been deleted in your local project's Phoenix folder:
    * You should no longer see "template-*-params-{your-new-environment}.json" files in your local Phoenix project.
4. Update "template-pipeline.json" with a pipeline stage for your new environment.
   * Remove the entire "DeployTo{name-of-environment}" section from within "template-pipeline.json":
    ```
    {
      "Name": "DeployTo{name-of-environment}",
      "Actions": [
        {
          ...
        }
      ]
     }
    ```
5. Update the pipeline stack with "./deploy-pipeline.sh update"
6. Create a git commit and push your new parameter files to the master branch of your project.

## Deployment Shell Scripts
Phoenix uses shell scripts for deploying both CloudFormation stacks and Lambda functions. There are 3 types of shell scripts
within Phoenix:

1. Account Specific
2. Project Specific
3. Developer Environment Specific

The account specific shell scripts deploy CloudFormation stacks that can be shared account multiple Phoenix projects in
the same AWS account. This currently includes dev/testing/prod VPC stacks and the Jenkins stack (which is optional).
These scripts are mostly used by DevOps when creating a new AWS account.

The project specific shell scripts deploy CloudFormation stacks and Lambda functions shared by all environments within
a single Phoenix project. This includes S3 buckets, ECR repos, GitHub webhook infrastructure, the main project pipeline,
ACM/SSL certificates, etc. These scripts are mostly used by DevOps when creating a new AWS account, but may also be used
by a project team lead to alter the pipeline or to add global SSM parameters.

The developer environment specific shell scripts deploy "developer cloud" CloudFormation stacks and Lambda functions. These
shell scripts make up the bulk of shell scripts within Phoenix are used mostly be developers who make changes to AWS
infrastructure via CloudFormation templates.

All shell scripts within Phoenix follow the same pattern:
1. Validate shell script arguments
2. Extract properties from the "template-ssm-globals-macro-params.json" file and store in local variables.
3. Build Lambda zip bundles and upload to S3 bucket (optional step)
4. Massage the CloudFormation template and parameter file a little (Set VERSION_ID, make macro name unique, etc.)
5. Validate the CloudFormation template
6. Create and execute CloudFormation change set


It is important to note that deployment shell scripts **do not** deploy to any pipeline environments (testing, e2e, prod).
These shell scripts are scoped only to the account, project, or developer specific environments. All of the other environments
within a Phoenix projects are deployed to via **AWS CodePipeline**.

### Account Specific Shell Scripts
Account specific deployment scripts are used to deploy CloudFormation stacks used across the entire AWS account. These
scripts will probably not be used by application developers. Usage will likely be limited to DevOps team members
when create a new AWS account for a new Phoenix project.

#### deploy-vpc.sh
Deploys a dev VPC, a testing VPC, and a prod VPC.

Usage:
```
./deploy-vpc.sh create
./deploy-vpc.sh update
```

A Phoenix project can contain any number of VPC's, but there three environments supported (dev, testing, prod) out of the box. Multiple Phoenix projects within the same AWS account can use the same VPC's. The VPC CloudFormation stacks export values such as VPC and Subnet Id's to be imported by other CloudFormation stacks. Each VPC includes the minimal networking resources for high availability, including 2 private subnets and 2 public subnets per VPC, each in different availability zones. VPC templates can be modified if more or less networking resources are required.

Related Files:
```
deploy-vpc.sh
template-vpc.json
template-vpc-params-dev.json
template-vpc-params-testing.json
template-vpc-params-prod.json
```


#### deploy-jenkins.sh
Deploys a single Jenkins instance.

Usage:
```
./deploy-jenkins.sh
```

You can deploy the Jenkins instance in a private or public subnet, but private is recommended. This instance is deployed
into the dev VPC by default, but this can be changed.

A CNAME with a default prefix of "jenkins.{your-domain}", where {your-domain} can be found in "template-ssm-globals-macro-params.json" is added by default, but this can be changed.

If you need to update this stack, it it recommended to delete the stack and restore it again from a snapshot. If this CloudFormation stack is deleted, an EBS volume snapshot is created.


Related Files:
```
deploy-jenkins.sh
template-jenkins.json
template-jenkins-params.json
```

### Project Specific Shell Scripts
Project specific deployment scripts are used to deploy CloudFormation stacks used across all environments (dev, testing, prod, etc.) of a Phoenix project. These scripts will probably not be used by most application developers. Usage will likely be limited to team leads for a given Phoenix project, or DevOps team members. The only scripts that developers probably
need to be aware of are "deploy-pipeline.sh" and "deploy-ssm-globas-macro.sh".

#### deploy-acm-certificates.sh
Deploys AWS ACM Certificates for a Phoenix project in a single CloudFormation stack. Upon running this script,
**you must login into the <a href="https://console.aws.amazon.com/acm/home?region=us-east-1#/">AWS ACM console</a>
and manually approve the creation of CNAMES for each certificate**.

Usage:
```
./deploy-acm-certificates.sh create
./deploy-acm-certificates.sh update
```

Related Files:
```
deploy-acm-certifactes.sh
template-acm-certificates.json
```

#### deploy-s3-ecr.sh
Deploys S3 buckets and an ECR repository for your Phoenix project.

A single ECR repository is created with a life cycle policy that removes docker images after the first 900 images to
avoid hitting the ECR limit.

S3 buckets are created for load balancer logs, storing versioned lambda functions, code build logs, code pipeline logs,
and project cloudformation templates.

This stack also creates and calls a few custom lambda functions to automatically delete S3 files and ECR images when S3 buckets and ECR repositories are deleted upon stack deletion. If these lambda functions didn't exist, this stack would not be able to be deleted since S3 buckets and ECR repos cannot be deleted if they contain artifacts/files.

Usage:
```
./deploy-s3-ecr.sh create
./deploy-s3-ecr.sh update
```

Related Files:
```
deploy-s3-ecr.sh
template-s3-ecr.json
lambda/delete_s3_files/lambda_function.py
lambda/delete_ecr_repos/lambda_function.py
```

#### deploy-ssm-globals-macro.sh
Deploys project wide configuration values, such as project and domain name, into SSM Parameter Store. This script also
deploys an <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html">AWS CloudFormation Macro Lambda function</a> as well as other project wide macros.

All SSM parameters deployed from this script are deployed to the following SSM path:
```
/microservice/{your-project-name}/global/{ssm-parameter-key}
```

You can access SSM parameters in the <a href="https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Parameters:sort=Name">AWS EC2 console here</a>.

This script also deploys three different Lambda functions. One function is responsible for deleting network interfaces
associated with VPC Lambda functions (Lambda functions deployed within a VPC) that do not get automatically cleaned up
when deleting CloudFormation stacks with Lambda functions. If this function didn't exist within Phoenix, it could take up
to 45 minutes to delete CloudFormation stacks with VPC Lambda functions. You can read more about this issue <a href="https://forums.aws.amazon.com/thread.jspa?messageID=756642">here</a>. Another function is responsible for creating/updating/deleting encrypted SSM secrets during CloudFormation create/update/delete operations. Both of these
functions have exported ARN's that can be imported and used by other CloudFormation stacks.

Lastly, there is a CloudFormation Lambda Macro function that reads all SSM parameters into memory and renders CloudFormation templates dynamically. This macro is used by most Phoenix CloudFormation templates. The macro solves the following problems:

1. Provides central storage of global and environment specific SSM parameters across a small known set of files.
2. Avoids duplication of "template-ssm-globals-macro-params.json" params accross dozens of Cloudformation parameter files.
3. Avoids the CloudFormation limit of 60 SSM parameters per stack.
4. Avoids rate limiting associated with bursty SSM parameter calls from CloudFormation stacks.
5. Avoids having to add dozens of parameters to each CloudFormation template.
6. Enables easier git merges between the core Phoenix repository and other Phoenix repositories since project config is limited to a small group of files.

See [macro](#macro) for more information.

Usage:
```
./deploy-ssm-globals-macro.sh create
./deploy-ssm-globals-macro.sh update
```

Related Files:
```
deploy-ssm-globals-macro.sh
template-ssm-globals-macro-params.json
template-ssm-globals-macro.json
lambda/macro/lambda_function.py
lambda/delete_network_interface/lambda_function.py
lambda/ssm_secret/lambda_function.py
```

Before deploying this script, you must configure your project values in "template-ssm-globals-macro-params.json":

The project wide configuration values include, but aren't limited to, the following:
* Organization name
    * This would typically be the name of the company/organization associated with the repo.
* Project name
    * The name of your project. (User all lowercase, no dashes).
* Git repo name
    * The name of your git repository in GitHub.
* Git root project branch
    * The name of the git branch used to deploy to production
* Git current project branch
    * This is a deprecated field that can just be the same as the root project branch.
* GitHub organization
    * The name of your GitHub Organization
* Domain
    * The name of your domain (use "api.your-domain.com" for API's, and "your-domain.com" for applications)
* Hosted Zone ID
    * You must manually create a public hosted zone in the AWS Route53 console and enter this ID here.
* Key pair name
    * You must manually create an EC2 SSH key and enter the name of the key here (use "us-east-1-{your-aws-account-id}"
* Notification email
    * An email to send build notification to and other alerts
* IAM Role
    * You must manually create an IAM role with admin permissions which includes secretsmanager.amazonaws.com, cloudformation.amazonaws.com, codepipeline.amazonaws.com, codebuild.amazonaws.com, and lambda.amazonaws.com in the trust policy. This will get you started, but should obviously be changed if strong security is a concern.
* Code Build Docker Image
    * Enter the ID, including the image tag, of the ECR image you are using for your AWS CodeBuild jobs.
* NodeJS Build Docker Image
    * For build that require NodeJS, enter the ID, including the image tag, of the ECR image you are using. You can also just use the same ID as the code build docker image above.
* Git URL
    * This can just be "https://github.com"
* Pipeline Environments
    * A comma delimited list of environment names you wish to deploy to in the main pipeline.
* Release Environments
    * A comma delimited list of release environment names you wish to deploy to in all release pipelines.
* Version
    * The VERSION_ID value in this field will usually be replace with a timestamp from one of the deployment shell scripts.


#### deploy-pipeline.sh
Deploys an AWS CodePipeline for CI/CD on the main branch of your project. This will probably be the most frequently used
non-dev deployment script. You can add or remove pipeline stages and actions to your pipeline using this script. To do so,
just edit "template-pipeline.json" after reviewing the <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codepipeline-pipeline.html">CloudFormation AWS::CodePipeline::Pipeline</a> resource. A pipeline includes <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages.html">Stages</a>, which consist of one or more <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-codepipeline-pipeline-stages-actions.html">Actions</a>. Actions have a <a href="https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#action-requirements">Action Configuration</a> for specifying the behavior of the action, like building with AWS CodeBuild, Deploying with CloudFormation, or invoking a Lambda function. Actions and be run in parallel or sequentially within a stage using a numerica stage-scoped value called a "RunOrder". Actions can also be blocked until manual approval.

It is important to note that pushing changes to "template-pipeline.json" to your master branch does not update the pipeline.
To update the pipeline, you must run "./deploy-pipeline.sh update".

Since this template is so large, this deployment script first uploads the template to S3 before creating the stack. This is
because the template size is greater than <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html">51,200 bytes</a> and therefore cannot be read from locally when using the CloudFormation CLI.

Usage:
```
./deploy-pipeline.sh create
./deploy-pipeline.sh update
```

Related Files:
```
deploy-pipeline.sh
template-pipeline.json
```

#### deploy-github-access-token.sh
Uploads a GitHub access token into SSM Parameter Store that is used to create webhooks and make GitHub API requests. This script is usually run by the DevOps team when creating a new Phoenix project.

You must generate an access token within GitHub and pass it to this script. To generate a token, install pwgen locally and run 'pwgen 32 -1'.

This token is used in the following ways:
1) To create the webhook associated with the main pipeline of your project.
2) To create any other webhooks (pull requests, releases, etc.)
3) Making GitHub API calls through Lambda Custom Resources within CloudFormation templates.

When creating the webhook in GitHub, give it a name like "{YourProjectName}Webhook"
and give in the "repo" and "admin:repo_hook" scopes. Also be sure to select "Enable SSO"
and then "Authorize" else the token will not work.

Usage:
```
  ./deploy-github-access-token.sh {Github Token}
```

#### deploy-github-webhook-pull-request.sh
Deploys a pull request API Gateway endpoint and Lambda handler to dynamically generate pull request pipelines.

This script deploys a CloudFormation stack that does the following:
1. Deploys an API Gateway endpoint (for the GitHub webhook to send the pull request event to)
2. Generates a shared secret used by both GitHub and Lambda to HMAC authenticate requests (stored in SSM parameter store)
3. Creates the GitHub webhook with the shared secret and sets the webhook URL to the API Gateway endpoint.
4. Creates a Lambda function for receiving the webhook event which orhestrates pull request pipelines.
5. Creates another Lambda function which handles the final step of a pull request pipeline run.

This script is usually executed by the DevOps team when creating a new Phoenix project.

Usage:
```
  ./deploy-github-webhook-pull-request.sh create
  ./deploy-github-webhook-pull-request.sh update
```

Related Files:
```
deploy-github-webhook-pull-request.sh
template-pull-request-pipeline.json
template-github-webhook.json
lambda/pull_request_webhook/lambda_function.py
lambda/create_pull_request_webhook/lambda_function.py
lambda/post_pullrequests/lambda_function.py
```


#### deploy-github-webhook-release.sh

#### deploy-microservice-init.sh
This script bootstraps a new Phoenix project. Before invoking this script, you must follow the steps in both [One time configuration of your AWS account to work with Phoenix](#one-time-configuration-of-your-aws-account-to-work-with-phoenix) and
[Initial Phoenix Project Setup](#initial-phoenix-project-setup)

For details on the {GitHub token} argument, see the deploy-github-access-token.sh script.

Usage:
```
  ./deploy-microservice-init.sh {GitHub token}
```

Related Files:
```
deploy-microservice-init.sh
deploy-github-access-token.sh
```

#### deploy-microservice-cleanup.sh
Creates or updates a single CodeBuild job capable of destroying one or more environments and all AWS resources within that environment by deleting CloudFormation stacks in the correct order.

Note that invoking this script does not actually execute the CodeBuild job. To execute the CodeBuild job, you must
login to the CodeBuild console and kick off the "deploy-{project-name}-microservice" job. Click "Start Build", then click
"Environment Variable Override". Edit the following environment variables:

ENVIRONMENTS_TO_DELETE:
- This is a space delimited list of environment you'd like to delete.
- All CloudFormation stacks associated with this environment will be deleted.

DELETE_ENVIRONMENT_STATEFUL_RESOURCES:
- Whether to delete the stateful environment related resources associated with the environment.
- Stateful resources include RDS database instances, API documentation S3 buckets, Cognito resources, and API Custom Domain.

DELETE_GLOBAL_PROJECT_STATEFUL_RESOURCES:
- Whether to delete the global resources associated with the project.
- Global stateful resources include the pull request webhook, release webhook, pipeline, global SSM parameters, S3 buckets, ECR repository, ACM certificates, and the microservice cleanup stack.

Finally, click "Start Build" to delete the CloudFormation stacks.

Usage:
```
  ./deploy-microservice-cleanup.sh create
  ./deploy-microservice-cleanup.sh update
```

Related Files:
```
deploy-microservice-cleanup.sh
template-microservice-cleanup.json
buildspec-destroy-microservice.yml
```

### Developer Environment Specific Shell Scripts
A dev deploy script is a shell script within Phoenix that matches the file pattern of "deploy-dev-\*.sh". There are currently
13 such scripts, all of which deploy one or more dev environment CloudFormation stacks. All [Environment Specific Stacks](#environment-specific-stacks) have dev deployment scripts.

Note that these developer scripts are for deploying to developer environments only. None of these dev deploy scripts will
deploy to a testing, ec2, prod, pull request, or any other non-dev specific environment. Each developer on a team may execute
any shell script starting with "deploy-dev" safely without impacting production or any other environment.

Before running these scripts, a developer must execute the [generate_dev_params.py](#generate_dev_paramspy) Python script
with a unique dev environment name. Also, the ordering of calling these scripts should be in the following order:

```
./deploy-dev-ssm-environments.sh create
./deploy-dev-database.sh create --> Optional. If this stack already exists, skip this script.
./deploy-dev-ec2.sh create
./deploy-dev-lambda.sh create
./deploy-dev-ecs-task-main.sh create ecs --> Replace "ecs" with "sbt" for Scala projects.
./deploy-dev-api-custom-domain.sh create
./deploy-dev-api.sh create
./deploy-dev-api-deployment.sh create
```

Since all developer environments share a single Aurora database MySQL instance, the "deploy-dev-database.sh" script
only needs to be executed once for the entire Project. Individual devlopers do not need to invoke this script.

To delete a developer environment, See the instructions in [deploy-microservice-cleanup.sh](#deploy-microservice-cleanupsh)
to manually invoke a CodeBuild job to delete the developer environment.

#### API Dev Deployment Scripts
There are five developer API related deployment scripts:

Use by DevOps:
* [deploy-dev-api-custom-domain.sh](#deploy-dev-api-custom-domainsh)
* [deploy-dev-api-documentation.sh](#deploy-dev-api-documentationsh)

Used by developers:
* [deploy-dev-api.sh](#deploy-dev-apish)
* [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh)
* [deploy-dev.sh](#deploy-devsh)

Both the [deploy-dev-api-custom-domain.sh](#deploy-dev-api-custom-domainsh) and [deploy-dev-api-documentation.sh](#deploy-dev-api-documentationsh) are scripts that are mostly used by DevOps and can be ignored by developers.

The understand the differences between the three API scripts used by developers ([deploy-dev-api.sh](#deploy-dev-apish), [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh), and [deploy-dev.sh](#deploy-devsh)), developers must understand some basic <a href="https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-basic-concept.html">API Gateway Concepts</a>.

When running the [deploy-dev-api.sh](#deploy-dev-apish) script, it will update the API deployed in the Resources section of
your API in the <a href="https://console.aws.amazon.com/apigateway">API Gateway Console</a>, but will not be deployed in the
Stages section of your API. To deploy the API into the Stages section, you must run the [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh) script. Deploying your API deployment to a stage like V0 or V1 will make your API accessible via a nice looking URL like "https://devjason.api.you-domain.com/v0".

You cannot re-run [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh). To work around this, you should use the [deploy-dev.sh](#deploy-devsh) script with the correct arguments to see changes in your stage.


##### deploy-dev-api-custom-domain.sh
Deploys an API Gateway Custom Domain for your project's API.

When you deploy an edge-optimized API, API Gateway sets up an Amazon CloudFront distribution and a DNS record to map the API domain name to the CloudFront distribution domain name. Requests for the API are then routed to API Gateway through the mapped CloudFront distribution.

Usage:
```
  ./deploy-dev-api-custom-domain.sh create
  ./deploy-dev-api-custom-domain.sh update
```

Related Files:
```
deploy-dev-api-custom-domain.sh
template-api-custom-domain.json
template-api-custom-domain-params-dev.json
```

##### deploy-dev-api-deployment.sh
Deploys an immutable API Gateway deployment (API Snapshot) of a given API configuration. This script also deploys
additional configuration on the API that is not easily configurable using raw CloudFormation.

Within API Gateway resource methods, you can add a custom "Mapping Template" within the "Integration Request" portion
of the method congiruation. These mappings allow manipulation of the request headers and body before forwarding to Lambda.
These mapping templates use <a href="https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-mapping-template-reference.html">Apache Velocity</a> and are quite verbose. Hard coding these mappings directly into the CloudFormation template would require
lots of copy pasting and code duplication, so a <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda backed custom resource</a> was added to this template to automatically add this mapping template to any API methods that require
it.

It's important to note that **CloudFormation does not update previously deployed API Gateway stages** even if you change
the underlying API or the CloudFormation code. You can <a href="https://stackoverflow.com/questions/41423439/cloudformation-doesnt-deploy-to-api-gateway-stages-on-update">view this issue in detail here</a>. To redeploy to a state, you can deploy
via the API Gateway console. If you are deploying to an API Gateway stage for a developer environment, running the
[deploy-dev.sh](#deploy-devsh) shell script will automagically do this for you by making the appropriate AWS CLI calls so
 you don't have to redeploy to a stage using the AWS console.

Usage:
```
  ./deploy-dev-api-deployment.sh create
  ./deploy-dev-api-deployment.sh update
```

Related Files:
```
deploy-dev-api-deployment.sh
template-api-deployment
template-api-params-dev.json
lambda/api_internals/lambda_function.py
```

##### deploy-dev-api-documentation.sh
Deploys AWS resources required to support versioned API documentation. Resources include a static S3 website/bucket, Bucket policy, CloudFront distribution, Web Application Firewall ACL, WAF rules, and WAF predicates for managing API documentation access.

Note that this does not deploy API documentation itself. It just deploys the infrastructure required for hosting API
documentation securely.

It's challenging to store documentation in an S3 static **website** without exposting it to the world. While using a VPC endpoint to remove S3 bucket access from the internet works, this requires a lot of networking infrastructure to work with our VPN. The solution I chose was to add a "/global/api-docs-user-agent" SSM parameter to all Phoenix enabled AWS accounts and store a token used to auth HTTP requests made to the API documentation. This token is used by AWS Web Application Firewall to authenticate requests. API documentation viewers can install the "User-Agent Switcher for Google Chrome" extension to automatically pass this token to HTTP requests. You can view <a href="http://agibalov.io/2017/10/03/A-funny-way-to-restrict-access-to-website-hosted-on-S3/">this post</a> for details. This method may only be slightly better than having
publicly exposed API documentation and is insufficient for securing senstive information contained in API documentation. API documentation should not contain sensitive information, but having some level of privacy minimizes potential attack surface area. The Chrome extension should be **disabled** when not viewing API documentation to avoid page rendering issues when accessing websites that rely on this header.

API versioning works like this. The V0 API stage is intended to be used for the latest, most bleeding edge API development. It is not a stable version for releasing externally consumable API's. Once the team is ready to launch, a V1 stage can be
added by creating V1 template parameter files can a V1 api deployment stage in the pipeline. Try to stick with V1 as long
as possible before adding a V2 API.

Each developer may have their own V0, V1, V2, ... API deployments that can mirror what is running in other environments such as testing and production.

Usage:
```
  ./deploy-dev-api-documentation.sh create
  ./deploy-dev-api-documentation.sh update
```

Related Files:
```
deploy-dev-api-documentation.sh
template-api-documentation.json
template-api-documentation-{v0,v1,etc}-params-dev.json
```

##### deploy-dev-api.sh
Deploys an API Gateway API into a development environment.

This deploys an API Gateway API, API resources, API methods, and any other API Gateway related resources.

There are 2 different scripts that developers can used to deploy


Usage:
```
When first creating this stack, use the 'deploy-dev-api.sh' script:

  ./deploy-dev-api.sh create

For updates, it's better to use the 'deploy-dev.sh' script:

  ./deploy-dev.sh update ..

For example:

  ./deploy-dev-environment.sh update api-deploy l1l5pcj1xc v0

Where 'v0' is the API stage you are deploying to and 'l1l5pcj1xc' is an example API Gateway REST API ID.
```

You can find the REST API ID for your developer API between a set of parentheses in the gray nav bar at the top of the <a href="https://console.aws.amazon.com/apigateway">API Gateway Console</a> after clicking on your API on the left sidebar.

Before running "deploy-dev.sh", make sure to install <a href="https://www.npmjs.com/package/spectacle-docs">spectacle-docs</a> using the following command:
```
npm install -g spectacle-docs
```


See [deploy-dev.sh](#deploy-devsh) for more details.

Related Files:
```
deploy-dev-api.sh
deploys-dev.sh
template-api.json
template-api-params-dev.json
```

#### deploy-dev.sh
This script does the following:
1. Calls all of the appropriate dev scripts in the correct order to spin up an entire developer environment.
2. Deploys and updates a developer API deployment in API Gateway.
3. Launches local API documentation in the browser using <a href="https://www.npmjs.com/package/spectacle-docs">spectacle-docs</a>.

You may notice that this script makes aws apigateway API calls directly to forcefully delete and recreate API stages.
This is not possible using CloudFormation alone, so API calls are necessary.

Usage:
```
    ./deploy-dev-environment.sh create --> Creates entire developer environment.
    ./deploy-dev-environment.sh update api-deploy {rest-api-id} {stage-name} --> Deploys/updates API and locally launches API docs.

Where 'stage-name' is the API stage you are deploying to (v0, v1, etc) and 'rest-api-id' is an API Gateway REST API ID.
```

You can find the REST API ID for your developer API between a set of parentheses in the gray nav bar at the top of the <a href="https://console.aws.amazon.com/apigateway">API Gateway Console</a> after clicking on your API on the left sidebar.

Before running "deploy-dev.sh", make sure to install <a href="https://www.npmjs.com/package/spectacle-docs">spectacle-docs</a> using the following command:
```
npm install -g spectacle-docs
```

See [deploy-dev-api.sh](#deploy-dev-apish) for more details.

Related Files:
```
deploy-dev.sh
deploy-dev-api.sh
deploy-dev-api-deployment.sh
template-api-deployment-params-dev.sh
```

#### Cognito Dev Deployment Scripts
The Cognito developer scripts launch developer specific Cognito user pools, user pool clients, app client ID's,
and auth domains. Developers can test Cognito changes in their own dev cloud before merging changes into the main
pipeline.

##### deploy-dev-cognito.sh
Creates a Cognito app client and Cognito user pool for a developer cloud. This app client can be used as
an authorizor for API Gateway requests.

Usage:
```
  ./deploy-dev-cognito.sh create
  ./deploy-dev-cognito.sh update
```

Related Files:
```
deploy-dev-cognito.sh
template-cognito.json
template-cognito-params-dev.json
```

##### deploy-dev-cognito-internals.sh
Creates additional Cognito configuration for Cognito resources not supported by CloudFormation.

Take a look at the lambda function in the "lambda/cognito_internals" folder to see what resources
are provisioned with this script. It creates a Cognito resource server, a route53 record set
for an auth domain, and optionally a custom auth domain. Note that there is a hard limit of
4 custom auth domains per account, so it is only recommended to use "custom" auth domain
for production while using non-custom auth domains for all other environments.

Usage:
```
  ./deploy-dev-cognito-internals.sh create
  ./deploy-dev-cognito-internals.sh update
```

Related Files:
```
deploy-dev-cognito-internals.sh
template-cognito-internals.json
template-cognito-internals-params-dev.json
lambda/cognito_internals/lambda_function.py
```

#### deploy-dev-database.sh
This script deploys an Aurora MySQL cluster and supports cluster restores from snapshots. A custom Lambda resource within the template auomatically generates a password for new database instances, with some support for password rotation as well. There is also a CodeBuild job defined in this template that can be used for database migrations within the CI/CD CodePipeline.

Note that all developer clouds use the same dev database instance. This means the single dev database instance must
be able to handle load and connections from potentially several developer database clouds. Make sure to update
"template-database-params-dev.json" with a larger instance type if you plan on supporting several developer clouds.

This script is invoked once per Phoenix project since the dev database is shared accross multiple dev clouds.
It is possible to provide developers within their own databases with some modification in various files.

For further detail on the following:

* Creating a new database stack (without a snapshot)
* Updating a database stack (without a snapshot)
* Creating a database stack (with a snapshot)
* Updating a database stack (with a snapshot)
* Deleting a database instance
* Password rotation
* Finding historical passwords in SSM parameter store
* Testing Plan for the Lambda password generator

See <a href="https://docs.google.com/document/d/16UUY3h-4wU372XF8D0Fs1IQ3ABLrO-Vjn5ao2YkB84M/edit#">Phoenix for Datbase Admins</a>

Usage:
```
  ./deploy-dev-database.sh update
```

Related Files:
```
deploy-dev-database.sh
template-database.json
template-database-params-dev.json
lambda/password_generator/lambda_function.py
```

#### deploy-dev-ec2.sh
Generates developer cloud EC2 resources, some of which may run one or more ECS tasks/services in a given environment.

Phoenix tries to decouple EC2 resources from ECS resource by providing separate templates for EC2 and ECS resources.
There is a tiny bit of ECS configuration within the EC2 template, however. For example, Phoenix uses the EC2 template
to create the ECS cluster resource. We could have instead provision the ECS cluster in the ECS template, but then
each stack instance of the ECS template would create a new cluster, which probably isn't desired.

Also, the EC2 template is aware of whether or not Fargate is used instead of EC2 from the computer layer of ECS,
and will set to AutoScalingGroup to 0 if Fargate is used since no EC2 instances are required in this case.

This EC2 template also includes an API Documentation CodeBuild job which generates environment specific API documentation
artifacts and deploys them to an static website S3 bucket. Because this CodeBuild job is environment specific, it must
live in an environment specific stack and connect live in buildspec.yml. The EC2 template was chosen for this CodeBuild
job, but it could have been any other environment specific template.

Befor executing this script (or any developer script), you must complete a one-time configuration of your developer params:
```
    cd Phoenix
    python generate_dev_params.py dev{your-lowercase-firstname}

    For example, if you username is john.doe:
      python generate_dev_params.py devjohn
```

Usage:
```
  ./deploy-dev-ec2.sh create
  ./deploy-dev-ec2.sh update
```

Related Files:
```
deploy-dev-ec2.sh
template-ec2.json
template-ec2-params-dev.json
```

#### deploy-dev-ecs-task-main.sh
Generates a random docker image tag, builds a docker image, updates the CloudFormation parameters file with the new image tag,
and either creates or updates a developer cloud CloudFormation stack which deploys the locally build docker image to the
Dev ECS cluster in AWS.

This is probably one of the most complex templates within Phoenix. This shell script does the following:
1. Builds a local image from a local Dockerfile
    * The second argument of this script should be a folder that includes a Dockerfile.
    * If using a scala/sbt generated Dockerfile, you must do the following:
        * Make sure the relative path of "server/target/docker/stage" in the shell script points to your projects Dockerfile, else change it.
        * Pass in the value of "sbt" rather than the folder location of the Dockerfile as the second argument to this shell script.
2. Tags the Docker image with a timestamp (in non-developer environments, the first 7 characters of the Git commit is used)
3. Pushes the tagged docker image to the ECR repo
4. Creates/updates the developer ECS task to use the tagged Docker image. Visit the URL to view the live dev ECS service.

##### Viewing your ECS service
To view your developer cloud ECS service, access the URL via the CloudFormation console:
1. Open the <a href="https://console.aws.amazon.com/cloudformation/home">CloudFormation console</a> (make sure to switch to the right AWS region, us-east-1 is the default)
2. In the "Filter stacks" text field, type "ecs" and press enter.
3. Click on the stack with your username ({project-name}-ecs-main-dev{your-first-name})
4. Click on the "Outputs" tab
5. Click on the service URL (make sure you are logged into VPN since all ECS resources are in a private subnet by default)

##### Updating your ECS service
To make changes to your ECS service:
1. Edit "template-ecs-task-main-params-dev.json"
    * Change "DesiredTaskCount" to 2
2. Update the stack:
    * cd Phoenix
    * ./deploy-dev-ecs-task-main.sh update {path-to-folder-with-Dockerfile}
3. Open the <a href="https://console.aws.amazon.com/ecs/home">ECS Console</a> in the correct region to view your service
4. Click on your developer cluster
5. Click on the "Tasks" tab for your service
6. Verify that the number of task changed from 1 to 2.
7. Change the Change "DesiredTaskCount" back to 1, update, and verify the number of tasks again.

##### Multiple Task/Service/Container Scenario
Within Phoenix, developers have the ability to configure their own isolated developer ECS clusters with as many ECS tasks/services
as needed. Each ECS task can include up to 10 Docker containers (usually a main container and 9 sidecar containers). There
is one ECS task per stack instance of "template-ecs-task.json". Phoenix ships with a default/main ECS task
called "main" but there can be many tasks. For example, a project might have a "worker" task that has 3 supporting sidecar
containers for logging, monitoring, and caching. In addition, this project may have separate "frontend" and "backend" tasks/services for handling frontend and backend requests, each also having sidecar containers for logging, and caching. So, 3 different tasks/services
with 3 * (1 + 3) = 12 containers in total. Since all tasks/services have similar task configuration in our example, they all use the
same "template-ecs-task.json" template to configure their tasks. **For each environment**, the following files could be created for
this setup:

```
template-ecs-task-frontend-{environment}-params.json
template-ecs-task-backend-{environment}-params.json
template-ecs-task-worker-{environment}-params.json
```

The following deploys scripts would also be created (or the existing ecs dev deploy script could be parameterized):
```
deploy-dev-ecs-task-frontend.sh
deploy-dev-ecs-task-backend.sh
deploy-dev-ecs-task-worker.sh
```

To launch the above tasks into a pipeline, new Pipeline actions would have to be added to all pipeline files
and all relevant buildspec YAML files would also need to be updated. All of the above task types (frontend, backend, worker)
could potentially use the same "template-ecs-task.json" template, but if the task definitions diverge significantly, you
could create new templates for each task type:

```
template-ecs-task-frontend.json
template-ecs-task-backend.json
template-ecs-task-worker.json
```

In the above example, the networking and service discovery can be added by following documentation:
* <a href="https://aws.amazon.com/blogs/aws/amazon-ecs-service-discovery/">ECS Service Discovery Blog Post</a>
* <a href="https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html">ECS Service Discovery Documentation</a>
* <a href="https://aws.amazon.com/cloud-map/">AWS CloudMap</a>
    * <a href="https://aws.amazon.com/about-aws/whats-new/2018/11/introducing-aws-cloud-map/">AWS Cloud Map Blog Post</a>
    * <a href="https://aws.amazon.com/blogs/aws/aws-cloud-map-easily-create-and-maintain-custom-maps-of-your-applications/">AWS Cloud Map Blog Post</a>

This flexibility of adding new CloudFormation files, creating your own shell scripts, updating your Pipeline files,
and configuring networking & service discovery as you see fit highlights that Phoenix is **not a framework**. AWS is LEGO,
and Phoenix is just a set of instructions to build microservice LEGO castles.



Usage:
```
    ./deploy-dev-ecs-task-main.sh [ create | update ] sbt --> Always use this command for Play/SBT projects.
    ./deploy-dev-ecs-task-main.sh [ create | update ] .   --> Dockerfile in project root dir.
    ./deploy-dev-ecs-task-main.sh [ create | update ] ecs   --> Dockerfile in ecs dir.
```

Related Files:
```
deploy-dev-ecs-task-main.sh
template-ecs-task.json
template-ecs-task-params-dev.json
lambda/password_generator/lambda_function.py
```

#### deploy-dev-lambda.sh
Deploys developer cloud specific Lambda functions. Each developer will have their own set of these functions.

You can read more about these individual functions here:
[vpc_proxy])(#vpc_proxy)
[proxy](#proxy)
[alb_listener_rule](#alb_listener_rule)
[projects](#projects)

Usage:
```
    ./deploy-dev-lambda.sh create
    ./deploy-dev-lambda.sh update
```

Related Files:
```
deploy-dev-lambda.sh
template-lambda-params-dev.json
template-lambda.json
lambda/vpc_proxy/lambda_function.js
lambda/proxy/lambda_function.py
lambda/alb_listener_rule/lambda_function.py
lambda/projects/lambda_function.py
```


#### deploy-dev-ssm-environments.sh
Deploys developer cloud specific SSM parameters.

Phoenix encourages centralization of both global and environment specific project configuration. All config should
be decoupled from deployment artifacts such as docker images. While execution environments and config often change across
each deployment environment, artifacts deployed in these environments should not. This is why config should be decoupled
from deployment artifacts (see the <a href="https://12factor.net/config">Config</a> rule in 12 Factor Apps).

All environments, including developer environments, have their own SSM parameter CloudFormation stack for storing
config in SSM parameter store for that environment. This script deploys developer specific config values into
SSM parameter store.

To add a new config value and make it available to another CloudFormation stack, you must do the following:
1. Add a new key/value pair in "template-ssm-environments-dev.json"
2. Create a new "AWS::SSM::Parameter" resource in "template-ssm-environments.json"
3. In a different CloudFormation template, inject the value anywhere you wish:
```
{"PhoenixSSM": "/microservice/{ProjectName}/{Environment}/{your-parameter-key-name"}
```
**Take a look at the "Outputs" section near the bottom of the "template-lambda.json" template for an example**

The "PhoenixSSM" function isn't really a function, it's just a string that tells the Phoenix [macro](#macro) that this is a special value that must be replaced by an SSM parameter lookup. The [macro](#macro) replaces {ProjectName} with your
project's name and replaces {Environment} with the "Environment" parameter passed into your template before querying
SSM parameter store and replacing with value.

Usage:
```
    ./deploy-dev-ssm-environments.sh create
    ./deploy-dev-ssm-environments.sh update
```

Related Files:
```
deploy-dev-ssm-environments.sh
template-ssm-environments-dev.json
template-ssm-environments.json
```

## CodeBuild buildspec.yml Files
A <a href="https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html">build spec</a> is a collection of build commands and related settings, in YAML format, that AWS CodeBuild uses to run a build. You can include a build spec as part of the source code or you can define a build spec when you create a build project. For information about how a build spec works, see <a href="https://docs.aws.amazon.com/codebuild/latest/userguide/concepts.html#concepts-how-it-works">How AWS CodeBuild Works</a>.

Phoenix groups CodeBuild jobs into three different types:
1. Build Stage
2. Environment Specific
3. Manually Invoked

"Build Stage" CodeBuild jobs run in the "Build" stage of a code pipeline, before any environments are deployed to. These jobs, build artifacts, run unit tests against code, and run static analysis or lint checks on the code. If any of these jobs
fail, the pipeline stops.

"Environment Specific" CodeBuild jobs run in a specific deployment stage (testing, ec2, prod) of a CodePipeline. These CodeBuild jobs often require infrastructure like RDS databases to be up before the job starts. For example, "buildspec-rds-migration.yml" runs a database migration for a specific database deployed in a given environment. If any of these jobs
fail, the deployment stage is failed in that environment.

"Manually Invoked" CodeBuild jobs are jobs that are not invoked in a CodePipeline, but are invoked manually by a user from within the CodeBuild console.

### Build Stage CodeBuild jobs
These CodeBuild jobs run in the "Build" stage of a code pipeline, before any environments are deployed to. These jobs, build artifacts, run unit tests against code, and run static analysis or lint checks on the code. If any of these jobs
fail, the pipeline stops.

#### buildspec.yml
Builds docker images, lambda functions, and infrastructure artifacts such as CloudFormation template parameter files.

This is the most important build spec in Phoenix. This same buildspec.yml is used for all pipelines:
1. Main Pipeline
2. Pull Request Pipelines
3. Release Pipelines

Each of the above 3 pipeline types has a CloudFormation template:
```
template-pipeline.json
template-pull-request-pipeline.json
template-release-environment-pipeline.json
```

Each cloudFormation template above has a single CodeBuild job that points to the same buildspec.yml file. The only difference
between these 3 CodeBuild jobs (all pointing to the same buildspec.yml) is that the environment variables configured for
each CodeBuild job are different.

This buildspec.yml job does the following:
1. Receives all source code associated with a single git commit.
2. Generates a $VERSION_ID environment variable from the first 7 characters of the git commit SHA1.
3. Loops through all environments (testing, e2e, prod, etc.) and injects the $VERSION_ID value into the Cloudformation parameter files.
4. Builds a docker image and tags it with the $VERSION_ID.
5. Loops through several lambda functions and deploys their source bundles into an S3 folder with the $VERSION_ID as the folder name.
6. Runs the Phoenix/pull_request_codebuild.py script (this will be a no-op for non-pull request builds)
    * For pull request builds, this script will report build statuses back to GitHub.
7. Pushes the docker image to the project's ECR repo.
8. Exports all artifacts, including Cloudformation templates and parameter files, for later pipeline deployment actions.


Related Files:
```
buildspec.yml
template-pipeline.json
template-pull-request-pipeline.json
template-release-environment-pipeline.json
pull_request_codebuild.py
```

#### buildspec-unit-test.yml
This is a placeholder file for running unit tests against source code. If your tests are large, consider
splitting your tests across muiltiple unit testing CodeBuild jobs running in parallel.

#### buildspec-lint.yml
This is a placeholder file for running lint or static analysis against source code to check for code quality.

### Environment Specific CodeBuild jobs
These CodeBuild jobs run in a specific deployment stage (testing, ec2, prod) of a CodePipeline. These CodeBuild jobs often require infrastructure like RDS databases to be up before the job starts. For example, "buildspec-rds-migration.yml" runs a database migration for a specific database deployed in a given environment. If any of these jobs
fail, the deployment stage is failed in that environment.

#### buildspec-api-documentation.yml
Generates an publishes environment specific API documentation for your API.

1. Exports a swagger file from your API Gateway deployment.
2. Generates API documentation using <a href="https://www.npmjs.com/package/spectacle-docs">spectacle docs</a>.
3. Uploads this documentation to an S3 bucket.
4. Invalidates the CloudFormation cache to ensure the latest documentation is visible.

#### buildspec-integration-test.yml
This is a placeholder file for running integration tests against a deployed environment.

#### buildspec-rds-migration.yml
This is a placeholder file for running a database migration within a deployment stage.

#### buildspec-post-prod-deploy.yml
This is a post production deployment hook to do anything you want. Currently it's being used to enable termination
protection on production Cloudformation stacks.

###  Manually Invoked CodeBuild jobs
CodeBuild jobs are jobs that are not invoked in a CodePipeline, but are invoked manually by a user from within the CodeBuild console.

#### buildspec-destroy-microservice.yml
This CodeBuild job can destroy all stacks in one or more deployment environments.

See [deploy-microservice-cleanup.sh](#deploy-microservice-cleanupsh) for details.


## Python Helper Scripts
Phoenix ships with various Python scripts to automate various tasks. The naming convention for these Python script files
is to use underscores.

### parameters_generator.py
Converts CloudFormation parameters to the native format expected by the CloudFormation CLI.

Code Pipeline expects <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html#w2ab2c13c15c13">this format</a> for CloudFormation parameters, while CloudFormation expects <a href="https://aws.amazon.com/blogs/devops/passing-parameters-to-cloudformation-stacks-with-the-aws-cli-and-powershell/">this format</a>.

This Python script is often called from the main buildspec.yml file and also many of the local shell scripts.

Usage:
```
    python parameters_generator.py template.json {cloudformation | codepipeline} > temp.json
```

Where "template.json" is in either cloudformation or codepipeline parameter format and the next argument
specifies which format is desired in the output file.

If "cloudformation" is specified, the "temp.json" file would be used in CloudFormation CLI calls:
```
    aws cloudformation create-stack --stack-name <stack_name> --template-body file://template.json --parameters file://temp.json
```

If "codepipeline" is specified, the "temp.json" file would be used in CodePipeline deployment actions (see template-pipeline.json):
```
    "TemplateConfiguration": "BuildOutput::temp.json",
```

### search_and_replace.py
Recursively searches and replaces all strings in a given directory for a given file pattern.

This is a very simple but extremely useful Python script, especially for refactoring.

Usage:
```
  $ python search_and_replace.py {directory_to_search} {string_to_find} {replacement_string} {pattern}
```

Example:
  The following Recursively searches for the string FOO and replaces with BAR
  for all text files in the current directory and all subdirectories.

```
  $ python search_and_replace.py . FOO BAR    ==> Matches ALL files, like *
  $ python search_and_replace.py . FOO BAR file.txt  ==> Matches a single file.
  $ python search_and_replace.py . FOO BAR "*"  ==> Matches ALL files, like *
  $ python search_and_replace.py . FOO BAR "*.txt"  ==> Matches
```

### generate_environment_params.py
Generates CloudFormation JSON environment specific parameter files.

This script just copies all of the *params-testing.json files and generates
namespaced *-params-{environment}.json files. If the '--delete' flag is passed
in, all files matching *-params-{environment}.json will be deleted.

Typically you'll only need to run this script once per new environment. It is
a utility script to make is easier to generate all of the cloudformation
parameter files for a new environment.

The 'environment' arg can be something like 'staging' or 'rc'.
When CloudFormation stacks are launched using these parameter files,
all AWS resources will be identified by this environment such as
URL's, ECS clusters, Lambda functions, etc.

Usage:
```
    python generate_environment_params.py {environment}
    python generate_environment_params.py {environment} --delete
```

Examples:
```
    python generate_environment_params.py staging
    python generate_environment_params.py staging --delete
```

### rename_ssm_parameter.py
Renames SSM parameter **keys** from an old value to a new value, optionally for encrypted parameters (True|False).

Use this script only for parameters that are **not deployed via CloudFormation** (see template-ssm-globals-macro-params.json). This is because CloudFormation contains the source of truth for parameter names.

You can use this script refactor the base paths of several manually configured SSM parameters, such as for secrets and tokens.

Usage:
```
    python rename_ssm_parameter.py {old_param_key} {new_param_key} [True | False]
```

Examples:
```
    python rename_ssm_parameter.py /some/param/key /some/param/new-key True --> param is encrypted.
    python rename_ssm_parameter.py /some/param/key /some/param/new-key False --> param is not encrypted
```

### cfn_stacks.py
Helper script used to make CloudFormation API calls.

Add functions to this script when making CloudFormation CLI calls from shell code or buildspec YAML files involves
more complex logic.

Usage:
```
    python cfn_stacks.py delete-if-exists {stack_name}
    python cfn_stacks.py disable-termination-protection {stack_name}
```

Examples:
```
    python cfn_stacks.py delete-if-exists some-stack-name
    python cfn_stacks.py disable-termination-protection some-stack-name
```

### generate_dev_params.py
Generates CloudFormation JSON dev parameter files.

This script just copies all of the *params-testing.json files and generates
namespaced *params-dev.json files. Dev param files are used only by developers when
launching CloudFormation stacks during local development.

The 'environment_name' arg can be something like 'dev{username}' where
username is the developers username. When CloudFormation stacks are launched
using these parameter files, many AWS resources will be identified by this
environment_name such as URL's, ECS clusters, Lambda functions, etc.

Usually this script only needs to be invoked once per team member per project. When a new developer starts working
with Phoenix for the first time, they should run this script once in their local project git repo.

The *params-dev.json files are ignored by .gitignore so so the dev parameter files associated with different
developers do not conflict/clash with eachother. This script's exection impacts local files only.

Usage:
```
    python generate_dev_params.py {environment_name}
```

Examples:
```
    python generate_dev_params.py devjason
```

### pull_request_codebuild.py
Handles CodeBuild jobs executing in the context of a GitHub Pull Request.

```
    python pull_request_codebuild.py [build | unit-test | lint]
```

The main function of this Python script is to notify GitHub of build/unit-test/lint CodeBuild job statuses (pass or fail?) during GitHub pull request pipeline executions.

This script is usually invoked in the "post_build" step of the following buildspec YAML files:
```
    buildspec.yml
    buildspec-unit-test.yml
    buildspec-lint.yml
```

This script accesses environment variables available on the CodeBuild node host to determine what to do. These environment variables are automatically set on the CodeBuild job definition from the 'template-pull-request-pipeline.json' CloudFormation stack. This stack is created by a Lambda function that is invoked by a GitHub webhook for pull request events.

This script does the following:
1) Persists a github.json file that is passed by CodePipeline to a Lambda function.
2) Notifies GitHub of the status of AWS CodeBuild jobs.
3) Generates an ECS parameter template specifically for spinning up
   a dev ECS instance used during code review.

As long as you have the environment variables set as specified in the
initializer, you can run this script either locally or on AWS CodeBuild.

## Python 3.6 Lambda Functions
Phoenix leverage AWS Lambda for many event based workloads, such as handling GitHub webhooks or cleaning up AWS resources
during stack deletions.

All Lambda functions are located in the "lambda" subfolder of the Phoenix directory. Most of these functions use the
Python3.6 runtime but a few use NodeJS.

There are many frameworks out there that deploy Lambda functions, but Phoenix deploys Lambda simply by zipping up the
file contents, saving the zip to a versioned S3 folder (either using a timestamp or a git commit SHA1), and provisioning
the Lambda functions using CloudFormation (which then pick up the source in the versioned S3 folder).

For example, the shell code snippet below loops through some function names within the "Phoenix/lambda" folder:
```
listOfPythonLambdaFunctions='projects delete_network_interface alb_listener_rule proxy'
for functionName in $listOfPythonLambdaFunctions
do
  mkdir -p builds/$functionName
  cp -rf lambda/$functionName/* builds/$functionName/
  cd builds/$functionName/
  pip install -r requirements.txt -t .
  zip -r lambda_function.zip ./*
  aws s3 cp lambda_function.zip s3://$LAMBDA_BUCKET_NAME/$VERSION_ID/$functionName/
  cd ../../
  rm -rf builds
done
```

Where $LAMBDA_BUCKET_NAME is usually {organization-name}-{project-name}-lambda and the $VERSION_ID is usually a
timestamp for developer deployments or a git SHA1 for pipeline deployments.

The CloudFormation code snippet below deploys the Lambda function itself:
```
    "LambdaProjects": {
      "Type": "AWS::Lambda::Function",
      "Properties": {
        "Handler": "lambda_function.lambda_handler",
        "Code": {
          "S3Bucket" : "your-bucket-name",
          "S3Key" : {"Fn::Join": ["/", [
            {"Ref": "Version"},
            "projects",
            "lambda_function.zip"
          ]]}
        },
        "Runtime": "python3.6",
        "Timeout": "25"
      }
    },
```

Where the above function deploys a Python Lambda function that times out after 25 seconds. The source code of the Lambda
function would be found at "s3://your-bucket-name/$VERSION_ID/projects/lambda_function.zip", which is where our
shell code above deployed it to on the first loop iteration.


### alb_listener_rule
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> for creating ALB redirection rules.

This is particularly useful for adding HTTP->HTTPS redirects to Application
Load Balancers.

At the time this was created, AWS had introduced redirect rules on ALBs but
had not yet made them available in CloudFormation. The boto3 Python library
does support it however.

Original Git Repo:
https://github.com/jheller/alb-rule/blob/master/lambda/alb_listener_rule.py

Related Files:
```
lambda/alb_listener_rule/lambda_function.py
deploy-dev-lambda.sh
template-lambda.json
buildspec.yml
```


### api_internals
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> for altering the request body of API Gateway HTTP requests being sent
to Lambda functions.

See [deploy-dev-api-deployment.sh](#deploy-dev-api-deploymentsh) for details.

Related Files:
```
lambda/api_internals/lambda_function.py
deploy-dev-api-deployment.sh
template-api-deployment.json
buildspec.yml
```

### cognito_internals
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> for creating/updating/delete Cognito resources that are not supported
by CloudFormation.

See [deploy-dev-cognito-internals.sh](#deploy-dev-cognito-internalssh) and [template-cognito-internals.json](#template-cognito-internalsjson) for details.

Related Files:
```
lambda/cognito_internals/lambda_function.py
deploy-dev-cognito-internals.sh
template-cognito-internals.json
buildspec.yml
```

### create_pull_request_webhook
Creates a GitHub webhook within GitHub for sending pull request events to an endpoint.

View the full GitHub Pull Request REST API <a href="https://developer.github.com/v3/activity/events/types/#pullrequestevent">here</a>.

This Lambda function calls three lambda functions depending on the stack even type:
1. create_webook()
2. update_webhook()
3. delete_webhook()

When "create_webhook" is called, it grabs the project's Git access token and a shared pull request secret from SSM parameter store and makes a GitHub API call to create a pull request webook. When the CloudFormation stack is deleted, this Lambda function automatically deletes the GitHub webhook.

This function creates the pull request webhook. The [pull_request_webhook](#pull_request_webhook) processes webhook events to orchestrate pull request pipelines.

Related Files:
```
lambda/create_pull_request_webhook/lambda_function.py
deploy-github-webhook-pull-request.sh
template-github-webhook-pull-request-params.json
Phoenix/lambda/create_pull_request_webhook
Phoenix/lambda/pull_request_webhook
Phoenix/lambda/post_pullrequests
```

### create_release_webhook
Creates a GitHub webhook within GitHub for sending release related events to an endpoint.

This Lambda function calls three lambda functions depending on the stack even type:
1. create_webook()
2. update_webhook()
3. delete_webhook()

When "create_webhook" is called, it grabs the project's Git access token and a shared release secret from SSM parameter store and makes a GitHub API call to create a release webook. When the CloudFormation stack is deleted, this Lambda function automatically deletes the GitHub webhook.

This function creates the release webhook. The [release_webhook](#release_webhook) processes webhook events to orchestrate release pipelines.

Related Files:
```
lambda/create_release_webhook/lambda_function.py
deploy-github-webhook-release.sh
template-github-webhook-release-params.json
Phoenix/lambda/create_release_webhook
Phoenix/lambda/release_webhook
```

### delete_ecr_repos
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> that automatically deletes all images in one or more ECR repos, as well as the ECR repo itself. This is particularly useful for automatically deleting ECR repos upon stack deletion since CloudFormation cannot delete non-empty ECR repos.

Related Files:
```
lambda/delete_ecr_repos/lambda_function.py
deploy-s3-ecr.sh
template-s3-ecr.json
```

### delete_network_interface
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> that force deletes the ENI associated with a Lambda function residing
inside of a VPC upon stack deletion. There is currently a <a href="https://forums.aws.amazon.com/thread.jspa?messageID=756642">bug</a> where CloudFormation fails to delete lambda functions (functions that are created inside of a VPC) upon stack deletion. As a result, the stack will hang.

Some Lambda functions are deployed into an VPC. When Cloudformation stacks with these functions are deleted, the stack will
wait up to **45 minutes** for the Elastic Networking Interface (ENI) associated with the Lambdas to be deleted.

Before I wrote this function, I had to complete the following to delete CloudFormation stacks that had VPC Lambdas:
1. Find security group id associated with the Lambda function
2. Open the EC2 console and click on the "elastic networkg interface" section
3. Search for the ENI associated with the security
4. Delete the ENI
5. Wait a few minutes for CloudFormation to detect the deleted ENI and finally delete the stack

The "delete_network_interface" function automates the above steps, so cleanup happens automatically.

Related Files:
```
lambda/delete_network_interface/lambda_function.py
deploy-dev-lambda.sh
deploy-ssm-globals-macro.sh
template-ssm-globals-macro.json
buildspec.yml
```

### delete_s3_files
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> that automatically deletes all files in one or more S3 buckets upon
stack deletion.

This is useful when deleting S3 bucket resources in CloudFormation since CloudFormation cannot delete non-empty S3 buckets
when CloudFormation stacks are deleted.

If this Lambda function did not exist, you would not be able to delete the S3/ECR stacks without first deleting the following:
1. All files in all CloudFormation created S3 buckets.
2. All images in all CloudFormation created ECR repositories.

Related Files:
```
lambda/delete_s3_file/lambda_function.py
deploy-s3-ecr.sh
deploy-dev-api-documentation.sh
template-s3-ecr.json
buildspec.yml
```

### macro
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html">Lambda Macro function</a> that adds custom function to CloudFormation templates, such as reading all SSM parameters into memory and rendering the values into CloudFormation templates dynamically, or copying JSON files from S3 and rendering them into CloudFormation templates. The "PhoenixSSM" custom function within the macro is used by most Phoenix CloudFormation templates. The function solves the following problems:

1. Provides centralize storage of global and environment specific SSM parameters across a small known set of files.
2. Avoids duplication of "template-ssm-globals-macro-params.json" params accross dozens of Cloudformation parameter files.
3. Avoids the CloudFormation limit of 60 SSM parameters per stack.
4. Avoids rate limiting associated with bursty SSM parameter calls from CloudFormation stacks.
5. Avoids having to add **dozens of parameters** to each CloudFormation template.
6. Enables easier git merges between the core Phoenix repository and other Phoenix repositories since project config is limited to a small group of files.

See [deploy-ssm-globals-macro.sh](#deploy-ssm-globals-macrosh] for more information.

All throughout Phoenix templates, you'll see values such as this:
```
    {"PhoenixSSM": "/microservice/{ProjectName}/global/project-name"}
    {"PhoenixSSM": "/microservice/{ProjectName}/global/domain"}
    {"PhoenixSSM": "/microservice/{ProjectName}/global/iam-role"}
    {"PhoenixSSM": "/microservice/{ProjectName}/global/hosted-zone-id"}
    {"PhoenixSSM": "/microservice/{ProjectName}/global/code-build-docker-image"},
    {"PhoenixSSM": "/microservice/{ProjectName}/global/lambda-bucket-name"}
    {"PhoenixSSM": "/microservice/{ProjectName}/global/ssl-certificate-arn-api-docs"}
```
Where {ProjectName} is replaced by Lambda with your project's name.

The SSM replacement function can also interpolate on CloudFormation parameter values:
```
{"PhoenixSSM": "/microservice/{ProjectName}/{Environment}/{your-parameter-key-name"}
```
Where {Environment} is a CloudFormation parameter in the template that gets passed to the macro for interpolation.

The above {"PhoenixSSM":...} values will be replaced by the macro with whatever is in SSM parameter store for your project.
To add, update, or delete these SSM parameters to your project, see [deploy-ssm-globals-macro.sh](#deploy-ssm-globals-macrosh) and [deploy-dev-ssm-environments.sh](#deploy-dev-ssm-environmentssh).

I've created a very basic CloudFormation macro <a href="https://github.com/jasondebolt/cloudformation-search-and-replace-macro">in this GitHub repo</a> for anybody to experiment with. Feel free to clone this repo and poke around. More detailed information about CloudFormation macros can be found <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-macros.html">here</a>

In addition the SSM parameter injection, this macro also supports AWS S3 transforms:
```
    Replaces references like the following:

    {"PhoenixS3Transform": "transform-filename.json"}
    {"PhoenixS3Transform": {"Ref": "SomeFilenameParam"}

    ..with JSON from a file in S3.

    This assumes that the file has already been uploaded to your Phoenix project's S3 bucket
    under the 'cloudformation' folder of the bucket.

    This is similar to the CloudFormation Transform AWS::Include macro, but less limiting
    because "AWS::Include" can't be used form within certain CloudFormation intrinsic functions.
```

Related Files:
```
lambda/macro/lambda_function.py
template-ssm-globals-macro.json
deploy-ssm-globals-macro.sh
```

### password_generator
A CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> that generates, encrypts, and stores RDS or Aurora instance MasterUser passwords in SSM parameter store.

Optionally retrieves passwords and returns to a Cloudformation stack. However, this is not recommended as it would expose the
password in the CloudFormation logs. It's better to have the application query SSM parameter store instead.

Related Files:
```
lambda/password_generator/lambda_function.py
deploy-dev-database.sh
template-database.json
buildspec.yml
```

### post_pullrequests
Handles the final stages of the pull request pipeline, after all tests pass and the ECS container is deployed.

The function is called from the CodePipeline service during the final action of a Pull Request Pipeline. Note that
this function is only called if a pull request environment is deployed to.

The Lambda function does the following:
1. Receives a CodePipeline event object.
2. Extracts the ECS URL and Git Commit SHA1 from the CodePipeline event object.
3. Generates the below request body to send to GitHub:
   ```
   View deployed container (<a href={ecr-url}>{ecr-url}</a>) @ commit {git-commit-sha1}
   ```
4. Sends the request via the GitHub API to the pull request associated with pipeline.

Related Files:
```
lambda/post_pullrequests/lambda_function.py
deploy-github-webhook-pull-request.sh
pull_request_codebuild.py
template-github-webhook-pull-request-params.json
```

### projects
This is a Lambda function used for testing purposes.

This function can be called by invoking the "/projects" API gateway endpoint within the API Gateway console.
The projects function demonstrates how to write up a Lambda function to API Gateway. It can be deleted as long as all
references to this file are deleted as well (see Related Files below).

Related Files:
```
lambda/project/lambda_function.py
template-api.json
template-lambda.json
deploy-dev-lambda.sh
buildspec.yml
```

### proxy
A bare bones Lambda proxy that does the following:

1. Receives an HTTP request from API Gateway.
2. Forwards the HTTP request to another server.
3. Returns the HTTP response back to API Gateway.

The reason Lambda proxy functions are useful it because API Gateway can forward requests to Lambda functions
that are deployed in a VPC. These Lambda functions can then forward the request to other resources in the VPC.

API Gateway can forward request to public IP address, but not to private IP's associated with a VPC resources. The workaround
is to forward the requests to a VPC Lambda, which can then proxy the request to a private IP.

Related Files:
```
lambda/proxy/lambda_function.py
deploy-dev-lambda.sh
template-lambda.json
buildspec.yml
```

### pull_request_webhook
Handles <a href="https://developer.github.com/v3/activity/events/types/#pullrequestevent">GitHub pull request events</a> from GitHub.

This is probably the most important Lambda function within Phoenix since it orchestrates pull request pipelines.
This function creates, updates, and deletes pull request pipelines upon receiving GitHub pull request events
from GitHub. This function depends on [create_pull_request_webhook](#create_pull_request_webhook) having already
been deployed.

After [create_pull_request_webhook](#create_pull_request_webhook) creates a single webhook to handle all pull
request events from GitHub, these pull request events will later be consumed by yet another lambda function (this one,
[pull_request_webhook](#pull_request_webhook)). The "pull_request_webhook" function sits behind API Gateway and processes
the pull request event by creating, updating, or deleting a pull request pipeline. If a pull request is deleted,
the pull request pipeline as well as all AWS resources deployed in the pipeline (EC2 instances, ECS clusters, etc.)
are deleted as well.

Related Files:
```
lambda/pull_request_webhook/lambda_function.py
deploy-github-webhook-pull-request.sh
template-github-webhook-pull-request-params.json
template-github-webhook.json
```

### release_webhook
Handles <a href="https://developer.github.com/v3/activity/events/types/#pushevent">GitHub push events</a> associated with release branches from GitHub.

This function depends on [create_release_webhook](#create_release_webhook) having already been deployed.

A release branch is any branch matching the pattern "release-\d{8}$". So, a release on December 15th 2018 would have a git branch like "release-20181215" and a separate release pipeline for every release environment in your [template-ssm-globals-macro.json](#template-ssm-globals-macrojson) file.

To create a release environment, do the following:
1. Create the [release_webhook](#create_release_webhook) if it already hasn't been created.
2. Create and checkout a new git branch locally with a branch name matching the pattern "release-\d{8}$":
    * You can use 8 digits for today's date in YYYYMMDD format.
3. Provide a named environment like "staging" in the "ReleaseEnvironments" parameter of the
[template-ssm-globals-macro.json](#template-ssm-globals-macrojson) file.
    * A comma delimted list for multiple release environments is allowed.
4. Update the "ssm-globals-macro" stack and wait for the stack to complete.
```
    ./deploy-ssm-globals-macro.sh update
```
5. Create CloudFormation parameter files for your new release environment.
    * See [generate_environment_params.py](#generate_environment_paramspy) for details.
```
    python generate_environment_params.py staging
```
6. Git commit these changes in the release branch and push the branch to github.
7. Open AWS CodePipeline and view one or pipelines pertaining to your release environments.

Notes on release environments:
* You can have many release pipelines (each associated with a separate, isolated environment)
* Each environment has its own EC2 instances, security groups, lambda functions, URL's, etc.
* All release pipelines listen to the same release branch, so you should try to have only one release branch at a time.
* Deleting a release branch will delete all release pipelines, but will not delete the release environment's AWS resources.
* Creating a new release branch and pushing changes to it will do the following:
    * Create new release pipelines, one for each release environment.
    * Create or update all release environments.
    * Any existing release environments associated with other release branchs will be overwritten.
* To delete a release environment, execute the [destroy microservice](#deploy-microservice-cleanupsh) CodeBuild job
  for the release environment in question.

Related Files:
```
lambda/release_webhook/lambda_function.py
deploy-github-webhook-release.sh
template-github-webhook-release-params.json
template-github-webhook.json
```

### ssm_secret
Creates, updates, and deletes **secret** SSM parameters in parameter store.

**warning** these secrets are deleted upon stack deletion. Only used these secrets for things like GitHub webhook
tokens that can be easily replaced. In fact, GitHub webhook tokens are currently all that this function is used for.

GitHub webhooks required a shared secret between the sender (GitHub) and the receiver (Lambda) to authenticate using HMAC auth. This shared secret is generated by this "ssm_secret" lambda function and made available at the following points:
1. At the time the webhook is created ([template-github-webhook.json](#template-github-webhookjson))
2. At the time the webhook event is received/handled by Lambda:
    * ([pull_request_webhook](#pull_request_webhook)))
    * ([release_webhook](#release_webhook)))

If you look at [template-github-webhook.json](#template-github-webhookjson) you will see that this Lambda function is
used to create a CloudFormation <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-custom-resources-lambda.html">Lambda-backed custom resource</a> called "CustomResourceGitHubSecret". This custom resource
invokes the lambda function which generates a 100 character secret that is persisted to SSM parameter store. This
same secret is used by both the

Related Files:
```
lambda/ssm_secret/lambda_function.py
deploy-ssm-globals-macro.sh
template-ssm-globals-macro.json
template-github-webhook-release-params.json
template-github-webhook-pull-request-params.json
template-github-webhook.json
```


## Non-Python Lambda Functions
Whenever possible, try to use Python3.6 for all Lambda functions within Phoenix, as well as for all local Python scripts.
Sometimes this isn't possible since off-the-shelf Lambda functions can be leveraged to solve common problems.

### vpc_proxy
Proxies HTTP requests from API Gateway to resources in a VPC.

To isolate critical parts of their app’s architecture, we often rely on Virtual Private Cloud (VPC) and private subnets. Today, Amazon API Gateway cannot directly integrate with endpoints that live within a VPC without internet access. However, it is possible to proxy calls to your VPC endpoints using AWS Lambda functions.

This is exactly how to function is used. This function is nearly identical to the one documented in the <a href="https://aws.amazon.com/blogs/compute/using-api-gateway-with-vpc-endpoints-via-aws-lambda/">Using API Gateway with VPC endpoints via AWS Lambda</a> blog post.


Related Files:
```
lambda/vpc_proxy/lambda_function.py
deploy-dev-lambda.sh
template-lambda.json
lambda/api_internals/lambda_function.py
template-api.json
template-api-deployment.json
```

## Example Dockerfile
A basic Dockerfile used for testing within Phoenix.

You can find where this image is build in the main pipeline's [buildspec.yml](#buildspecyml) file:
```
    docker build -t $MAIN_REPOSITORY_URI:$IMAGE_TAG $CODEBUILD_SRC_DIR/Phoenix/ecs
```

For dev cloud deployments, you can find where this test image is build in the [deploy-dev-ecs-task-main.sh](#deploy-dev-ecs-task-mainsh) file.
```
    docker build -t $ECR_REPO $2
```

I decided to use a Python Flask app for the example/test image because it's extremely lightweight. This Dockerfile
can be replace with anything, but make sure the exposed port in the ECS main task parameter file matches the port
of your app.

Related Files:
```
ecs/app.py
ecs/Dockerfile
ecs/requirements.txt
buildspec.yml
deploy-dev-ecs-task-main.sh
template-ecs-task-main-params-*.json
template-ecs-task.json
```
