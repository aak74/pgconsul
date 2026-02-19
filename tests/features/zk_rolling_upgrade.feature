Feature: ZooKeeper rolling upgrade
    pgconsul should survive rolling upgrade of ZooKeeper cluster
    from 3.7.2 to 3.9.4 without false failovers or data loss

    Background:
        Given a "pgconsul" container common config
        """
            pgconsul.conf:
                global:
                    priority: 0
                    use_replication_slots: 'yes'
                    quorum_commit: 'yes'
                primary:
                    change_replication_type: 'yes'
                    change_replication_metric: 'count'
                replica:
                    allow_potential_data_loss: 'no'
                    primary_switch_checks: 1
                    primary_unavailability_timeout: 2
                    min_failover_timeout: 1
                commands:
                    rewind: /usr/local/bin/pg_rewind.sh %m %p
        """
        Given a following cluster with "zookeeper" with replication slots
        """
            postgresql1:
                role: primary
            postgresql2:
                role: replica
                config:
                    pgconsul.conf:
                        global:
                            priority: 2
            postgresql3:
                role: replica
                config:
                    pgconsul.conf:
                        global:
                            priority: 1
        """
        Then zookeeper "zookeeper1" has holder "pgconsul_postgresql1_1.pgconsul_pgconsul_net" for lock "/pgconsul/postgresql/leader"
        Then container "postgresql2" is in quorum group
        Then container "postgresql2" is a replica of container "postgresql1"
        Then container "postgresql3" is a replica of container "postgresql1"
        Then pgbouncer is running in container "postgresql1"
        Then pgbouncer is running in container "postgresql2"
        Then pgbouncer is running in container "postgresql3"

    @zk_rolling_upgrade
    Scenario: Rolling upgrade ZK 3.7.2 to 3.9.4 - cluster stays healthy
        # Переводим все ZK-ноды на старую версию 3.7.2
        When we switch zookeeper in container "zookeeper1" to version "3.7.2"
        And we switch zookeeper in container "zookeeper2" to version "3.7.2"
        And we switch zookeeper in container "zookeeper3" to version "3.7.2"
        And we wait "15.0" seconds
        Then zookeeper "zookeeper1" node is alive
        And zookeeper "zookeeper2" node is alive
        And zookeeper "zookeeper3" node is alive
        And zookeeper "zookeeper1" is running version "3.7.2"
        # PG cluster should be stable on old ZK
        And zookeeper "zookeeper1" has holder "pgconsul_postgresql1_1.pgconsul_pgconsul_net" for lock "/pgconsul/postgresql/leader"
        And container "postgresql2" is a replica of container "postgresql1"
        And container "postgresql3" is a replica of container "postgresql1"

        # --- Rolling upgrade: нода 1 ---
        When we switch zookeeper in container "zookeeper1" to version "3.9.4"
        And we wait "10.0" seconds
        Then zookeeper "zookeeper1" node is alive
        And zookeeper "zookeeper1" is running version "3.9.4"
        # PG cluster should be stable (проверяем через живую ноду)
        And zookeeper "zookeeper2" has holder "pgconsul_postgresql1_1.pgconsul_pgconsul_net" for lock "/pgconsul/postgresql/leader"
        And container "postgresql2" is a replica of container "postgresql1"
        And container "postgresql3" is a replica of container "postgresql1"
        And pgbouncer is running in container "postgresql1"
        And pgbouncer is running in container "postgresql2"
        And pgbouncer is running in container "postgresql3"

        # --- Rolling upgrade: нода 2 ---
        When we switch zookeeper in container "zookeeper2" to version "3.9.4"
        And we wait "10.0" seconds
        Then zookeeper "zookeeper2" node is alive
        And zookeeper "zookeeper2" is running version "3.9.4"
        And zookeeper "zookeeper1" has holder "pgconsul_postgresql1_1.pgconsul_pgconsul_net" for lock "/pgconsul/postgresql/leader"
        And container "postgresql2" is a replica of container "postgresql1"
        And container "postgresql3" is a replica of container "postgresql1"
        And pgbouncer is running in container "postgresql1"
        And pgbouncer is running in container "postgresql2"
        And pgbouncer is running in container "postgresql3"

        # --- Rolling upgrade: нода 3 (последняя) ---
        When we switch zookeeper in container "zookeeper3" to version "3.9.4"
        And we wait "10.0" seconds
        Then zookeeper "zookeeper3" node is alive
        And zookeeper "zookeeper3" is running version "3.9.4"
        # Весь ZK-кластер на 3.9.4 — финальная проверка
        And zookeeper "zookeeper1" has holder "pgconsul_postgresql1_1.pgconsul_pgconsul_net" for lock "/pgconsul/postgresql/leader"
        And container "postgresql2" is in quorum group
        And container "postgresql3" is in quorum group
        And container "postgresql2" is a replica of container "postgresql1"
        And container "postgresql3" is a replica of container "postgresql1"
        And pgbouncer is running in container "postgresql1"
        And pgbouncer is running in container "postgresql2"
        And pgbouncer is running in container "postgresql3"
        When we wait "120.0" seconds
        And we wait "120.0" seconds
        And we wait "120.0" seconds
        And we wait "120.0" seconds
        And we wait "120.0" seconds
        And we wait "12000.0" seconds
