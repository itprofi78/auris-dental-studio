# -*- coding: utf-8 -*-
"""Заливає медіа auris-dental-studio на Cloudinary (папка 3d-saity/auris).
Ключі з ai-prodavec/.env (той самий акаунт що forma-3d)."""
import hashlib
import json
import mimetypes
import os
import time
import urllib.request
import uuid

ENV_PATH = r"C:\AI-projects\my-business-ai\ai-prodavec\.env"
FOLDER = "3d-saity/auris"
BASE = r"C:\AI-projects\my-business-ai\auris-dental-studio\media"

FILES = [
    ("hero.mp4", "video"),
    ("hero_poster.webp", "image"),
    ("case1_before.webp", "image"),
    ("case1_after.webp", "image"),
    ("case2_before.webp", "image"),
    ("case2_after.webp", "image"),
    ("case3_before.webp", "image"),
    ("case3_after.webp", "image"),
    ("case4_before.webp", "image"),
    ("case4_after.webp", "image"),
]


def env(path, key):
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError(f"{key} не знайдено в {path}")


def sign(params, api_secret):
    to_sign = "&".join(f"{k}={v}" for k, v in sorted(params.items()) if k not in ("file", "api_key"))
    return hashlib.sha1((to_sign + api_secret).encode("utf-8")).hexdigest()


def multipart_upload(url, fields, file_path, file_field="file"):
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode()
    filename = os.path.basename(file_path)
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        data = f.read()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n".encode()
    body += data
    body += f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(url, data=body, method="POST",
                                  headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    cloud_name = env(ENV_PATH, "CLOUDINARY_CLOUD_NAME")
    api_key = env(ENV_PATH, "CLOUDINARY_API_KEY")
    api_secret = env(ENV_PATH, "CLOUDINARY_API_SECRET")

    results = []
    for fname, resource_type in FILES:
        file_path = os.path.join(BASE, fname)
        # public_id без розширення, щоб URL був чистий і стабільний
        public_id = os.path.splitext(fname)[0]
        timestamp = str(int(time.time()))
        params = {"folder": FOLDER, "public_id": public_id, "overwrite": "true", "timestamp": timestamp}
        signature = sign(params, api_secret)
        fields = {**params, "api_key": api_key, "signature": signature}
        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{resource_type}/upload"
        data = multipart_upload(url, fields, file_path)
        if "secure_url" in data:
            results.append((fname, data["secure_url"]))
            print("OK", fname, "->", data["secure_url"])
        else:
            print("FAIL", fname, json.dumps(data, ensure_ascii=False)[:400])

    out_path = os.path.join(BASE, "cloudinary_urls.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for name, url in results:
            f.write(f"{name}\t{url}\n")
    print("Збережено:", out_path)


if __name__ == "__main__":
    main()
