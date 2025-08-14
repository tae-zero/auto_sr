import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import random
import time

logger = logging.getLogger(__name__)

class ServiceInstance:
    """서비스 인스턴스 정보"""
    
    def __init__(self, host: str, port: int, weight: int = 1, metadata: Dict = None):
        self.host = host
        self.port = port
        self.weight = weight
        self.metadata = metadata or {}
        self.health = True
        self.last_health_check = datetime.now()
        self.connection_count = 0
        self.response_time = 0.0
    
    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"
    
    def to_dict(self) -> Dict:
        return {
            "host": self.host,
            "port": self.port,
            "weight": self.weight,
            "health": self.health,
            "last_health_check": self.last_health_check.isoformat(),
            "connection_count": self.connection_count,
            "response_time": self.response_time,
            "metadata": self.metadata
        }

class LoadBalancer:
    """로드 밸런서 클래스"""
    
    @staticmethod
    def round_robin(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        min_connections = min(inst.connection_count for inst in healthy_instances)
        candidates = [inst for inst in healthy_instances if inst.connection_count == min_connections]
        return random.choice(candidates)
    
    @staticmethod
    def least_connections(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        return min(healthy_instances, key=lambda x: x.connection_count)
    
    @staticmethod
    def random(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        return random.choice(healthy_instances)
    
    @staticmethod
    def weighted_round_robin(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        total_weight = sum(inst.weight for inst in healthy_instances)
        if total_weight == 0:
            return random.choice(healthy_instances)
        rand = random.uniform(0, total_weight)
        current_weight = 0
        for instance in healthy_instances:
            current_weight += instance.weight
            if rand <= current_weight:
                return instance
        return healthy_instances[0]

class ServiceDiscovery:
    """서비스 디스커버리 클래스"""
    
    def __init__(self, registry: Dict[str, Any] = None):
        self.registry = registry or {}
        self.health_check_client = httpx.AsyncClient(timeout=5.0)
        self.load_balancers = {
            "round_robin": LoadBalancer.round_robin,
            "least_connections": LoadBalancer.least_connections,
            "random": LoadBalancer.random,
            "weighted_round_robin": LoadBalancer.weighted_round_robin
        }
    
    def register_service(self, service_name: str, instances: List[Dict], 
                        load_balancer_type: str = "round_robin") -> None:
        service_instances = []
        for instance_data in instances:
            instance = ServiceInstance(
                host=instance_data["host"],
                port=instance_data["port"],
                weight=instance_data.get("weight", 1),
                metadata=instance_data.get("metadata", {})
            )
            service_instances.append(instance)
        
        self.registry[service_name] = {
            "instances": service_instances,
            "load_balancer_type": load_balancer_type,
            "health_check_path": instances[0].get("health_check_path", "/health")
        }
        
        logger.info(f"Service {service_name} registered with {len(service_instances)} instances")
    
    def get_service_instance(self, service_name: str) -> Optional[ServiceInstance]:
        if service_name not in self.registry:
            logger.warning(f"Service {service_name} not found in registry")
            return None
        
        service = self.registry[service_name]
        instances = service["instances"]
        load_balancer_type = service["load_balancer_type"]
        
        if not instances:
            logger.warning(f"No instances available for service {service_name}")
            return None
        
        load_balancer = self.load_balancers.get(load_balancer_type, LoadBalancer.round_robin)
        instance = load_balancer(instances)
        
        if instance:
            instance.connection_count += 1
            logger.debug(f"Selected instance {instance.host}:{instance.port} for service {service_name}")
        
        return instance
    
    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """서비스의 모든 인스턴스 반환 (디버깅용)"""
        if service_name not in self.registry:
            logger.warning(f"Service {service_name} not found in registry")
            return []
        
        service = self.registry[service_name]
        instances = service["instances"]
        
        logger.debug(f"Returning {len(instances)} instances for service {service_name}")
        return instances
    
    def release_instance(self, service_name: str, instance: ServiceInstance) -> None:
        if instance:
            instance.connection_count = max(0, instance.connection_count - 1)

    # ✅ ✅ ✅ 여기만 수정됨 ✅ ✅ ✅
    async def health_check_instance(self, instance: ServiceInstance, health_check_path: str) -> bool:
        """개발용 - 실제 요청 없이 건강하다고 간주"""
        instance.health = True
        instance.last_health_check = datetime.now()
        instance.response_time = 0.01
        logger.debug(f"[DEV] Skipped real health check for {instance.host}:{instance.port} — marked as healthy.")
        return True
    
    async def health_check_all_services(self) -> None:
        for service_name, service in self.registry.items():
            instances = service["instances"]
            health_check_path = service["health_check_path"]
            tasks = [
                self.health_check_instance(instance, health_check_path)
                for instance in instances
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_service_status(self, service_name: str) -> Optional[Dict]:
        if service_name not in self.registry:
            return None
        
        service = self.registry[service_name]
        instances = service["instances"]
        
        return {
            "service_name": service_name,
            "total_instances": len(instances),
            "healthy_instances": len([inst for inst in instances if inst.health]),
            "load_balancer_type": service["load_balancer_type"],
            "instances": [inst.to_dict() for inst in instances]
        }
    
    def get_all_services_status(self) -> Dict:
        return {
            service_name: self.get_service_status(service_name)
            for service_name in self.registry.keys()
        }
    
    async def request(self, method: str, path: str, headers: Dict = None, 
                     body: bytes = None, files: Dict = None, params: Dict = None, 
                     data: Dict = None) -> Any:
        """서비스에 요청을 전달하는 메서드"""
        try:
            # 서비스 이름 추출 (path의 첫 번째 부분)
            service_name = path.split('/')[0] if path else "chatbot-service"
            
            # 서비스 인스턴스 선택
            instance = self.get_service_instance(service_name)
            if not instance:
                raise Exception(f"Service {service_name} not available")
            
            # 요청 URL 구성
            url = f"{instance.url}/{path}"
            
            # 요청 파라미터 구성
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers or {},
                "timeout": 30.0
            }
            
            if body:
                request_kwargs["content"] = body
            elif files:
                request_kwargs["files"] = files
            elif data:
                request_kwargs["json"] = data
            
            if params:
                request_kwargs["params"] = params
            
            # 요청 전송
            async with httpx.AsyncClient() as client:
                response = await client.request(**request_kwargs)
                
                # 응답 반환
                if response.status_code < 400:
                    return response.json()
                else:
                    return {
                        "error": True,
                        "status_code": response.status_code,
                        "detail": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "error": True,
                "detail": str(e)
            }
        finally:
            # 인스턴스 해제
            if 'instance' in locals():
                self.release_instance(service_name, instance)
