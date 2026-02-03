import subprocess
from govscape.indexing import SQLiteMetadataIndex
import json
import argparse
import pandas as pd
from urllib.parse import urlparse
import time
import os
import multiprocessing
import shutil
from govscape.data_loader import build_data_loader

def extract_subdomain(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    if hostname is None:
        return None
    parts = hostname.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return hostname

PROGRESS_PATH = "index_metadata_progress.json"
BATCH_SIZE = 100000
# gets metadata files from s3
def list_metadata_files(data_loader, s3_metadata_prefix, num_pages=1):
    metadata_files = []
    pages_retrieved = 0
    while True:
        result = data_loader.list_objects(s3_metadata_prefix)
        metadata_keys = [key for key in result.keys if key.endswith('.json')]
        metadata_files.extend(metadata_keys)
        pages_retrieved += 1
        if result.is_truncated:
            finished = False

        if pages_retrieved >= num_pages:
            finished = False
            break

        if not result.is_truncated:
            finished = True
            break
    return finished, metadata_files

def download_files_from_backend(backend, bucket_name, local_base_dir, s3_keys, local_path):
    data_loader = build_data_loader(backend, bucket_name, local_base_dir)
    for s3_key in s3_keys:
        digest = os.path.dirname(s3_key).split('/')[-1]
        local_file_path = os.path.join(local_path, digest, "metadata.json")
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        data_loader.download_file(s3_key, local_file_path)

def main():    
    parser = argparse.ArgumentParser(description='Process CDX files from S3.')
    parser.add_argument('--bucket_name', required=True, help='S3 bucket name')
    parser.add_argument('--cdx_parquet_key', required=True, help='S3 Key for CDX parquet file')
    parser.add_argument('--metadata_prefix', required=True, help='S3 Prefix for metadata')
    parser.add_argument('--output_prefix', required=True, help='S3 Prefix for output')
    parser.add_argument('--output_dir', required=True, help='Local directory to save output files')
    parser.add_argument('--num_pages_to_process', type=int, default=100, help='Number of metadata files to process from S3')
    parser.add_argument('--backend', choices=['s3', 'local'], default='s3', help='Data backend to use')
    parser.add_argument('--local_base_dir', type=str, default='data', help='Base directory for local backend')
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    bucket_name = args.bucket_name
    s3_metadata_prefix = args.metadata_prefix
    data_loader = build_data_loader(
        args.backend,
        bucket_name,
        args.local_base_dir,
        checkpoint_path=PROGRESS_PATH,
    )
    try:
        data_loader.download_file(f'{args.output_prefix}/{PROGRESS_PATH}.json', PROGRESS_PATH)
    except Exception as e:
        print(e)

    # Download the CDX parquet file from S3
    print("Reading CDX data")
    local_parquet_path = args.output_dir + "/cdx_metadata.parquet"
    os.makedirs(os.path.dirname(local_parquet_path), exist_ok=True)
    if not os.path.exists(local_parquet_path):
        data_loader.download_file(args.cdx_parquet_key, local_parquet_path)
    cdx_df = pd.read_parquet(local_parquet_path)
    cdx_df['digest'] = cdx_df['digest'].astype(str).str.replace("sha1:", "")

    print("Initializing Index")
    # Initialize the SQLite metadata index
    db_path = f'{args.output_dir}/metadata.db'
    data_loader.download_file(f'{args.output_prefix}/metadata.db', db_path)
    index = SQLiteMetadataIndex(args.output_dir)

    # Create the metadata table
    index.build_index()
    is_finished, metadata_files = False, []
    files_processed = 0
    # get the pdf files from s3
    while not is_finished and files_processed < args.num_pages_to_process*1000:
        is_finished, metadata_files = list_metadata_files(data_loader, s3_metadata_prefix, int(BATCH_SIZE/1000))
        local_metadata_path = os.path.join(args.output_dir, 'metadata_files')
        os.makedirs(local_metadata_path, exist_ok=True)
        start_time = time.time()
        print("Downloading Metadata Files from S3")
        download_batches = [metadata_files[i:i + 250] for i in range(0, len(metadata_files), 250)]
        with multiprocessing.Pool(processes=64) as pool:
            pool.starmap(download_files_from_backend, [(args.backend, bucket_name, args.local_base_dir, download_batch, local_metadata_path) for download_batch in download_batches])

        print("Adding Metadata to Index")
        rows = []
        for metadata_file in metadata_files:
            digest = os.path.dirname(metadata_file).split('/')[-1]
            filepath = os.path.join(local_metadata_path, digest, "metadata.json")
            try:
                with open(filepath, 'r') as f:
                    metadata_json = json.load(f)
                digest_val = os.path.dirname(filepath).split('/')[-1]
                rows.append({
                    'digest': digest_val,
                    'num_pages': metadata_json.get('num_pages', None)
                })
                os.remove(filepath)  # Clean up the file after reading
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

        digest_to_pagecount = pd.DataFrame(rows, columns=['digest', 'num_pages'])
        metadata_df = digest_to_pagecount.merge(cdx_df, on='digest')

        print("Building Index")
        assert args.output_prefix[-1] != '/'
        index.build_index()
        cur_batch = []
        rows_added = 0
        for _, row in metadata_df.iterrows():
            cur_batch.append({
                'crawl_url': row['url'],
                'crawl_date': row['crawl_date'],
                'pdf_name': row['digest'],
                'sub_domain': extract_subdomain(row['url']),
                'page_count': row['num_pages'],
                    's3_url': data_loader.to_uri(os.path.join('archive/2020/PDFs', f"{row['digest']}.pdf"))
            })
            if len(cur_batch) >= 1000:
                index.add_batch(cur_batch)
                rows_added += len(cur_batch)
                print(f"Added {rows_added} rows to index")
                cur_batch = []
        if len(cur_batch) > 0:
            index.add_batch(cur_batch)
            rows_added += len(cur_batch)
            print(f"Added {rows_added} rows to index")
        
        print("Uploading Index")
        data_loader.upload_file(db_path, f'{args.output_prefix}/metadata.db')

        data_loader.save_checkpoint()
        data_loader.upload_file(PROGRESS_PATH, f'{args.output_prefix}/{PROGRESS_PATH}.json')
        files_processed += len(metadata_files)
        print("Is Finished:", is_finished, "Files Processed", files_processed, "Total Time:", time.time() - start_time)
        try:
            if os.path.exists(local_metadata_path):
                shutil.rmtree(local_metadata_path)
        except Exception as e:
            print(f"Failed to remove {local_metadata_path}: {e}")
    print("Saving Index")
    index.save_index()
    
    print("Uploading Index")
    data_loader.upload_file(db_path, f'{args.output_prefix}/metadata.db')

main()
