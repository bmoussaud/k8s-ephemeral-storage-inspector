FROM gcr.io/buildpacks/gcp/run:v1
ENV BS 1M
ENV OUTPUT_DIRECTORY /tmp/filler

# ENV ENGINE K8S
ENV ENGINE LOCAL