# Movie Malarkey
Welcome to **Movie Malarkey**, a web-based creative multiplayer game.

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=MovieMalarkey)](https://sonarcloud.io/dashboard?id=MovieMalarkey)

## Running Locally
### Setup/Pre-requisites
To run locally, you'll need the following installed:
* `python3`

Run the following commands for first-time setup of your virtual environment:
```buildoutcfg
# Create virtual environment
sudo apt-get install python3-venv
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install necessary requirements
python3 -m pip install -r requirements.txt
```

### Dataset Loading
**Movie Malarkey** requires an ingested dataset from IMDb. These datasets can be [downloaded from IMDb](https://datasets.imdbws.com/). The **title.basics.tsv.gz** dataset is the expected dataset.

Download & unzip the dataset (`unzip title.basics.tsv.gz`), then ingest it to **Movie Malarkey** using the following command:
```buildoutcfg
python3 scripts/ingest_dataset.py PATH/TO/title.basics.tsv
```

### Running
To run locally, simply run the `main.py` script:
```
python3 main.py
```

This will launch the application at `localhost:8010` by default.

## Development
This section of the README covers development for Movie Malarkey.

### Environment
For ease of development, you will want to modify your `PYTHONPATH` environment to include `<MOVIE_MALARKEY>/src`.

### Style & Conventions
Where possible, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions.

### Unit tests
Movie Malarkey is unit tested with Python's `unittest` framework. To run unit tests, run the following from Movie Malarkey's root directory:
```
python3 -m unittest discover test
```
This finds and automatically runs all unit tests in the `test` directory.

#### Unit Tests with Coverage
To run unit tests in a format that can later provide coverage, run:
```
python3 scripts/run_tests.py
```

### SonarQube Coverage
To run SonarQube analysis, run:
```
python3 scripts/run_analysis.py
```
This assumes you have your `SONAR_TOKEN` environment variable correctly setup.