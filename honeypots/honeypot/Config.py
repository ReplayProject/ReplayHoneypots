"""
Stores information for honeypot configuraion
"""
import json


class Config:
    __name__ = "Config"

    def __init__(self, config_doc):
        self.response_delay = config_doc["response_delay"]
        self.metrics_interval = config_doc["metrics_interval"]
        self.update_interval = config_doc["update_interval"]
        self.portscan_window = config_doc["portscan_window"]
        self.portscan_threshold = config_doc["portscan_threshold"]
        self.whitelist_addrs = config_doc["whitelist_addrs"]
        self.whitelist_ports = config_doc["whitelist_ports"]
        self.os = config_doc["os"]
        self.fingerprint = config_doc["fingerprint"]
        self.filtered_ports = config_doc["filtered_ports"]
        self.open_ports = []
        self.tcp_services = []
        self.udp_services = []
        self.services = []
        for s in config_doc["services"]:
            service_obj = self.Service(s)
            self.services.append(service_obj)
            self.open_ports.append(service_obj.port)
            if service_obj.protocol == "tcp":
                self.tcp_services.append(service_obj)
            if service_obj.protocol == "udp":
                self.udp_services.append(service_obj)

    def json(self):
        return json.dumps(self.__dict__)

    class Service:
        def __init__(self, service_doc):
            self.name = service_doc["name"]
            self.port = service_doc["port"]
            self.protocol = service_doc["protocol"]
            self.response_model = service_doc["response_model"]
