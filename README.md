# SRE CLI Tool

This CLI tool interacts with a Kubernetes cluster to manage deployments.

## Setup

1. Install Python 3.8+.
2. Install dependencies:
   ```bash
   pip install kubernetes
3. Configure your kubeconfig file (~/.kube/config)
4. For your own convenient there is a sample deployment you can apply `flask-deployment.yaml` by running
   ```bash
   kubectl apply -f flask-deployment.yaml

## Usage

### List Deployments
```bash
python3 sre.py list --namespace=default
```
### Scale a Deployment
```bash
python3 sre.py scale --deployment=flask --replicas=3 --namespace=default
```
### Get Deployment Info
```bash
python3 sre.py info --deployment=flask --namespace=default
```
### Diagnose Deployment Health
```bash
python3 sre.py diagnostic --deployment=flask
```