import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import boto3
from botocore.config import Config

from agent_bucket.config import Settings


@dataclass(frozen=True)
class StoredObject:
    key: str
    uri: str
    etag: str
    size: int


class StorageAdapter(Protocol):
    def inventory(self) -> list[StoredObject]: ...
    def read(self, item: StoredObject) -> bytes: ...


class DemoStorage:
    def __init__(self, root: Path, max_bytes: int, max_objects: int) -> None:
        self.root = root.resolve(strict=True)
        self.max_bytes = max_bytes
        self.max_objects = max_objects

    def inventory(self) -> list[StoredObject]:
        objects = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            path.resolve().relative_to(self.root)
            key = path.relative_to(self.root).as_posix()
            size = path.stat().st_size
            if size > self.max_bytes:
                raise ValueError("Demo object exceeds AB_MAX_OBJECT_BYTES")
            data = path.read_bytes()
            objects.append(
                StoredObject(key, f"demo://{key}", hashlib.sha256(data).hexdigest(), size)
            )
            if len(objects) > self.max_objects:
                raise ValueError("Inventory exceeds AB_MAX_OBJECTS")
        return objects

    def read(self, item: StoredObject) -> bytes:
        path = (self.root / item.key).resolve(strict=True)
        path.relative_to(self.root)
        with path.open("rb") as stream:
            data = stream.read(self.max_bytes + 1)
        if len(data) > self.max_bytes or hashlib.sha256(data).hexdigest() != item.etag:
            raise ValueError("Demo object changed during sync or exceeds size limit; retry sync")
        return data


class S3Storage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            region_name=settings.s3_region,
            config=Config(
                s3={"addressing_style": settings.s3_addressing_style},
                connect_timeout=10,
                read_timeout=60,
                retries={"max_attempts": 3},
            ),
        )

    def inventory(self) -> list[StoredObject]:
        objects = []
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=self.settings.s3_bucket, Prefix=self.settings.s3_prefix
        ):
            for item in page.get("Contents", []):
                key = item["Key"]
                if key.endswith("/"):
                    continue
                objects.append(
                    StoredObject(
                        key, f"s3://{self.settings.s3_bucket}/{key}", item["ETag"], item["Size"]
                    )
                )
                if len(objects) > self.settings.max_objects:
                    raise ValueError("Inventory exceeds AB_MAX_OBJECTS; narrow AB_S3_PREFIX")
        return objects

    def read(self, item: StoredObject) -> bytes:
        if item.size > self.settings.max_object_bytes:
            raise ValueError("Object exceeds AB_MAX_OBJECT_BYTES")
        response = self.client.get_object(
            Bucket=self.settings.s3_bucket, Key=item.key, IfMatch=item.etag
        )
        stream = response["Body"]
        try:
            data = stream.read(self.settings.max_object_bytes + 1)
        finally:
            stream.close()
        if len(data) > self.settings.max_object_bytes:
            raise ValueError("Object exceeds AB_MAX_OBJECT_BYTES")
        return data
