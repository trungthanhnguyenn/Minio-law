# MinIO DB Utility

This repository provides a set of Python utilities for interacting with a [MinIO](https://min.io/) object storage server. It includes tools for uploading, downloading, listing, and managing files and buckets, all configurable via a `.env` file.

---

## Features

- **Easy MinIO client initialization** using environment variables
- **Upload/download files and folders**
- **List, copy, move, and delete objects**
- **Bucket management** (create, delete, check policy)
- **Presigned URL generation** for secure temporary access

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd minio-db
```

### 2. Configure Environment Variables

Edit the `.env` file to match your MinIO server configuration:

```properties
MINIO_ENDPOINT=localhost:1000
MINIO_ACCESS_KEY=USERNAME
MINIO_SECRET_KEY=P@SSWORD
MINIO_SECURE=false
```

### 3. (Optional) Start MinIO with Docker

A `docker-compose.yml` is provided for quick local setup:

```bash
docker-compose up -d
```

This will start MinIO on `localhost:1000` (API) and `localhost:1001` (console).

---

## Usage

### 1. MinIO Client

Initialize a MinIO client in your Python code:

```python
from client import MinioClient

minio_client = MinioClient()
buckets = minio_client.list_buckets()
for bucket in buckets:
    print(bucket.name)
```

### 2. File Operations with MinioLoader

Use the `MinioLoader` class for advanced operations:

```python
from client import MinioClient
from module.loader import MinioLoader

minio_client = MinioClient()
loader = MinioLoader(minio_client)

# Upload a file
loader.upload_file("/path/to/local/file.txt", "my-bucket", "folder/file.txt")

# List files in a bucket/folder
loader.list_files("my-bucket", "folder/")

# Download a file
loader.download_file("my-bucket", "folder/file.txt", "/local/save/dir")

# Delete a file
loader.delete_file("my-bucket", "folder/file.txt")
```

See `test.py` for more usage examples.

---

## Folder Structure

```
minio-db/
│
├── client.py           # MinIO client wrapper
├── module/
│   └── loader.py       # High-level MinIO operations
├── uploader/
│   └── upload.py       # (Optional) Upload helper
├── .env                # MinIO credentials/config
├── docker-compose.yml  # For local MinIO server
└── test.py             # Example usage
```

---

## Requirements

- Python 3.7+
- [minio](https://pypi.org/project/minio/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:

```bash
pip install minio python-dotenv
```

---

## Notes

- Make sure your `.env` file is correctly configured before running any scripts.
- The MinIO server must be running and accessible at the endpoint specified in `.env`.
- For production, set `MINIO_SECURE=true` and use HTTPS.

---

## Tips

| Feature       | How to Use                                                |
| ------------- | --------------------------------------------------------- |
| Upload file   | `upload_file(local_path, bucket, object_path)`            |
| Upload folder | `upload_folder(local_dir, bucket, prefix)`                |
| List files    | `list_files(bucket, prefix)`                              |
| Get file info | `get_file_info(bucket, object_path)`                      |
| Download file | `download_file(bucket, object_path, local_path_or_dir)`   |
| Move file     | `move_file(bucket, src_path, dest_path)`                  |
| Copy file     | `copy_file(src_bucket, src_path, dest_bucket, dest_path)` |
| Delete file   | `delete_file(bucket, object_path)`                        |
| Delete folder | `delete_folder(bucket, prefix)`                           |
| Delete bucket | `delete_bucket(bucket)`                                   |

---

## License

MIT License

---

## Author

- [trungthanhnguyenn]