local_run:
	FLASK_APP=fill_app/app.py flask run

build:
	docker build --rm --pull -f "/Users/benoitmoussaud/Workspace/bmoussaud/fill-storage-image/Dockerfile" --label "com.microsoft.created-by=visual-studio-code" -t "fillstorageimage:latest" "/Users/benoitmoussaud/Workspace/bmoussaud/fill-storage-image"


run: build
	docker run --rm  -p 5000:5000/tcp fillstorageimage:latest
