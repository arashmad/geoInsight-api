### Test

```bash
cd geoinsight_api
make test
```

### Docker build and check

```bash
docker build -t geoinsight-api .
docker run --rm -p 8000:8000 geoinsight-api
curl http://127.0.0.1:8000/health
```
