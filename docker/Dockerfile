FROM kuralabs/python3-dev:latest
LABEL mantainer="info@kuralabs.io"

USER root


# Install supervisord
RUN apt-get update && apt-get --yes install \
        supervisor dirmngr apt-transport-https


# Install mongodb
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6 && \
    echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb.list && \
    apt-get update && apt-get install --yes \
        mongodb-org


# Install InfluxDB
RUN curl --location https://repos.influxdata.com/influxdb.key | apt-key add - && \
    echo "deb https://repos.influxdata.com/ubuntu zesty stable" | tee /etc/apt/sources.list.d/influxdb.list && \
    apt-get update && apt-get install --yes \
        influxdb


# Install component dependencies
RUN apt-get update && apt-get install --yes \
        lcov


# Configure and start supervisord
COPY supervisord/*.conf /etc/supervisor/conf.d/
COPY entrypoint.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
