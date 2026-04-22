from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import json
import uuid
import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ----- MOCK MCP FUNCTIONS (FOR LOCAL TESTING) -----
# These mock functions simulate the behavior of the actual MCP functions
# They will only be used when the real MCP functions aren't available

# In-memory storage for mock Airtable records
mock_airtable_records = {}

def mock_google_drive_retrieve_file(id):
    """Mock function for MCP Google Drive file retrieval"""
    print(f"MOCK: Retrieving Google Drive file with ID: {id}")
    # Return mock data that simulates a Google Drive file
    return {
        'id': id,
        'name': f'example_image_{id}.jpg',
        'mimeType': 'image/jpeg',
        'size': '123456',
        'createdTime': datetime.datetime.now().isoformat(),
        'modifiedTime': datetime.datetime.now().isoformat()
    }

def mock_airtable_find_records(baseId, tableIdOrName, formula):
    """Mock function for MCP Airtable record search"""
    print(f"MOCK: Searching Airtable {baseId}.{tableIdOrName} with formula: {formula}")
    # Parse the formula to extract the File ID
    # Formula format: {File ID} = 'some-id'
    import re
    match = re.search(r"'([^']*)'", formula)
    if match:
        file_id = match.group(1)
        # Check if we have a mock record with this file_id
        table_key = f"{baseId}_{tableIdOrName}"
        if table_key in mock_airtable_records and file_id in mock_airtable_records[table_key]:
            return [mock_airtable_records[table_key][file_id]]
    return []

def mock_airtable_update_record(baseId, tableIdOrName, recordId, fields):
    """Mock function for MCP Airtable record update"""
    print(f"MOCK: Updating Airtable record {recordId} in {baseId}.{tableIdOrName}")
    table_key = f"{baseId}_{tableIdOrName}"
    if table_key in mock_airtable_records:
        for file_id, record in mock_airtable_records[table_key].items():
            if record.get('id') == recordId:
                record.update(fields)
                return record
    return None

def mock_airtable_create_record(baseId, tableIdOrName, fields):
    """Mock function for MCP Airtable record creation"""
    print(f"MOCK: Creating Airtable record in {baseId}.{tableIdOrName}")
    # Generate a random record ID
    record_id = str(uuid.uuid4())
    # Create the record
    record = {'id': record_id, **fields}
    # Store it in our mock database
    table_key = f"{baseId}_{tableIdOrName}"
    if table_key not in mock_airtable_records:
        mock_airtable_records[table_key] = {}
    # Use File ID as the key for easy lookup
    file_id = fields.get('File ID')
    mock_airtable_records[table_key][file_id] = record
    return record

# Try to import the real MCP functions, use mocks if not available
try:
    # Try to access one of the MCP functions to see if they're available
    # This will raise a NameError if MCP functions aren't available
    test = mcp_Zapier_MCP_google_drive_retrieve_file_or_
    print("Using real MCP functions")
    USE_MOCK_MCP = False
except NameError:
    print("MCP functions not available. Using mock implementations for testing.")
    # Define mock functions as the real MCP functions
    globals()['mcp_Zapier_MCP_google_drive_retrieve_file_or_'] = mock_google_drive_retrieve_file
    globals()['mcp_Zapier_MCP_airtable_find_records'] = mock_airtable_find_records
    globals()['mcp_Zapier_MCP_airtable_update_record'] = mock_airtable_update_record
    globals()['mcp_Zapier_MCP_airtable_create_record'] = mock_airtable_create_record
    USE_MOCK_MCP = True

# ----- ACTUAL APPLICATION CODE -----

def get_file_metadata_from_drive(file_id):
    """Retrieves metadata for a specific file from Google Drive using MCP."""
    print(f"Getting metadata for file ID: {file_id}")
    
    try:
        # Use the MCP function to retrieve file metadata by ID
        file_data = mcp_Zapier_MCP_google_drive_retrieve_file_or_(id=file_id)
        
        # Check if the file was found
        if not file_data or isinstance(file_data, list) and len(file_data) == 0:
            print(f"No file found with ID: {file_id}")
            return None
            
        # If result is a list (sometimes MCP returns lists), take the first item
        if isinstance(file_data, list):
            file_data = file_data[0]
        
        # Extract relevant metadata from the response
        metadata = {
            'id': file_data.get('id'),
            'name': file_data.get('name', file_data.get('title', 'Unknown')),
            'mimeType': file_data.get('mimeType'),
            'size': file_data.get('size', file_data.get('fileSize', '0')),
            'createdTime': file_data.get('createdTime', file_data.get('createdDate')),
            'modifiedTime': file_data.get('modifiedTime', file_data.get('modifiedDate'))
        }
        
        print(f"Retrieved metadata from Drive: {metadata}")
        return metadata
        
    except Exception as e:
        print(f"An error occurred retrieving file metadata: {e}")
        return None

def save_metadata_to_airtable(metadata):
    """Saves file metadata to Airtable using MCP.
    First checks if a record already exists with the file ID and updates it if found,
    otherwise creates a new record.
    """
    try:
        # Prepare common fields for both create and update operations
        # Convert size to integer if it's a string
        size_bytes = 0
        try:
            size_bytes = int(metadata.get('size', 0))
        except (ValueError, TypeError):
            print(f"Warning: Could not convert size to integer: {metadata.get('size')}")
            
        # Create the fields for Airtable
        fields = {
            'File ID': metadata.get('id'),
            'Name': metadata.get('name'),
            'Type': metadata.get('mimeType'),
            'Size (bytes)': size_bytes,
            'Created Time': metadata.get('createdTime'),
            'Modified Time': metadata.get('modifiedTime')
        }
        
        # First, search for existing record with this File ID
        print(f"Searching for existing Airtable record with File ID: {metadata.get('id')}")
        
        # Define search formula to find records with matching File ID
        formula = f"{{File ID}} = '{metadata.get('id')}'"
        
        # Use MCP to find records in Airtable
        search_results = mcp_Zapier_MCP_airtable_find_records(
            baseId=os.getenv('AIRTABLE_BASE_KEY'),
            tableIdOrName=os.getenv('AIRTABLE_TABLE_NAME'),
            formula=formula
        )
        
        # Check if we found any matching records
        if search_results and len(search_results) > 0:
            # Record exists, perform update
            existing_record = search_results[0]
            record_id = existing_record.get('id')
            
            print(f"Found existing record with ID: {record_id}. Updating...")
            
            # Use MCP to update the existing record
            update_response = mcp_Zapier_MCP_airtable_update_record(
                baseId=os.getenv('AIRTABLE_BASE_KEY'),
                tableIdOrName=os.getenv('AIRTABLE_TABLE_NAME'),
                recordId=record_id,
                fields=fields
            )
            
            print(f"Airtable MCP update response: {update_response}")
            return {'updated': True}
        else:
            # No existing record found, create new record
            print(f"No existing record found. Creating new record in Airtable with fields: {fields}")
            
            # Use MCP to create a record in Airtable
            create_response = mcp_Zapier_MCP_airtable_create_record(
                baseId=os.getenv('AIRTABLE_BASE_KEY'),
                tableIdOrName=os.getenv('AIRTABLE_TABLE_NAME'),
                fields=fields
            )
            
            print(f"Airtable MCP create response: {create_response}")
            return {'updated': False}

    except Exception as e:
        print(f"An error occurred interacting with Airtable via MCP: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    if request.method == 'POST':
        file_id = request.form.get('file_id')
        if file_id:
            metadata = get_file_metadata_from_drive(file_id)
            if metadata:
                # We'll modify the save_metadata_to_airtable function to return more info
                result = save_metadata_to_airtable(metadata)
                if result:
                    # Check if it was a new record or update based on result
                    return redirect(url_for('index', success=True, filename=metadata.get('name'), updated=result.get('updated', False)))
                else:
                    error_message = "Could not save metadata to Airtable. Check logs."
            else:
                error_message = "Could not retrieve file metadata from Google Drive. Check logs."
        else:
            error_message = "Please provide a Google Drive File ID."

    success = request.args.get('success')
    filename = request.args.get('filename')
    updated = request.args.get('updated', 'False').lower() == 'true'
    
    # Pass info about mock mode to the template
    return render_template('index.html', 
                          success=success, 
                          filename=filename, 
                          error=error_message, 
                          updated=updated,
                          mock_mode=USE_MOCK_MCP)

if __name__ == '__main__':
    app.run(debug=True) # debug=True for development 