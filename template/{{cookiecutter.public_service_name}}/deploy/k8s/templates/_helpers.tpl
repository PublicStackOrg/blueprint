{{/*
Common labels and selector helpers.
*/}}

{{- define "ps.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "ps.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "ps.databaseUrl" -}}
{{- if .Values.externalPostgres.enabled -}}
{{- .Values.externalPostgres.url -}}
{{- else -}}
postgresql+asyncpg://{{ .Values.postgresql.auth.username }}:$(POSTGRES_PASSWORD)@{{ .Release.Name }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- end -}}
{{- end -}}

{{- define "ps.redisUrl" -}}
{{- if .Values.externalRedis.enabled -}}
{{- .Values.externalRedis.url -}}
{{- else -}}
redis://:$(REDIS_PASSWORD)@{{ .Release.Name }}-redis-master:6379/0
{{- end -}}
{{- end -}}
