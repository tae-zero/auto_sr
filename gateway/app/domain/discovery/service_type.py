from enum import Enum

class ServiceType(str, Enum):
    """서비스 타입 enum"""
    CHATBOT = "chatbot-service"
    GRI = "gri-service"
    MATERIALITY = "materiality-service"
    REPORT = "report-service"
    TCFD = "tcfd-service"
    USER = "user-service"
    AUTH = "auth-service" 