# pipeline

## Immuteble python pipeline
This pipeline using PDM PEP-582 for immutable code behaviour


## Development environment

Install  **PDM** to your local machine. \
We chose **PDM**, because of support [PEP-582](https://peps.python.org/pep-0582/) by default.

You also need  **[pyenv](https://github.com/pyenv/pyenv)**

```toml
.pdm-python
  # Example for windows
path = "C:\\Users\\{USER}\\.pyenv\\versions\\3.9.0\\python3.9.exe"
```

#### PDM troubleshooting 

If you will have an issues with **PDM** cli, - you can try  \
remove `__pypackages__` and run `pdm install -d -v` \
If after run `pdm install -d` - was created ".venv" folder - rename it to \
`__pypackages__` and run `pdm sync -d`

### Development preparation

- Clone this repo
- Enable pep582 `eval "$(pdm --pep582)"` **[instructions](https://pdm-project.org/latest/usage/pep582/#__tabbed_1_2)**
- Sync packages `pdm sync -d`
