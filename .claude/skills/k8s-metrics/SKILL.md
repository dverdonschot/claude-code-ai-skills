---
name: k8s-metrics
description: Generate comprehensive Kubernetes cluster health and resource usage reports. Shows pod status, resource distribution, failed containers, node health, and cluster utilization metrics.
---

# Kubernetes Cluster Metrics

Generate comprehensive reports on Kubernetes cluster health, resource usage, and operational metrics.

## Context

Use this skill when:
- User asks for Kubernetes cluster health status
- User wants to see resource usage and distribution
- User needs to identify failed or problematic pods/containers
- User requests cluster utilization metrics
- User wants insights into node status and capacity

## Process

### 1. Check Kubernetes Access

```bash
# Verify kubectl is available and cluster is accessible
kubectl cluster-info
kubectl version --short 2>/dev/null || kubectl version
```

If kubectl is not available or cluster is not accessible, inform the user.

### 2. Gather Cluster Metrics

Run the metrics collection script:

```bash
./.claude/skills/k8s-metrics/scripts/collect-metrics.sh
```

This script will:
- Check all pods across namespaces
- Identify failed/problematic containers
- Collect resource requests and limits
- Check node status and capacity
- Count deployments, services, and other resources
- Identify resource-intensive workloads

### 3. Generate Report

Use the Python report generator for detailed analysis:

```bash
./.claude/skills/k8s-metrics/scripts/generate-report.py
```

This will:
- Parse kubectl output
- Calculate utilization percentages
- Identify resource bottlenecks
- Highlight failed/unhealthy resources
- Generate a formatted human-readable report
- Save detailed JSON report to `k8s-metrics.json`

**JSON Output**: The script generates a `k8s-metrics.json` file containing:
- All specific resource names (pods, containers, nodes) with issues
- Exact namespace and name for each failed resource
- Structured data optimized for AI consumption
- Allows quick kubectl commands without token-heavy searches

### 4. Investigate Specific Issues (Optional)

If the JSON report identifies issues, use the specific resource names to investigate:

```bash
# Read the JSON report to get exact resource names
cat k8s-metrics.json | grep -A 3 "failed_pods"

# Then investigate specific resources
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

### 5. Present Findings

Create a structured report with:
- **Cluster Overview**: Node count, namespaces, overall health
- **Pod Status**: Running, pending, failed, and crashed pods
- **Resource Usage**: CPU and memory requests/limits by namespace
- **Node Health**: Node status, capacity, and utilization
- **Failed Containers**: List of containers with issues
- **Recommendations**: Potential issues and optimization suggestions
- **JSON Report**: Reference to `k8s-metrics.json` for detailed investigation

## Guidelines

### Data Collection
- Check cluster connectivity before proceeding
- Query all namespaces for comprehensive view
- Handle cases where metrics-server is not installed
- Use kubectl built-in commands (avoid dependencies on metrics-server)
- Filter system namespaces separately from user workloads

### Analysis Approach
- Identify patterns in failures (same namespace, similar workloads)
- Calculate resource utilization (requests vs limits vs actual)
- Highlight resource pressure or over-provisioning
- Check for pods stuck in pending/terminating states
- Look for restart loops (high restart counts)

### Report Structure
Present findings in this order:
1. Executive summary (cluster health score/status)
2. Critical issues (failed pods, crashloops, resource pressure)
3. Resource distribution (by namespace and node)
4. Detailed breakdowns (pod status, container failures)
5. Recommendations for optimization or investigation

### Resource Categories
- **CPU**: Measured in millicores (m) or cores
- **Memory**: Measured in Mi, Gi, or bytes
- **Storage**: PersistentVolumes and claims

### Common Issues to Flag
- Pods with high restart counts (>5)
- Containers in CrashLoopBackOff
- Pods stuck in Pending state
- Nodes in NotReady state
- Resource requests exceeding node capacity
- No resource limits set (potential unbounded usage)
- Evicted pods

## Output

Provide:
1. **Cluster Summary**
   - Total nodes, namespaces, pods
   - Overall health status
   - Cluster version

2. **Pod Status Breakdown**
   - Running: X pods
   - Pending: X pods
   - Failed: X pods
   - CrashLoopBackOff: X pods

3. **Resource Distribution**
   - CPU requests/limits by namespace
   - Memory requests/limits by namespace
   - Top resource consumers

4. **Node Health**
   - Node status (Ready/NotReady)
   - Capacity vs allocatable resources
   - Current utilization (if metrics available)

5. **Failed Containers**
   - Namespace, pod, container name
   - Failure reason
   - Restart count

6. **Recommendations**
   - Resource optimization suggestions
   - Pods to investigate
   - Potential scaling needs

## Example

**User**: "Show me the health of my Kubernetes cluster"

**Steps**:
1. Run `kubectl cluster-info` to verify connectivity
2. Execute `./.claude/skills/k8s-metrics/scripts/collect-metrics.sh`
3. Run `./.claude/skills/k8s-metrics/scripts/generate-report.py`
4. Parse output and create summary
5. Highlight critical issues
6. Provide actionable recommendations

## Error Handling

- If kubectl not found: Explain that kubectl must be installed
- If cluster unreachable: Check kubeconfig and network connectivity
- If permissions denied: Explain RBAC requirements
- If no pods found: Verify namespace and cluster state
- If metrics-server unavailable: Use basic pod/node stats only

## Advanced Options

Users can request:
- Specific namespace analysis: `--namespace=production`
- Historical comparison: If data is saved, compare with previous runs
- Export to JSON/CSV: For further processing
- Filtering by labels: Focus on specific workloads
