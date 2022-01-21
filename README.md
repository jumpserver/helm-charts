# JumpServer Kubernetes Helm Chart

[![Release Charts](https://github.com/jumpserver/helm-charts/actions/workflows/release.yml/badge.svg)](https://github.com/jumpserver/helm-charts/actions/workflows/release.yml)

- Kubernetes 1.20+
- Helm 3.0

## Usage

[Helm](https://helm.sh) must be installed to use the charts.
Please refer to Helm's [documentation](https://helm.sh/docs/) to get started.

Once Helm is set up properly, add the repo as follows:

```bash
helm repo add jumpserver https://jumpserver.github.io/helm-charts
helm repo list
```

You can then run `helm search repo jumpserver` to see the charts.

<!--
## License

[Apache 2.0 License](https://github.com/jumpserver/helm-charts/blob/main/LICENSE).  

-->

## [Documentation](https://docs.jumpserver.org/zh/master/install/setup_by_fast/)

```bash
wget https://raw.githubusercontent.com/jumpserver/helm-charts/main/charts/jumpserver/values.yaml
vi values.yaml
```

### install
```bash
helm install jms-k8s jumpserver/jumpserver -n default -f values.yaml
```
