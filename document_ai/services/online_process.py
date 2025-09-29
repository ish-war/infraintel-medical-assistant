from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from config.settings import PROJECT_ID, LOCATION, PROCESSOR_ID

# The local file in your current working directory
FILE_PATH = "image.jpg"
MIME_TYPE = "image/jpeg"

# Instantiates a client
docai_client = documentai.DocumentProcessorServiceClient(
    client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
)

# Full resource name
RESOURCE_NAME = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

# Read the file into memory
with open(FILE_PATH, "rb") as image:
    image_content = image.read()

# Load Binary Data into Document AI RawDocument Object
raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)

# Configure the process request
request = documentai.ProcessRequest(name=RESOURCE_NAME, raw_document=raw_document)

# Process the document
result = docai_client.process_document(request=request)

document_object = result.document
print("Document processing complete.")
print(f"Text: {document_object.text}")
