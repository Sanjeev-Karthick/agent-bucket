import os
from pathlib import Path

import boto3


def main() -> None:
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("AB_TEST_S3_ENDPOINT", "http://127.0.0.1:9000"),
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        region_name="us-east-1",
    )
    bucket = "agent-bucket-demo"
    if bucket not in [item["Name"] for item in client.list_buckets()["Buckets"]]:
        client.create_bucket(Bucket=bucket)
    for path in (Path(__file__).resolve().parents[1] / "examples/demo-data").iterdir():
        if path.is_file():
            client.upload_file(str(path), bucket, path.name)
    print(f"Seeded synthetic demo documents into s3://{bucket}")


if __name__ == "__main__":
    main()
