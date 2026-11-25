<h1 align="center">JumpServer Helm Chart</h1>

<p align="center">
  <a href="./README.md">English</a> · <a href="./README.zh-hans.md">簡體中文</a> · <strong>繁體中文</strong>
</p>

[JumpServer](https://www.jumpserver.org/) 是全球首款完全開源的堡壘機（PAM），是符合 4A 規範的運維安全審計系統，使用 GPL-3.0 開源協議。

本 Chart 用於在 Kubernetes 上部署 JumpServer。資料庫、Redis 與持久化儲存需要提前準備，Chart 不會自動部署。

## 元件

| 元件 | 說明 | 預設部署 | 預設連接埠 | 預設持久化 |
| --- | --- | --- | --- | --- |
| `core` | 核心服務：API、認證、授權、審計與非同步任務（celery） | 是 | `web: 8080` | 100Gi |
| `koko` | 通用協議連線與代理元件，並內建 guacd 提供圖形工作階段 | 是 | `web: 5000`、`ssh: 2222` | 10Gi |
| `chen` | Web 資料庫連線元件 | 是 | `web: 8082` | 10Gi |
| `web` | Web 閘道器與靜態資源（nginx），Ingress 指向該服務 | 是 | `web: 80` | 1Gi |
| `magnus` | 企業版資料庫協議代理 | 需 `xpack.enabled` | `web: 8088` 及資料庫連接埠 | 10Gi |
| `razor` | 企業版 RDP 協議代理 | 需 `xpack.enabled` | `web: 8084`、`rdp: 3389` | 50Gi |
| `video` | 企業版工作階段錄影轉碼 | 需 `xpack.enabled` | `web: 9000` | 50Gi |
| `facelive` | 企業版 FaceLive 元件 | 需 `xpack.enabled` 且 `facelive.enabled` | `web: 9999` | 10Gi |
| `nec` | 企業版 VNC 協議代理 | 需 `xpack.enabled` 且 `nec.enabled` | `web: 8085`、`vnc: 15900` | 10Gi |
| `xrdp` | 企業版 XRDP 元件 | 需 `xpack.enabled` | `rdp: 3390` | 50Gi |

關於版本類型：

- `xpack.enabled=false`（預設）：使用 `-ce` 映像，僅部署 `core`、`koko`、`chen`、`web`。
- `xpack.enabled=true`：使用 `-ee` 映像，並部署企業版元件，需要有效的企業版授權。
- `magnus`、`razor`、`video`、`xrdp` 僅由 `xpack.enabled` 控制，元件自身的 `enabled` 目前不會生效；`facelive` 和 `nec` 還需各自 `enabled: true`。
- 從 v5 起，圖形工作階段已合併到 Koko，不再部署獨立 Lion。

## 環境要求

- Kubernetes 1.20+
- Helm 3.0+
- PostgreSQL（預設）或 MySQL，需可被叢集存取
- Redis，或 Redis Sentinel
- 支援 `ReadWriteMany` 的 StorageClass，預設名稱為 `jumpserver-data`
- 生產環境建議使用 Ingress Controller 或 LoadBalancer 暴露 Web 與 SSH 服務

## 安裝

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo update
helm search repo jumpserver
```

下載預設參數檔案並按需修改：

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
```

至少需要設定以下參數，否則安裝會失敗或服務不可用：

| 參數 | 說明 | 預設值 |
| --- | --- | --- |
| `core.config.secretKey` | 加密金鑰，必須設定；生產環境請使用隨機字串並妥善保管 | `""`（必填） |
| `core.config.bootstrapToken` | 元件註冊使用的預共享 Token，必須設定 | `""`（必填） |
| `externalDatabase.host` | 資料庫位址 | `localhost` |
| `externalDatabase.password` | 資料庫密碼 | `""` |
| `externalDatabase.database` | 資料庫名稱 | `jumpserver` |
| `externalRedis.host` | Redis 位址（未使用 Sentinel 時） | `localhost` |
| `global.storageClass` | 叢集中可用的 RWX StorageClass | `""` |

安裝：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

檢視狀態：

```bash
kubectl -n jumpserver get pods
```

## 存取

### Ingress

預設啟用 Ingress，並將流量轉送到 `web` 服務。將 `ingress.hosts` 修改為實際網域：

```yaml
ingress:
  enabled: true
  hosts:
    - jms.example.com
```

如需 TLS，設定 `ingress.tls`：

```yaml
ingress:
  tls:
    - secretName: jms-tls
      hosts:
        - jms.example.com
```

### 連接埠轉送

未設定 Ingress 時，可以臨時轉送服務：

```bash
# Web
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-web 8080:80

# SSH（Koko）
kubectl -n jumpserver port-forward svc/jms-k8s-jumpserver-jms-koko 2222:2222
```

> Service 名稱由 release 名稱和 Chart 名稱組成，以上範例基於 release 名稱 `jms-k8s`，請透過 `kubectl -n jumpserver get svc` 確認。

初始管理員帳號為 `admin`，首次登入後請及時修改密碼。

### 關於 NodePort

目前模板在 `service.type=NodePort` 時，會對渲染 `nodePort` 的連接埠直接使用 Service 連接埠作為 `nodePort`（如 Web 的 `80`、Koko SSH 的 `2222`）。這些預設連接埠不在 Kubernetes 預設 NodePort 範圍 `30000-32767` 內，直接啟用會安裝失敗。如需 NodePort，請同時把連接埠調整到該範圍，並確認容器實際監聽連接埠與 Service 連接埠一致；生產環境推薦使用 Ingress 或 LoadBalancer。

## 參數

### 全域參數

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `nameOverride` | 覆蓋 Chart 名稱 | `""` |
| `fullnameOverride` | 覆蓋資源全名 | `""` |
| `global.imageRegistry` | 映像倉庫位址，設定後覆蓋各元件的 `image.registry` | `docker.io` |
| `global.imageOwner` | 映像倉庫命名空間 | `jumpserver` |
| `global.imagePullSecrets` | 私有倉庫拉取憑證列表 | `[]` |
| `global.storageClass` | 全域 StorageClass，設定後覆蓋各元件的 `persistence.storageClassName` | `""` |

### 資料庫

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `externalDatabase.engine` | 資料庫類型，支援 `postgresql`、`mysql` | `postgresql` |
| `externalDatabase.host` | 資料庫位址 | `localhost` |
| `externalDatabase.port` | 資料庫連接埠 | `5432` |
| `externalDatabase.user` | 資料庫使用者名稱 | `postgres` |
| `externalDatabase.password` | 資料庫密碼 | `""` |
| `externalDatabase.database` | 資料庫名稱 | `jumpserver` |

> 使用 MySQL 時，請同時將 `externalDatabase.port` 改為 `3306`。

### Redis 與 Sentinel

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `externalRedis.host` | Redis 位址 | `localhost` |
| `externalRedis.port` | Redis 連接埠 | `6379` |
| `externalRedis.password` | Redis 密碼 | `""` |
| `externalSentinel.hosts` | Sentinel 位址池，格式為 `mymaster/host1:26379,host2:26379` | 空 |
| `externalSentinel.password` | Sentinel 認證密碼 | 空 |
| `externalSentinel.socketTimeout` | Sentinel 逾時時間（秒） | `5` |

> 設定 `externalSentinel.hosts` 後將優先使用 Sentinel，`externalRedis` 不再生效。
>
> Sentinel 密碼與 Redis 密碼需要分別設定。

### Ingress

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `ingress.enabled` | 是否啟用 Ingress | `true` |
| `ingress.annotations` | Ingress 註解，預設包含 nginx、請求體大小與 WebSocket 設定 | 見 `values.yaml` |
| `ingress.hosts` | 存取網域列表 | `["test.jumpserver.org"]` |
| `ingress.tls` | TLS 設定 | `[]` |

> Ingress 的 backend 為 `web` 服務，因此需要保持 `web.enabled=true`。

### ServiceAccount

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `serviceAccount.create` | 是否建立 ServiceAccount | `false` |
| `serviceAccount.name` | 使用的 ServiceAccount 名稱 | `""` |

### 元件通用參數

以下參數對大多數元件適用，將 `<component>` 替換為元件名稱即可；個別例外已在對應行說明。

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `<component>.enabled` | 是否部署該元件（`magnus`、`razor`、`video`、`xrdp` 除外） | `true` |
| `<component>.replicaCount` | 副本數 | `1` |
| `<component>.labels` | 附加到資源的標籤 | 見 `values.yaml` |
| `<component>.image.registry` | 映像倉庫，會被 `global.imageRegistry` 覆蓋（後者預設 `docker.io`） | 見 `values.yaml` |
| `<component>.image.pullPolicy` | 映像拉取策略 | `IfNotPresent` |
| `<component>.config.log.level` | 日誌等級（`web` 沒有 `config` 設定塊） | `ERROR` |
| `<component>.env` | 附加環境變數，使用 `KEY: value` 鍵值對 | 見 `values.yaml` |
| `<component>.service.type` | Service 類型，支援 `ClusterIP`、`LoadBalancer`、`NodePort` | `ClusterIP` |
| `<component>.service.<port>` | 元件連接埠，詳見上方元件表 | 見 `values.yaml` |
| `<component>.persistence.storageClassName` | 持久化 StorageClass | `jumpserver-data` |
| `<component>.persistence.accessModes` | 存取模式 | `ReadWriteMany` |
| `<component>.persistence.size` | 儲存容量 | 見上方元件表 |
| `<component>.persistence.existingClaim` | 使用已有 PVC；設定後不再建立 PVC | `""` |
| `<component>.persistence.subPath` | 資料卷內子路徑 | `""` |
| `<component>.persistence.annotations` | PVC 註解，預設保留 PVC | `helm.sh/resource-policy: keep` |
| `<component>.persistence.finalizers` | PVC finalizers | `kubernetes.io/pvc-protection` |
| `<component>.resources` | CPU/記憶體 requests 與 limits | `{}` |
| `<component>.podSecurityContext` | Pod 安全上下文 | `{}` |
| `<component>.securityContext` | 容器安全上下文；`koko` 預設開啟 `privileged` | 見 `values.yaml` |
| `<component>.livenessProbe` | 存活探針 | 見 `values.yaml` |
| `<component>.readinessProbe` | 就緒探針；預設僅 `chen` 在 `values.yaml` 中設定，`facelive` 和 `nec` 模板不會渲染該參數 | 見 `values.yaml` |
| `<component>.nodeSelector` | 節點選擇器 | `{}` |
| `<component>.tolerations` | 污點容忍 | `[]` |
| `<component>.affinity` | 親和性設定 | `{}` |
| `<component>.volumeMounts` | 附加 volumeMounts | `[]` |
| `<component>.volumes` | 附加 volumes | `[]` |

環境變數使用對映（map）格式，例如：

```yaml
core:
  env:
    DOMAINS: "jms.example.com"
    SESSION_EXPIRE_AT_BROWSER_CLOSE: true
```

### 元件專屬參數

`core`：

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `core.config.secretKey` | 加密金鑰，必填 | `""` |
| `core.config.bootstrapToken` | 預共享 Token，必填 | `""` |
| `core.config.debug` | 是否開啟除錯模式 | `false` |
| `core.config.log.level` | 日誌等級 | `ERROR` |

`koko`：

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `koko.service.web.port` | Koko Web/圖形工作階段連接埠 | `5000` |
| `koko.service.ssh.port` | Koko SSH 連接埠 | `2222` |
| `koko.persistence.size` | Koko 資料卷容量 | `10Gi` |

圖形工作階段透過 `/koko/lion/` 存取，使用 `koko.service.web.port` 和 Koko 資料卷；guacd 在 Koko 容器內執行，無需單獨部署。

`web`：

| 參數 | 描述 | 預設值 |
| --- | --- | --- |
| `web.env.CLIENT_MAX_BODY_SIZE` | nginx 客戶端請求體大小限制 | `4096m` |
| `web.env.USE_LB` | 是否位於負載平衡之後；`1` 時使用 `$remote_addr` 作為客戶端 IP | `0` |
| `web.persistence.size` | Web 日誌卷容量 | `1Gi` |

> `web` 會掛載 `core` 的資料卷（`core.persistence`），請保持 `core.enabled=true`。

`chen`、`magnus`、`razor`、`video`、`facelive`、`nec`、`xrdp` 的 `env` 同樣使用鍵值對格式，可參考 [JumpServer 環境變數說明文件](https://docs.fit2cloud.com/jumpserver/manual/ops/env/)。

## 從獨立 Lion 升級

v5 起圖形工作階段已合併到 Koko，不再部署獨立 Lion。請使用包含圖形工作階段和 guacd 的 Koko 映像，並與 Core、Web 的版本保持一致。圖形工作階段透過 `/koko/lion/` 存取，使用 `koko.service.web.port` 和 Koko 資料卷；guacd 在 Koko 容器內執行，無需單獨部署。

從獨立 Lion 升級時：

- 將原 `lion.env` 中需要保留的圖形工作階段設定移到 `koko.env`，例如 `JUMPSERVER_ENABLE_FONT_SMOOTHING`。副本數、資源和持久化容量統一由 `koko` 設定，需要按合併後的負載調整。
- `lion.*` 參數不再生效；關閉 `koko.enabled` 會同時關閉終端機和圖形工作階段。
- 新的圖形工作階段錄影和檔案寫入 Koko 資料卷。舊 Lion PVC 預設帶有 `helm.sh/resource-policy: keep`，升級後保留，但不會自動掛載或遷移到 Koko；升級前應處理未上傳的錄影及需要保留的檔案。

## 範例

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

安裝：

```bash
helm upgrade --install jms-k8s jumpserver/jumpserver \
  --namespace jumpserver --create-namespace \
  -f values.yaml
```

也可以直接使用 `--set` 覆蓋參數：

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

## 解除安裝

```bash
helm uninstall jms-k8s -n jumpserver
```

PVC 預設帶有 `helm.sh/resource-policy: keep`，解除安裝後會被保留。確認資料不再需要後，可手動刪除：

```bash
kubectl -n jumpserver get pvc
kubectl -n jumpserver delete pvc <pvc-name>
```

## 鳴謝

本專案初始程式碼由 [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba) 貢獻，原倉庫位址：[xiaomaimuchanyiyiba/jumpserver](https://github.com/xiaomaimuchanyiyiba/jumpserver)。
