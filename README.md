# k8s-project![image]
Cluster Installation:

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



Installation Preparation 
Git clone the kubespray github project.

Creating the cluster inventory hosts: 
# cp -r inventory/sample inventory/dev-cluter
# declare -a IPS=(192.168.1.51 192.168.1.52 192.168.1.53)
# CONFIG_FILE=inventory/dev-cluter/hosts.yml python3 contrib/inventory_builder/inventory.py ${IPS[@]}

Expected Output: 
 


Inventory should look like this: 
 

Apply ipv4 network routing capabilities and load on each host:
#sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf && sysctl -p

Change Add-ons values.  
# vim inventory/dev-cluter/group_vars/k8s_cluster/addons.yml
Get all lines approved: 
#cat inventory/dev-cluter/group_vars/k8s_cluster/addons.yml  | grep -v '#' | grep -v 'false' | awk NF

 


Modify the k8s cluster yaml configurations: 
# vim inventory//dev-cluter/group_vars/k8s_cluster/k8s-cluster.yml


Make sure to consisting the following in the yaml.
 CNI, cluster name, pod and services subnets, and the container runtime manager, Arp strict in case of metallb, also apply multus as it better of with it and doesn’t bother the CNI itself

#vi inventory/hotmobile/group_vars/k8s_cluster/k8-cluster.yml
kube_version: v1.26.1
kube_network_plugin: calico
kube_network_plugin_multus: true
container_manager: crio
kube_proxy_strict_arp: true
kubeconfig_localhost: true
cluster_name: cluster.local (can other name you want like home.local or cluster.home.net)

Before Running the installation please make sure firewall or Iptables are not running on any host: 
If running on Ubuntu then do: 
# systemctl disable –now ufw

Running the cluster Installtion Playbook:
Lets check ping are successful from host/bastion server 
# ansible -i inventory/dev-cluter/hosts.yml all -m ping -b -u kubeadmin | grep SUCCESS
If All is good then run the playbook ansible version must be running ansible between 2.11 to 2.13 versions 
# ansible-playbook -i inventory/dev-cluter/hosts.yml cluster.yml -u kubeadmin -b

Installation runs between 20 to 30 minutes















Checking Cluster Connectivity 

1.	Copy the admin.conf file from master node into the bastion-server 
admin.conf is at /etc/Kubernetes copy it to your home directory. 
2.	At the bastion server you need to configure the admin conf to connect to the cluster via the master node which is the controlplaine when you are querying for pods, svc etc. 
a. configure the /etc/hosts file and add a name to the master node for convenience
 
b. Then edit admin conf file and adjust the url with the name: 
 
c. Export the admin.conf as KUBECONFIG :
# export KUBECONFIG=admin.conf 
d. now run the following command: 
# kubectl get nodes and Voiala you have a running 3 nodes cluster: 
  


Configuring Helm:
On installation, you have enabled helm. 
On the bastion host helm is yet configured and you would like to match the same version as the master node 

1. Go to master node and type helm version –short 
2. Go to Helm Releases on github  - https://github.com/helm/helm/releases 
3. Find the right version and package that comply with your server OS and Architecture 
 
4. Download the package straight to bastion server in case you have internet access
# wget https://get.helm.sh/helm-v3.10.3-linux-amd64.tar.gz 
5. Extract tar.gz file 
# tar -zxvf helm-v3.10.3-linux-amd64.tar.gz
6. Move helm binaries under /usr/local/bin 
# mv linux-amd64/helm /usr/local/bin/helm
 




















After Deployment has Ended now I can check the k8s cluster: 

Checking nodes and Pods are running as expected: 
 

you Can see here that im not having an ingress or loadbalcancer to shift traffic inside the Kubernetes cluster. Here fore I will be using helm charts to deploy Ingress controller of type Nginx 

A Few word about ingress: 
An Ingress in Kubernetes exposes HTTP and HTTPS routes from outside the cluster to services running within the cluster

Ingress Controller:
An Ingress controller is what fulfils the Ingress, usually with a load balancer. Below is an example on how an Ingress sends all the client traffic to a Service in Kubernetes Cluster:
Helm Nginx Ingress Controller Deployment 


For the standard HTTP and HTTPS traffic, an Ingress Controller will be configured to listen on ports 80 and 443. It should bind to an IP address from which the cluster will receive traffic from. A Wildcard DNS record for the domain used for Ingress routes will point to the IP address(s) that Ingress controller listens on.




Helm Nginx Ingress Controller
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
     # kubectl create namespace ingress-nginx

7. Change values.yaml file to set number of replicas to the number of the node in the envrioments: 

# vim values.yaml 
#  Change replicas from 1 pod to number of nodes in the case is 3: 
change here: At line  809
 
And Here: At line 310
 


8. Deploy the nginx-controller:
    # helm install -n ingress-nginx ingress-nginx  -f values.yaml .
9. You should be getting the following output: 
 

10. Execute kubectl get all -n ingress-nginx to checkout all nginx-ingress resource
11. Then Execute kubectl get pod -n ingress-nginx to make sure that there are exactly the number of ingress-controller pods specified.  

In my Case 3 pods  are running as I specified : 
 










Important Note to make, 
When installing the Helm chart of the Nginx-controller, In order for the externalIP expose it uses 
service of type loadbalancer by default configuration, if not have a loadbalancer in your environment then use nodePort service for your application. So at the ingress level the backend service will be that particular nodePort service. 

Now we Wouldn’t like to execute a nodePort to any new app that comes along the way.
 Since it will bid us extend another port of the node. And do ppre-allocationsand more. 


Therefore we will be Install Metallb to have that loadBalancer we need 


I didn’t want to use nodeport for that method of exposing in order to get the app at the ingress level Therefore I have connected the loadbalancer external ip to worker IPs. 



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
namespace/metallb-system created
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
validatingwebhookconfiguration.admissionregistration.k8s.io/metallb-webhook-configuration created

2.	Check and list running pods 
root@bastion-dev:/home/kubeadmin/manifests# kubectl get pods -n metallb-system
NAME                          READY   STATUS    RESTARTS   AGE
controller-68bf958bf9-gbt2d   1/1     Running   0          77m
speaker-bgtdh                 1/1     Running   0          77
speaker-gcsml                 1/1     Running   0          77m
speaker-jtwqf                 1/1     Running   0          77m


Now Create the LoadBalancer Service Pool of ip Address 
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

Apply ip-pool and file
# kubectl create -f  ipaddress_pools.yaml




Now  we need to connect the ingress to the metallb since the ingress-controller service is LoadBlancer Type 

1. I Patched the Ingress to the loadBalancer just to make sure it is in the correct service 
  # kubectl -n ingress-nginx patch svc ingress-nginx-controller --type='json' -p '[{"op":"replace","path":"/spec/type","value":"LoadBalancer"}]'

got the following output: 
service/ingress-nginx-controller patched (no change) – service was already on LoadBlancer Type 
* I wasn’t deployed ingress-nginx-controller with nodeport service type”



























Creating the App: 

1.	In order to create the app you need a docker file when deploying the pods then you will have the image for the containers. 

After Creating and Establishing everything I need im now ready to building my image with docker build command 

a. cd to the directory where the dockerfile is located 
     # docker build  <registry-user-name>/<name-of-repository>:<tag> . (don’t forget the dot)
     * in my case It was docker build orenrahav/flask-app:test-v1 .* (don’t forget the dot)
      Push Image to registry – make sure you are logged in before pushing 
     # docker push <image-name>:<tage> 
     for example docker push orenrahav/flask-app:test-v1
    

Building the deployment service and ingress 
you can deploy it separately in different yaml
also for this project I have created a namespace called tbd to assing to the application  
Go to the Deployment yaml I created and see how to build it
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
--- 
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
--- 
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


Now go to the browser, take the domain name you created in the ingress manifest for taking the request
In that case we have exposed via ingress port 80 

so we will attach the url name  with http://flask-demo.apps.cluster.local

And get the following: 
 In here We see that we have succeeded and reached the application we be built



