# Taiga.io exporter

Tool for export stats from [Taiga.io](taiga.io) service to [Google Spreadsheets](https://docs.google.com/spreadsheets/). This tool uses [Taiga.io API v1](https://taigaio.github.io/taiga-doc/dist/api.html).

## Installation

### Requirements

* Python 3.3 and up ![Version](https://img.shields.io/badge/version-1.0.0-lightgrey.svg)
* [requirements.txt](./requirements.txt)

`$ pip install -r requirements.txt`

## Usage

```shell
usage: start.py [-h] --sheet-name SHEET_NAME --output-table OUTPUT_TABLE
                [--taiga-creds TAIGA_CREDS] [--gsheets-creds GSHEETS_CREDS]

Tool is used for loading Taiga.io stats to GSheets

optional arguments:
  -h, --help            show this help message and exit
  --sheet-name SHEET_NAME
                        The name of sheet in Google Sheets
  --output-table OUTPUT_TABLE
                        The name of output table
  --taiga-creds TAIGA_CREDS
                        Taiga.io credentials (path to json file) with 'host',
                        'username' and 'password' keys
  --gsheets-creds GSHEETS_CREDS
                        Google Sheets credentials (path to json file)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](./LICENSE)