# King County House Prices: From Notebook to Pipeline, API and Container

This project takes the exploratory [King County notebook](King-County.ipynb) and turns its data cleaning, feature engineering and modeling into a reusable Python pipeline. It then serves a trained model through a FastAPI price-prediction endpoint that runs in a Docker container.

The original assignment is in [project-description.md](project-description.md).

## 📄 Conclusions

**[Read my conclusions (PDF)](conclusions.pdf)**

## What I built

| Step | Where | What it does |
|---|---|---|
| Data loading | [src/data_loading.py](src/data_loading.py) | Reads the raw King County CSV. |
| Data cleaning | [src/data_cleaning.py](src/data_cleaning.py) | Removes bedroom/bathroom outliers, reconstructs `sqft_basement`, fills missing `view`/`waterfront` and merges `yr_built`/`yr_renovated` into `last_known_change`. |
| Feature engineering | [src/data_processing.py](src/data_processing.py) | Adds price per sqft, distance to Seattle's center and distance to the nearest waterfront house. |
| Modeling | [src/modeling.py](src/modeling.py) | ElasticNet with polynomial features and scaling in one scikit-learn `Pipeline`, tuned with 5-fold `GridSearchCV`. Saved with [skops](https://skops.readthedocs.io/). |
| Pipeline entry point | [src/data_pipeline.py](src/data_pipeline.py) | Runs load → clean → process → train → save from the command line. |
| API | [app/](app/) | FastAPI app that loads the model at startup and serves `POST /prediction`. |
| Tests | [tests/test_api.py](tests/test_api.py) | Checks predictions and input validation. |
| Container | [Dockerfile](Dockerfile) | Trains the model during the build and runs the API. |

### Two models

The pipeline can train two models. Both are defined in `MODEL_CONFIGS` in [src/modeling.py](src/modeling.py).

- **`full`**: uses 19 features, including the engineered location features.
- **`basic`**: uses 5 features a user can easily type in (`bedrooms`, `bathrooms`, `sqft_living`, `sqft_lot`, `floors`). The API serves this one. Test R² is about 0.55.

### Design choices

- **Every step is a small, pure function.** Each takes a DataFrame and returns a new one without modifying its input. That makes the steps easy to test and reorder.
- **Preprocessing lives inside the model.** Polynomial expansion and scaling are part of the saved scikit-learn `Pipeline`, so the API passes raw feature values and can't apply the transformations differently from training.
- **The API checks its model on startup.** If the model file is missing, or its features don't match the config, the app refuses to start and says how to fix it.
- **Input validation.** [app/schemas.py](app/schemas.py) sets realistic ranges (for example 1–15 bedrooms), so invalid requests get a `422` instead of a meaningless price.

## Project structure

```
.
├── app/                  # FastAPI app (main.py, schemas.py)
├── src/                  # Pipeline: loading, cleaning, processing, modeling
│   └── helpers/          # Distance calculation
├── tests/                # API tests
├── data/                 # Raw dataset (processed.csv is generated, not tracked)
├── model/                # Trained models (generated, not tracked)
├── Dockerfile
├── King-County.ipynb     # Original notebook
├── conclusions.pdf       # Project reflection
└── pyproject.toml / uv.lock
```

## Getting started

### Option A: Docker (quickest)

You only need [Docker](https://docs.docker.com/get-docker/). The build trains the model, so no local Python setup is required.

```bash
docker build -t king-county-api .
docker run -p 8000:8000 king-county-api
```

Then open http://localhost:8000/docs to try the API in your browser.

### Option B: Run locally

You need [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.13 (see [.python-version](.python-version)). uv can install the right Python for you.

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Train a model. The API needs `basic`; `full` is optional.

   ```bash
   uv run python -m src.data_pipeline --model basic
   uv run python -m src.data_pipeline --model full
   ```

   This writes `data/processed.csv` and `model/basic_model.bin` (or `model/model.bin`) and prints the best hyperparameters and test R².

3. Start the API:

   ```bash
   uv run fastapi dev
   ```

   Open http://localhost:8000/docs.

4. Run the tests. They need the `basic` model from step 2.

   ```bash
   uv run pytest
   ```

## Using the API

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check. |
| `POST` | `/prediction` | Predicts a house price from 5 features. |

Example request:

```bash
curl -X POST http://localhost:8000/prediction \
  -H "Content-Type: application/json" \
  -d '{"bedrooms": 3, "bathrooms": 2, "sqft_living": 1800, "sqft_lot": 5000, "floors": 1}'
```

Example response:

```json
{"price": 457450.45}
```

## How the Docker image works

The [Dockerfile](Dockerfile) has three stages:

1. **`base`** installs the locked dependencies from `uv.lock` with uv.
2. **`trainer`** copies `src/` and the raw CSV and runs the pipeline to train the `basic` model.
3. **`runtime`** copies `app/`, `src/` and only the trained model file, then starts uvicorn on port 8000.

The `model/` folder is in `.gitignore`, so a fresh clone has no model file. Training during the build means `docker build` works straight from the repository. It also means the model is saved and loaded with the exact same scikit-learn and skops versions. [.dockerignore](.dockerignore) keeps the build small by sending only the files the image needs.