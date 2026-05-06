# kubespray-config

Our customizations on top of vendored Kubespray. The `kubespray/` directory
itself is gitignored (vendored upstream tree).

## Contents

| File | What |
|---|---|
| `cluster.yml` | Wrapper playbook — imports the upstream `playbooks/cluster.yml` then our `argocd-bootstrap.yml` so a single `ansible-playbook` run provisions the cluster AND applies the root ArgoCD app |
| `argocd-bootstrap.yml` | Post-deploy task: installs ArgoCD on the first control-plane node, waits for it, applies `../argocd/root-app.yaml`. Idempotent. |
| `inventory/mycluster/inventory.ini` | Node inventory — three control-plane VMs at `192.168.105.47-49` |
| `inventory/mycluster/group_vars/all/all.yml` | Cluster-wide kubespray vars |
| `inventory/mycluster/group_vars/k8s_cluster/k8s-cluster.yml` | Kubernetes-specific kubespray vars |
| `inventory/mycluster/group_vars/k8s_cluster/addons.yml` | Addons (CNI choice, MetalLB toggle, etc.) |

## How it overlays

After cloning vendored Kubespray into `kubespray/`, copy these files in:

```bash
cp kubespray-config/cluster.yml          kubespray/cluster.yml
cp kubespray-config/argocd-bootstrap.yml kubespray/argocd-bootstrap.yml
cp -R kubespray-config/inventory/mycluster kubespray/inventory/mycluster
```

Then run from the kubespray directory:

```bash
cd kubespray
ansible-playbook -i inventory/mycluster/inventory.ini cluster.yml
```

This single command:

1. Provisions the cluster via Kubespray's `playbooks/cluster.yml`
2. Installs ArgoCD on the first control-plane node
3. Applies `argocd/root-app.yaml`, which cascades into the 18 child Applications

From that point everything is GitOps — no further imperative steps.
