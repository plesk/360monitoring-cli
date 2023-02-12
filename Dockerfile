FROM ubuntu

RUN apt-get update && apt-get -y install python3 && apt-get -y install pip
RUN pip install 360monitoringcli

COPY cli360monitoring/test_cli.sh /

ENV api-key=""

#ENTRYPOINT [ "360monitoring", "config", "save", "--api-key" ]
CMD ["sh", "-c", "360monitoring config save --api-key ${api-key};360monitoring sites list;./test_cli.sh"]
