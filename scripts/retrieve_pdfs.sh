poetry run python3 scripts/python_helpers/process_cdxs.py --bucket 'eotarchive' --cdx_file_paths 'data/cdx_dir/cdx.paths' --output_dir 'data/cdx_dir'

poetry run python3 scripts/python_helpers/retrieve_pdfs.py --bucket_name 'bcgl-public-bucket' --s3_prefix 'dev-serving/PDFs' --local_dir './data/PDFs'

