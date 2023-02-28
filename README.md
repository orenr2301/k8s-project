# K8s Home Project 

# Author : Oren Rhav 

# Prequisistes

Installation method: Kubespray 
3 nodes cluster 
1 bastion 

On bastion:
update and upgrade 
Installed Ansible 2.11+ and jinja2 version 2.11+ 
made sure I’m able to ssh without password by copy the keys to the ansible hosts 
hosts in etc/hosts are published in each node

On nodes: 
update and upgrade 
put user into sudoers
made sure they are having internet connection 
  
# k8s Cluster Pre Installtion

Git clone the kubespray github project.

Creating the cluster inventory hosts: 
- cp -r inventory/sample inventory/dev-cluter
- declare -a IPS=(192.168.1.51 192.168.1.52 192.168.1.53)  < put here the nodes IP for the cluster 
- CONFIG_FILE=inventory/dev-cluter/hosts.yml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
look at below image for expeted output : 
![image](https://user-images.githubusercontent.com/117763723/221852389-b4748696-f106-4cee-9e69-ce8c284b9edb.png)

Inverntory should look like this: 
```
all:
  hosts:
    master-dev-1:
      ansible_host: 192.168.1.51
      ip: 192.168.1.51
      access_ip: 192.168.1.51
    worker-dev-01:
      ansible_host: 192.168.1.52
      ip: 192.168.1.52
      access_ip: 192.168.1.52
    worker-dev-02:
      ansible_host: 192.168.1.53
      ip: 192.168.1.53
      access_ip: 192.168.1.53
  children:
    kube_control_plane:
      hosts:
        master-dev-01:
    kube_node:
      hosts:
        master-dev-01:
        worker-dev-01:
        worker-dev-02:
    etcd:
      hosts:
        master-dev-01:
    k8s_cluster:
      children:
        kube_control_plane:
        kube_node:
    calico_rr:
      hosts: {}
```

Apply ipv4 network routing capabilities and load on each host:

```
sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && sysctl -p
```

Change Addons values 

```
vim inventory/dev-cluter/group_vars/k8s_cluster/addons.yml
```

Get all lines approved make sure not missed anything you wanted to add: 

```
cat inventory/dev-cluter/group_vars/k8s_cluster/addons.yml  | grep -v '#' | grep -v 'false' | awk NF

dashboard_enabled: true
helm_enabled: true
metrics_server_enabled: true
ingress_publish_status_address: ""
krew_root_dir: "/usr/local/krew"
```

**Ingress -Controller is enabled by default to get install so make sure to put set false instead of true **

```
ingress_nginx_enabled = flase
```


Modify the k8s-cluster-yaml Configurations under inventory/youprojectName/group_vars/k8s_cluster-k8s-cluter.yaml
CNI, cluster name, pod and services subnets, and the container runtime manager, Arp strict in case of metallb, also apply multus as it better of with it and doesn’t bother the CNI itself

For exmaple: 

```
kube_version: v1.26.1
kube_network_plugin: calico
container_manager: crio
kube_proxy_strict_arp: true 
kubeconfig_localhost: true
cluster_name: cluster.local (can other name you want like home.local or cluster.home.net)
```

# k8s Cluster Installtion 


**Before Running the installation please make sure firewall or Iptables are not running on any host: 
If running on Ubuntu then do: **


Lets check ping are successful from host/bastion server 

```
ansible -i inventory/<yourProjectName>/hosts.yml all -m ping -b -u kubeadmin | grep SUCCESS
```

If All is good then run the playbook ansible version must be running ansible between 2.11 to 2.13 versions 


**Now Run The Installtion **

```
ansible-playbook -i inventory/dev-cluter/hosts.yml cluster.yml -u kubeadmin -b
```


**Installation runs between 20 to 30 minutes **


# Explore Environemt 

# Nginx Ingress Controller Installtion 

# Metallb Installtion and Configuration 

# App Deployment 

# App Service Attachment 

# App Ingress Attachment  
