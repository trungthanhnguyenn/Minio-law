from client import MinioClient
from module.loader import MinioLoader
from minio.error import S3Error

# Initialize paths and settings
source_file = "path/to/your/single/file/to/upload"
source_folder = "path/to/your/folder/to/upload"
bucket_name = "your bucket name in minio" # Example: law-database
prefix = "your folder name to store data on minio" # Example: raw-json
destination_file = "path/to/your/single/file/on/minio"
new_object_dir = "path/on/minio/to/move/file"
folder_to_delete = "name of folder you want to delete on minio" # Example: raw-json
save_dir = "path/to/load/folder/to/save/file/downloaded"
dest_folder = "your new folder on minio" # Example # raw-article-json

# Initialize MinIO loader
uploader = MinioLoader(MinioClient())

try:
    # ============================
    # 📤 Upload a single file
    # ============================
    uploader.upload_file(source_file, bucket_name, destination_file)

    # ============================
    # 📁 Upload a folder recursively
    # ============================
    uploader.upload_folder(source_folder, bucket_name, dest_folder)

    # ============================
    # 📃 List files in a folder
    # ============================
    uploader.list_files(bucket_name, prefix)

    # ============================
    # 🧾 Get metadata for a file
    # ============================
    uploader.get_file_info(bucket_name, destination_file)

    # ============================
    # 📥 Download file to local directory
    # ============================
    uploader.download_file(bucket_name, destination_file, save_dir)

    # ============================
    # 🔄 Move file to new location within same bucket
    # ============================
    uploader.move_file(bucket_name, destination_file, new_object_dir)

    # ============================
    # 📋 Copy file to another bucket/folder
    # ============================
    uploader.copy_file(bucket_name, destination_file, dest_folder, new_object_dir)

    # ============================
    # ❌ Delete a single file
    # ============================
    uploader.delete_file(bucket_name, destination_file)

    # ============================
    # 🧹 Delete a folder and its contents
    # ============================
    uploader.delete_folder(bucket_name, dest_folder)

    # ============================
    # 🗑️ Delete a bucket entirely
    # ============================
    uploader.delete_bucket(bucket_name)

except S3Error as exc:
    print("❌ An error occurred while interacting with MinIO:", exc)
