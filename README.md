# Ecount Automation
Automated solution to extract data from Ecount.

## Prerequisites
1. Python version 3
2. Git
3. Ecount account

## Initialization
Before running anything, ensure you have an API key from Ecount. For more information, read [here](https://sboapi.ecount.com/ECERP/OAPI/OAPIView?lan_type=en-PH#).

Then, create a new `.env` file in the root directory. Copy and paste your API key and/or variable secrets in this file.

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
Enter `python main.py` in your terminal to run the script.