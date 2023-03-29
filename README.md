## HDB Resale
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://layonsan-hdb-resale.streamlit.app/)

Public repository to showcase data visualisation assignment for SD6105 Data Visualisation course under Masters of Science in Data Science in NTU.


### Installation and Usage
```
# initialise new python environment
python3 -m venv .venv

# activate environment
source .venv/bin/activate

# install python dependencies
pip install -r requirements.txt

# freeze dependencies
pip freeze > requirements.txt

# run python as modules
python -m src.<module-name>

python -m src.prepare # example of running prepare.py as module

```

### Limitations
- While caching was used for performance optimisation, session state was not leveraged to share variables across rerun for each user session. 

### Other Notes
- The app may take some time to load. Streamlit automatically puts the app to sleep if left unactive for a period of time. When that happens, you might need to give it a few minutes to reboot the app.

