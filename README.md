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
'''
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
'''

# k8s Cluster Installtion 

# Explore Environemt 

# Nginx Ingress Controller Installtion 

# Metallb Installtion and Configuration 

# App Deployment 

# App Service Attachment 

# App Ingress Attachment  
