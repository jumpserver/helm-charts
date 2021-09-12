# Jumpserver

[Jumpserver](http://www.jumpserver.org/) 是全球首款完全开源的堡垒机, 使用 GNU GPL v2.0 开源协议, 是符合 4A 的专业运维审计系统。

## 使用方法

```bash
helm install jumpserver ./
```

## 介绍

当前 Chart 包含了 Jumpserver 所需的基本组件

## 依赖

- Kubernetes 1.20+
- Helm 3.0

## 安装

发布名为 `jumpserver` 的 release:

```bash
helm install jumpserver ./
```

安装到指定 namespace

```bash
helm install jumpserver ./ -n default
```

上条命令把默认配置的 JumpServer 部署到了 kubernetes 集群中，[参数](#参数)一节中列出了配置参数

**Tip**: List all releases using `helm list`

## 卸载

删除 `jumpserver` release:

```bash
$ helm delete jumpserver
```

上条命令删除了所有包含在 release 中的组件

## 参数

下面的表格中列出了一些必要的参数，发布前请先阅读并设置

### 总览

| 参数                   | 描述                | 默认值       |
| ---------------------- | ------------------ | ----------- |
| `nameOveride`          | name override      | `nil`       |
| `fullNameOveride`      | full name override | `nil`       |
| `global.imageRegistry` | 仓库地址            | `docker.io` |
| `ingress.enabled`      | 开启 ingress       | `true`      |
| `core.enabled`         | 开启 core          | `true`      |
| `koko.enabled`         | 开启 koko          | `true`      |
| `lion.enabled`         | 开启 lion          | `true`      |
| `web.enabled`          | 开启 web           | `true`      |
| `xpack.enable`         | 开启 xpack         | `false`     |

### core

| 参数             | 描述                                                                    | 默认值                 |
| ---------------- | ---------------------------------------------------------------------- | ---------------------- |
| `secretKey`      | 加密秘钥 生产环境中请修改为随机字符串，请勿外泄, 可使用命令生成              | `nil`                 |
| `bootstrapToken` | 预共享Token coco和guacamole用来注册服务账号，不在使用原来的注册接受机制     | `nil`                  |
| `debug`          | 开启 debug 模式                                                         | `false`                |
| `log.level`      | 日志等级                                                                | `ERROR`                |
| `db.engine`      | 数据库引擎                                                              | `mysql`                |
| `db.host`        | 数据库IP地址                                                            | `nil`                  |
| `db.port`        | 数据库端口                                                              | `3306`                 |
| `db.username`    | 数据库用户名                                                            | `jumpserver`           |
| `db.password`    | 数据库密码                                                              | `nil`                  |
| `db.name`        | 数据库名称                                                              | `nil`                  |
| `redis.host`     | redisIP地址                                                             | `nil`                  |
| `redis.port`     | redis端口                                                               | `6379`                 |
| `redis.password` | redis密码                                                               | `nil`                  |
| `replicaCount`   | 副本数量                                                                | `1`                    |
| `tag`            | 版本号                                                                  | `nil`                  |
| `persistence`    | 持久化存储相关设置                                                       | `nil`                  |

### 其他组件

| 参数                  | 描述                                                       | 默认值  |
| --------------------- | --------------------------------------------------------- | ------- |
| `log.level`           | 日志等级                                                   | `INFO`  |
| `replicaCount`        | 副本数量                                                   | `1`     |
| `tag`                 | 版本号                                                     | `nil`   |
| `persistence`         | 持久化存储相关设置                                          | `nil`   |

在 `helm install` 时通过 `--set key=value[,key=value]` 指定参数. 举例:

```bash
helm install jumpserver ./ \
--set ingress.enabled=true
```

上条命令开启了 ingress.

**注**: 默认使用 [values.yaml](values.yaml)

### 示例

```bash
helm install jumpserver . -n jms \
--set core.config.secretKey=GxrLH7rewfsRN8B9Zl6MEGD50Uou4LF6UVsEIayGMhYll8dqmn \
--set core.config.bootstrapToken=ilR8RvAbK7lgRTxs \
--set global.storageClass=nfs \
--set externalDatabase.engine=mysql \
--set externalDatabase.host=jms-mysql \
--set externalDatabase.port=3306 \
--set externalDatabase.user=jms \
--set externalDatabase.password=Password131 \
--set externalDatabase.database=jumpserver \
--set externalRedis.host=jms-redis-master \
--set externalRedis.port=6379 \
--set koko.service.type=NodePort \
--set web.service.type=NodePort \
--set externalRedis.password=PasswordRedis
```

## 鸣谢说明

本项目初始代码是由 [xiaomaimuchanyiyiba](https://github.com/xiaomaimuchanyiyiba) 贡献。[原仓库地址](https://github.com/xiaomaimuchanyiyiba/jumpserver)
