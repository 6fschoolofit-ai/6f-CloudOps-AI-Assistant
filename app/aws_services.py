
import boto3

AWS_REGION = "ap-south-2"
S3_BUCKET = "cloudops-ai-data-6f"


def get_ec2_instances():
    ec2 = boto3.client(
        "ec2",
        region_name=AWS_REGION
    )

    paginator = ec2.get_paginator("describe_instances")
    instances = []

    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "State": instance["State"]["Name"],
                    "InstanceType": instance["InstanceType"],
                    "PrivateIp": instance.get("PrivateIpAddress", "N/A")
                })

    return instances


def get_s3_buckets():
    s3 = boto3.client(
        "s3",
        region_name=AWS_REGION
    )

    response = s3.list_buckets()
    buckets = []

    for bucket in response.get("Buckets", []):
        bucket_name = bucket["Name"]

        location = s3.get_bucket_location(
            Bucket=bucket_name
        )

        bucket_region = location.get("LocationConstraint") or "us-east-1"

        buckets.append({
            "BucketName": bucket_name,
            "Region": bucket_region,
            "CreationDate": bucket["CreationDate"].isoformat()
        })

    return buckets

