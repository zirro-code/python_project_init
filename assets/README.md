## Project description

TODO

## How to use

For UNIX:

```
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

For Windows:

```
python -m venv venv
./venv/Scripts/activate.bat
pip install -r requirements.txt
```

### Env setup

Create .env file (or rename the example one), and fill with the values from instruction inside

### Run from the project home directory using

For UNIX:

```
set -a && source .env && set +a; clear; python -m src
```

For Windows (untested):

```
Get-Content .env | ForEach-Object { if ($_ -match '^\s*([^#][^=]+)=(.*)$') { Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim() } }; clear; python -m src
```

## Development

### Setup

```
python3.11 -m venv venv && source ./venv/bin/activate && pip install -r requirements.txt
```

#### Env setup

Create .env file (or rename the example one), and fill with the values from instruction inside

### Testing

```
./ci.sh
```

### Performance

```
mkdir ./profiling
```

---

```
python -m cProfile -o profiling/cprofile.prof -m src
```

```
pip install py-spy &&
py-spy record -o profiling/pyspy.svg -- python -m src;
pip uninstall py-spy
```
