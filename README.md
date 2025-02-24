# Ecount Automation
Automated solution to extract data from Ecount.

## Prerequisites
1. Python version 3 installed on your system.

    1.1 Verify Python is installed by entering `python --version` on your terminal.
 
2. Git (to clone this repository)
3. Ecount account

### How to clone
1. Open your terminal.
2. Navigate to a directory where you want to store the repository (ex: `"Documents"` or `"Desktop"`)
3. Enter the following command:
    ```
    git clone git@github.com:LednirNaabus/ecount-automation.git
    ```

## Initialization
Before running anything, ensure you have an API key from Ecount. For more information, read [here](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).

Then, create a new `.env` file in the root directory. Copy and paste your API key and/or variable secrets in this file. Refer to the example `.env` file below.

### Example `.env` file

```
API_CERT_KEY = "YOUR API KEY HERE"
OTHER_STUFF = "..."
```

Next, first run `pip install -r requirements.txt` to install dependencies.

## Configuration
Edit the `config.json` file to adjust parameters such as `COMPANY_CODE`, `USER_ID`, etc. You can also add warehouses in the `config.json` file by appending. Adjusting the `json` file will sync with `config.py`.

```json
{
    ...,
    "Warehouses" : {
        "ID1" : "Warehouse1",
        "ID2" : "Warehouse2",
        # add here
    }
}
```

## Run the script
Open your terminal, navigate to the directory where you stored this project (i.e., `"Documents/ecount-automation/"`).

Enter `python main.py` in your terminal to run the script.