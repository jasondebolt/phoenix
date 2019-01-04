# Phoenix Microservice
A full CI/CD solution for continuously building and deploying RDS, ECS, Lambda, and API Gateway resources.
<img src="/Phoenix/images/logo.png" height="70px"/>

![Pipeline](/Phoenix/images/pipeline_1a.png)
![Pipeline](/Phoenix/images/pipeline_1b.png)


#### What ships with Phoenix?
##### Phoenix Microservice (template-pipeline.json)
* Creates a local CodeCommit repo which stores all of your source code, buildspecs, templates, etc.
* Creates an ECR repo for your project's Docker images.
* Creates an AWS CodePipeline which will CI/CD any changes pushed to master.
* Creates an S3 bucket to store Lambda functions.
* Creates an S3 bucket to store load balancer logs.
* Creates an S3 bucket to store CodePipeline artifacts.
* Creates an S3 bucket to store CodeBuild artifacts.
* Creates an SNS topic which triggers on master branch commits.
* Creates an SNS topic which triggers on master branch commits.
* Creates a CodePipeline service role.
* Creates a CodeBuild service role.
* Creates a CodePipeline approval SNS topic to notify pipeline approvers.
* Creates a Codebuild project for building Docker images, Lambda functions, and versioning.
* Creates a Codebuild project linting source code.
* Creates a Codebuild project unit testing source code.
* Creates a Codebuild project for running static analysis on source code.
* Creates a Codebuild project calculating AWS costs for deployed resources.
* Creates a Codebuild project for running integration tests.
* Creates a deployment script to create/update a dev RDS instance.
* Creates a deployment script to build docker images and push to a dev ECS cluster.
* Creates a deployment script to build, zip, and deploy a set of dev Lambda functions.
* Creates a deployment script to create/update an API Gateway REST API.
* Creates a deployment script to do "last 10" rolling deploys of API Gateway stages.

##### Phoenix Database (template-database.json)
For each environment (dev, testing, prod), and additional developer environments:
* Creates an RDS Aurora cluster
* Creates an RDS Aurora instance
* Creates a DB Security Group
* Creates an RDS Subnet Group
* Creates an RDS Parameter Group
* Creates an RDS cluster Parameter Group
* Creates a Lambda custom resource to generate, encrypt, and store database password in Parameter Store
* Creates a Lambda password generator function.
* Creates a Lambda custom resource to retrieve and decrypt database password from Parameter Store before injecting password into 'MasterPassword' field.
* Creates a Lambda Role and Lambda Role Policy for the password generator lambda function
* Creates a DNS record set to map DB address to a user friendly URL.
* Creates ingress rules to allow Database Migration Service to access from specific CIDR blocks.

##### Phoenix EC2 (template-ec2.json)
For each environment (dev, testing, prod), and additional developer environments:
* Creates an ECS Cluster.
* Creates an ECS Task Definition.
* Creates an ECS Service.
* Creates one or more EC2 instances or a Fargate service (you can choose which one)
* Creates an EC2 Auto Scalaing Group
* Creates an EC2 Instance Profile
* Creates an EC2 Role
* Creates an Application Load Balancer
* Creates an Auto Scaling Role
* Creates a CloudWatch alarm to scale up ECS service counts when receiving HTTP 500 errors.
* Creates an ApplicationAutoScaling::ScalingPolicy to scale up ECS service tasks when receiving HTTP 500 errors.
* Creates an ApplicationAutoScaling::ScalableTarget to scale up ECS service tasks.
* Creates a CloudWatch Logs Group to log ECS container logs.
* Creates an Elastic Load Balancer S3 logs bucket policy.
* Creates a V2 Elastic Load Balancer target group.
* Creates a V2 Elastic Load Balancer listener on port 443.
* Creates a V2 Elastic Load Balancer listener on port 80.
* Creates an ECS Task Execution Role.
* Creates a Web Security Group for the EC2 instances, containers, and fargate services.
* Creates Application Load Balancer security group.
* Creates an DNS record set to map an environment specific URL to the Application Load Balancer.
* Creates a security group ingress rule to allow Web security group to access RDS cluster.
* Creates a security group ingress rule to allow Web security group to access itself.
* Creates a security group ingress rule to allow ELB to access web security group.
* Creates a security group ingress rule to allow traffic to ELB.
* Creates a security group ingress rule to allow internal network CIDR blocks to access Web security group.
* Creates a security group ingress rule to allow internal network CIDR blocks to access ELB security group.

##### Phoenix Lambda (template-lambda.json)
* Jason to fill out

##### Phoenix API Gateway (template-api.json)
* Jason to fill out

##### Phoenix Jenkins (template-jenkins.json)
* Jason to fill out


### Getting started
* Update all of the params....json files with your project info
* The ProjectName should match the name of this Git repo. Use all lower case, optionally with dashes, keep it short.
```

Make sure there are no dashes in the DatabaseNamePrefix or MasterUsername parameters in the
template-database-params JSON files.
```
* Execute the following commands in order, waiting for each to complete before running the next.
```
cd Phoenix
./deploy-vpc.sh create
./deploy-pipeline.sh create
./deploy-dev-database.sh create
./deploy-dev-ec2.sh create ecs
./deploy-dev-lambda.sh create
./deploy-dev-api.sh create
./deploy-dev-api-deployment.sh create
```
* If all of the above stacks complete, push to the master branch of the CodeCommit repo that was created.
```
git commit
git remote -v
git remote add origin	https://git-codecommit.us-east-1.amazonaws.com/v1/repos/{name of your repo}
git push origin master
```
* After you've pushed your changes, open the CodePipeline and watch it go.

### Creating and updating a microservice project
* Update the template-pipeline file with your project details.
```
cd Phoenix
./deploy-pipeline.sh create
./deploy-pipeline.sh update
```

### Deploying a local Docker container to the Dev ECS cluster (skips the pipeline)
* Update all of the template-ecs-{environment} param files with your information.
* Don't forget to specify which port you want to open on the container in the ecs param files.
```
./deploy-dev-ec2.sh [create | update] [path location of folder containing dockerfile]
```

### Deploying the entire microservice to production.
Just merge to the master branch and watch the pipeline go.

### Best Practices
#### Consistency
* Please be consistent with naming conventions. Seriously. If you are unsure
how to name something like a CloudFormation Resource, Output Export Name, a
Parameter, or anything else, then please refer to existing code or ask someone
who knows. Consistency in naming conventions helps significantly with refactoring,
renaming, readability, seeing patterns arise, building abstractions, and detecting bugs.
Even if we do it differently than everyone else, consistency within the codebase
trumps all external conventions or style guides.

#### Stack Exports
* Use the pattern of {ProjectName}-{AWS service or function}-{Environment}-{Resource}. Here's an example:
```
"Outputs": {
    "EndpointAddress": {
      "Export": {
        "Name": {
          "Fn::Join": ["-", [
            {"PhoenixSSM": "/microservice/{ProjectName}/global/project-name"},
            "database",
            {"Ref": "Environment"},
            "EndpointAddress"
          ]]
        }
      },
      "Value": {
        "Fn::GetAtt": ["RDSCluster", "Endpoint.Address"]
      }
    }
  }
```
