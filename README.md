# K8s Home Project 

## Author : Oren Rhav 

### Prequisistes
<details><summary>SHOW</summary>
<p>
Installation method: Kubespray 
3 nodes cluster 
1 bastion 
OS Ubuntu 20.04 
CPU: 4
RAM: 8


On bastion:
update and upgrade 
Installed Ansible 2.11+ and jinja2 version 2.11+ 
made sure I’m able to ssh without password by copy the keys to the ansible hosts 
hosts in etc/hosts are published in each node

On nodes: 
update and upgrade 
put user into sudoers
made sure they are having internet connection 
</p>
</details>  
### k8s Cluster Pre Installtion
<details><summary>SHOW</summary>
<p>
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
</p>
</details> 
### k8s Cluster Installtion 
<details><summary>SHOW</summary>
<p>

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

</p>
</details> 
### Explore Environemt 
<details><summary>SHOW</summary>
<p>
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

 </p>
</details> 
### Nginx Ingress Controller Installtion 
<details><summary>SHOW</summary>
<p>
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
![image](https://user-images.githubusercontent.com/117763723/221919530-1a3fb667-1090-4e42-97c4-21aaeaff89ed.png)
And Here: At line 310
![image](https://user-images.githubusercontent.com/117763723/221919581-5433431f-b3b5-4940-afc6-7b78631ca3c5.png)


```
8. Deploy the nginx-controller:
    # helm install -n ingress-nginx ingress-nginx  -f values.yaml .
```
9. You should be getting the following output: 
![image](https://user-images.githubusercontent.com/117763723/221920107-4aacd21d-5a23-42e8-a6c6-3d7ce8305aab.png)

10 .Check al ingress-nginx namespace resource
```
kubectl get all -n ingress-nginx 
```

11. Make sure all ingress-controller pods are running
```
kubectl get pod -n ingress-nginx 
```
In my Case 3 pods  are running as I specified (having 1 master and 2 workers) : 
![image](https://user-images.githubusercontent.com/117763723/221920675-66b69a30-5ef9-43c6-962a-d5eac500b711.png)
</p>
</details> 
### Metallb Installtion and Configuration 
<details><summary>SHOW</summary>
<p>
By Default The Above Helm Chart Executed comes with LoadBalancer Service type for the ingress-nginx-controller. I decied to stick with it and not using the nodePort Method 
There fore i will be needed an upper level plugin for that service. 
Therefor  i will be using the metallb plugin to have that loadbalancer we need.

```
1.	Install metallb 
a. Get the latest MetalLB release tag:
 #   MetalLB_RTAG=$(curl -s https://api.github.com/repos/metallb/metallb/releases/latest|grep tag_name|cut -d '"' -f 4|sed 's/v//')
# echo $MetalLB_RTAG

b . create a directory for metallb 
   # mkdir metallb
   # cd metallb 

c. download the installation manifest: 
# wget \  https://raw.githubusercontent.com/metallb/metallb/v$MetalLB_RTAG/config/manifests/metallb-native.yaml

d. install it over the k8s cluster 
  #   kubectl apply -f metallb-native.yaml

You should  be be getting the following output : 
**namespace/metallb-system created
customresourcedefinition.apiextensions.k8s.io/addresspools.metallb.io created
customresourcedefinition.apiextensions.k8s.io/bfdprofiles.metallb.io created
customresourcedefinition.apiextensions.k8s.io/bgpadvertisements.metallb.io created
customresourcedefinition.apiextensions.k8s.io/bgppeers.metallb.io created
customresourcedefinition.apiextensions.k8s.io/communities.metallb.io created
customresourcedefinition.apiextensions.k8s.io/ipaddresspools.metallb.io created
customresourcedefinition.apiextensions.k8s.io/l2advertisements.metallb.io created
serviceaccount/controller created
serviceaccount/speaker created
role.rbac.authorization.k8s.io/controller created
role.rbac.authorization.k8s.io/pod-lister created
clusterrole.rbac.authorization.k8s.io/metallb-system:controller created
clusterrole.rbac.authorization.k8s.io/metallb-system:speaker created
rolebinding.rbac.authorization.k8s.io/controller created
rolebinding.rbac.authorization.k8s.io/pod-lister created
clusterrolebinding.rbac.authorization.k8s.io/metallb-system:controller created
clusterrolebinding.rbac.authorization.k8s.io/metallb-system:speaker created
secret/webhook-server-cert created
service/webhook-service created
deployment.apps/controller created
daemonset.apps/speaker created
validatingwebhookconfiguration.admissionregistration.k8s.io/metallb-webhook-configuration created**

2.	Check and list running pods 
root@bastion-dev:/home/kubeadmin/manifests# kubectl get pods -n metallb-system
NAME                          READY   STATUS    RESTARTS   AGE
controller-68bf958bf9-gbt2d   1/1     Running   0          77m
speaker-bgtdh                 1/1     Running   0          77m
speaker-gcsml                 1/1     Running   0          77m
speaker-jtwqf                 1/1     Running   0          77m
```
Now Create the LoadBalancer Service Pool of ip Address

```
vim/nano ip_pooladdresses.yaml

apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: production
   namespace: metallb-system
spec:
  addresses:
   - 192.168.1.52-192.168.1.55
- - -
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2-advert
  namespace: metallb-system
``` 
Now it will allocates any ip from that pool, since only my workers IP's are in there it will allocates 192.168.1.52 and 192.168.1.53

Apply ip-pool object 

```
kubectl create -f  ipaddress_pools.yaml
```

All is left is to connect the Ingress-controller to metallb since the ingress-controller's service is LoadBlancer type

```
1. I Patched the Ingress to the loadBalancer just to make sure it is in the correct service 
  # kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p '[{"op":"replace","path":"/spec/type","value":"LoadBalancer"}]'

got the following output: 
service/ingress-nginx-controller patched (no change) 

```
**service was already on LoadBlancer Type 
I wasn’t deployed ingress-nginx-controller with nodeport service type**

All patched together and IPs have been assinged, we can now proceed to build and deploy our app 
</p>
</details> 

### App Deployment 

1.	In order to have the app over k8s you need a docker image when deploying the pods.
    When deploying pods with containers in it they will need an image which holds your app. 

    For this to happen you will have to create a dockerfile and from it to build the the image


1. create a directory, which in this diractory you will store all the application filesystem and code. 
2. cd to that Directory after done with building the code and app FS, and in that directore create a Dockerfile to hold up your application to an image
** Of Course make sure you have docker-ce installed on your host**

3. Execute the following: 

```
"docker build  <registry-user-name>/<name-of-repository>:<tag> ." (don’t forget the dot)
```

For example in my case:

```
 docker build orenrahav/flask-app:test-v1 .
```

Then Push it to your registry - make sure you are logged in before doing this 

```
"docker push <image-name>:<tage>  == docker push <registry-user-name>/<name-of-repository>:<tag>"
```
In this case i was able to jump over the image tagging stage

My Docker registry image wich i pushed 
![image](https://user-images.githubusercontent.com/117763723/221927565-0a13f64e-abd2-4ce2-b4f3-38d55869a1f8.png)

Now We can deploy our app, i decided to deploy it all over the node workes and masters

Beware that in here i have deployed the pods services and ingress in a namespace called **tbd** i wanted to todo it as **TBD**, but k8s doesnt except UPPER case
due to one of their RFC's

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
  namespace: tbd
spec:
   replicas: 3
   selector:
      matchLabels:
        app: flask
        dev: test
   template:
     metadata:
       labels:
         app: flask
         dev: test
     spec:
       containers:
       - name: flask-cont
         image: orenrahav/flask-app:test-v1
         ports:
         - containerPort: 8080
```

![image](https://user-images.githubusercontent.com/117763723/221928916-e7859c96-b700-45a6-a46c-931acc002eb4.png)

I have told in the end since my app in the end using port 8080 i was telling container inside the pod to communicate over port 8080


### App Service Attachment 
<details><summary>SHOW</summary>
<p>

Now we need to expose out pods to the cluster network 
Therfore we will assign as service to those pods: 

They way it is assigning them its by labels - look at previous section at the deployment file, and see the labels i have attached to the pods
app=flask and dev=test

Below the service yaml file for it

```
apiVersion: v1
kind: Service
metadata:
   name: flask-service
   namespace: tbd
spec:
   selector:
     app: flask
     dev: test
   ports:
   - protocol: TCP
     port: 8080
     targetPort: 8080
   type: ClusterIP
```

The Service should be of type ClusterIP, dont forget i have an ingress which will get the request for the app and communicate it back to the service and from service to pods. 

</p>
</details>
### App Ingress Attachment  
<details><summary>SHOW</summary>
<p>
For the Most cruical part, the ingress-nginx deployment

For us to get to the app which relies inside the pods we need an ingress to catch out requeste/traffic and deliver it inside to the cluster from outside the cluster
I will assing the ingress backend to the pods service whci i have assigned previously and also give it a host/domain to direct my reuqest

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: flask-ingress
  namespace: tbd
spec:
  ingressClassName: nginx
  rules:
  - host: flask-demo.apps.cluster.local
    http:
     paths:
     - path: /
       pathType: Prefix
       backend:
        service:
          name: flask-service
          port:
           number: 8080
```

In this exmaple i have told ingress to take request over http(port 80)
In order for me to do this i cannot just get in, i will need to use the host name i provided to the app which the ingress will expect to get the request from. 

The URL i will put in the browser will be: 
```
flask-demo.apps.cluster.local
```

Since im not having a core network or external IP to translate my request, i will use my local computer dns and edit the host file to be: 

```
 192.168.1.52 flask-demo.apps.cluster.local 
 192.168.1.53 flask-demo.apps.cluster.local
```
I can do only once since my ingress can get request from both ends

Now putting the URL in my brower (i have used chrome in icgonito for not store cache) got me the expected result and im able to get into my app from outside the cluster!

![image](https://user-images.githubusercontent.com/117763723/221932769-e71626c1-f92f-4ed5-943c-b93222483031.png)

</p>
</details>
