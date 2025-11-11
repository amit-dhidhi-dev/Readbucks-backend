import requests
import tempfile
import os
from botocore.client import Config
from boto3 import client


def download_pdf_from_r2(url: str) -> str:
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        for chunk in response.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp_path = tmp.name
    return tmp_path

# def cleanup_file(path: str):
#     if os.path.exists(path):
#         os.remove(path)

s3 = client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            config=Config(signature_version="s3v4"))


# get presigned url 
def generate_get_url(key: str):
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": os.getenv("R2_BUCKET"),
            "Key": key
        },
        ExpiresIn=3600  # 1 hour validity
    )
    return url

# put presigned url
def generate_put_url(key: str, content_type: str):
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": os.environ["R2_BUCKET"], 
            "Key": key, 
            "ContentType": content_type
        },
        ExpiresIn=3600
    )
    
    return url



def upload_to_r2(bucket_name: str, file_path: str, key: str) -> str:
    """Upload a file to Cloudflare R2 and return its public URL."""
    s3.upload_file(file_path, bucket_name, key)
    return f"{os.getenv('R2_PUBLIC_URL')}/{key}"

def download_from_r2(bucket_name: str, key: str, local_path: str):
    """Download file from R2 to local temp folder."""
    # s3.download_file(bucket_name, key, local_path)
    try:
        s3.head_object(Bucket=bucket_name, Key=key)
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f"❌ File not found in R2: {key}")
            return
        raise
    s3.download_file(bucket_name, key, local_path)
    print("✅ File downloaded successfully.")




