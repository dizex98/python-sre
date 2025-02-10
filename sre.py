import argparse
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def load_kube_config():
    try:
        config.load_kube_config()
    except Exception as e:
        print(f"Error loading kubeconfig: {e}")
        exit(1)


def list_deployments(namespace=None):
    v1_apps = client.AppsV1Api()
    try:
        if namespace:
            deployments = v1_apps.list_namespaced_deployment(namespace)
        else:
            deployments = v1_apps.list_deployment_for_all_namespaces()
        for deployment in deployments.items:
            print(f"Namespace: {deployment.metadata.namespace}, Name: {deployment.metadata.name}")
    except ApiException as e:
        print(f"Error listing deployments: {e}")


def scale_deployment(deployment, replicas, namespace=None):
    v1_apps = client.AppsV1Api()
    try:
        if namespace:
            v1_apps.patch_namespaced_deployment_scale(
                name=deployment,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
        else:
            # Search across all namespaces
            deployments = v1_apps.list_deployment_for_all_namespaces(field_selector=f"metadata.name={deployment}")
            if not deployments.items:
                print(f"Deployment '{deployment}' not found.")
                return
            namespace = deployments.items[0].metadata.namespace
            v1_apps.patch_namespaced_deployment_scale(
                name=deployment,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
        print(f"Scaled deployment '{deployment}' to {replicas} replicas.")
    except ApiException as e:
        print(f"Error scaling deployment: {e}")


def get_deployment_info(deployment, namespace=None):
    v1_apps = client.AppsV1Api()
    try:
        if namespace:
            dep = v1_apps.read_namespaced_deployment(deployment, namespace)
        else:
            # Search across all namespaces
            deployments = v1_apps.list_deployment_for_all_namespaces(field_selector=f"metadata.name={deployment}")
            if not deployments.items:
                print(f"Deployment '{deployment}' not found.")
                return
            dep = deployments.items[0]
        print(f"Name: {dep.metadata.name}")
        print(f"Namespace: {dep.metadata.namespace}")
        print(f"Replicas: {dep.spec.replicas}")
        print(f"Available Replicas: {dep.status.available_replicas}")
    except ApiException as e:
        print(f"Error fetching deployment info: {e}")

def diagnose_deployment(deployment, namespace=None, include_pods=False):
    v1_apps = client.AppsV1Api()
    v1_core = client.CoreV1Api()
    try:
        if namespace:
            dep = v1_apps.read_namespaced_deployment(deployment, namespace)
        else:
            deployments = v1_apps.list_deployment_for_all_namespaces(field_selector=f"metadata.name={deployment}")
            if not deployments.items:
                print(f"Deployment '{deployment}' not found.")
                return
            dep = deployments.items[0]
            namespace = dep.metadata.namespace

        print(f"Diagnosing deployment '{deployment}' in namespace '{namespace}'")
        pods = v1_core.list_namespaced_pod(namespace, label_selector=f"app={deployment}")
        for pod in pods.items:
            print(f"Pod: {pod.metadata.name}, Status: {pod.status.phase}")
            if include_pods:
                for container_status in pod.status.container_statuses:
                    print(f"  Container: {container_status.name}, Ready: {container_status.ready}")
    except ApiException as e:
        print(f"Error diagnosing deployment: {e}")


def main():
    parser = argparse.ArgumentParser(description="SRE CLI for Kubernetes")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List deployments")
    list_parser.add_argument("--namespace", help="Namespace to list deployments in", default=None)

    # Scale command
    scale_parser = subparsers.add_parser("scale", help="Scale a deployment")
    scale_parser.add_argument("--replicas", type=int, required=True, help="Number of replicas")
    scale_parser.add_argument("--deployment", required=True, help="Name of the deployment")
    scale_parser.add_argument("--namespace", help="Namespace of the deployment", default=None)

    # Info command
    info_parser = subparsers.add_parser("info", help="Get deployment info")
    info_parser.add_argument("--deployment", required=True, help="Name of the deployment")
    info_parser.add_argument("--namespace", help="Namespace of the deployment", default=None)

    # Diagnostic command
    diag_parser = subparsers.add_parser("diagnostic", help="Diagnose deployment health")
    diag_parser.add_argument("--deployment", required=True, help="Name of the deployment")
    diag_parser.add_argument("--namespace", help="Namespace of the deployment", default=None)
    diag_parser.add_argument("--pod", action="store_true", help="Include pod-level diagnostics")

    args = parser.parse_args()

    load_kube_config()

    if args.command == "list":
        list_deployments(args.namespace)
    elif args.command == "scale":
        scale_deployment(args.deployment, args.replicas, args.namespace)
    elif args.command == "info":
        get_deployment_info(args.deployment, args.namespace)
    elif args.command == "diagnostic":
        diagnose_deployment(args.deployment, args.namespace, args.pod)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()