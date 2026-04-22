# Google Drive to Airtable Integration via MCP

This application retrieves metadata for image files from Google Drive and saves that metadata to an Airtable database, all using Zapier's Model Context Protocol (MCP).

## Features

- Fetch file metadata from Google Drive via MCP
- Store metadata in Airtable via MCP
  - Automatically checks for existing records and updates them instead of creating duplicates
  - Shows whether a record was created or updated
- Simple web interface for entering Google Drive file IDs
- No API keys or authentication tokens required (handled by MCP)

## Requirements

- Python 3.7+
- Flask web framework
- Access to MCP (Model Context Protocol) environment
- Zapier MCP actions enabled for:
  - Google Drive: `mcp_Zapier_MCP_google_drive_retrieve_file_or_`
  - Airtable: `mcp_Zapier_MCP_airtable_create_record`, `mcp_Zapier_MCP_airtable_find_records`, `mcp_Zapier_MCP_airtable_update_record`

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Copy or rename `.env.example` to `.env` (if not already done)
   - Add your Airtable base ID and table name to the `.env` file:
     ```
     AIRTABLE_BASE_KEY='your_airtable_base_id'
     AIRTABLE_TABLE_NAME='your_table_name'
     ```

3. Set up your Airtable base:
   - Create a table with the following fields:
     - File ID (text)
     - Name (text)
     - Type (text)
     - Size (bytes) (number)
     - Created Time (date/time)
     - Modified Time (date/time)

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://127.0.0.1:5000
   ```

3. Enter a Google Drive file ID in the input field and click "Fetch and Save Metadata"
   - If a record with this File ID already exists, it will be updated
   - If not, a new record will be created
   - The application will display whether it created a new record or updated an existing one

## How to Find a Google Drive File ID

1. Open the file in Google Drive
2. Look at the URL. It should look something like:
   ```
   https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i/view
   ```
3. The File ID is the part between `/d/` and `/view`
   (In this example: `1a2b3c4d5e6f7g8h9i`)

## About MCP Integration

This application uses Zapier's Model Context Protocol (MCP) for both Google Drive and Airtable integrations:

- **MCP Google Drive Integration**: Retrieves file metadata without requiring OAuth credentials
- **MCP Airtable Integration**: Handles all Airtable operations including searching, creating, and updating records

MCP handles all authentication and authorization transparently, making the app simpler and more secure. 