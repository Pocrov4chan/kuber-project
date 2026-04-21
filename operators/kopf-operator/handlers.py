import kopf
from kubernetes import client

GROUP = "platform.pocrov4chan.io"
VERSION = "v1"

SYSTEM_NAMESPACES = {
    "kube-system", "kube-public", "kube-node-lease",
    "argocd", "monitoring", "longhorn-system",
    "vpa", "sealed-secrets", "platform-system", "default",
}


@kopf.on.create(GROUP, VERSION, "debugsessions")
def create_debug_session(spec, name, namespace, body, logger, **_):
    pod_name = spec["podName"]
    target_port = spec["targetPort"]

    v1 = client.CoreV1Api()
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    selector = pod.metadata.labels or {}
    if not selector:
        raise kopf.PermanentError(
            f"pod {pod_name} has no labels; cannot build a Service selector"
        )

    svc_name = f"debug-{name}"
    svc = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=svc_name,
            namespace=namespace,
            owner_references=[client.V1OwnerReference(
                api_version=f"{GROUP}/{VERSION}",
                kind="DebugSession",
                name=name,
                uid=body["metadata"]["uid"],
                block_owner_deletion=True,
                controller=True,
            )],
        ),
        spec=client.V1ServiceSpec(
            type="NodePort",
            selector=selector,
            ports=[client.V1ServicePort(port=target_port, target_port=target_port)],
        ),
    )
    created = v1.create_namespaced_service(namespace=namespace, body=svc)
    node_port = created.spec.ports[0].node_port
    logger.info(f"exposed pod {pod_name} via NodePort {node_port} as Service {svc_name}")

    return {"serviceName": svc_name, "nodePort": node_port}


@kopf.on.create("namespaces")
@kopf.on.resume("namespaces")
def bootstrap_namespace_rbac(name, logger, **_):
    if name in SYSTEM_NAMESPACES:
        logger.info(f"skipping system namespace {name}")
        return

    rbac = client.RbacAuthorizationV1Api()
    for role in ("view", "edit", "admin"):
        rb = client.V1RoleBinding(
            metadata=client.V1ObjectMeta(name=f"{role}-binding", namespace=name),
            role_ref=client.V1RoleRef(
                api_group="rbac.authorization.k8s.io",
                kind="ClusterRole",
                name=role,
            ),
            subjects=[client.RbacV1Subject(
                kind="Group",
                name=f"platform:{role}",
                api_group="rbac.authorization.k8s.io",
            )],
        )
        try:
            rbac.create_namespaced_role_binding(namespace=name, body=rb)
            logger.info(f"created RoleBinding {role}-binding in {name}")
        except client.exceptions.ApiException as e:
            if e.status == 409:
                logger.info(f"RoleBinding {role}-binding already exists in {name}")
            else:
                raise
