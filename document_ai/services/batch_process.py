import re
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import InternalServerError, RetryError
from google.cloud import documentai
from google.cloud import storage

# Import FAISS functions
from document_ai.faiss_encode.faiss_utils import create_or_load_faiss_index, add_text_to_faiss, save_faiss_index

# GCP variables
from config.settings import (
    PROJECT_ID as project_id,
    PROCESSOR_ID as processor_id,
    LOCATION as location,
    GCS_INPUT_URI as gcs_input_uri,
    GCS_OUTPUT_URI as gcs_output_uri,
)

processor_version_id = None
field_mask = "text,entities,pages.pageNumber"

# Supported MIME types
MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


def get_mime_type(filename: str) -> str:
    for ext, mime in MIME_TYPES.items():
        if filename.lower().endswith(ext):
            return mime
    raise ValueError(f"Unsupported file type: {filename}")


def batch_process_documents(
    project_id: str,
    location: str,
    processor_id: str,
    gcs_input_uri: str,
    gcs_output_uri: str,
    processor_version_id: str = None,
    field_mask: str = None,
    timeout: int = 400,
):
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    client = documentai.DocumentProcessorServiceClient(client_options=opts)
    storage_client = storage.Client()
    faiss_index = create_or_load_faiss_index()

    matches = re.match(r"gs://(.*?)/(.*)", gcs_input_uri)
    if not matches:
        raise ValueError(f"Invalid GCS URI: {gcs_input_uri}")
    input_bucket_name, input_prefix = matches.groups()
    blobs = storage_client.list_blobs(input_bucket_name, prefix=input_prefix)

    for blob in blobs:
        try:
            mime_type = get_mime_type(blob.name)
        except ValueError:
            print(f"Skipping unsupported file: {blob.name}")
            continue

        print(f"Processing {blob.name} with MIME type {mime_type}...")

        gcs_document = documentai.GcsDocument(
            gcs_uri=f"gs://{input_bucket_name}/{blob.name}", mime_type=mime_type
        )
        input_config = documentai.BatchDocumentsInputConfig(
            gcs_documents=documentai.GcsDocuments(documents=[gcs_document])
        )
        gcs_output_config = documentai.DocumentOutputConfig.GcsOutputConfig(
            gcs_uri=gcs_output_uri, field_mask=field_mask
        )
        output_config = documentai.DocumentOutputConfig(gcs_output_config=gcs_output_config)

        if processor_version_id:
            name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
        else:
            name = client.processor_path(project_id, location, processor_id)

        request = documentai.BatchProcessRequest(
            name=name, input_documents=input_config, document_output_config=output_config
        )

        operation = client.batch_process_documents(request)
        try:
            print(f"Waiting for operation {operation.operation.name} to complete...")
            operation.result(timeout=timeout)
        except (RetryError, InternalServerError) as e:
            print(f"Error processing {blob.name}: {e}")
            continue

        # Fetch output JSON
        metadata = documentai.BatchProcessMetadata(operation.metadata)
        for process in metadata.individual_process_statuses:
            output_matches = re.match(r"gs://(.*?)/(.*)", process.output_gcs_destination)
            if not output_matches:
                continue
            output_bucket, output_prefix = output_matches.groups()
            output_blobs = storage_client.list_blobs(output_bucket, prefix=output_prefix)
            for oblob in output_blobs:
                if oblob.content_type != "application/json":
                    continue
                document = documentai.Document.from_json(oblob.download_as_bytes(), ignore_unknown_fields=True)
                text = document.text.strip()
                if not text:
                    continue
                print(f"Adding text from {blob.name} to FAISS index...")
                faiss_index = add_text_to_faiss(text, index=faiss_index)

    save_faiss_index(faiss_index)


if __name__ == "__main__":
    batch_process_documents(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        gcs_input_uri=gcs_input_uri,
        gcs_output_uri=gcs_output_uri,
        processor_version_id=processor_version_id,
        field_mask=field_mask,
    )
