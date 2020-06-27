# ChaosEngineering

For running the tools with your AWS application, please follow the steps below:-

Create an S3 bucket for storing the config files

a)Chaos Monkey:-

Create a new AWS lambda function, remove any default existing files and upload the code file for this tool

Attach the following policies to its IAM role:-

1) AWSLambdaBasicExecutionRole

2) S3 access

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::config--bucket"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::config--bucket/*"
            ]
        }
    ]
}

3) ECS-control

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:*",
                "ecs:UpdateContainerInstancesState"
            ],
            "Resource": [
                "arn:aws:ecs:ap-south-1:773591337265:cluster/ChaosTest"
            ]
        }
    ]
}

Finally create a cron job which triggers this every 1 min

b)Security Monkey:-

Create a new AWS lambda function, remove any default existing files and upload the code file for this tool

Attach the following policies to its IAM role:-

1) AWSLambdaBasicExecutionRole

2) S3 access (same as defined above)

3) sg-policy

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:DeleteSecurityGroup",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": "arn:aws:ec2:*:*:security-group/*"
        },
        {
            "Action": [
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSecurityGroupReferences",
                "ec2:DescribeStaleSecurityGroups",
                "ec2:DescribeVpcs"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
