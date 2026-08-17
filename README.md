# IPL Analysis

A small Python project that loads Indian Premier League (IPL) match data from CSV files into a database and produces basic analyses and plots using Matplotlib.

## Features
- Load match and delivery data from CSV files
- Insert data into a MySQL database (scripts can be adapted to SQLite)
- Generate simple analyses and charts (team wins, top players, run distributions)
- Command-line execution with minimal setup

## Requirements
- Python 3.8 or later
- MySQL server (or SQLite as an alternative)
- Python packages: pandas, matplotlib, mysql-connector-python (or mysqlclient)

## Repository structure (example)
- ipl_analysis_p1.py        — main script that loads data and creates plots
- matches.csv               — match-level data (example)
- deliveries.csv            — ball-by-ball data (example)
- README.md

Adjust paths and filenames if your files are organized differently.

## Setup
1. Install Python dependencies:
   pip install pandas matplotlib mysql-connector-python

   Or create a requirements.txt and run:
   pip install -r requirements.txt

2. Prepare a MySQL database and note the connection details (host, port, user, password, database). Alternatively, update scripts to use SQLite.

3. Place CSV files (for example `matches.csv` and `deliveries.csv`) in the project directory or update the script to point to their locations.

4. Update the database connection settings in the script or provide them via environment variables.

## Running
From the project directory run:
- With system python:
  python ipl_analysis_p1.py

- Or with a full Python path on Windows:
  "C:/path/to/python.exe" ipl_analysis_p1.py

The script will load the CSVs into the configured database and open Matplotlib windows with plots. Some scripts may also save figures to files.

## Notes
- Review the script to confirm table names, schema, and file paths before running.
- If you prefer not to use MySQL, switching to SQLite usually requires only a small change to the connection code.
- Add a requirements.txt and a LICENSE file to make the project easier to use and reuse.

## Contributing
Contributions, issues, and suggested improvements are welcome. Open an issue or submit a pull request.

## License
Include a LICENSE file in the repository to specify how the project may be used.
