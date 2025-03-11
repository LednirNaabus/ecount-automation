# Ecount Automation
Automated solution to extract data from Ecount.

## Prerequisites
1. Python version 3 installed on your system.

    1.1 Verify Python is installed by entering `python --version` on your terminal.
 
2. Git (optional)
3. Ecount account
4. Google Account to enable Google API services

### Copying files

#### How to clone
1. Open your terminal. Make sure git is installed on your system.
2. Navigate to a directory where you want to store the repository (ex: `"Documents"` or `"Desktop"`)
3. Enter the following command:
    ```
    git clone git@github.com:LednirNaabus/ecount-automation.git
    ```

#### Another Method
Click the green button of this repository located on the upper right. In the dropdown selection, click "***Download ZIP***".

## Setting it all up
- Ensure you have an API key from [Ecount](https://login.ecount.com/Login/). For more information about the Ecount OpenAPI, read [here](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).

- Then, create a new `.env` file in the root directory. Copy and paste your API key and/or variable secrets in this file. Refer to the example `.env` file below.

### Example `.env` file

```
API_CERT_KEY = "YOUR API KEY HERE"
OTHER_STUFF = "..."
```

### Setting up Google API and Add Key
In order for the script to work and import the data to Google Sheets, you will have to create a Google [Service Account](https://cloud.google.com/iam/docs/service-accounts).

1. Go to [Google Cloud Console](https://console.developers.google.com/) and create a new project.

    ![Create a new project](https://cdn.analyticsvidhya.com/wp-content/uploads/2024/09/new_project.webp)

2. Enable the APIs required. Click on **Enable APIs and Services**.

    ![Enable APIs](https://cdn.analyticsvidhya.com/wp-content/uploads/2024/10/image-36.png)

3. Then search for **Google Sheets API** and **Google Drive API**.

4. Create the credentials for your service account.

    ![Credentials](https://cdn.analyticsvidhya.com/wp-content/uploads/2024/10/screenshot-from-2020-07-22-18-28-29-6708c0226aca9.webp)

5. Go to the Navigation menu located on the left and then go to **APIs & Services** > **Credentials** > *__your service account__* > **Keys** > **Add Key**.

    ![Add key](add_key.png)

    This will generate a key for you stored in a `.json` file.

**Note:** Place a copy of the generated key `.json` file under `C:\ecount-automation\config\` in this repository. It is also recommended to rename the config file to `google-api-key.json`.

6. In the same page, click **Details** then copy your Google Service account email. You will need this in the next step.

    ![Email](google_service_account.png)

7. Open Google Sheets and create a new Spreadsheet. Name it to whatever name you set in `config.json` (`"SHEET_NAME"`).

8. Modify the share access of the Spreadsheet to "**Anyone with the link**".

9. Paste your Google Service Account information from your clipboard into the text box. Click "**Done**" once done.

    ![Share Access](sheets_share_access.png)

## Configuration
Inside of the `config` directory, create a `config.json` file to adjust parameters such as `COMPANY_CODE`, `USER_ID`, etc. You can also add warehouses in the `config.json` file by inserting the desired warehouse. Changing the parameters in the `json` file will sync with `config.py`.

### Sample configuration file

You can copy this sample configuration `json` file and modify the needed parameters.

```json
{
    "COMPANY_CODE" : "000001",
    "USER_ID" : "ABCD",
    "LAN_TYPE" : "en-US",
    "BASE_DATE" : "2024-12-01",
    "SHEET_NAME" : "Untitled Sheet",
    "INGESTION_WORKSHEET_NAME" : "ingestion_sheet",
    "Warehouses" : {
        "ID1" : "Warehouse 1",
        "ID2" : "Warehouse 2"
    }
}
```

## Initialization (IMPORTANT)
- Before actually running the script, install the required dependencies first.
- Enter `pip install -r requirements.txt` to install the dependecies.

## Run the script
Open your terminal, navigate to the directory where you cloned this project (i.e., `"Documents/ecount-automation/"`).

Enter `python main.py` in your terminal to run the script.

**[Back to top](#prerequisites)**
