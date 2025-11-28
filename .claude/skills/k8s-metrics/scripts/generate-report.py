#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///

"""
Kubernetes Cluster Health Report Generator
Analyzes kubectl output and generates structured reports

Outputs:
1. Human-readable summary to stdout
2. Detailed JSON report to k8s-metrics.json (for AI consumption)
"""

import subprocess
import json
import sys
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def run_kubectl(args):
    """Run kubectl command and return output"""
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running kubectl: {e}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print("Error: kubectl not found. Please install kubectl.", file=sys.stderr)
        sys.exit(1)

def get_cluster_info():
    """Get basic cluster information"""
    try:
        cluster_info = run_kubectl(["cluster-info"])
        version_info = run_kubectl(["version", "--short"]) or run_kubectl(["version"])
        return cluster_info, version_info
    except Exception as e:
        print(f"Error getting cluster info: {e}", file=sys.stderr)
        return None, None

def get_nodes():
    """Get node information"""
    output = run_kubectl(["get", "nodes", "-o", "json"])
    if not output:
        return []

    data = json.loads(output)
    nodes = []

    for node in data.get("items", []):
        name = node["metadata"]["name"]
        status = "Unknown"

        for condition in node["status"].get("conditions", []):
            if condition["type"] == "Ready":
                status = "Ready" if condition["status"] == "True" else "NotReady"

        capacity = node["status"].get("capacity", {})
        allocatable = node["status"].get("allocatable", {})

        nodes.append({
            "name": name,
            "status": status,
            "cpu_capacity": capacity.get("cpu", "N/A"),
            "memory_capacity": capacity.get("memory", "N/A"),
            "cpu_allocatable": allocatable.get("cpu", "N/A"),
            "memory_allocatable": allocatable.get("memory", "N/A"),
        })

    return nodes

def get_pods_by_namespace():
    """Get all pods grouped by namespace"""
    output = run_kubectl(["get", "pods", "--all-namespaces", "-o", "json"])
    if not output:
        return {}

    data = json.loads(output)
    pods_by_ns = defaultdict(list)

    for pod in data.get("items", []):
        namespace = pod["metadata"]["namespace"]
        name = pod["metadata"]["name"]
        phase = pod["status"].get("phase", "Unknown")

        # Count container statuses
        restarts = 0
        failed_containers = []

        for container_status in pod["status"].get("containerStatuses", []):
            restarts += container_status.get("restartCount", 0)

            if not container_status.get("ready", False):
                state = container_status.get("state", {})
                reason = "Unknown"

                if "waiting" in state:
                    reason = state["waiting"].get("reason", "Waiting")
                elif "terminated" in state:
                    reason = state["terminated"].get("reason", "Terminated")

                failed_containers.append({
                    "name": container_status["name"],
                    "reason": reason
                })

        pods_by_ns[namespace].append({
            "name": name,
            "phase": phase,
            "restarts": restarts,
            "failed_containers": failed_containers
        })

    return pods_by_ns

def get_resource_usage():
    """Get resource usage by namespace (requires metrics-server)"""
    output = run_kubectl(["top", "pods", "--all-namespaces"])
    if not output or "error" in output.lower():
        return None

    # Parse the output
    lines = output.split('\n')[1:]  # Skip header
    usage_by_ns = defaultdict(lambda: {"cpu": 0, "memory": 0, "count": 0})

    for line in lines:
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) >= 4:
            namespace = parts[0]
            cpu = parts[2]  # e.g., "10m"
            memory = parts[3]  # e.g., "50Mi"

            # Simple parsing (could be improved)
            cpu_value = int(cpu.rstrip('m')) if 'm' in cpu else int(cpu) * 1000

            usage_by_ns[namespace]["cpu"] += cpu_value
            usage_by_ns[namespace]["count"] += 1

    return dict(usage_by_ns)

def print_header(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_summary(nodes, pods_by_ns):
    """Print executive summary"""
    print_header("CLUSTER HEALTH SUMMARY")

    total_nodes = len(nodes)
    ready_nodes = sum(1 for n in nodes if n["status"] == "Ready")
    total_namespaces = len(pods_by_ns)

    all_pods = [pod for pods in pods_by_ns.values() for pod in pods]
    total_pods = len(all_pods)
    running_pods = sum(1 for p in all_pods if p["phase"] == "Running")
    failed_pods = sum(1 for p in all_pods if p["phase"] == "Failed")
    pending_pods = sum(1 for p in all_pods if p["phase"] == "Pending")

    # Calculate health score (simple metric)
    health_score = 100
    if total_nodes > 0:
        health_score -= ((total_nodes - ready_nodes) / total_nodes) * 30
    if total_pods > 0:
        health_score -= (failed_pods / total_pods) * 40
        health_score -= (pending_pods / total_pods) * 20

    health_score = max(0, min(100, health_score))

    # Determine status
    if health_score >= 90:
        status = "HEALTHY ✓"
    elif health_score >= 70:
        status = "DEGRADED ⚠"
    else:
        status = "CRITICAL ✗"

    print(f"Cluster Status: {status}")
    print(f"Health Score: {health_score:.1f}/100")
    print(f"\nNodes: {ready_nodes}/{total_nodes} Ready")
    print(f"Namespaces: {total_namespaces}")
    print(f"Pods: {running_pods}/{total_pods} Running")

    if failed_pods > 0:
        print(f"  └─ {failed_pods} Failed")
    if pending_pods > 0:
        print(f"  └─ {pending_pods} Pending")

def print_node_details(nodes):
    """Print node details"""
    print_header("NODE DETAILS")

    for node in nodes:
        status_symbol = "✓" if node["status"] == "Ready" else "✗"
        print(f"{status_symbol} {node['name']}")
        print(f"  Status: {node['status']}")
        print(f"  CPU: {node['cpu_allocatable']} allocatable / {node['cpu_capacity']} capacity")
        print(f"  Memory: {node['memory_allocatable']} allocatable / {node['memory_capacity']} capacity")
        print()

def print_pod_status(pods_by_ns):
    """Print pod status by namespace"""
    print_header("POD STATUS BY NAMESPACE")

    for namespace in sorted(pods_by_ns.keys()):
        pods = pods_by_ns[namespace]
        running = sum(1 for p in pods if p["phase"] == "Running")
        total = len(pods)

        print(f"\n{namespace} ({running}/{total} running)")

        # Show failed/pending pods
        problems = [p for p in pods if p["phase"] != "Running" and p["phase"] != "Succeeded"]
        if problems:
            for pod in problems:
                print(f"  ✗ {pod['name']}: {pod['phase']}")
                for container in pod["failed_containers"]:
                    print(f"    └─ {container['name']}: {container['reason']}")

        # Show high restart counts
        high_restarts = [p for p in pods if p["restarts"] > 5]
        if high_restarts:
            print(f"  High restart counts:")
            for pod in high_restarts:
                print(f"    ⟳ {pod['name']}: {pod['restarts']} restarts")

def print_recommendations(nodes, pods_by_ns):
    """Print recommendations based on cluster state"""
    print_header("RECOMMENDATIONS")

    recommendations = []

    # Check for NotReady nodes
    not_ready_nodes = [n for n in nodes if n["status"] != "Ready"]
    if not_ready_nodes:
        recommendations.append(
            f"⚠ {len(not_ready_nodes)} node(s) not ready. Investigate: " +
            ", ".join(n["name"] for n in not_ready_nodes)
        )

    # Check for failed pods
    all_pods = [pod for pods in pods_by_ns.values() for pod in pods]
    failed_pods = [p for p in all_pods if p["phase"] == "Failed"]
    if failed_pods:
        recommendations.append(
            f"⚠ {len(failed_pods)} failed pod(s). Check logs and events."
        )

    # Check for pending pods
    pending_pods = [p for p in all_pods if p["phase"] == "Pending"]
    if pending_pods:
        recommendations.append(
            f"⚠ {len(pending_pods)} pending pod(s). May indicate resource constraints."
        )

    # Check for high restart counts
    high_restarts = [p for p in all_pods if p["restarts"] > 10]
    if high_restarts:
        recommendations.append(
            f"⚠ {len(high_restarts)} pod(s) with >10 restarts. Investigate crash loops."
        )

    # Check for failed containers
    failed_containers = [p for p in all_pods if p["failed_containers"]]
    if failed_containers:
        recommendations.append(
            f"⚠ {len(failed_containers)} pod(s) with failed containers. Check container logs."
        )

    if not recommendations:
        print("✓ No critical issues detected.")
        print("✓ Cluster appears to be operating normally.")
    else:
        for rec in recommendations:
            print(f"{rec}")

    print("\nNext Steps:")
    print("• Review pod logs: kubectl logs <pod-name> -n <namespace>")
    print("• Check events: kubectl get events --all-namespaces --sort-by='.lastTimestamp'")
    print("• Describe resources: kubectl describe pod <pod-name> -n <namespace>")

def generate_json_report(nodes, pods_by_ns):
    """Generate detailed JSON report for AI consumption"""
    all_pods = [pod for pods in pods_by_ns.values() for pod in pods]

    # Collect all issues with specific resource names
    issues = {
        "failed_pods": [],
        "pending_pods": [],
        "high_restart_pods": [],
        "crashloop_pods": [],
        "failed_containers": [],
        "not_ready_nodes": []
    }

    # Nodes not ready
    for node in nodes:
        if node["status"] != "Ready":
            issues["not_ready_nodes"].append({
                "name": node["name"],
                "status": node["status"]
            })

    # Analyze pods
    for namespace, pods in pods_by_ns.items():
        for pod in pods:
            pod_ref = {
                "namespace": namespace,
                "name": pod["name"]
            }

            # Failed pods
            if pod["phase"] == "Failed":
                issues["failed_pods"].append({
                    **pod_ref,
                    "phase": pod["phase"]
                })

            # Pending pods
            if pod["phase"] == "Pending":
                issues["pending_pods"].append({
                    **pod_ref,
                    "phase": pod["phase"]
                })

            # High restart counts
            if pod["restarts"] > 5:
                issues["high_restart_pods"].append({
                    **pod_ref,
                    "restarts": pod["restarts"]
                })

            # Failed containers
            if pod["failed_containers"]:
                for container in pod["failed_containers"]:
                    if "CrashLoopBackOff" in container["reason"]:
                        issues["crashloop_pods"].append({
                            **pod_ref,
                            "container": container["name"],
                            "reason": container["reason"]
                        })

                    issues["failed_containers"].append({
                        **pod_ref,
                        "container": container["name"],
                        "reason": container["reason"]
                    })

    # Calculate summary metrics
    total_pods = len(all_pods)
    running_pods = sum(1 for p in all_pods if p["phase"] == "Running")

    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_nodes": len(nodes),
            "ready_nodes": sum(1 for n in nodes if n["status"] == "Ready"),
            "total_namespaces": len(pods_by_ns),
            "total_pods": total_pods,
            "running_pods": running_pods,
            "failed_pods": sum(1 for p in all_pods if p["phase"] == "Failed"),
            "pending_pods": sum(1 for p in all_pods if p["phase"] == "Pending")
        },
        "nodes": nodes,
        "namespaces": {
            ns: {
                "pod_count": len(pods),
                "running_count": sum(1 for p in pods if p["phase"] == "Running")
            }
            for ns, pods in pods_by_ns.items()
        },
        "issues": issues
    }

    return report

def save_json_report(report, output_file="k8s-metrics.json"):
    """Save JSON report to file"""
    try:
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        return output_path
    except Exception as e:
        print(f"Warning: Could not save JSON report: {e}", file=sys.stderr)
        return None

def main():
    """Main report generation function"""
    print(f"\nKubernetes Cluster Health Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check cluster connectivity
    cluster_info, version_info = get_cluster_info()
    if not cluster_info:
        print("Error: Cannot connect to Kubernetes cluster.")
        sys.exit(1)

    # Gather data
    print("Collecting cluster metrics...")
    nodes = get_nodes()
    pods_by_ns = get_pods_by_namespace()

    # Generate and save JSON report
    json_report = generate_json_report(nodes, pods_by_ns)
    json_path = save_json_report(json_report)

    # Generate human-readable report
    print_summary(nodes, pods_by_ns)
    print_node_details(nodes)
    print_pod_status(pods_by_ns)
    print_recommendations(nodes, pods_by_ns)

    print(f"\n{'='*60}")
    print("Report Complete")
    print(f"{'='*60}")

    if json_path:
        print(f"\nDetailed JSON report saved to: {json_path}")
        print("AI agents can use this file to quickly identify and investigate specific resources.")
    print()

if __name__ == "__main__":
    main()
