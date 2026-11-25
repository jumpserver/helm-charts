<h1 align="center">JumpServer Kubernetes Helm Chart</h1>

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://img.shields.io/github/license/jumpserver/jumpserver" alt="License: GPLv3"></a>
  <a href="https://shields.io/github/downloads/jumpserver/helm-charts/total"><img src="https://shields.io/github/downloads/jumpserver/helm-charts/total" alt="Downloads"></a>
  <a href="https://github.com/jumpserver/helm-charts"><img src="https://img.shields.io/github/stars/jumpserver/helm-charts?color=%231890FF&style=flat-square" alt="Stars"></a>
  <a href="https://github.com/jumpserver/helm-charts/commits"><img src="https://img.shields.io/github/last-commit/jumpserver/helm-charts.svg" alt="Last commit"></a>
  <a href="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml"><img src="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml/badge.svg" alt="Release Charts"></a>
</p>

<p align="center">
  <a href="https://github.com/jumpserver/helm-charts/blob/main/README.md">English</a> · <a href="https://github.com/jumpserver/helm-charts/blob/main/README.zh-hans.md">簡體中文</a> · <strong>繁體中文</strong>
</p>

本倉庫提供 [JumpServer](https://www.jumpserver.org/) 的 Kubernetes Helm Chart。JumpServer 是全球首款完全開源的堡壘機（PAM），是符合 4A 規範的運維安全審計系統。

Chart 版本與對應的 JumpServer 版本請見 [Chart.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/Chart.yaml)。

## 環境要求

| 依賴 | 要求 |
| --- | --- |
| Kubernetes | 1.20+ |
| Helm | 3.0+ |
| 資料庫 | PostgreSQL（預設）或 MySQL，需可被叢集存取 |
| 快取 | Redis，或 Redis Sentinel |
| 儲存 | 支援 `ReadWriteMany` 的 StorageClass，預設名稱為 `jumpserver-data` |
| 入口 | Ingress Controller（預設啟用 Ingress），或 LoadBalancer / NodePort |

> Chart 不會部署資料庫、Redis 和 StorageClass，請提前準備好。儲存、資料庫與 Redis 的詳細參數見 [Chart 說明文件](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hant.md)。

## 快速開始

### 1. 新增 Helm 倉庫

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

### 2. 準備 values.yaml

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

至少需要設定以下參數：

| 參數 | 說明 |
| --- | --- |
| `core.config.secretKey` | 加密金鑰，請使用隨機字串並妥善保管 |
| `core.config.bootstrapToken` | 元件註冊使用的預共享 Token |
| `externalDatabase.*` | 資料庫連線資訊 |
| `externalRedis.*` 或 `externalSentinel.*` | Redis 或 Sentinel 連線資訊 |
| `ingress.hosts` | 存取網域 |
| `global.storageClass` | 叢集中可用的 RWX StorageClass |

範例：

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

生成隨機字串：

```bash
# secretKey
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 50
# bootstrapToken
cat /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 24
```

### 3. 安裝

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

### 4. 檢查狀態

```bash
kubectl -n jumpserver get pods
```

## 存取

預設啟用 Ingress，將 `ingress.hosts` 設定為你的網域後，透過 `http(s)://<網域>` 存取。

未設定 Ingress 時，可以臨時轉送 Web 服務：

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80
# 瀏覽器存取 http://127.0.0.1:8080
```

透過 Koko 存取 SSH 終端機：

```bash
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
ssh -p 2222 admin@127.0.0.1
```

> 以上 Service 名稱基於 release 名稱 `jms-k8s`，實際名稱由 release 名稱和 Chart 名稱組成，可在 `kubectl -n jumpserver get svc` 中確認。
>
> 初始管理員帳號為 `admin`，首次登入後請及時修改密碼。

## 設定

- 完整參數說明：[charts/jumpserver/README.zh-hant.md](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hant.md)
- 預設參數檔案：[charts/jumpserver/values.yaml](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/values.yaml)

安裝時也可以透過 `--set key=value[,key=value]` 覆蓋參數，例如：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml \
  --set ingress.enabled=true
```

## 升級

```bash
helm repo update
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver \
  -f values.yaml
```

升級時會自動執行資料庫遷移（`pre-upgrade` Job）。從 v4 的獨立 Lion 元件升級到 v5 時，請先閱讀 [從獨立 Lion 升級](https://github.com/jumpserver/helm-charts/blob/main/charts/jumpserver/README.zh-hant.md#從獨立-lion-升級)。

## 解除安裝

```bash
helm uninstall jms-k8s -n jumpserver
```

PVC 預設帶有 `helm.sh/resource-policy: keep`，解除安裝後會被保留。確認資料不再需要後，可手動刪除：

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## 文件與支援

- [JumpServer 官方文件](https://docs.jumpserver.org/)
- [JumpServer 官網](https://www.jumpserver.org/)
- [問題回報](https://github.com/jumpserver/helm-charts/issues)

## 授權

本專案依 [GPL-3.0](https://github.com/jumpserver/helm-charts/blob/main/LICENSE) 授權條款授權。

## 致謝

本專案初始程式碼由 [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba) 貢獻，原倉庫位址：[xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver)。
