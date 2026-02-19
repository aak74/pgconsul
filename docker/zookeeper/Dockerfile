FROM pgconsulbase:latest
ARG VERSION
ARG OLD_VERSION=""
ENV ZK_VERSION ${VERSION}

RUN apt-get update && apt-get install netcat-openbsd

# Распаковать основную версию
RUN tar -xzf /var/lib/dist/docker/zookeeper/zookeeper-${VERSION}.tar.gz -C /opt && \
    mv /opt/apache-zookeeper-${VERSION}-bin /opt/zookeeper-${VERSION} && \
    cp /var/lib/dist/docker/zookeeper/zoo.cfg /opt/zookeeper-${VERSION}/conf/zoo.cfg && \
    cp /var/lib/dist/docker/zookeeper/pre.sh /opt/zookeeper-${VERSION}/bin/pre.sh && \
    chmod +x /opt/zookeeper-${VERSION}/bin/pre.sh

# Распаковать старую версию (если задана и tar.gz существует)
RUN if [ -n "${OLD_VERSION}" ] && [ -f /var/lib/dist/docker/zookeeper/zookeeper-${OLD_VERSION}.tar.gz ]; then \
        tar -xzf /var/lib/dist/docker/zookeeper/zookeeper-${OLD_VERSION}.tar.gz -C /opt && \
        mv /opt/apache-zookeeper-${OLD_VERSION}-bin /opt/zookeeper-${OLD_VERSION} && \
        cp /var/lib/dist/docker/zookeeper/zoo.cfg /opt/zookeeper-${OLD_VERSION}/conf/zoo.cfg && \
        cp /var/lib/dist/docker/zookeeper/pre.sh /opt/zookeeper-${OLD_VERSION}/bin/pre.sh && \
        chmod +x /opt/zookeeper-${OLD_VERSION}/bin/pre.sh; \
    fi

# Симлинк на текущую рабочую версию
RUN ln -s /opt/zookeeper-${VERSION} /opt/zookeeper

# Supervisor конфиг и логи
RUN sed -i "s/{zk_version}/${VERSION}/g" /var/lib/dist/docker/zookeeper/zookeeper.conf && \
    cp /var/lib/dist/docker/zookeeper/zookeeper.conf /etc/supervisor/conf.d && \
    mkdir -p /var/log/zookeeper
