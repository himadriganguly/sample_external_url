# Sample External URL
This is a sample application in **Python** which is collecting external **URL** metrics and producing Prometheus format metrics at the endpoint **/metrics**. Prometheus is collecting the metrics from the endpoint and a dashboard in Grafana is used to display the metrics.

The following **URLS** are being used as demo:-
1. [https://httpstat.us/200](https://httpstat.us/200)
2. [https://httpstat.us/503](https://httpstat.us/503)

The metrics currently being collected are:-
1. **URL response time in milliseconds**
2. **URL status up or down using 1 or 0 respectively**

There is also **Dockerfile** which is converting the **Python** application into a container based application and then the application is being deployed to **K8s** cluster.

## Using The Application For Development
**Python3.9 is required**

0. Clone git repository and enter into the folder
```
git clone https://github.com/himadriganguly/sample_external_url.git
cd sample_external_url
```

1. Create and activate a virtual environment

`Linux`

```
python -m venv venv
source venv/bin/activate
```

`Windows`

```
python -m venv venv
.\venv\Scripts\activate.bat
```

2. Install the required packages inside the environment

```
pip install -r src/requirements-dev.txt
```

3. Run unit-test of the application using **pytest**

```
pytest
```

4. Export environment variables for the application

`Linux`

```
export URLS='https://httpstat.us/503','https://httpstat.us/200'
export TIMEOUT=2
export PORT=8080
```

`Windows`

[https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/set_1](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/set_1)

5. Run the application

```
python src/app.py
```

6. Check the application
Open your browser and point to [http://localhost:8080](http://localhost:8080) you will see a text message.
To see the metrics point your browser to [http://localhost:8080/metrics](http://localhost:8080/metrics)

7. Exit the application
```
Ctrl + c
```
You will see a good bye message.

## Building The Container Image For Production
**Docker is required**

1. Build the Docker image

```
docker build -t sample_external_url .
```

2. Check the application if the container is working perfectly

```
docker run -d -p 8080:8080 --env-file ./env-file --name sample sample_external_url
```
Open your browser and point to [http://localhost:8080](http://localhost:8080) you will see a text message.
To see the metrics point your browser to [http://localhost:8080/metrics](http://localhost:8080/metrics)

3. Create new repository on **DockerHub** or your preferred docker registry.

4. Login to your docker registry in console

```
docker login
```

5. Push the image to **DockerHub** or to your preferred docker registry

```
docker tag sample_external_url:latest [USERNAME]/sample_external_url:latest
docker push [USERNAME]/sample_external_url:latest
```

## Deploy The Application Container Image On K8s Cluster

The folder **k8s** contains the **sample_external_url.yaml** file which contains the code for **Kubernetes** deployment.

The file contains following segments:-

1. **CongfigMap** - This contains all the configuration of the application that is the environment variables.

2. **Deployment** - This contains the **k8s** deployment of the application. The **POD** refers to the **configmap** for the configuration. Image used for the **POD** is **image: himadriganguly/sample_external_url**, change that according to your registry url.

**Note:-** DockerHub URL [https://hub.docker.com/r/himadriganguly/sample_external_url](https://hub.docker.com/r/himadriganguly/sample_external_url)

3. **Service** - This will expose the application as **ClusterIP** on **port 80** and **targetPort 8080**. Change the **targetPort** value according to the **PORT** value in **configmap**.

### Deploy The Application

1. Create a namespace

```
kubectl create ns sample-external-url
```

2. Deploy application in the above created namespace

```
kubectl apply -f k8s/sample_external_url.yaml -n sample-external-url
```

3. Display all the components deployed

```
kubectl get all -n sample-external-url
```

![Kubectl Get All Resources](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/kubectl-get-all.png "Kubectl Get All Resources")

**Note:-** Write down the **CLUSTER-IP** we would need it later.

4. Check the application

```
kubectl port-forward service/sample-external-url-service 8080:80 -n sample-external-url
```
Open your browser and point to [http://localhost:8080](http://localhost:8080) you will see a text message.
To see the metrics point your browser to [http://localhost:8080/metrics](http://localhost:8080/metrics)

## Deploy Prometheus

1. Get Repo Info

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add kube-state-metrics https://kubernetes.github.io/kube-state-metrics
helm repo update
```

2. Install Chart

```
helm install prometheus prometheus-community/prometheus
```

**Note:-** [https://artifacthub.io/packages/helm/prometheus-community/prometheus](https://artifacthub.io/packages/helm/prometheus-community/prometheus)

## Deploy Grafana

1. Get Repo Info

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Install Chart

```
helm install grafana grafana/grafana
```

**Note:-** [https://github.com/grafana/helm-charts/tree/main/charts/grafana](https://github.com/grafana/helm-charts/tree/main/charts/grafana)

3. Get the login username and password

```
kubectl get secrets grafana -o jsonpath='{.data.admin-password}' | base64 --decode | cut -d "%" -f1
kubectl get secrets grafana -o jsonpath='{.data.admin-user}' | base64 --decode | cut -d "%" -f1
```

## Update Prometheus Config To Scrape Metrics From The Application

1. Update configmap for Prometheus

```
kubectl edit cm/prometheus-server
```

2. Add the following config under **scrape_configs**

```
- job_name: 'sample_external'
      static_configs:
      - targets: ['CLUSTER-IP:80']
```
**Note:-** Replace **CLUSTER-IP** with the ip that we noted down earlier. In my case it will be **10.104.174.69**.

## Port Forward Prometheus And Grafana

1. Port forward Prometheus

```
kubectl port-forward service/prometheus-server 9090:80
```

2. Port forward Grafana

```
kubectl port-forward service/grafana 3000:80
```

3. Open Prometheus

Open your browser and point to [http://localhost:9090](http://localhost:9090) you will see **Prometheus UI**.

4. Check Prometheus config

Open your browser and point to [http://localhost:9090](http://localhost:9090) you will see **Prometheus UI**. Go to **Status** > **Configuration** and you can see that your configuration has been added under **scrape_configs:**.

![Prometheus Configuration](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/prometheus-config.png "Prometheus Configuration")

5. Check **Prometheus** metrics collected from our **Application**

![Prometheus External URL Response Milliseconds](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/prometheus-external-url-response-ms-table.png "Prometheus External URL Response Milliseconds")

![Prometheus External URL Response Milliseconds](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/prometheus-external-url-response-ms.png "Prometheus External URL Response Milliseconds")

![Prometheus External URL Up](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/prometheus-external-url-up-table.png "Prometheus External URL Up")

![Prometheus External URL Up](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/prometheus-external-url-up.png "Prometheus External URL Up")

6. Open Grafana

Open your browser and point to [http://localhost:3000](http://localhost:3000) you will see **Grafana Login**.

Enter the **username** and **password** we already collected to login.

## Add Prometheus Data Source To Grafana

1. Open Grafana

Open your browser and point to [http://localhost:3000](http://localhost:3000) you will see **Grafana Login**.

Enter the **username** and **password** we already collected to login.

2. Click on **Configuration** > **Data Sources**

3. Click on **Add data source**

![Grafana Add Data Source](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-configuration.png "Grafana Add Data Source")

4. Select **Prometheus** as the data source

![Grafana Add Data Source Prometheus](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-configuration-add-data-source.png "Grafana Add Data Source Prometheus")

5. Check Prometheus cluster ip

```
kubectl get svc
```

**Note:-** Write down the **ClusterIP** for **prometheus-server**

![Kubectl Get Prometheus Cluster IP](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/kubectl-get-svc.png "Kubectl Get Prometheus Cluster IP")

6. Add the **ClusterIP** as the **Prometheus** url

![Grafana Add Data Source Prometheus IP](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-configuration-add-data-source-prometheus.png "Grafana Add Data Source Prometheus IP")

7. Click **Save & Test**


## Import Grafana Dashboard

1. Click on **Create** > **Import**

2. Click on **Upload JSON file** and select the file from the **grafana** folder within this repository.

![Import Grafan Dashboard Step1](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-import-dashboard1.png "Import Grafan Dashboard Step1")

![Import Grafan Dashboard Step2](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-import-dashboard2.png "Import Grafan Dashboard Step2")

3. Click on **Import** button it will create the dashboard with the **Prometheus** metrics.

![Import Grafan Dashboard Step3](https://raw.githubusercontent.com/himadriganguly/sample_external_url/main/screenshots/grafan-import-dashboard3.png "Import Grafan Dashboard Step3")

test2
