# Cluster Monitoring

This repo contains a script that sends a ping to Opsgenie's Heartbeat every 5 minutes. If the cluster is down, Opsgenie will not get a ping and will send a mail to inform team members of the cluster's failed state.

The script is deployed into the ArgoCD cluster under monitoring. Once this cluster is down, pings will not be sent to Opsgenie, triggering an alert which is sent to concerned team members.

## Running the script

- Create a ```.env``` file, with the following contents
```bash
OPSGENIE_API_KEY=<some-value>
HEARTBEAT_NAME=<some-value>
PING_SLEEP=<some-value>
```

- Runing the script
```python
$ docker run --env-file .env ghcr.io/glueops/cluster-monitoring:main
```