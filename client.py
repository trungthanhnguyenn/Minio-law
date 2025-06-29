import os
from minio import Minio
from dotenv import load_dotenv

# Load environment variables from .env file at project root
load_dotenv(dotenv_path=".env")

class MinioClient:
    """
    A wrapper around the MinIO Python SDK that loads credentials from a .env file
    and provides an initialized `Minio` client for file operations.

    Attributes:
        endpoint (str): The MinIO server endpoint (e.g. "localhost:9000").
        access_key (str): The access key used to authenticate with MinIO.
        secret_key (str): The secret key used to authenticate with MinIO.
        secure (bool): Whether to use HTTPS (True) or HTTP (False) when connecting.
        client (Minio): The actual MinIO client instance from the SDK.
    """

    def __init__(self):
        """
        Initializes the MinioClient by loading environment variables and
        creating a MinIO client instance.
        """
        self.endpoint = os.getenv("MINIO_ENDPOINT")
        self.access_key = os.getenv("MINIO_ACCESS_KEY")
        self.secret_key = os.getenv("MINIO_SECRET_KEY")
        self.secure = os.getenv("MINIO_SECURE", "true").lower() == "true"

        self._debug_env()
        self._validate_env()

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

    def _debug_env(self):
        """
        Debugging utility to print environment variable values (safely masks secret key).
        """
        print(f"📌 MINIO_ENDPOINT: {self.endpoint}")
        print(f"📌 MINIO_ACCESS_KEY: {self.access_key}")
        print(f"📌 MINIO_SECRET_KEY: {'****' if self.secret_key else None}")
        print(f"📌 MINIO_SECURE: {self.secure}")

    def _validate_env(self):
        """
        Validates that all required environment variables are present.
        Raises:
            ValueError: If any required environment variable is missing.
        """
        if not all([self.endpoint, self.access_key, self.secret_key]):
            raise ValueError("❌ Missing environment variables. Please check your .env file.")

    def list_buckets(self):
        """
        Lists all buckets on the MinIO server.

        Returns:
            List[Bucket]: A list of bucket metadata objects.
        """
        return self.client.list_buckets()
