# Ecount Automation
Automated solution to extract data from Ecount.

## Branch: `streamlit-wrapper-v1`

### To do:

- [x] Add Streamlit
    - [x] Add downloadable dataframe of extracted data from Ecount API.
        - [x] Fix pickle serialization

- [ ] Handle empty responses from API

- [ ] If `ERROR 500` rewrite the data if the script is run again

- [ ] Optimize/speed up API response

- [x] Add feature to extract to BigQuery table

- [x] Refactor `config/config.py`

- [x] modify `config.json` file to include BigQuery configs

- [x] Change export to Google Sheets to DataFrame instead

- [x] Add logging

    - [ ] Refactor