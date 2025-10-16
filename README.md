# bill_segment_extractor

A small project for extracting structured data from credit card bills (PDFs).
It uses a Go frontend to handle file validation, orchestration, and formatting, and a Python backend to actually parse the PDF and extract transactions, totals, and other useful info.

I built this mostly to automate some personal finance tracking — but it could be extended for other kinds of statements too.

## 🧩 What It Does

You give it:

- A PDF file of a credit card bill
- A provider type (for now just pdf or default)
- An optional config file

It gives you:

- Structured data in JSON or CSV
- Either as a file, or directly printed to stdout
- The Go code acts as the “controller,” and the Python code does the extraction work.

Here’s the general flow:

![alt text](https://github.com/adamzki99/bill_segment_extractor/blob/main/RepoResources/sequenceDiagram.svg)

## 🧱 Project Structure
```
bill_segment_extractor/
├── go-frontend/
│   ├── main.go
│   ├── frontend/
│   │   ├── extract.go
│   │   ├── validator.go
│   │   └── converter.go
│   └── registry/
│       └── provider_registry.go
│
├── python-provider/
│   ├── extract.py
│   ├── bill_parser.py
│   ├── utils/
│   │   ├── pdf_reader.py
│   │   └── text_cleaner.py
│   └── requirements.txt
│
└── <repo_files>
```

## ⚙️ Example Usage
From the command line
```bash
go run main.go extract --file ./samples/creditcard_bill.pdf --provider pdf --config config.json --output ./output/bill.csv
```

Example Output
```json
{
  "card_holder": "John Doe",
  "statement_period": "2025-08-01 to 2025-08-31",
  "total_due": 1234.56,
  "transactions": [
    { "date": "2025-08-03", "description": "Amazon Purchase", "amount": 42.50 },
    { "date": "2025-08-12", "description": "Grocery Store", "amount": 78.90 }
  ]
}
```

🧾 Config Example

config.json
```json
{
  "output_format": "csv",
  "return_data": false,
  "provider_options": {
    "currency_symbol": "$",
    "table_detection": "auto"
  }
}
```

## 🪓 Error Handling

|Error |Where it happens |What it means |
|------|-----------------|--------------|
|File not found| Go| Input file path doesn’t exist |
|Invalid provider| Go| Provider type isn’t registered |
|Invalid PDF| Python| Couldn’t open or parse the PDF |
|Extraction failed| Python| Parsing didn’t return valid data |
|Write error| Go| Couldn’t write output file |

## 🧪 Notes

This project started as a way to automate how I record credit card transactions for budgeting.
The extraction logic is currently pretty basic — it just tries to find transaction tables and totals — but it’s easy to tweak for different bill formats.

Things I might add later:

- Table parsing in Go
- Support for multiple providers (different banks)
- Export to Excel or JSON Lines
