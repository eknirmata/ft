# Function to get pod information from a project
def get_pods_info(dyn_client, project_name):
    v1_pods = dyn_client.resources.get(api_version='v1', kind='Pod')
    pod_list = v1_pods.get(namespace=project_name)
    pods_info = []
    for pod in pod_list.items:
        containers_info = []
        for container in pod.spec.containers:
            containers_info.append({
                'container_name': container.name,
                'container_image': container.image
            })
        pods_info.append({
            'pod_name': pod.metadata.name,
            'node_name': pod.spec.nodeName,  # Node name where the pod is running
            'containers': containers_info,
            'create_time': pod.metadata.creationTimestamp
        })
    return pods_info



#--

# Prepare the CSV file for writing the output
with open('cluster_projects_pods.csv', mode='w', newline='') as file:
    fieldnames = ['cluster', 'project_name', 'pod_name', 'node_name', 'container_name', 'container_image', 'create_time']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header

    # Read the CSV file and loop through the clusters
    with open('clusters.csv', mode='r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            k8s_client = login_to_cluster(row['apihost'], row['username'], row['password'])
            dyn_client = DynamicClient(k8s_client)
            project_list = get_projects(dyn_client)

            for project in project_list.items:
                project_name = project.metadata.name
                pods_info = get_pods_info(dyn_client, project_name)

                for pod_info in pods_info:
                    for container_info in pod_info['containers']:
                        writer.writerow({
                            'cluster': row['apihost'],
                            'project_name': project_name,
                            'pod_name': pod_info['pod_name'],
                            'node_name': pod_info['node_name'],  # Include node name in the output
                            'container_name': container_info['container_name'],
                            'container_image': container_info['container_image'],
                            'create_time': pod_info['create_time']
                        })



####
# Prepare the CSV file for writing the output
with open('cluster_projects_pods.csv', mode='w', newline='') as file:
    fieldnames = ['cluster', 'project_name', 'pod_name', 'node_name', 'container_name', 'container_image', 'image_id', 'create_time']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  # Write the header

    # Read the CSV file and loop through the clusters
    with open('clusters.csv', mode='r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            k8s_client = login_to_cluster(row['apihost'], row['username'], row['password'])
            dyn_client = DynamicClient(k8s_client)
            project_list = get_projects(dyn_client)

            for project in project_list.items:
                project_name = project.metadata.name
                pods_info = get_pods_info(dyn_client, project_name)

                for pod_info in pods_info:
                    for container_info in pod_info['containers']:
                        writer.writerow({
                            'cluster': row['apihost'],
                            'project_name': project_name,
                            'pod_name': pod_info['pod_name'],
                            'node_name': pod_info['node_name'],
                            'container_name': container_info['container_name'],
                            'container_image': container_info['container_image'],
                            'image_id': container_info['image_id'],  # Include imageID in the output
                            'create_time': pod_info['create_time']
                        })


#---
# Function to get pod information from a project
def get_pods_info(dyn_client, project_name):
    v1_pods = dyn_client.resources.get(api_version='v1', kind='Pod')
    pod_list = v1_pods.get(namespace=project_name)
    pods_info = []
    for pod in pod_list.items:
        containers_info = []
        # Check if the containerStatuses field is present and has statuses
        if 'containerStatuses' in pod.status and pod.status.containerStatuses:
            for status in pod.status.containerStatuses:
                containers_info.append({
                    'container_name': status.name,
                    'container_image': status.image,
                    'image_id': status.imageID  # Include imageID from container status
                })
        pods_info.append({
            'pod_name': pod.metadata.name,
            'node_name': pod.spec.nodeName,
            'containers': containers_info,
            'create_time': pod.metadata.creationTimestamp
        })
    return pods_info

