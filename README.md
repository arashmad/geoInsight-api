# GeoInsight API

FastAPI backend for geospatial analysis workflows.

### Test

```bash
cd geoinsight_api
make test
```

### Docker build and check

using docker

```bash
docker build -t geoinsight-api .
docker run --rm -p 8000:8000 geoinsight-api
curl http://127.0.0.1:8000/health
```

using docker compose

```bash
# build and start the container
docker compose up --build
# stop the container
docker compose down
```
