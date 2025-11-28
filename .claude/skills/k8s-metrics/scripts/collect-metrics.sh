#!/bin/bash

# Kubernetes Cluster Metrics Collection Script
# Collects comprehensive metrics about cluster health and resource usage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "  Kubernetes Cluster Metrics Report"
echo "========================================="
echo ""

# Check kubectl availability
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}ERROR: kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}ERROR: Cannot connect to Kubernetes cluster.${NC}"
    echo "Please check your kubeconfig and cluster connectivity."
    exit 1
fi

echo -e "${GREEN}✓ Connected to cluster${NC}"
echo ""

# 1. CLUSTER OVERVIEW
echo -e "${BLUE}=== CLUSTER OVERVIEW ===${NC}"
kubectl version --short 2>/dev/null || kubectl version | head -2
echo ""

# Node count
NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)
echo "Total Nodes: $NODE_COUNT"

# Namespace count
NS_COUNT=$(kubectl get namespaces --no-headers 2>/dev/null | wc -l)
echo "Total Namespaces: $NS_COUNT"

# Total pods
TOTAL_PODS=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l)
echo "Total Pods: $TOTAL_PODS"
echo ""

# 2. NODE STATUS
echo -e "${BLUE}=== NODE STATUS ===${NC}"
kubectl get nodes -o wide
echo ""

echo -e "${BLUE}=== NODE CAPACITY ===${NC}"
kubectl top nodes 2>/dev/null || echo "Note: 'kubectl top nodes' requires metrics-server to be installed"
echo ""

# 3. POD STATUS SUMMARY
echo -e "${BLUE}=== POD STATUS SUMMARY ===${NC}"
echo "Running pods:"
kubectl get pods --all-namespaces --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l

echo "Pending pods:"
kubectl get pods --all-namespaces --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l

echo "Failed pods:"
kubectl get pods --all-namespaces --field-selector=status.phase=Failed --no-headers 2>/dev/null | wc -l

echo "Unknown status pods:"
kubectl get pods --all-namespaces --field-selector=status.phase=Unknown --no-headers 2>/dev/null | wc -l
echo ""

# 4. FAILED OR PROBLEMATIC PODS
echo -e "${BLUE}=== FAILED OR PROBLEMATIC PODS ===${NC}"
echo ""
echo "Pods not in Running state:"
kubectl get pods --all-namespaces --field-selector=status.phase!=Running,status.phase!=Succeeded --no-headers 2>/dev/null || echo "None"
echo ""

echo "Pods with high restart count (>5):"
kubectl get pods --all-namespaces --no-headers 2>/dev/null | awk '$5 > 5 {print $0}' || echo "None"
echo ""

echo "Containers in CrashLoopBackOff:"
kubectl get pods --all-namespaces --no-headers 2>/dev/null | grep CrashLoopBackOff || echo "None"
echo ""

# 5. RESOURCE DISTRIBUTION BY NAMESPACE
echo -e "${BLUE}=== RESOURCE DISTRIBUTION BY NAMESPACE ===${NC}"
echo ""
for ns in $(kubectl get namespaces -o jsonpath='{.items[*].metadata.name}'); do
    POD_COUNT=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
    if [ "$POD_COUNT" -gt 0 ]; then
        echo -e "${GREEN}Namespace: $ns${NC} (Pods: $POD_COUNT)"
        kubectl top pods -n "$ns" 2>/dev/null || echo "  (metrics-server not available)"
        echo ""
    fi
done

# 6. DEPLOYMENTS, STATEFULSETS, DAEMONSETS
echo -e "${BLUE}=== WORKLOAD RESOURCES ===${NC}"
echo ""
echo "Deployments:"
kubectl get deployments --all-namespaces --no-headers 2>/dev/null | wc -l
echo ""

echo "StatefulSets:"
kubectl get statefulsets --all-namespaces --no-headers 2>/dev/null | wc -l
echo ""

echo "DaemonSets:"
kubectl get daemonsets --all-namespaces --no-headers 2>/dev/null | wc -l
echo ""

echo "Jobs:"
kubectl get jobs --all-namespaces --no-headers 2>/dev/null | wc -l
echo ""

# 7. SERVICES
echo -e "${BLUE}=== SERVICES ===${NC}"
echo "Total Services: $(kubectl get services --all-namespaces --no-headers 2>/dev/null | wc -l)"
echo "LoadBalancer Services: $(kubectl get services --all-namespaces --no-headers 2>/dev/null | grep LoadBalancer | wc -l)"
echo "NodePort Services: $(kubectl get services --all-namespaces --no-headers 2>/dev/null | grep NodePort | wc -l)"
echo ""

# 8. PERSISTENT VOLUMES
echo -e "${BLUE}=== STORAGE ===${NC}"
echo "PersistentVolumes: $(kubectl get pv --no-headers 2>/dev/null | wc -l)"
echo "PersistentVolumeClaims: $(kubectl get pvc --all-namespaces --no-headers 2>/dev/null | wc -l)"
echo ""

# 9. EVENTS (Recent errors/warnings)
echo -e "${BLUE}=== RECENT EVENTS (Warnings & Errors) ===${NC}"
kubectl get events --all-namespaces --field-selector type=Warning --sort-by='.lastTimestamp' 2>/dev/null | tail -20 || echo "No recent warnings"
echo ""

# 10. RESOURCE QUOTAS
echo -e "${BLUE}=== RESOURCE QUOTAS ===${NC}"
kubectl get resourcequotas --all-namespaces 2>/dev/null || echo "No resource quotas configured"
echo ""

echo "========================================="
echo "  Report Complete"
echo "========================================="
