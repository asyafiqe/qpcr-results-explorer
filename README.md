# qPCR results explorer 
**A simple streamlit app to explore qPCR data.**

Please create *plate_id.csv* file before running the app. Check *plate_id_example.csv* above.

## Running
There are two ways to run this app: portable standalone build for Windows and conda environment (advanced).

### Portable standalone build for Windows
Download zip file from [release page](https://github.com/asyafiqe/qpcr-results-explorer/releases).

Extract the downloaded zip file.

Open **run.bat** file.

App will launched in the browser. If not, open http://localhost:8501 in a browser.

### Conda environment
Clone this repo
```
git clone https://github.com/asyafiqe/qpcr-results-explorer.git && cd qpcr-results-explorer
```
Create conda environment
```
conda env create -f environment.yml
```
Run the app
```
streamlit run app.py
```
App will launched in the browser. If not, open http://localhost:8501 in a browser.

## Notes
Orca may takes a while to run for the first run. Graph will be loaded once orca finished boot up.
