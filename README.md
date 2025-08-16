# Final Project – MySQL logs in SigNoz (short guide)

**Goal:** Send MySQL logs (general + slow) to SigNoz and view them in the UI.

---

## 1) Start SigNoz (UI on 8081)
- Edit `signoz\deploy\docker\docker-compose.yaml` and make sure the `signoz` service has:
```yaml
ports:
  - "8081:8080"
```
- Start SigNoz:
```cmd
cd C:\Assignments\Finals\database\PROG8850-finalassignment\signoz\deploy\docker
docker compose up -d --remove-orphans
```
- Open **http://localhost:8081**

---

## 2) MySQL: write logs to files
- Ensure the container name is `mysql-logs` and it’s running.
- Turn on file logs inside MySQL:
```cmd
docker exec -it mysql-logs bash -lc "mkdir -p /var/log/mysql && chown -R mysql:mysql /var/log/mysql"
docker exec -it mysql-logs mysql -uroot -prootpassword -e ^
"SET PERSIST log_output='FILE'; ^
 SET PERSIST general_log=ON; ^
 SET PERSIST general_log_file='/var/log/mysql/general.log'; ^
 SET PERSIST slow_query_log=ON; ^
 SET PERSIST long_query_time=1; ^
 SET PERSIST slow_query_log_file='/var/log/mysql/slow.log';"
docker restart mysql-logs
```

---

## 3) Sidecar collector (reads files → sends to SigNoz)
Create `signoz\deploy\docker\filelog-collector.yaml`:
```yaml
receivers:
  filelog/mysql:
    include: [/var/log/mysql/*.log]
    start_at: beginning
    include_file_path: true
    include_file_name: true
    operators:
      - type: move
        from: body
        to: attributes["log.message"]

processors:
  resource/mysql:
    attributes:
      - action: upsert
        key: service.name
        value: automated-mysql-server
  batch: {}

exporters:
  otlp:
    endpoint: otel-collector:4317
    tls: { insecure: true }

service:
  pipelines:
    logs/mysql:
      receivers: [filelog/mysql]
      processors: [resource/mysql, batch]
      exporters: [otlp]
```

Add this service to `docker-compose.yaml` (under `services:`):
```yaml
mysql-filelog-collector:
  image: otel/opentelemetry-collector-contrib:0.95.0
  container_name: mysql-filelog-collector
  command: ["--config=/etc/otelcol/filelog-collector.yaml"]
  volumes:
    - "./filelog-collector.yaml:/etc/otelcol/filelog-collector.yaml:ro"
    - "C:/Assignments/Finals/database/PROG8850-finalassignment/mysql/logs:/var/log/mysql:ro"
  depends_on:
    - otel-collector
  networks:
    - signoz-net
```

Start the sidecar:
```cmd
cd C:\Assignments\Finals\database\PROG8850-finalassignment\signoz\deploy\docker
docker compose up -d mysql-filelog-collector
```

---

## 4) Make some logs
```cmd
mysql -h 127.0.0.1 -P 3308 --protocol=tcp -uroot -prootpassword -e ^
"USE project_db; SELECT NOW(); SELECT SLEEP(2);"
```

---

## 5) View in SigNoz
- Open **Logs → Explorer**
- Try:
  - `attributes.log.file.path contains "/var/log/mysql/"`
  - `service.name = "automated-mysql-server"`

**Group 4:** Keerthana Garimella, Preethi Jakhar, Suman Kumari Jakhar.
