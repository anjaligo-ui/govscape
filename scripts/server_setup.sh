#!/usr/bin/env bash
set -e

# Server setup
s5cmd sync 's3://bcgl-public-bucket/prod-serving/*' data/prod
poetry run python scripts/start_api_server.py --pdf-directory ./data/PDFs --data-directory ./data/prod --text_model SentenceTransformer --visual_model CLIP 

