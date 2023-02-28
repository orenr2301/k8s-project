# K8s Home Project 

## Author : Oren Rhav 

### Prequisistes

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
  
### k8s Cluster Pre Installtion

Make sure Bastion hosts files has a naming for everyone

![image](https://user-images.githubusercontent.com/117763723/221857982-a233f129-bde4-4363-8ba7-97bba4e8edf4.png)


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

### k8s Cluster Installtion 


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


### Explore Environemt 

To Start Exploring Enviroment we need to load the k8s environment to load it we need the kubeconfig file  
This File is called the kubeconfig 
and the kubespray matter it is creating an admin.conf file at the master node 

**At the bastion server you need to configure the admin conf to connect to the cluster via the master node which is the controlplaine when you are querying for pods, svc etc. 
**


Checking Cluster Connectivity 

1.	Copy the admin.conf file from master node into the bastion-server 
admin.conf is at /etc/Kubernetes at master-node. 
copy it to your bastion host home directory. 

2.	At the bastion server you need to configure the admin conf to connect to the cluster via the master node which is the controlplaine when you are querying for pods, svc etc. 

a. configure the /etc/hosts file and add a name to the master node for convenience
 
b. Then edit admin conf file and adjust the url with the name: 
 
c. Export the admin.conf as KUBECONFIG :
```
export KUBECONFIG=admin.conf 
```

d. now run the following command, and see that you are a running 3 nodes cluster at ready state: 
```
 kubectl get nodes  
```
![image](https://user-images.githubusercontent.com/117763723/221905880-2f0db023-8dab-48e7-98a9-bf3e7c86d910.png)


e. Also Explore you initiative deployment configuration and also make sure pods are running
Execute :
``` 
kubectl get pods -A
```
![image](https://user-images.githubusercontent.com/117763723/221908688-3dfe1181-d03a-4bd7-85fd-61847632c778.png)

On Basic Overall both commands to check the first state 

![image](https://user-images.githubusercontent.com/117763723/221918161-fc492d8f-4bf0-4f20-895f-b14994b3c113.png)

 

### Nginx Ingress Controller Installtion 

After We made Sure cluster is operational and up we need to install the Nginx-Ingress Controller 

In Previous Section you Can see here that im not having an ingress or loadbalcancer to shift traffic inside the Kubernetes cluster.
For that I will be using helm charts to deploy Ingress controller of type Nginx 

```
A Few word about ingress: 
An Ingress in Kubernetes exposes HTTP and HTTPS routes from outside the cluster to services running within the cluster

**Ingress Controller:**
An Ingress controller is what fulfils the Ingress, usually with a load balancer. Below is an example on how an Ingress sends all the client traffic to a Service in Kubernetes Cluster:
Helm Nginx Ingress Controller Deployment 
```

```
1.	Make sure to have helm3 install on the bastion host and master node 

2.	Download latest stable Release of Nginx Ingress Controller:
    # controller_tag=$(curl -s https://api.github.com/repos/kubernetes/ingress-nginx/releases/latest | grep tag_name | cut -d '"' -f 4)
    # wget https://github.com/kubernetes/ingress-nginx/archive/refs/tags/${controller_tag}.tar.gz

3.	Extract The file Downloaded: 
    # tar xvf ${controller_tag}.tar.gz

4. Switch to Directory Created: 
   # cd ingress-nginx-${controller_tag}

5. Change your working directory to charts folder:
   # cd charts/ingress-nginx/

6. Create namespace
   kubectl create namespace ingress-nginx

7. Change values.yaml file to set number of replicas to the number of the node in the envrioments: 


 # vim values.yaml 
 # Change replicas from 1 pod to number of nodes in the case is 3: 
```
change here: At line  809


### Metallb Installtion and Configuration 

### App Deployment 

### App Service Attachment 

### App Ingress Attachment  
