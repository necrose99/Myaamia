podman run -d -e JUPYTER_PASSWORD="mypassword" -p 8888:8888 -p 8000:8000 -p 2222:22 -v "${PWD}:/workspace/work" --device nvidia.com/gpu=all --security-opt label=disable unsloth/unsloth
