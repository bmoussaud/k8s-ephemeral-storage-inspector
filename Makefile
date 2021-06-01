IMAGE_NAME=bmoussaud/k8s-ephemeral-storage-inspector
IMAGE_VERSION=0.0.3
IMAGE=$(IMAGE_NAME):$(IMAGE_VERSION)
SOURCE_BRANCH=v0.0.1

local_run:
	FLASK_APP=fill_app/app.py flask run

build:
	docker build \
	--label org.label-schema.build-date=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
	--label org.label-schema.vcs-ref=`git rev-parse --short HEAD` \
	--label org.label-schema.vcs-url="https://github.com:bmoussaud/fill-storage-image.git" \
	--label org.label-schema.version="$(SOURCE_BRANCH)" \
	--label org.label-schema.schema-version="1.0" \
	-f . \
	-t $(IMAGE) \
	.

custom_runner:
	docker build -t $(IMAGE_NAME)_run -f run.Dockerfile .

buildpack: custom_runner
	pack build $(IMAGE) --builder=gcr.io/buildpacks/builder:v1  --run-image $(IMAGE_NAME)_run

buildpack_run: buildpack
	docker run -it --rm -e BS=10M -e ENGINE=LOCAL -e PORT=5000 -p 5000:5000 $(IMAGE)

docker-runin: build
	docker run --rm --entrypoint /bin/bash -it $(IMAGE)

dockerhub-push:
	docker push $(IMAGE)

run: build
	docker run --rm -e BS=10M  -e ENGINE=LOCAL -p 5000:5000/tcp $(IMAGE)

apply:
	kubectl apply -f k8s/deploy.yaml -n inspector

apply_sample_app:
	kubectl apply -f k8s/myapp.yaml -n inspector

apply_tkgs:
	kubectl apply -f k8s/deploy_tkgs.yaml -n inspector

delete:
	kubectl delete -f k8s -n inspector

vsphere-login:
	kubectl vsphere login --server=172.17.12.128 --vsphere-username administrator@cpod-tanzu2.az-fkd.cloud-garage.net  --insecure-skip-tls-verify
	kubectl config use-context 172.17.12.128

cluster-login:
	kubectl vsphere login --server 172.17.12.128 --vsphere-username administrator@cpod-tanzu2.az-fkd.cloud-garage.net --insecure-skip-tls-verify --tanzu-kubernetes-cluster-name dev01 --tanzu-kubernetes-cluster-namespace bmoussaud
	kubectl config use-context dev01