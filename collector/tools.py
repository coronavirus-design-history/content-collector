import hashlib


def content_updated(file, content):
    with open(file, "r") as f:
        existing_content = "".join(f.readlines())
    existing = hashlib.md5(existing_content.encode("utf-8")).hexdigest()
    new = hashlib.md5(content.encode("utf-8")).hexdigest()
    return existing != new
