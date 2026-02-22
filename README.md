# Instructions

- Clone repo
- Create a venv with `python3 -m venv venv`
- source the venv with `source venv/bin/activate` (mac) or `source venv/Scripts/activate` (windows)
- Install requirements.txt with `pip install -r requirements.txt`
- Copy .env.example and change name to .env
- Add in the API key
- Run `python data_ingest.py` and select a league to ingest
- If running the data update selection, run the script again and choose the aggregate data option
- Run `python team_stats_v2.py` and select a league and team to see team stats and last 10 match form

## Notes

- The betting folder is included because it houses the data_loader which is required for the stats v2 script