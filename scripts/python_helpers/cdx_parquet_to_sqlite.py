from govscape.indexing import SQLiteMetadataIndex

import argparse
import pandas as pd
from urllib.parse import urlparse
import boto3
import os

def extract_subdomain(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    if hostname is None:
        return None
    parts = hostname.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return hostname

def main():    
    parser = argparse.ArgumentParser(description='Process CDX files from S3.')
    parser.add_argument('--bucket_name', required=True, help='S3 bucket name')
    parser.add_argument('--cdx_parquet_key', required=True, help='S3 Key for CDX parquet file')
    parser.add_argument('--output_prefix', required=True, help='S3 Prefix for output')
    parser.add_argument('--output_dir', required=True, help='Local directory to save output files')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Download the CDX parquet file from S3
    print("Reading CDX data")
    s3 = boto3.client('s3')
    local_parquet_path = args.output_dir + "/cdx_metadata.parquet"
    os.makedirs(os.path.dirname(local_parquet_path), exist_ok=True)
    s3.download_file(args.bucket_name, args.cdx_parquet_key, local_parquet_path)
    df = pd.read_parquet(local_parquet_path)

    # Initialize the SQLite metadata index
    db_path = args.output_dir + "/metadata.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    index = SQLiteMetadataIndex(args.output_dir+"/metadata.db")

    # Create the metadata table
    index.build_index()

    print("Building Index")
    assert args.output_prefix[-1] != '/'
    index.build_index()
    cur_batch = []
    rows_added = 0
    for _, row in df.iterrows():
        cur_batch.append({
            'crawl_url': row['url'],
            'crawl_date': row['crawl_date'],
            'pdf_name': row['digest'],
            'sub_domain': extract_subdomain(row['url']),
            's3_url': f"https://{args.bucket_name}.s3.amazonaws.com/{args.output_prefix}/PDFs/{row['digest']}.pdf"
        })
        if len(cur_batch) >= 1000:
            index.add_batch(cur_batch)
            rows_added += len(cur_batch)
            print(f"Added {rows_added} rows to index")
            cur_batch = []
    
    print("Saving Index")
    index.save_index()

    print("Uploading Index")
    s3 = boto3.client('s3')
    s3.upload_file('data/index_metadata/metadata.db', 'bcgl-public-bucket', 'archive/2020/cdx_metadata/metadata.db')
main()
