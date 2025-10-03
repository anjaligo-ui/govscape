#!/usr/bin/env bash
set -e

# Clear the data directory
rm -rf data/prod

s3_prefix="s3://bcgl-public-bucket"
data_dir="dev-serving"

# Download the indices
s5cmd sync $s3_prefix/$data_dir/index_keyword/* data/$data_dir/index_keyword

# Run the embeddings pipeline
poetry run python scripts/python_helpers/cdx_parquet_to_sqlite.py --bucket_name 'bcgl-public-bucket' --cdx_parquet_key 'archive/metadata/pdf_metadata.parquet' --output_prefix 'dev-serving/index_metadata' --output_dir 'data/index_metadata'

