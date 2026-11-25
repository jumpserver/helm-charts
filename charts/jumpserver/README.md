<h1 align="center">JumpServer Helm Chart</h1>

<p align="center">
  <strong>English</strong> · <a href="./README.zh-hans.md">简体中文</a> · <a href="./README.zh-hant.md">繁體中文</a>
</p>

[JumpServer](https://www.jumpserver.org/) is the world's first fully open-source bastion host (PAM) and a 4A-compliant operations security audit system, licensed under GPL-3.0.

This chart deploys JumpServer on Kubernetes. The database, Redis, and persistent storage must be prepared in advance; the chart does not deploy them.

## Components

| Component | Description | Deployed by default | Default ports | Default persistence |
| --- | --- | --- | --- | --- |
| `core` | Core service: API, authentication, authorization, auditing and async tasks (celery) | Yes | `web: 8080` | 100Gi |
| `koko` | General-purpose protocol connector and proxy, with built-in guacd for graphical sessions | Yes | `web: 5000`, `ssh: 2222` | 10Gi |
| `chen` | Web-based database connector | Yes | `web: 8082` | 10Gi |
| `web` | Web gateway and static assets (nginx); Ingress targets this service | Yes | `web: 80` | 1Gi |
| `magnus` | Enterprise database protocol proxy | Requires `xpack.enabled` | `web: 8088` plus database ports | 10Gi |
| `razor` | Enterprise RDP protocol proxy | Requires `xpack.enabled` | `web: 8084`, `rdp: 3389` | 50Gi |
| `video` | Enterprise session recording transcoder | Requires `xpack.enabled` | `web: 9000` | 50Gi |
| `facelive` | Enterprise FaceLive component | Requires `xpack.enabled` and `facelive.enabled` | `web: 9999` | 10Gi |
| `nec` | Enterprise VNC protocol proxy | Requires `xpack.enabled` and `nec.enabled` | `web: 8085`, `vnc: 15900` | 10Gi |
| `xrdp` | Enterprise XRDP component | Requires `xpack.enabled` | `rdp: 3390` | 50Gi |

About editions:

- `xpack.enabled=false` (default): uses `-ce` images and deploys only `core`, `koko`, `chen`, and `web`.
- `xpack.enabled=true`: uses `-ee` images and deploys the enterprise components; a valid enterprise license is required.
- `magnus`, `razor`, `video`, and `xrdp` are controlled only by `xpack.enabled`; their own `enabled` flags currently have no effect. `facelive` and `nec` additionally require their own `enabled: true`.
- Since v5, graphical sessions are handled by Koko and standalone Lion is no longer deployed.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.0+
- PostgreSQL (default) or MySQL, reachable from the cluster
- Redis, or Redis Sentinel
- A `ReadWriteMany` capable StorageClass, named `jumpserver-data` by default
- An Ingress controller or LoadBalancer for exposing the web and SSH services in production

## Installation

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

Download the default values file and adjust it:

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

The following values must be configured, otherwise installation fails or the services will not work:

| Value | Description | Default |
| --- | --- | --- |
| `core.config.secretKey` | Encryption key; required. Use a random string in production and keep it safe | `""` (required) |
| `core.config.bootstrapToken` | Pre-shared token for component registration; required | `""` (required) |
| `externalDatabase.host` | Database host | `localhost` |
| `externalDatabase.password` | Database password | `""` |
| `externalDatabase.database` | Database name | `jumpserver` |
| `externalRedis.host` | Redis host (when not using Sentinel) | `localhost` |
| `global.storageClass` | An RWX StorageClass available in the cluster | `""` |

Install:

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

Check the status:

```bash
kubectl -n jumpserver get pods
```

## Access

### Ingress

Ingress is enabled by default and forwards traffic to the `web` service. Set `ingress.hosts` to your domain:

```yaml
ingress:
  enabled: true
  hosts:
    - jms.example.com
```

To enable TLS, configure `ingress.tls`:

```yaml
ingress:
  tls:
    - secretName: jms-tls
      hosts:
        - jms.example.com
```

### Port forwarding

Without Ingress, port-forward the services temporarily:

```bash
# Web
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80

# SSH (Koko)
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
```

> Service names combine the release name and the chart name. The examples above assume the release name `jms-k8s`; confirm the actual names with `kubectl -n jumpserver get svc`.

The initial administrator account is `admin`. Change its password after the first login.

### About NodePort

With `service.type=NodePort`, the chart uses the Service port directly as `nodePort` for the ports that render one (for example, `80` for web and `2222` for Koko SSH). These defaults are outside the default Kubernetes NodePort range `30000-32767`, so enabling NodePort with the defaults fails. If you need NodePort, adjust the ports into that range and make sure the container's actual listening port matches the Service port. Ingress or LoadBalancer is recommended for production.

## Parameters

### Global parameters

| Value | Description | Default |
| --- | --- | --- |
| `nameOverride` | Overrides the chart name | `""` |
| `fullnameOverride` | Overrides the full resource name | `""` |
| `global.imageRegistry` | Image registry; overrides each component's `image.registry` | `docker.io` |
| `global.imageOwner` | Image registry namespace | `jumpserver` |
| `global.imagePullSecrets` | Image pull secrets for a private registry | `[]` |
| `global.storageClass` | Global StorageClass; overrides each component's `persistence.storageClassName` | `""` |

### Database

| Value | Description | Default |
| --- | --- | --- |
| `externalDatabase.engine` | Database type: `postgresql` or `mysql` | `postgresql` |
| `externalDatabase.host` | Database host | `localhost` |
| `externalDatabase.port` | Database port | `5432` |
| `externalDatabase.user` | Database user | `postgres` |
| `externalDatabase.password` | Database password | `""` |
| `externalDatabase.database` | Database name | `jumpserver` |

> When using MySQL, also change `externalDatabase.port` to `3306`.

### Redis and Sentinel

| Value | Description | Default |
| --- | --- | --- |
| `externalRedis.host` | Redis host | `localhost` |
| `externalRedis.port` | Redis port | `6379` |
| `externalRedis.password` | Redis password | `""` |
| `externalSentinel.hosts` | Sentinel host pool, in the form `mymaster/host1:26379,host2:26379` | empty |
| `externalSentinel.password` | Sentinel authentication password | empty |
| `externalSentinel.socketTimeout` | Sentinel timeout in seconds | `5` |

> When `externalSentinel.hosts` is set, Sentinel takes precedence and `externalRedis` is ignored.
>
> The Sentinel password and the Redis password are configured separately.

### Ingress

| Value | Description | Default |
| --- | --- | --- |
| `ingress.enabled` | Whether to create an Ingress | `true` |
| `ingress.annotations` | Ingress annotations; includes nginx, body size, and WebSocket settings by default | see `values.yaml` |
| `ingress.hosts` | Access domains | `["test.jumpserver.org"]` |
| `ingress.tls` | TLS configuration | `[]` |

> The Ingress backend is the `web` service, so keep `web.enabled=true`.

### ServiceAccount

| Value | Description | Default |
| --- | --- | --- |
| `serviceAccount.create` | Whether to create a ServiceAccount | `false` |
| `serviceAccount.name` | ServiceAccount name to use | `""` |

### Common component parameters

The following parameters apply to most components. Replace `<component>` with the component name; exceptions are noted per row.

| Value | Description | Default |
| --- | --- | --- |
| `<component>.enabled` | Whether to deploy the component (except `magnus`, `razor`, `video`, `xrdp`) | `true` |
| `<component>.replicaCount` | Number of replicas | `1` |
| `<component>.labels` | Additional resource labels | see `values.yaml` |
| `<component>.image.registry` | Image registry; overridden by `global.imageRegistry` (`docker.io` by default) | see `values.yaml` |
| `<component>.image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `<component>.config.log.level` | Log level (`web` has no `config` block) | `ERROR` |
| `<component>.env` | Additional environment variables as a `KEY: value` map | see `values.yaml` |
| `<component>.service.type` | Service type: `ClusterIP`, `LoadBalancer`, or `NodePort` | `ClusterIP` |
| `<component>.service.<port>` | Component ports; see the components table above | see `values.yaml` |
| `<component>.persistence.storageClassName` | StorageClass for persistence | `jumpserver-data` |
| `<component>.persistence.accessModes` | Access modes | `ReadWriteMany` |
| `<component>.persistence.size` | Storage size | see the components table above |
| `<component>.persistence.existingClaim` | Use an existing PVC; no PVC is created when set | `""` |
| `<component>.persistence.subPath` | Sub-path within the volume | `""` |
| `<component>.persistence.annotations` | PVC annotations; the PVC is retained by default | `helm.sh/resource-policy: keep` |
| `<component>.persistence.finalizers` | PVC finalizers | `kubernetes.io/pvc-protection` |
| `<component>.resources` | CPU/memory requests and limits | `{}` |
| `<component>.podSecurityContext` | Pod security context | `{}` |
| `<component>.securityContext` | Container security context; `koko` enables `privileged` by default | see `values.yaml` |
| `<component>.livenessProbe` | Liveness probe | see `values.yaml` |
| `<component>.readinessProbe` | Readiness probe; only `chen` configures it in `values.yaml` by default; `facelive` and `nec` do not render it | see `values.yaml` |
| `<component>.nodeSelector` | Node selector | `{}` |
| `<component>.tolerations` | Tolerations | `[]` |
| `<component>.affinity` | Affinity rules | `{}` |
| `<component>.volumeMounts` | Additional volumeMounts | `[]` |
| `<component>.volumes` | Additional volumes | `[]` |

Environment variables use map format:

```yaml
core:
  env:
    DOMAINS: "jms.example.com"
    SESSION_EXPIRE_AT_BROWSER_CLOSE: true
```

### Component-specific parameters

`core`:

| Value | Description | Default |
| --- | --- | --- |
| `core.config.secretKey` | Encryption key; required | `""` |
| `core.config.bootstrapToken` | Pre-shared token; required | `""` |
| `core.config.debug` | Enable debug mode | `false` |
| `core.config.log.level` | Log level | `ERROR` |

`koko`:

| Value | Description | Default |
| --- | --- | --- |
| `koko.service.web.port` | Koko web/graphical session port | `5000` |
| `koko.service.ssh.port` | Koko SSH port | `2222` |
| `koko.persistence.size` | Koko data volume size | `10Gi` |

Graphical sessions are accessed through `/koko/lion/` using `koko.service.web.port` and the Koko data volume. guacd runs inside the Koko container and does not need to be deployed separately.

`web`:

| Value | Description | Default |
| --- | --- | --- |
| `web.env.CLIENT_MAX_BODY_SIZE` | nginx client request body size limit | `4096m` |
| `web.env.USE_LB` | Whether the service sits behind a load balancer; `1` uses `$remote_addr` as the client IP | `0` |
| `web.persistence.size` | Web log volume size | `1Gi` |

> `web` mounts the `core` data volume (`core.persistence`), so keep `core.enabled=true`.

The `env` values of `chen`, `magnus`, `razor`, `video`, `facelive`, `nec`, and `xrdp` also use map format. See the [JumpServer environment variable documentation](https://docs.fit2cloud.com/jumpserver/manual/ops/env/).

## Upgrading from standalone Lion

Since v5, graphical sessions are handled by Koko and standalone Lion is no longer deployed. Use a Koko image that includes graphical sessions and guacd, and keep its version aligned with Core and Web. Graphical sessions are accessed through `/koko/lion/` using `koko.service.web.port` and the Koko data volume. guacd runs inside the Koko container and does not need to be deployed separately.

When upgrading from standalone Lion:

- Move the graphical session settings that must be preserved from `lion.env` to `koko.env`, for example `JUMPSERVER_ENABLE_FONT_SMOOTHING`. Replicas, resources, and persistence are now configured under `koko`; adjust them for the combined workload.
- `lion.*` values no longer take effect. Disabling `koko.enabled` disables both terminal and graphical sessions.
- New graphical session recordings and files are written to the Koko data volume. Old Lion PVCs carry `helm.sh/resource-policy: keep` by default and are retained after the upgrade, but they are not mounted or migrated to Koko automatically. Handle unuploaded recordings and files that must be kept before upgrading.

## Example

`values.yaml`:

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

Install:

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

You can also override values with `--set`:

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  --set core.config.secretKey="REPLACE_WITH_RANDOM_STRING" \
  --set core.config.bootstrapToken="REPLACE_WITH_RANDOM_STRING" \
  --set global.storageClass=jumpserver-data \
  --set externalDatabase.engine=postgresql \
  --set externalDatabase.host=jms-postgresql \
  --set externalDatabase.port=5432 \
  --set externalDatabase.user=jumpserver \
  --set externalDatabase.password="REPLACE_WITH_DB_PASSWORD" \
  --set externalDatabase.database=jumpserver \
  --set externalRedis.host=jms-redis \
  --set externalRedis.port=6379 \
  --set externalRedis.password="REPLACE_WITH_REDIS_PASSWORD" \
  --set ingress.enabled=true \
  --set 'ingress.hosts[0]=jms.example.com'
```

## Uninstall

```bash
helm uninstall jms-k8s -n jumpserver
```

PVCs carry `helm.sh/resource-policy: keep` by default and are retained after uninstalling. Once the data is no longer needed, delete them manually:

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## Credits

The initial code was contributed by [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba). Original repository: [xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver).
