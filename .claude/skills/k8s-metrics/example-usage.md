# Kubernetes Metrics Skill - Example Usage

## Quick Start

```bash
# Generate a comprehensive cluster health report
./.claude/skills/k8s-metrics/scripts/generate-report.py
```

This will:
1. Print a human-readable summary to stdout
2. Save detailed JSON to `k8s-metrics.json`

## Example Output

### Human-Readable Report

```
============================================================
  CLUSTER HEALTH SUMMARY
============================================================

Cluster Status: HEALTHY ✓
Health Score: 92.5/100

Nodes: 3/3 Ready
Namespaces: 12
Pods: 47/50 Running
  └─ 2 Failed
  └─ 1 Pending
```

### JSON Report Structure

```json
{
  "generated_at": "2025-11-16T19:45:00.123456",
  "summary": {
    "total_nodes": 3,
    "ready_nodes": 3,
    "total_namespaces": 12,
    "total_pods": 50,
    "running_pods": 47,
    "failed_pods": 2,
    "pending_pods": 1
  },
  "issues": {
    "failed_pods": [
      {
        "namespace": "production",
        "name": "api-server-xyz-abc",
        "phase": "Failed"
      }
    ],
    "pending_pods": [
      {
        "namespace": "staging",
        "name": "worker-123-def",
        "phase": "Pending"
      }
    ],
    "high_restart_pods": [
      {
        "namespace": "production",
        "name": "cache-pod-789",
        "restarts": 12
      }
    ],
    "crashloop_pods": [
      {
        "namespace": "production",
        "name": "cache-pod-789",
        "container": "redis",
        "reason": "CrashLoopBackOff"
      }
    ],
    "failed_containers": [
      {
        "namespace": "production",
        "name": "cache-pod-789",
        "container": "redis",
        "reason": "CrashLoopBackOff"
      }
    ],
    "not_ready_nodes": []
  }
}
```

## Using JSON for Quick Investigation

Once you have the JSON report, you can quickly investigate specific issues:

```bash
# Find all failed pods
cat k8s-metrics.json | jq '.issues.failed_pods'

# Get the first failed pod's details
NAMESPACE=$(cat k8s-metrics.json | jq -r '.issues.failed_pods[0].namespace')
POD=$(cat k8s-metrics.json | jq -r '.issues.failed_pods[0].name')

# Investigate the failed pod
kubectl describe pod $POD -n $NAMESPACE
kubectl logs $POD -n $NAMESPACE
kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | grep $POD
```

## AI Usage Pattern

When Claude uses this skill:

1. **Run the report**: `./.claude/skills/k8s-metrics/scripts/generate-report.py`
2. **Show summary**: Display health score and critical issues to user
3. **Save JSON**: `k8s-metrics.json` contains all specific resource names
4. **Investigate issues**: If user wants details, Claude can:
   - Read specific entries from JSON (low token cost)
   - Run targeted kubectl commands with exact namespace/name
   - No need to search/grep/filter large outputs

## Benefits of JSON Output

1. **Token Efficiency**: Instead of running multiple kubectl commands to find issues, all resource names are in one structured file
2. **Precise Investigation**: Exact namespace and pod names for immediate kubectl commands
3. **Repeatable**: Can compare JSON files over time to track cluster health trends
4. **AI-Friendly**: Structured data is easier to parse than text output

## Integration with Other Tools

The JSON output can be used with:

```bash
# jq for filtering
cat k8s-metrics.json | jq '.issues.crashloop_pods[] | "\(.namespace)/\(.name)"'

# Python for analysis
python3 -c "
import json
with open('k8s-metrics.json') as f:
    data = json.load(f)
    for pod in data['issues']['high_restart_pods']:
        print(f'{pod[\"namespace\"]}/{pod[\"name\"]}: {pod[\"restarts\"]} restarts')
"

# Export to CSV for reporting
cat k8s-metrics.json | jq -r '.issues.failed_pods[] | [.namespace, .name, .phase] | @csv'
```
