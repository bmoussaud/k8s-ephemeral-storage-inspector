DOCKER_USERNAME=yyyy
DOCKER_PASSWORD=xxxxx

install:
	kubectl apply -f kpack-release-0.2.2.yaml

configure: install
	kubectl create secret docker-registry fill-storage-registry-credentials \
    --docker-username=$(DOCKER_USERNAME) \
    --docker-password=$(DOCKER_PASSWORD) \
    --docker-server=https://index.docker.io/v1/ \
    --namespace default

service-account: configure
	kubectl apply -f service-account.yaml

kpack:
	kubectl apply -f store.yaml
	kubectl apply -f stack.yaml
	kubectl apply -f build.yaml
	kubectl apply -f image.yaml
