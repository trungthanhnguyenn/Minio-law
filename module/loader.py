import os
from datetime import timezone, timedelta
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource
from client import MinioClient

def format_bytes(size):
    """
    Convert a size in bytes to a human-readable string (e.g., KB, MB).

    Args:
        size (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

class MinioLoader:
    """
    A utility class that wraps common operations on MinIO, including:
    - Bucket creation and deletion
    - File/folder upload & download
    - Object listing, deletion, and metadata
    - Copying, moving objects
    - Generating presigned URLs for secure access

    Attributes:
        client (MinioClient): An initialized MinIO client wrapper.
    """

    def __init__(self, minio_client=None):
        """
        Initialize the loader with an optional custom MinIO client.

        Args:
            minio_client (MinioClient, optional): A preconfigured MinIO client.
        """
        self.client = minio_client or MinioClient()

    # ---------- Bucket Management ----------

    def ensure_bucket(self, bucket_name):
        """
        Ensure that a bucket exists. Create it if it doesn't.

        Args:
            bucket_name (str): The name of the bucket to ensure.
        """
        if not self.client.client.bucket_exists(bucket_name):
            self.client.client.make_bucket(bucket_name)
            print(f"Created bucket {bucket_name}")
        else:
            print(f"Bucket {bucket_name} already exists")

    def delete_bucket(self, bucket_name):
        """
        Delete all objects inside a bucket and then delete the bucket itself.

        Args:
            bucket_name (str): The name of the bucket to delete.
        """
        try:
            if not self.client.client.bucket_exists(bucket_name):
                print(f"⚠️ Bucket '{bucket_name}' does not exist.")
                return
            print(f"🧹 Deleting all objects in bucket '{bucket_name}'...")
            for obj in self.client.client.list_objects(bucket_name, recursive=True):
                self.client.client.remove_object(bucket_name, obj.object_name)
                print(f"   - Deleted: {obj.object_name}")
            self.client.client.remove_bucket(bucket_name)
            print(f"✅ Bucket '{bucket_name}' deleted.")
        except S3Error as e:
            print(f"❌ Error deleting bucket '{bucket_name}': {e}")

    def get_bucket_policy(self, bucket_name):
        """
        Retrieve the bucket's access policy.

        Args:
            bucket_name (str): The name of the bucket.

        Returns:
            str or None: The bucket policy if available.
        """
        try:
            policy = self.client.client.get_bucket_policy(bucket_name)
            print("📜 Bucket Policy:")
            print(policy)
            return policy
        except S3Error as e:
            print(f"❌ Error retrieving policy for bucket '{bucket_name}': {e}")
            return None

    # ---------- Upload ----------

    def upload_file(self, source_file, bucket_name, destination_file):
        """
        Upload a single file to MinIO.

        Args:
            source_file (str): Path to local file.
            bucket_name (str): Bucket name in MinIO.
            destination_file (str): Object name in MinIO.
        """
        self.ensure_bucket(bucket_name)
        self.client.client.fput_object(bucket_name, destination_file, source_file)
        print(f"{source_file} uploaded as {destination_file} to bucket {bucket_name}")

    def upload_folder(self, source_folder, bucket_name, destination_folder=""):
        """
        Recursively upload all files in a folder to MinIO.

        Args:
            source_folder (str): Local folder path.
            bucket_name (str): Bucket name.
            destination_folder (str): Prefix/folder path in bucket.
        """
        self.ensure_bucket(bucket_name)
        for root, _, files in os.walk(source_folder):
            for file in files:
                local_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_path, source_folder)
                dest_path = os.path.join(destination_folder, rel_path).replace("\\", "/")
                self.client.client.fput_object(bucket_name, dest_path, local_path)
                print(f"{local_path} uploaded as {dest_path} to bucket {bucket_name}")

    # ---------- Download ----------

    def download_file(self, bucket_name, object_name, destination_path):
        """
        Download an object from MinIO.

        Args:
            bucket_name (str): Bucket name.
            object_name (str): Object name in MinIO.
            destination_path (str): Local file path or folder.
        """
        try:
            if os.path.isdir(destination_path):
                destination_path = os.path.join(destination_path, os.path.basename(object_name))
            self.client.client.fget_object(bucket_name, object_name, destination_path)
            print(f"✅ Downloaded '{object_name}' to '{destination_path}'")
        except S3Error as e:
            print(f"❌ Error downloading file: {e}")

    # ---------- Delete ----------

    def delete_file(self, bucket_name, object_name):
        """
        Delete a single object from a bucket.

        Args:
            bucket_name (str): Bucket name.
            object_name (str): Object name to delete.
        """
        try:
            self.client.client.remove_object(bucket_name, object_name)
            print(f"Deleted {object_name} from bucket {bucket_name}")
        except S3Error as e:
            print(f"Error deleting file: {e}")

    def delete_folder(self, bucket_name, folder_name):
        """
        Delete all objects within a given folder prefix.

        Args:
            bucket_name (str): Bucket name.
            folder_name (str): Folder prefix to delete.
        """
        try:
            for obj in self.client.client.list_objects(bucket_name, prefix=folder_name, recursive=True):
                self.client.client.remove_object(bucket_name, obj.object_name)
                print(f"Deleted: {obj.object_name}")
            print(f"Folder '{folder_name}' deleted from bucket '{bucket_name}'")
        except S3Error as e:
            print(f"Error deleting folder: {e}")

    # ---------- List ----------

    def list_files(self, bucket_name, prefix=""):
        """
        List all objects under a prefix (optional).

        Args:
            bucket_name (str): Bucket name.
            prefix (str, optional): Prefix or folder in bucket.

        Returns:
            List[str]: List of object names.
        """
        try:
            print(f"\n🔍 Objects in '{bucket_name}' (prefix: '{prefix}'):")
            object_names = []
            for obj in self.client.client.list_objects(bucket_name, prefix=prefix, recursive=True):
                print(f" - {obj.object_name}")
                object_names.append(obj.object_name)
            if not object_names:
                print("⚠️ No objects found.")
            return object_names
        except S3Error as e:
            print(f"Error listing files: {e}")
            return []

    # ---------- Metadata ----------

    def get_file_info(self, bucket_name, object_name):
        """
        Get metadata (size, type, last modified) of an object.

        Args:
            bucket_name (str): Bucket name.
            object_name (str): Object to inspect.

        Returns:
            dict or None: Metadata dictionary.
        """
        try:
            stat = self.client.client.stat_object(bucket_name, object_name)
            last_modified = stat.last_modified.astimezone(timezone(timedelta(hours=7)))
            info = {
                "📄 Object Name": stat.object_name,
                "📦 Size": format_bytes(stat.size),
                "📁 Content Type": stat.content_type,
                "🕒 Last Modified (VN)": last_modified.strftime("%Y-%m-%d %H:%M:%S"),
            }
            print("\n📌 File Metadata:")
            max_len = max(len(k) for k in info)
            for key, value in info.items():
                print(f" {key:<{max_len}} : {value}")
            return info
        except S3Error as e:
            print(f"Error retrieving metadata: {e}")
            return None

    # ---------- Copy & Move ----------

    def copy_file(self, src_bucket, src_object, dest_bucket, dest_object):
        """
        Copy an object from one location to another.

        Args:
            src_bucket (str): Source bucket name.
            src_object (str): Source object name.
            dest_bucket (str): Destination bucket name.
            dest_object (str): Destination object name.
        """
        try:
            source = CopySource(src_bucket, src_object)
            self.ensure_bucket(dest_bucket)
            self.client.client.copy_object(dest_bucket, dest_object, source)
            print(f"Copied '{src_object}' → '{dest_object}'")
        except S3Error as e:
            print(f"Error copying object: {e}")

    def move_file(self, bucket_name, source_object, dest_object):
        """
        Move a file within the same bucket.

        Args:
            bucket_name (str): Bucket name.
            source_object (str): Original object name.
            dest_object (str): New object name.
        """
        try:
            self.copy_file(bucket_name, source_object, bucket_name, dest_object)
            self.delete_file(bucket_name, source_object)
            print(f"✅ Moved '{source_object}' to '{dest_object}'")
        except S3Error as e:
            print(f"Error moving object: {e}")

    # ---------- URL ----------

    def generate_presigned_url(self, bucket_name, object_name, expiry=3600, method="GET"):
        """
        Generate a presigned URL for temporary access to a file.

        Args:
            bucket_name (str): Bucket name.
            object_name (str): Object name.
            expiry (int): Expiry time in seconds.
            method (str): 'GET' for download or 'PUT' for upload.

        Returns:
            str or None: Presigned URL.
        """
        try:
            expires = timedelta(seconds=expiry)
            if method.upper() == "GET":
                url = self.client.client.presigned_get_object(bucket_name, object_name, expires=expires)
            elif method.upper() == "PUT":
                url = self.client.client.presigned_put_object(bucket_name, object_name, expires=expires)
            else:
                raise ValueError("Method must be either 'GET' or 'PUT'")
            print(f"🔗 Presigned {method.upper()} URL: {url}")
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            return None
