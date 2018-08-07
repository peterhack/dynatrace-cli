@echo off
rem Use this to run the dtcli.py inside the docker container. all parameters will be passed to the dtcli.py
rem - if dtconfig.json doesnt exist an empty one will be created
rem - the monspec folder will be mapped into the docker container as monspec subfolder
rem here some examples on how to call this script
rem - dtclidocker.bat ent srv SampleService
rem - dtclidocker.bat monspec pull monspec/smplmonspec.json monspec/smplpipelineinfo.json SampleJSonService/Staging 60 0
docker run --name dynatrace-cli -v "%cd%/dtconfig.json":/dtcli/dtconfig.json -v "%cd%/monspec:/dtcli/monspec" -v "%cd%/smpljson":/dtcli/smpljson -w /dtcli -it --rm dynatrace-cli python3 dtcli.py %*