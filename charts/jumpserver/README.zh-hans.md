<h1 align="center">JumpServer Helm Chart</h1>

<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong> · <a href="./README.zh-hant.md">繁體中文</a>
</p>

[JumpServer](https://www.jumpserver.org/) 是全球首款完全开源的堡垒机（PAM），是符合 4A 规范的运维安全审计系统，使用 GPL-3.0 开源协议。

本 Chart 用于在 Kubernetes 上部署 JumpServer。数据库、Redis 与持久化存储需要提前准备，Chart 不会自动部署。

## 组件

| 组件 | 说明 | 默认部署 | 默认端口 | 默认持久化 |
| --- | --- | --- | --- | --- |
| `core` | 核心服务：API、认证、授权、审计与异步任务（celery） | 是 | `web: 8080` | 100Gi |
| `koko` | 通用协议连接与代理组件，并内置 guacd 提供图形会话 | 是 | `web: 5000`、`ssh: 2222` | 10Gi |
| `chen` | Web 数据库连接组件 | 是 | `web: 8082` | 10Gi |
| `web` | Web 网关与静态资源（nginx），Ingress 指向该服务 | 是 | `web: 80` | 1Gi |
| `magnus` | 企业版数据库协议代理 | 需 `xpack.enabled` | `web: 8088` 及数据库端口 | 10Gi |
| `razor` | 企业版 RDP 协议代理 | 需 `xpack.enabled` | `web: 8084`、`rdp: 3389` | 50Gi |
| `video` | 企业版会话录像转码 | 需 `xpack.enabled` | `web: 9000` | 50Gi |
| `facelive` | 企业版 FaceLive 组件 | 需 `xpack.enabled` 且 `facelive.enabled` | `web: 9999` | 10Gi |
| `nec` | 企业版 VNC 协议代理 | 需 `xpack.enabled` 且 `nec.enabled` | `web: 8085`、`vnc: 15900` | 10Gi |
| `xrdp` | 企业版 XRDP 组件 | 需 `xpack.enabled` | `rdp: 3390` | 50Gi |

关于版本类型：

- `xpack.enabled=false`（默认）：使用 `-ce` 镜像，仅部署 `core`、`koko`、`chen`、`web`。
- `xpack.enabled=true`：使用 `-ee` 镜像，并部署企业版组件，需要有效的企业版许可证。
- `magnus`、`razor`、`video`、`xrdp` 仅由 `xpack.enabled` 控制，组件自身的 `enabled` 当前不会生效；`facelive` 和 `nec` 还需各自 `enabled: true`。
- 从 v5 起，图形会话已合并到 Koko，不再部署独立 Lion。

## 环境要求

- Kubernetes 1.20+
- Helm 3.0+
- PostgreSQL（默认）或 MySQL，需可被集群访问
- Redis，或 Redis Sentinel
- 支持 `ReadWriteMany` 的 StorageClass，默认名称为 `jumpserver-data`
- 生产环境建议使用 Ingress Controller 或 LoadBalancer 暴露 Web 与 SSH 服务

## 安装

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

下载默认参数文件并按需修改：

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

至少需要设置以下参数，否则安装会失败或服务不可用：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `core.config.secretKey` | 加密密钥，必须设置；生产环境请使用随机字符串并妥善保管 | `""`（必填） |
| `core.config.bootstrapToken` | 组件注册使用的预共享 Token，必须设置 | `""`（必填） |
| `externalDatabase.host` | 数据库地址 | `localhost` |
| `externalDatabase.password` | 数据库密码 | `""` |
| `externalDatabase.database` | 数据库名称 | `jumpserver` |
| `externalRedis.host` | Redis 地址（未使用 Sentinel 时） | `localhost` |
| `global.storageClass` | 集群中可用的 RWX StorageClass | `""` |

安装：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

查看状态：

```bash
kubectl -n jumpserver get pods
```

## 访问

### Ingress

默认启用 Ingress，并将流量转发到 `web` 服务。将 `ingress.hosts` 修改为实际域名：

```yaml
ingress:
  enabled: true
  hosts:
    - jms.example.com
```

如需 TLS，配置 `ingress.tls`：

```yaml
ingress:
  tls:
    - secretName: jms-tls
      hosts:
        - jms.example.com
```

### 端口转发

未配置 Ingress 时，可以临时转发服务：

```bash
# Web
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80

# SSH（Koko）
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
```

> Service 名称由 release 名和 Chart 名组成，以上示例基于 release 名 `jms-k8s`，请通过 `kubectl -n jumpserver get svc` 确认。

初始管理员账号为 `admin`，首次登录后请及时修改密码。

### 关于 NodePort

当前模板在 `service.type=NodePort` 时，会对渲染 `nodePort` 的端口直接使用 Service 端口作为 `nodePort`（如 Web 的 `80`、Koko SSH 的 `2222`）。这些默认端口不在 Kubernetes 默认 NodePort 范围 `30000-32767` 内，直接启用会安装失败。如需 NodePort，请同时把端口调整到该范围，并确认容器实际监听端口与 Service 端口一致；生产环境推荐使用 Ingress 或 LoadBalancer。

## 参数

### 全局参数

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `nameOverride` | 覆盖 Chart 名称 | `""` |
| `fullnameOverride` | 覆盖资源全名 | `""` |
| `global.imageRegistry` | 镜像仓库地址，设置后覆盖各组件的 `image.registry` | `docker.io` |
| `global.imageOwner` | 镜像仓库命名空间 | `jumpserver` |
| `global.imagePullSecrets` | 私有仓库拉取凭据列表 | `[]` |
| `global.storageClass` | 全局 StorageClass，设置后覆盖各组件的 `persistence.storageClassName` | `""` |

### 数据库

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `externalDatabase.engine` | 数据库类型，支持 `postgresql`、`mysql` | `postgresql` |
| `externalDatabase.host` | 数据库地址 | `localhost` |
| `externalDatabase.port` | 数据库端口 | `5432` |
| `externalDatabase.user` | 数据库用户名 | `postgres` |
| `externalDatabase.password` | 数据库密码 | `""` |
| `externalDatabase.database` | 数据库名称 | `jumpserver` |

> 使用 MySQL 时，请同时将 `externalDatabase.port` 改为 `3306`。

### Redis 与 Sentinel

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `externalRedis.host` | Redis 地址 | `localhost` |
| `externalRedis.port` | Redis 端口 | `6379` |
| `externalRedis.password` | Redis 密码 | `""` |
| `externalSentinel.hosts` | Sentinel 地址池，格式为 `mymaster/host1:26379,host2:26379` | 空 |
| `externalSentinel.password` | Sentinel 认证密码 | 空 |
| `externalSentinel.socketTimeout` | Sentinel 超时时间（秒） | `5` |

> 配置 `externalSentinel.hosts` 后将优先使用 Sentinel，`externalRedis` 不再生效。
>
> Sentinel 密码与 Redis 密码需要分别配置。

### Ingress

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `ingress.enabled` | 是否启用 Ingress | `true` |
| `ingress.annotations` | Ingress 注解，默认包含 nginx、请求体大小与 WebSocket 配置 | 见 `values.yaml` |
| `ingress.hosts` | 访问域名列表 | `["test.jumpserver.org"]` |
| `ingress.tls` | TLS 配置 | `[]` |

> Ingress 的 backend 为 `web` 服务，因此需要保持 `web.enabled=true`。

### ServiceAccount

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `serviceAccount.create` | 是否创建 ServiceAccount | `false` |
| `serviceAccount.name` | 使用的 ServiceAccount 名称 | `""` |

### 组件通用参数

以下参数对大多数组件适用，将 `<component>` 替换为组件名即可；个别例外已在对应行说明。

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `<component>.enabled` | 是否部署该组件（`magnus`、`razor`、`video`、`xrdp` 除外） | `true` |
| `<component>.replicaCount` | 副本数 | `1` |
| `<component>.labels` | 附加到资源的标签 | 见 `values.yaml` |
| `<component>.image.registry` | 镜像仓库，会被 `global.imageRegistry` 覆盖（后者默认 `docker.io`） | 见 `values.yaml` |
| `<component>.image.pullPolicy` | 镜像拉取策略 | `IfNotPresent` |
| `<component>.config.log.level` | 日志级别（`web` 没有 `config` 配置块） | `ERROR` |
| `<component>.env` | 附加环境变量，使用 `KEY: value` 键值对 | 见 `values.yaml` |
| `<component>.service.type` | Service 类型，支持 `ClusterIP`、`LoadBalancer`、`NodePort` | `ClusterIP` |
| `<component>.service.<port>` | 组件端口，详见上方组件表 | 见 `values.yaml` |
| `<component>.persistence.storageClassName` | 持久化 StorageClass | `jumpserver-data` |
| `<component>.persistence.accessModes` | 访问模式 | `ReadWriteMany` |
| `<component>.persistence.size` | 存储容量 | 见上方组件表 |
| `<component>.persistence.existingClaim` | 使用已有 PVC；设置后不再创建 PVC | `""` |
| `<component>.persistence.subPath` | 数据卷子路径 | `""` |
| `<component>.persistence.annotations` | PVC 注解，默认保留 PVC | `helm.sh/resource-policy: keep` |
| `<component>.persistence.finalizers` | PVC finalizers | `kubernetes.io/pvc-protection` |
| `<component>.resources` | CPU/内存 requests 与 limits | `{}` |
| `<component>.podSecurityContext` | Pod 安全上下文 | `{}` |
| `<component>.securityContext` | 容器安全上下文；`koko` 默认开启 `privileged` | 见 `values.yaml` |
| `<component>.livenessProbe` | 存活探针 | 见 `values.yaml` |
| `<component>.readinessProbe` | 就绪探针；默认仅 `chen` 在 `values.yaml` 中配置，`facelive` 和 `nec` 模板不会渲染该参数 | 见 `values.yaml` |
| `<component>.nodeSelector` | 节点选择器 | `{}` |
| `<component>.tolerations` | 污点容忍 | `[]` |
| `<component>.affinity` | 亲和性配置 | `{}` |
| `<component>.volumeMounts` | 附加 volumeMounts | `[]` |
| `<component>.volumes` | 附加 volumes | `[]` |

环境变量使用映射（map）格式，例如：

```yaml
core:
  env:
    DOMAINS: "jms.example.com"
    SESSION_EXPIRE_AT_BROWSER_CLOSE: true
```

### 组件专属参数

`core`：

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `core.config.secretKey` | 加密密钥，必填 | `""` |
| `core.config.bootstrapToken` | 预共享 Token，必填 | `""` |
| `core.config.debug` | 是否开启调试模式 | `false` |
| `core.config.log.level` | 日志级别 | `ERROR` |

`koko`：

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `koko.service.web.port` | Koko Web/图形会话端口 | `5000` |
| `koko.service.ssh.port` | Koko SSH 端口 | `2222` |
| `koko.persistence.size` | Koko 数据卷容量 | `10Gi` |

图形会话通过 `/koko/lion/` 访问，使用 `koko.service.web.port` 和 Koko 数据卷；guacd 在 Koko 容器内运行，无需单独部署。

`web`：

| 参数 | 描述 | 默认值 |
| --- | --- | --- |
| `web.env.CLIENT_MAX_BODY_SIZE` | nginx 客户端请求体大小限制 | `4096m` |
| `web.env.USE_LB` | 是否位于负载均衡之后；`1` 时使用 `$remote_addr` 作为客户端 IP | `0` |
| `web.persistence.size` | Web 日志卷容量 | `1Gi` |

> `web` 会挂载 `core` 的数据卷（`core.persistence`），请保持 `core.enabled=true`。

`chen`、`magnus`、`razor`、`video`、`facelive`、`nec`、`xrdp` 的 `env` 同样使用键值对格式，可参考 [JumpServer 环境变量文档](https://docs.fit2cloud.com/jumpserver/manual/ops/env/)。

## 从独立 Lion 升级

v5 起图形会话已合并到 Koko，不再部署独立 Lion。请使用包含图形会话和 guacd 的 Koko 镜像，并与 Core、Web 的版本保持一致。图形会话通过 `/koko/lion/` 访问，使用 `koko.service.web.port` 和 Koko 数据卷；guacd 在 Koko 容器内运行，无需单独部署。

从独立 Lion 升级时：

- 将原 `lion.env` 中需要保留的图形会话配置移到 `koko.env`，例如 `JUMPSERVER_ENABLE_FONT_SMOOTHING`。副本数、资源和持久化容量统一由 `koko` 配置，需要按合并后的负载调整。
- `lion.*` 参数不再生效；关闭 `koko.enabled` 会同时关闭终端和图形会话。
- 新的图形会话录像和文件写入 Koko 数据卷。旧 Lion PVC 默认带有 `helm.sh/resource-policy: keep`，升级后保留，但不会自动挂载或迁移到 Koko；升级前应处理未上传的录像及需要保留的文件。

## 示例

`values.yaml`：

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

安装：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

也可以直接使用 `--set` 覆盖参数：

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

## 卸载

```bash
helm uninstall jms-k8s -n jumpserver
```

PVC 默认带有 `helm.sh/resource-policy: keep`，卸载后会被保留。确认数据不再需要后，可手动删除：

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## 鸣谢

本项目初始代码由 [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba) 贡献，原仓库地址：[xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver)。
