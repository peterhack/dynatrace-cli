# Use this to run the dtcli.py inside the docker container. all parameters will be passed to the dtcli.py
# - if dtconfig.json doesnt exist an empty one will be created
# - the monspec folder will be mapped into the docker container as monspec subfolder
# here some examples on how to call this script
# - dtclidocker.sh ent srv SampleService
# - dtclidocker.sh monspec pull monspec/smplmonspec.json monspec/smplpipelineinfo.json SampleJSonService/Staging 60 0
sudo docker run --name dynatrace-cli -v "${PWD}/dtconfig.json":/dtcli/dtconfig.json -v "${PWD}/monspec:/dtcli/monspec" -w /dtcli -it --rm dynatrace-cli python3 dtcli.py "$@"