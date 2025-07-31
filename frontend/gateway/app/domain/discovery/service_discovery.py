import httpx
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
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
        """라운드 로빈 방식으로 인스턴스 선택"""
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        
        # 가장 적은 연결 수를 가진 인스턴스 선택
        min_connections = min(inst.connection_count for inst in healthy_instances)
        candidates = [inst for inst in healthy_instances if inst.connection_count == min_connections]
        
        return random.choice(candidates)
    
    @staticmethod
    def least_connections(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """최소 연결 수 방식으로 인스턴스 선택"""
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        
        return min(healthy_instances, key=lambda x: x.connection_count)
    
    @staticmethod
    def random(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """랜덤 방식으로 인스턴스 선택"""
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        
        return random.choice(healthy_instances)
    
    @staticmethod
    def weighted_round_robin(instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """가중 라운드 로빈 방식으로 인스턴스 선택"""
        healthy_instances = [inst for inst in instances if inst.health]
        if not healthy_instances:
            return None
        
        # 가중치에 따른 선택
        total_weight = sum(inst.weight for inst in healthy_instances)
        if total_weight == 0:
            return random.choice(healthy_instances)
        
        # 가중치 기반 랜덤 선택
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
        """서비스 등록"""
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
        """서비스 인스턴스 선택"""
        if service_name not in self.registry:
            logger.warning(f"Service {service_name} not found in registry")
            return None
        
        service = self.registry[service_name]
        instances = service["instances"]
        load_balancer_type = service["load_balancer_type"]
        
        if not instances:
            logger.warning(f"No instances available for service {service_name}")
            return None
        
        # 로드 밸런서 선택
        load_balancer = self.load_balancers.get(load_balancer_type, LoadBalancer.round_robin)
        instance = load_balancer(instances)
        
        if instance:
            instance.connection_count += 1
            logger.debug(f"Selected instance {instance.host}:{instance.port} for service {service_name}")
        
        return instance
    
    def release_instance(self, service_name: str, instance: ServiceInstance) -> None:
        """인스턴스 연결 해제"""
        if instance:
            instance.connection_count = max(0, instance.connection_count - 1)
    
    async def health_check_instance(self, instance: ServiceInstance, health_check_path: str) -> bool:
        """인스턴스 헬스 체크"""
        try:
            start_time = time.time()
            response = await self.health_check_client.get(f"{instance.url}{health_check_path}")
            response_time = time.time() - start_time
            
            instance.response_time = response_time
            instance.last_health_check = datetime.now()
            
            if response.status_code == 200:
                instance.health = True
                logger.debug(f"Health check passed for {instance.host}:{instance.port}")
                return True
            else:
                instance.health = False
                logger.warning(f"Health check failed for {instance.host}:{instance.port} - Status: {response.status_code}")
                return False
                
        except Exception as e:
            instance.health = False
            instance.last_health_check = datetime.now()
            logger.error(f"Health check error for {instance.host}:{instance.port}: {str(e)}")
            return False
    
    async def health_check_all_services(self) -> None:
        """모든 서비스의 헬스 체크 수행"""
        for service_name, service in self.registry.items():
            instances = service["instances"]
            health_check_path = service["health_check_path"]
            
            tasks = []
            for instance in instances:
                task = self.health_check_instance(instance, health_check_path)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_service_status(self, service_name: str) -> Optional[Dict]:
        """서비스 상태 조회"""
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
        """모든 서비스 상태 조회"""
        return {
            service_name: self.get_service_status(service_name)
            for service_name in self.registry.keys()
        } 