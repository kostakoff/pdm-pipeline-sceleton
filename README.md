# Pipeline

## Description
This pipeline using PDM PEP-582 for immutable code behaviour

## Development requirements
- [X] python3.9 or higher
- [X] virtualenv
- [X] PDM package manager

## Prepare development environment
- Clone this repo
- Optional run docker container with PDM
```bash
docker run -v $(pwd):/home/user -w /home/user --user $(id -u):$(id -g) -e HOME=/tmp --rm -it --entrypoint bash docker.io/kostakoff/rocky-base-images:8-python3.9
```
- Navigate to pipeline folder `cd pipeline`
- Enable pep582 **[instructions](https://pdm-project.org/latest/usage/pep582/#__tabbed_1_2)**
```bash
eval "$(pdm --pep582)"
``` 
- Sync packages 
```bash
pdm sync -d
```

## PDM troubleshooting
If you will have an issues with **PDM** cli, - you can try  \
remove `__pypackages__`, optional pdm.lock and run `
```bash
pdm install -d -v
```
folder `__pypackages__` should be created from scratch

## Run pipeline
- run pipeline cli
```bash
python3 ./pipeline/pipeline.py --validate
```
