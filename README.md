# JumpServer Kubernetes Helm Chart

<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html"><img src="https://img.shields.io/github/license/jumpserver/jumpserver" alt="License: GPLv3"></a>
  <a href="https://shields.io/github/downloads/jumpserver/helm-charts/total"><img src="https://shields.io/github/downloads/jumpserver/helm-charts/total" alt=" release"></a>
  <a href="https://hub.docker.com/u/jumpserver"><img src="https://img.shields.io/docker/pulls/jumpserver/jms_all.svg" alt="Codacy"></a>
  <a href="https://github.com/jumpserver/helm-charts/commits"><img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/jumpserver/helm-charts.svg" /></a>
  <a href="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml"><img alt="Release Charts" src="https://github.com/jumpserver/helm-charts/actions/workflows/release.yml/badge.svg" /></a>
  <a href="https://github.com/jumpserver/helm-charts"><img src="https://img.shields.io/github/stars/jumpserver/helm-charts?color=%231890FF&style=flat-square" alt="Stars"></a>
</p>


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
