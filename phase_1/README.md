## Run Weaviate (local)

This project needs a running Weaviate server.  
Start it with Docker:

```bash
docker run -d --name weaviate \
  -p 8081:8080 \
  semitechnologies/weaviate:1.25.7
```

## Check if it’s ready

```bash
curl http://127.0.0.1:8081/v1/.well-known/ready
```

You should see: `{"status":"READY"}`.