# siu_result

siu_result is a command-line tool to obtain your SIU result pdf without spending multiple lifetimes waiting for their servers to respond with something other than a 503.

## Usage

1. Clone this repo 

    (`git clone https://github.com/zeffo/siu_result`)


2. Install dependencies 

    (`python -m poetry install`) 
    
    > Ensure you have [poetry](https://pypi.org/project/poetry/) installed first


3. Run the scraper 
    
    (`python -m siu_result (prn) (seat_no) (output_file_path)`)


> Currently only supports Firefox.