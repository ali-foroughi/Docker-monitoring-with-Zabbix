import docker
import time
from datetime import datetime, timezone
from pyzabbix import ZabbixMetric, ZabbixSender

zabbix_server = '172.20.8.12'
interval = 60

def get_all_container_info():
    client = docker.from_env()

    # Get a list of all containers (running and exited)
    all_containers = client.containers.list(all=True)

    # Extract container information
    container_info = []
    for container in all_containers:
        info_dict = {
            'name': container.name,
            'status': container.status,
            'exit_code': container.attrs['State']['ExitCode'],
            'uptime': get_container_uptime(container)
        }
        container_info.append(info_dict)

    return container_info


def get_container_uptime(container):
    # Get the container start time in UTC
    started_at = container.attrs['State']['StartedAt']

    # Truncate to 6 decimal places for the milliseconds instead of 9
    started_at = started_at[:26] + "Z"

    # Convert the timestamp to a datetime object with UTC offset
    started_time = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

    # Calculate the uptime in seconds and round up
    uptime_seconds = round((datetime.now(timezone.utc) - started_time).total_seconds())

    return uptime_seconds

if __name__ == "__main__":
    while True:
        all_container_info = get_all_container_info()

        # Save output to a file
        with open('log/container_info_output.txt', 'a') as file:
            for info in all_container_info:
                container_name = "5G-" + info['name']
                exit_code = info['exit_code']
                status = info['status']
                uptime = info['uptime']

                # Use the current epoch time
                time_now = int(time.time())

                # Write the formatted lines to the file
                file.write(f"{container_name} exit_code \"{time_now}\" \"{exit_code}\"\n")
                file.write(f"{container_name} status \"{time_now}\" \"{status}\"\n")
                file.write(f"{container_name} uptime \"{time_now}\" \"{uptime}\"\n")

                # Create Zabbix metrics for each container
                metrics = []
                exit_code_metric = ZabbixMetric(container_name, 'exit_code', exit_code)
                metrics.append(exit_code_metric)
                status_metric = ZabbixMetric(container_name, 'status', status)
                metrics.append(status_metric)
                uptime_metric = ZabbixMetric(container_name, 'uptime', uptime)
                metrics.append(uptime_metric)

                # Print metrics (for debugging)
                print(metrics)

                # Send metrics to Zabbix Server
                ZabbixSender(zabbix_server).send(metrics)

        # Sleep for 5 seconds before the next iteration
        time.sleep(interval)