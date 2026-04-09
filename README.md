# LEGO Catalog Pipeline

A Python-based pipeline to synchronize LEGO catalog data from Rebrickable to AWS S3.

## Features

- **CSV Downloading**: Fetches CSV files from Rebrickable.
- **S3 Synchronization**: Uploads new or updated CSVs to an S3 bucket.
- **Change Detection**: Compares file hashes to avoid unnecessary uploads.
- **Manifest Management**: Maintains a `manifest.json` in S3 to track file versions.
- **Error Handling**: Robust error handling for network and file operations.

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

AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_DEFAULT_REGION=your-aws-default-region
S3_BUCKET_NAME=your-s3-bucket-name

REBRICKABLE_PARTS_CSV_URL=https://cdn.rebrickable.com/media/downloads/parts.csv.gz
REBRICKABLE_CATEGORIES_CSV_URL=https://cdn.rebrickable.com/media/downloads/categories.csv.gz
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

## Project Structure

```
lego-catalog-pipeline/
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── csv_downloader.py  # CSV downloading logic
│   ├── file_utils.py      # File utility functions
│   └── s3_manager.py      # S3 interaction logic
├── main.py              # Pipeline entry point
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables (not version controlled)
└── README.md            # Project documentation
```

## Testing

To run the tests, use `pytest`:

```bash
pytest
```

## License

[MIT License](LICENSE)
