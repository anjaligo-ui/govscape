import os
import argparse
import boto3
import warcio
import json
import re
import gzip
import pandas as pd
from multiprocessing import Pool, Manager, cpu_count


def main():
    entries = []
    cdx_f = gzip.open('/home/ubuntu/govscape/data/cdx_dir/EOT2020_Test.cdx.gz')
    for cdx_line in cdx_f:
        try:
            cdx_line_string = cdx_line.decode().partition(' ')[2].partition(' ')[2]
            data = json.loads(cdx_line_string)
        except Exception:
            continue  # Skip lines that are not valid JSON
        if ((data.get('mime') == 'application/pdf') or (".pdf" in data.get('url'))) and data.get('status') == '200':
            pdf_entry = {
                'url': data.get('url'),
                'filename': data.get('filename'),
                'digest': data.get('digest'),
                'offset': data.get('offset'),
                'length': data.get('length'),
            }
            entries.append(pdf_entry)
    entries = pd.DataFrame(entries)
    entries.to_parquet('/home/ubuntu/govscape/data/cdx_dir/pdf_metadata.parquet', index=False)
    cdx_f.close()

main()