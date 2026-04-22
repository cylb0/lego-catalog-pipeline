# LEGO Catalog Pipeline

A Python-based pipeline to synchronize LEGO catalog data from Rebrickable to AWS S3.

## Features

- **CSV Downloading**: Fetches CSV files from Rebrickable.
- **S3 Synchronization**: Uploads new or updated CSVs to an S3 bucket.
- **Change Detection**: Compares file hashes to avoid unnecessary uploads.
- **Manifest Management**: Maintains a `manifest.json` in S3 to track file versions.
- **Error Handling**: Robust error handling for network and file operations.
- **SQS Integration**: Sends messages to an SQS queue for further processing.
- **LDraw to GLTF Conversion**: Converts LDraw parts to GLTF format.

## Prerequisites

- Python 3.8+
- AWS Credentials configured (e.g., via `~/.aws/credentials` or environment variables)
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lego-catalog-pipeline
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
MANIFEST_PATH=manifest.json
TMP_DIR=tmp

AWS_DEFAULT_REGION=your-aws-default-region
S3_BUCKET_NAME=your-s3-bucket-name
SQS_QUEUE_URL=your-sqs-queue-url

REBRICKABLE_PARTS_CSV_URL=https://cdn.rebrickable.com/media/downloads/parts.csv.gz
REBRICKABLE_CATEGORIES_CSV_URL=https://cdn.rebrickable.com/media/downloads/categories.csv.gz

LDRAW_COMPLETE_LIBRARY_URL=https://library.ldraw.org/library/updates/complete.zip

LOG_FILE=the path to the log file (default: logs/catalog_pipeline.log)
FORCE_CLOUD_LOGGING=true to force cloud logging (default: false)
CW_LOG_GROUP=the cloudwatch log group (default: lego-catalog-pipeline-dev)
```

## Usage

Run the pipeline using the following command:

```bash
python main.py
```

### How it works

1. **Initialization**: Reads configuration and fetches the `manifest.json` from S3.
2. **Download**: Downloads the latest CSV files from Rebrickable to a temporary directory.
3. **Compare**: Calculates the hash of the downloaded files and compares them with the manifest.
4. **Upload**: Uploads only the changed files to S3.
5. **Update**: Updates the manifest in S3 with the new file hashes and names.
6. **Download**: Downloads the latest LDraw parts library from LDraw.org to a temporary directory.
7. **Update**: Updates the manifest in S3 with and index of available LDraw parts.
8. **SQS Integration**: Sends messages to an SQS queue to trigger the LDraw to GLTF conversion pipeline for new parts.

## Project Structure

```
lego-catalog-pipeline/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── utils/
│   │   │   ├── file_utils.py             # File utility functions
│   │   │   └── network_utils.py          # Network utility functions
│   │   ├── catalog_manifest.py           # Manifest management
│   │   ├── logger.py                     # Logger configuration
│   │   ├── config.py                     # Configuration management
│   │   └── pipeline.py                   # Pipeline logic
│   ├── conversion/
│   │   ├── main.py                       # Main entry point for the conversion pipeline
│   │   ├── worker.py                     # Worker that polls SQS and processes messages
│   │   ├── converter.py                  # Converts LDraw parts to GLTF
│   │   ├── ldraw_unpacker.py             # Extracts LDraw parts library
│   │   ├── s3_client.py                  # S3 interaction logic for conversion
│   │   └── Dockerfile                    # Dockerfile for the conversion pipeline
│   ├── ingestion/
│   │   ├── csv_downloader.py             # CSV downloading logic
│   │   └── ldraw_downloader.py           # LDraw library management
│   ├── messaging/
│   │   └── sqs_handler.py                # SQS interaction logic
│   └── storage/
│   │   └── s3_manager.py                 # S3 interaction logic
├── tests/                                # Unit testing suite
├── logs/                                 # Application logs
├── main.py                               # Pipeline entry point
├── pytest.ini                            # Pytest configuration
├── requirements.txt                      # Project dependencies
├── .env                                  # Environment variables (not version controlled)
└── README.md                             # Project documentation
```

## Testing

To run the tests, use `pytest`:

```bash
pytest
```

## License

[MIT License](LICENSE)
