"""
src/kafka/consumer.py - Consumidor de Apache Kafka en Python para anuncios inmobiliarios.

Se suscribe al tópico de anuncios, valida su formato contra el modelo HousingAd,
gestiona errores de deserialización y registra los datos procesados en tiempo real.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Callable
from src.extraction.models import HousingAd
from .mock_broker import InMemoryKafkaBroker


class HousingKafkaConsumer:
    """Consumidor de Kafka para recibir e inspeccionar anuncios inmobiliarios."""

    DEFAULT_TOPIC = "euskadi-anuncios-inmobiliarios"
    DEFAULT_GROUP = "euskadi-vivienda-consumidores"

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        group_id: Optional[str] = None,
        simulation_mode: Optional[bool] = None
    ):
        self.bootstrap_servers = bootstrap_servers or os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = topic or os.environ.get("KAFKA_TOPIC", self.DEFAULT_TOPIC)
        self.group_id = group_id or os.environ.get("KAFKA_CONSUMER_GROUP", self.DEFAULT_GROUP)

        env_sim = os.environ.get("KAFKA_SIMULATION_MODE", "").lower() in ("true", "1", "yes")
        self.simulation_mode = simulation_mode if simulation_mode is not None else env_sim

        self._real_consumer = None
        self._mock_broker: Optional[InMemoryKafkaBroker] = None

        if not self.simulation_mode:
            self._init_real_consumer()

        if self._real_consumer is None:
            self.simulation_mode = True
            self._mock_broker = InMemoryKafkaBroker.get_broker(self.topic)

    def _init_real_consumer(self):
        """Intenta conectarse al broker real de Kafka."""
        try:
            from kafka import KafkaConsumer
            self._real_consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers.split(","),
                group_id=self.group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                consumer_timeout_ms=3000,
                value_deserializer=None
            )
        except Exception as error:
            raise ConnectionError("Kafka no disponible; la simulacion debe ser explicita") from error

    def consume_batch(
        self,
        max_messages: int = 10,
        timeout_seconds: float = 2.0,
        on_message_callback: Optional[Callable[[HousingAd, int], None]] = None
    ) -> List[HousingAd]:
        """
        Consume hasta max_messages del tópico.
        Valida que cada mensaje cumpla con el modelo HousingAd y descarta mensajes corruptos sin bloquearse.
        """
        received: List[HousingAd] = []

        if not self.simulation_mode and self._real_consumer:
            deadline = time.monotonic() + timeout_seconds
            while len(received) < max_messages and time.monotonic() < deadline:
                batch = self._real_consumer.poll(timeout_ms=min(250, max(1, int((deadline - time.monotonic()) * 1000))), max_records=1)
                for messages in batch.values():
                    for msg in messages:
                        try:
                            payload = json.loads(msg.value.decode('utf-8'))
                            ad = HousingAd(**payload)
                        except (ValueError, TypeError, UnicodeDecodeError) as error:
                            logging.getLogger(__name__).warning('Evento invalido en %s:%s: %s', msg.partition, msg.offset, error)
                            continue
                        # If persistence fails, do not commit the offset or suppress its error.
                        if on_message_callback:
                            on_message_callback(ad, len(received) + 1)
                            self._real_consumer.commit()
                        received.append(ad)
        else:
            # Modo broker en memoria
            if self._mock_broker:
                for idx in range(max_messages):
                    payload = self._mock_broker.poll(timeout_seconds=timeout_seconds)
                    if payload is None:
                        break
                    try:
                        ad = HousingAd(**payload)
                    except (ValueError, TypeError) as err:
                        logging.getLogger(__name__).warning("Mensaje simulado invalido: %s", err)
                        continue
                    if on_message_callback:
                        on_message_callback(ad, len(received) + 1)
                    received.append(ad)


        return received

    def close(self):
        """Cierra el consumidor y libera recursos."""
        if self._real_consumer:
            self._real_consumer.close()
