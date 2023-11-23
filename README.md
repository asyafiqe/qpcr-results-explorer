# qPCR results explorer 
**A simple streamlit app to explore qPCR data.**

Please create *plate_id.csv* file before running the app. Check *plate_id_example.csv* above.

## Running
There are several ways to run this app: through streamlit share (easiest), portable standalone build for Windows, conda environment, and docker.

### Streamlit share
Click the button below to launch the app:
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/asyafiqe/qpcr-results-explorer/main/app.py)

### Portable standalone build for Windows
Download zip file from [release page](https://github.com/asyafiqe/qpcr-results-explorer/releases).

Extract the downloaded zip file.

Open **run.bat** file.

App will launched in the browser. If not, open http://localhost:8501 in a browser.

### Conda environment
Clone this repo
```
git clone https://github.com/asyafiqe/qpcr-results-explorer.git
cd qpcr-results-explorer
```
Create conda environment
```
conda env create -f environment.yml
conda activate qpcr_explorer
```
Run the app
```
streamlit run app.py
```
App will launched in the browser. If not, open http://localhost:8501 in a browser.

### Docker
```
docker run -p 8501:8501 -it asyafiqe/qpcr-results-explorer
```

## Build from source

### Windows standalone
Clone this repo
```
git clone https://github.com/asyafiqe/qpcr-results-explorer.git
cd qpcr-results-explorer
```
Build
```
.\builder.bat
```

### Docker
Clone this repo
```
git clone https://github.com/asyafiqe/qpcr-results-explorer.git
cd qpcr-results-explorer
```
Build
```
docker build -f Dockerfile -t asyafiqe/qpcr-results-explorer --progress=plain . 2>&1 | Tee-Object -FilePath "build.log"
```


## Notes
~~Orca~~ Kaleido may takes a while to load for the first graph. Button to download graph will appear once ~~Orca~~ Kaleido finished loading. Please do not change option if the app still show running indicator (top right).