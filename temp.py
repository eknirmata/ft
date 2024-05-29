import csv
from kubernetes import client
from openshift.dynamic import DynamicClient
from openshift.helper.userpassauth import OCPLoginConfiguration


def read_cluster_info(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row['cluster'], row['apihost'], row['username'], row['password']

def get_kube_config(apihost, username, password):
    try:
        kubeConfig = OCPLoginConfiguration(ocp_username=username, ocp_password=password)
        kubeConfig.host = apihost
        kubeConfig.verify_ssl = True
        kubeConfig.ssl_ca_cert = './ocp.pem'
        kubeConfig.get_token()
        if kubeConfig.api_key and kubeConfig.api_key_expires:
            return kubeConfig
        else:
            print("Invalid kube config.")
            return None
    except Exception as e:
        print(f"Failed to get kube config: {e}")
        return None

def get_dyn_client(kubeConfig):
    k8s_client = client.ApiClient(kubeConfig)
    dyn_client = DynamicClient(k8s_client)
    return dyn_client

def is_cluster_reachable(dyn_client):
    try:
        v1_projects = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
        projects = v1_projects.get()
        if projects.items:
            print(f"Cluster is reachable.")
            return True
        else:
            print("Cluster is reachable but has no projects.")
            return False
    except Exception as e:
        print(f"Failed to reach cluster: {e}")
        return False

def get_projects(dyn_client):
    v1_projects = dyn_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
    return v1_projects.get()

def get_events(dyn_client):
    v1_events = dyn_client.resources.get(api_version='v1', kind='Event')
    return v1_events.get()

def write_output_to_csv(cluster, project_list, event_list, file_path):
    with open(file_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Cluster', 'Project', 'Event'])
        for project in project_list.items:
            for event in event_list.items:
                writer.writerow([cluster, project.metadata.name, event.metadata.name])

def main():
    for cluster, apihost, username, password in read_cluster_info('clusters.csv'):
        kubeConfig = get_kube_config(apihost, username, password)
        if kubeConfig is not None:
            dyn_client = get_dyn_client(kubeConfig)
            if is_cluster_reachable(dyn_client):
                project_list = get_projects(dyn_client)
                event_list = get_events(dyn_client)
                write_output_to_csv(cluster, project_list, event_list, 'output.csv')

if __name__ == "__main__":
    main()
