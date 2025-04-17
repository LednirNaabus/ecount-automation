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

- [ ] Add `stock_in` and `stock_out` formula in creating dataframe

    - Current dataframe columns:

        - `warehouse`, `item_code`, `item_name`, `spec`, `balance`, `Date`, `month_year`, `stock_in`, `stock_out`
    
    - Google sheets columns:

        - `warehouse`, `item_code`, `item_name`, `spec`, `Date`, `stock_in`, `stock_out`, `day_balance (balance)`, `out_of_stock_event`, `prev_balance`, `month_year`

https://www.reddit.com/r/learnpython/comments/l9spb2/trying_to_write_code_that_subtracts_previous_row/

https://www.reddit.com/r/learnpython/comments/kjgl6j/how_do_i_access_a_previous_row_when_iterating/

https://stackoverflow.com/questions/22081878/get-previous-rows-value-and-calculate-new-column-pandas-python