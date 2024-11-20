# Address Coding Project

This project is designed to process and code address data from CBDB address code table. The main script, 

code_addr.py

, reads your input data, processes it, and outputs coded address information.

## Files

- **code_addr.py**: Main script for processing and coding address data.
- **addr_data_schema.xlsx**: Schema for address data.
- **ADDRESSES.txt**: Processed address data.
- **cbdb_entity_address_types.csv**: List of address types.
- **input_small.txt**: Small input dataset for testing.
- **input.txt**: Main input dataset.
- **output.txt**: Output file with coded address data.
- **ZZZ_ADDRESSES.xlsx**: Original address data in Excel format.

## Usage

1. **Install Dependencies**:
   Ensure you have the required dependencies installed. You can install them using pip:
   ```sh
   pip install pandas char-converter
   ```

2. **Load your input data**:

Based on this schema

An example of the input schema:
```
id	dy	addr_name	addr_belong	time
1	宋	甌寧	建州	1279
2	清	江南太平府	no_info	no_info
```

Put your input data into **input.txt**

2. **Run the Script**:
   Execute the 

code_addr.py

 script to process the input data and generate the output:
   ```sh
   python code_addr.py
   ```

## Notes

- If you want to convert the varient to simplfied Chinese as a standarization step, please change

```python
use_char_converter = False
```

to 

```python
use_char_converter = True
```

- The script processes address data by reading from 

ZZZ_ADDRESSES.xlsx

You can download the newest ZZZ_ADDRESSES from [cbdb huggingface](https://huggingface.co/datasets/cbdb/cbdb-sqlite/blob/main/latest_ZZZ_tables.7z).

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license.