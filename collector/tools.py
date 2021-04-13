import hashlib
import os


def content_updated(file, content):
    if not os.path.exists(file):
        return True
    with open(file, "r") as f:
        existing_content = "".join(f.readlines())
    existing = hashlib.md5(existing_content.encode("utf-8")).hexdigest()
    new = hashlib.md5(content.encode("utf-8")).hexdigest()
    return existing != new
