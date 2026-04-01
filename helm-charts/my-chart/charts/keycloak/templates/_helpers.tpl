{{- define "keycloak.name" -}}
{{- .Release.Name }}-keycloak
{{- end }}

{{- define "keycloak.labels" -}}
app: {{ include "keycloak.name" . }}
{{- end }}

{{- define "keycloak.selectorLabels" -}}
app: {{ include "keycloak.name" . }}
{{- end }}
