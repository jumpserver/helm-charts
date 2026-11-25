<h1 align="center">JumpServer Kubernetes Helm Chart</h1>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://img.shields.io/github/license/jumpserver/jumpserver" alt="License: GPLv3"></a>
  <a href="https://shields.io/github/downloads/jumpserver/helm-charts/total"><img src="https://shields.io/github/downloads/jumpserver/helm-charts/total" alt="Downloads"></a>
  <a href="https://github.com/jumpserver/helm-charts"><img src="https://img.shields.io/github/stars/jumpserver/helm-charts?color=%231890FF&style=flat-square" alt="Stars"></a>
  <a href="https://github.com/jumpserver/helm-charts/commits"><img src="https://img.shields.io/github/last-commit/jumpserver/helm-charts.svg" alt="Last commit"></a>
  <a href="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml"><img src="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml/badge.svg" alt="Release Charts"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="https://github.com/jumpserver/helm-charts/blob/main/README.zh-hans.md">简体中文</a> · <a href="https://github.com/jumpserver/helm-charts/blob/main/README.zh-hant.md">繁體中文</a>
</p>

This repository provides the Kubernetes Helm chart for [JumpServer](https://www.jumpserver.org/), the world's first fully open-source bastion host (PAM) and a 4A-compliant operations security audit system.

For the chart version and the matching JumpServer version, see [Chart.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/Chart.yaml).

## Prerequisites

| Dependency | Requirement |
| --- | --- |
| Kubernetes | 1.20+ |
| Helm | 3.0+ |
| Database | PostgreSQL (default) or MySQL, reachable from the cluster |
| Cache | Redis, or Redis Sentinel |
| Storage | A `ReadWriteMany` capable StorageClass, named `jumpserver-data` by default |
| Ingress | An Ingress controller (Ingress is enabled by default), or LoadBalancer / NodePort |

> The chart does not deploy the database, Redis, or the StorageClass. Prepare them beforehand. See the [chart documentation](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.md) for all storage, database, and Redis options.

## Quick start

### 1. Add the Helm repository

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

### 2. Prepare values.yaml

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

At a minimum, configure the following:

| Value | Description |
| --- | --- |
| `core.config.secretKey` | Encryption key; use a random string and keep it safe |
| `core.config.bootstrapToken` | Pre-shared token used for component registration |
| `externalDatabase.*` | Database connection settings |
| `externalRedis.*` or `externalSentinel.*` | Redis or Sentinel connection settings |
| `ingress.hosts` | The domain used to access JumpServer |
| `global.storageClass` | An RWX StorageClass available in the cluster |

Example:

```yaml
global:
  storageClass: jumpserver-data

core:
  config:
    secretKey: "REPLACE_WITH_RANDOM_STRING"
    bootstrapToken: "REPLACE_WITH_RANDOM_STRING"

externalDatabase:
  engine: postgresql
  host: jms-postgresql
  port: 5432
  user: jumpserver
  password: "REPLACE_WITH_DB_PASSWORD"
  database: jumpserver

externalRedis:
  host: jms-redis
  port: 6379
  password: "REPLACE_WITH_REDIS_PASSWORD"

ingress:
  enabled: true
  hosts:
    - jms.example.com
```

Generate random strings:

```bash
# secretKey
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 50
# bootstrapToken
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 24
```

### 3. Install

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

### 4. Check the status

```bash
kubectl -n jumpserver get pods
```

## Access

Ingress is enabled by default. Set `ingress.hosts` to your domain and open `http(s)://<domain>`.

Without Ingress, port-forward the web service temporarily:

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80
# Open http://127.0.0.1:8080 in your browser
```

Access the SSH terminal through Koko:

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
ssh -p 2222 admin@127.0.0.1
```

> The service names above assume the release name `jms-k8s`; actual names combine the release name and chart name. Use `kubectl -n jumpserver get svc` to confirm them.
>
> The initial administrator account is `admin`. Change its password after the first login.

## Configuration

- Full parameter reference: [charts/jumpserver/README.md](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.md)
- Default values: [charts/jumpserver/values.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/values.yaml)

You can also override values with `--set key=value[,key=value]`:

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml \
  --set ingress.enabled=true
```

## Upgrade

```bash
helm repo update
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver \
  -f values.yaml
```

Database migrations run automatically through a `pre-upgrade` Job. When upgrading from a v4 deployment with a standalone Lion component to v5, read [Upgrading from standalone Lion](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.md#upgrading-from-standalone-lion) first.

## Uninstall

```bash
helm uninstall jms-k8s -n jumpserver
```

PVCs carry `helm.sh/resource-policy: keep` by default and are retained after uninstalling. Once the data is no longer needed, delete them manually:

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## Documentation and support

- [JumpServer documentation](https://docs.jumpserver.org/)
- [JumpServer website](https://www.jumpserver.org/)
- [Issue tracker](https://github.com/jumpserver/helm-charts/issues)

## License

This project is licensed under [GPL-3.0](https://github.com/jumpserver/helm-charts/blob/main/LICENSE).

## Credits

The initial code was contributed by [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba). Original repository: [xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver).
