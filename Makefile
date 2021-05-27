IMAGE_NAME=bmoussaud/fillstorage
IMAGE_VERSION=0.0.1
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

docker-runin: build
	docker run --rm --entrypoint /bin/bash -it $(IMAGE)

dockerhub-push: build
	docker push $(IMAGE)

run: build
	docker run --rm -e BS=10M  -e ENGINE=LOCAL -p 5000:5000/tcp $(IMAGE)

apply:
	kubectl apply -f k8s -n filler

delete:
	kubectl delete -f k8s -n filler