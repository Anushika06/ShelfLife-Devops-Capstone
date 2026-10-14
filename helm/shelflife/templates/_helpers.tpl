{{/* Chart name. */}}
{{- define "shelflife.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Release-scoped base name, e.g. "shelflife". */}}
{{- define "shelflife.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/* Common labels. */}}
{{- define "shelflife.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "shelflife.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: shelflife
{{- end }}

{{/* Selector labels for one component: include "shelflife.selectorLabels" (dict "ctx" . "component" "backend") */}}
{{- define "shelflife.selectorLabels" -}}
app.kubernetes.io/name: {{ include "shelflife.name" .ctx }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "shelflife.image" -}}
{{- $tag := required (printf "%s.image.tag is required: set it to the Git commit SHA published by CI (never 'latest')" .component) .image.tag -}}
{{- printf "%s:%s" .image.repository $tag -}}
{{- end }}

{{- define "shelflife.postgresSecretName" -}}
{{- default (printf "%s-postgres" (include "shelflife.fullname" .)) .Values.postgres.auth.existingSecret }}
{{- end }}

{{/* Hardened container security context shared by all app containers. */}}
{{- define "shelflife.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
runAsNonRoot: true
capabilities:
  drop: ["ALL"]
seccompProfile:
  type: RuntimeDefault
{{- end }}
