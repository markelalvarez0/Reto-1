#!/usr/bin/env bash
# Cluster efimero docente, solo loopback. No configura seguridad de produccion.
set -euo pipefail
: "${JAVA_HOME:?Se necesita JAVA_HOME (Java 11)}"
: "${RUNNER_TEMP:?Solo ejecutar en un entorno CI temporal}"
export HADOOP_HOME="$RUNNER_TEMP/hadoop-3.4.2"
if [ -e "$HADOOP_HOME/dfs/name" ]; then
  echo 'No se formatea un almacen existente' >&2; exit 1
fi
mkdir -p "$HADOOP_HOME"
curl -fL --retry 3 https://archive.apache.org/dist/hadoop/common/hadoop-3.4.2/hadoop-3.4.2.tar.gz -o "$RUNNER_TEMP/hadoop.tar.gz"
curl -fL --retry 3 https://archive.apache.org/dist/hadoop/common/hadoop-3.4.2/hadoop-3.4.2.tar.gz.sha512 -o "$RUNNER_TEMP/hadoop.sha512"
python - <<'PY'
import hashlib,os,re
from pathlib import Path
root=Path(os.environ['RUNNER_TEMP']);h=hashlib.sha512()
with (root/'hadoop.tar.gz').open('rb') as stream:
    for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
expected=re.findall(r'\b[0-9a-fA-F]{128}\b',(root/'hadoop.sha512').read_text())
assert h.hexdigest() in [s.lower() for s in expected], 'SHA512 incorrecto'
PY
tar -xzf "$RUNNER_TEMP/hadoop.tar.gz" -C "$HADOOP_HOME" --strip-components=1
cat > "$HADOOP_HOME/etc/hadoop/core-site.xml" <<EOF
<configuration><property><name>fs.defaultFS</name><value>hdfs://127.0.0.1:9000</value></property><property><name>hadoop.tmp.dir</name><value>$HADOOP_HOME/tmp</value></property></configuration>
EOF
cat > "$HADOOP_HOME/etc/hadoop/hdfs-site.xml" <<EOF
<configuration>
<property><name>dfs.replication</name><value>1</value></property>
<property><name>dfs.permissions.enabled</name><value>false</value></property>
<property><name>dfs.webhdfs.enabled</name><value>true</value></property>
<property><name>dfs.namenode.name.dir</name><value>file://$HADOOP_HOME/dfs/name</value></property>
<property><name>dfs.datanode.data.dir</name><value>file://$HADOOP_HOME/dfs/data</value></property>
<property><name>dfs.namenode.http-address</name><value>127.0.0.1:9870</value></property>
<property><name>dfs.namenode.rpc-bind-host</name><value>127.0.0.1</value></property>
<property><name>dfs.datanode.hostname</name><value>localhost</value></property>
<property><name>dfs.datanode.http.address</name><value>127.0.0.1:9864</value></property>
</configuration>
EOF
"$HADOOP_HOME/bin/hdfs" namenode -format -nonInteractive
"$HADOOP_HOME/bin/hdfs" --daemon start namenode
"$HADOOP_HOME/bin/hdfs" --daemon start datanode
for i in $(seq 1 60); do
  if curl -fsS 'http://127.0.0.1:9870/webhdfs/v1/?op=GETFILESTATUS&user.name=hadoop' >/dev/null; then break; fi
  sleep 2
done
"$HADOOP_HOME/bin/hdfs" dfsadmin -safemode leave
"$HADOOP_HOME/bin/hdfs" dfs -mkdir -p /data/reto1/raw /data/reto1/processed
printf 'HADOOP_HOME=%s\n' "$HADOOP_HOME" >> "$GITHUB_ENV"
