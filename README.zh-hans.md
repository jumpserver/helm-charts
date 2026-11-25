<h1 align="center">JumpServer Kubernetes Helm Chart</h1>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://img.shields.io/github/license/jumpserver/jumpserver" alt="License: GPLv3"></a>
  <a href="https://shields.io/github/downloads/jumpserver/helm-charts/total"><img src="https://shields.io/github/downloads/jumpserver/helm-charts/total" alt="Downloads"></a>
  <a href="https://github.com/jumpserver/helm-charts"><img src="https://img.shields.io/github/stars/jumpserver/helm-charts?color=%231890FF&style=flat-square" alt="Stars"></a>
  <a href="https://github.com/jumpserver/helm-charts/commits"><img src="https://img.shields.io/github/last-commit/jumpserver/helm-charts.svg" alt="Last commit"></a>
  <a href="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml"><img src="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml/badge.svg" alt="Release Charts"></a>
</p>

<p align="center">
  <a href="https://github.com/jumpserver/helm-charts/blob/main/README.md">English</a> · <strong>简体中文</strong> · <a href="https://github.com/jumpserver/helm-charts/blob/main/README.zh-hant.md">繁體中文</a>
</p>

本仓库提供 [JumpServer](https://www.jumpserver.org/) 的 Kubernetes Helm Chart。JumpServer 是全球首款完全开源的堡垒机（PAM），是符合 4A 规范的运维安全审计系统。

Chart 版本与对应的 JumpServer 版本请见 [Chart.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/Chart.yaml)。

## 环境要求

| 依赖 | 要求 |
| --- | --- |
| Kubernetes | 1.20+ |
| Helm | 3.0+ |
| 数据库 | PostgreSQL（默认）或 MySQL，需可被集群访问 |
| 缓存 | Redis，或 Redis Sentinel |
| 存储 | 支持 `ReadWriteMany` 的 StorageClass，默认名称为 `jumpserver-data` |
| 入口 | Ingress Controller（默认启用 Ingress），或 LoadBalancer / NodePort |

> Chart 不会部署数据库、Redis 和 StorageClass，请提前准备好。存储、数据库与 Redis 的详细参数见 [Chart 文档](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hans.md)。

## 快速开始

### 1. 添加 Helm 仓库

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

### 2. 准备 values.yaml

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

至少需要设置以下参数：

| 参数 | 说明 |
| --- | --- |
| `core.config.secretKey` | 加密密钥，请使用随机字符串并妥善保管 |
| `core.config.bootstrapToken` | 组件注册使用的预共享 Token |
| `externalDatabase.*` | 数据库连接信息 |
| `externalRedis.*` 或 `externalSentinel.*` | Redis 或 Sentinel 连接信息 |
| `ingress.hosts` | 访问域名 |
| `global.storageClass` | 集群中可用的 RWX StorageClass |

示例：

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

生成随机字符串：

```bash
# secretKey
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 50
# bootstrapToken
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 24
```

### 3. 安装

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

### 4. 检查状态

```bash
kubectl -n jumpserver get pods
```

## 访问

默认启用 Ingress，将 `ingress.hosts` 设置为你的域名后，通过 `http(s)://<域名>` 访问。

未配置 Ingress 时，可以临时转发 Web 服务：

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80
# 浏览器访问 http://127.0.0.1:8080
```

通过 Koko 访问 SSH 终端：

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
ssh -p 2222 admin@127.0.0.1
```

> 以上 Service 名称基于 release 名 `jms-k8s`，实际名称由 release 名和 Chart 名组成，可在 `kubectl -n jumpserver get svc` 中确认。
>
> 初始管理员账号为 `admin`，首次登录后请及时修改密码。

## 配置

- 完整参数说明：[charts/jumpserver/README.zh-hans.md](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hans.md)
- 默认参数文件：[charts/jumpserver/values.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/values.yaml)

安装时也可以通过 `--set key=value[,key=value]` 覆盖参数，例如：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml \
  --set ingress.enabled=true
```

## 升级

```bash
helm repo update
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver \
  -f values.yaml
```

升级时会自动执行数据库迁移（`pre-upgrade` Job）。从 v4 的独立 Lion 组件升级到 v5 时，请先阅读 [从独立 Lion 升级](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hans.md#从独立-lion-升级)。

## 卸载

```bash
helm uninstall jms-k8s -n jumpserver
```

PVC 默认带有 `helm.sh/resource-policy: keep`，卸载后会被保留。确认数据不再需要后，可手动删除：

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## 文档与支持

- [JumpServer 官方文档](https://docs.jumpserver.org/)
- [JumpServer 官网](https://www.jumpserver.org/)
- [问题反馈](https://github.com/jumpserver/helm-charts/issues)

## 许可证

本项目使用 [GPL-3.0](https://github.com/jumpserver/helm-charts/blob/main/LICENSE) 许可证。

## 致谢

本项目初始代码由 [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba) 贡献，原仓库地址：[xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver)。
