{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "jumpserver.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "jumpserver.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "jumpserver.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "jumpserver.labels" -}}
app.kubernetes.io/name: {{ include "jumpserver.name" . }}
helm.sh/chart: {{ include "jumpserver.chart" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "jumpserver.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{ default (include "jumpserver.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
{{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Define JumpServer database
*/}}

{{- define "jumpserver.mysql.fullname" -}}
{{- printf "%s-%s" .Release.Name "mysql" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "jumpserver.database.host" -}}
  {{- if .Values.mysql.enabled -}}
    {{- include "jumpserver.mysql.fullname" . -}}
  {{- else -}}
    {{- .Values.externalDatabase.host -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.database.port" -}}
  {{- if .Values.mysql.enabled -}}
    {{- print "3306" -}}
  {{- else -}}
    {{- .Values.externalDatabase.port -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.database.user" -}}
  {{- if .Values.mysql.enabled -}}
    {{- .Values.mysql.auth.username -}}
  {{- else -}}
    {{- .Values.externalDatabase.user -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.database.password" -}}
{{- .Values.externalDatabase.password -}}
{{- end -}}

{{- define "jumpserver.database.engine" -}}
  {{- if .Values.mysql.enabled -}}
    {{- print "mysql" -}}
  {{- else -}}
    {{- .Values.externalDatabase.engine -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.database.database" -}}
  {{- if .Values.mysql.enabled -}}
    {{- .Values.mysql.auth.database -}}
  {{- else -}}
    {{- .Values.externalDatabase.database -}}
  {{- end -}}
{{- end -}}

{{/*
Define JumpServer redis
*/}}

{{- define "jumpserver.redis.fullname" -}}
{{- printf "%s-%s-master" .Release.Name "redis" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "jumpserver.redis.host" -}}
  {{- if .Values.redis.enabled -}}
    {{- include "jumpserver.redis.fullname" . -}}
  {{- else -}}
    {{- .Values.externalRedis.host -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.redis.port" -}}
  {{- if .Values.mysql.enabled -}}
    {{- print "6379" -}}
  {{- else -}}
    {{- .Values.externalRedis.port -}}
  {{- end -}}
{{- end -}}

{{- define "jumpserver.redis.password" -}}
{{- .Values.externalRedis.password -}}
{{- end -}}

{{/*
Define JumpServer StorageClass
*/}}

{{- define "jumpserver.core.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.core.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.koko.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.koko.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.lion.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.lion.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.magnus.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.magnus.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.omnidb.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.omnidb.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.razor.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.razor.persistence.storageClassName -}}
{{- end -}}
{{- end -}}

{{- define "jumpserver.web.storageClass" -}}
{{- if .Values.global.storageClass }}
{{- .Values.global.storageClass }}
{{- else -}}
{{- .Values.razor.persistence.storageClassName -}}
{{- end -}}
{{- end -}}
