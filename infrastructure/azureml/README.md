# Azure ML model serving

The local training command writes a versioned joblib bundle. Register that bundle
as `synthetic-credit-risk`, then create the AAD-token-protected managed endpoint:

```bash
az ml model create --name synthetic-credit-risk \
  --path ../../services/ai-service/artifacts/risk-model.joblib
az ml online-endpoint create --file endpoint.yml
az ml online-deployment create --file deployment.yml --all-traffic
```

Run these commands from a network path allowed by the private Azure ML workspace.
The application uses `DefaultAzureCredential` when no API key is configured.
