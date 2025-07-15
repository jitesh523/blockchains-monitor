"""
Production monitoring service with health checks, metrics collection, and alerting.
"""
import asyncio
import logging
import time
import psutil
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.services.database_service import db_service
from src.services.cache_service import cache_service
from alerts import alert_user

logger = logging.getLogger(__name__)

@dataclass
class HealthCheck:
    service: str
    status: str  # "healthy", "unhealthy", "degraded"
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = None

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    timestamp: datetime

class MonitoringService:
    def __init__(self):
        self.is_running = False
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics_history: List[SystemMetrics] = []
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time": 5.0,  # seconds
            "error_rate": 0.05  # 5%
        }
        self.check_interval = 30  # seconds
        
    async def start(self):
        """Start the monitoring service"""
        self.is_running = True
        logger.info("Monitoring service started")
        
        await asyncio.gather(
            self.health_check_loop(),
            self.metrics_collection_loop(),
            self.alert_check_loop()
        )
    
    async def stop(self):
        """Stop the monitoring service"""
        self.is_running = False
        logger.info("Monitoring service stopped")
    
    async def check_database_health(self) -> HealthCheck:
        """Check database connection health"""
        start_time = time.time()
        
        try:
            if db_service.pool is None:
                return HealthCheck(
                    service="database",
                    status="unhealthy",
                    response_time=0.0,
                    timestamp=datetime.now(),
                    details={"error": "Database pool not initialized"}
                )
            
            # Simple query to test connection
            async with db_service.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            response_time = time.time() - start_time
            
            return HealthCheck(
                service="database",
                status="healthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"pool_size": len(db_service.pool._holders)}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="database",
                status="unhealthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_redis_health(self) -> HealthCheck:
        """Check Redis connection health"""
        start_time = time.time()
        
        try:
            if cache_service.redis_client is None:
                return HealthCheck(
                    service="redis",
                    status="degraded",
                    response_time=0.0,
                    timestamp=datetime.now(),
                    details={"error": "Redis not available, using fallback"}
                )
            
            # Ping Redis
            cache_service.redis_client.ping()
            
            response_time = time.time() - start_time
            
            return HealthCheck(
                service="redis",
                status="healthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"connection_pool_size": cache_service.redis_client.connection_pool.created_connections}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="redis",
                status="unhealthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_api_health(self) -> HealthCheck:
        """Check external API health (CoinGecko, Twitter, etc.)"""
        start_time = time.time()
        
        try:
            import requests
            response = requests.get(
                "https://api.coingecko.com/api/v3/ping",
                timeout=10
            )
            response.raise_for_status()
            
            response_time = time.time() - start_time
            
            return HealthCheck(
                service="external_apis",
                status="healthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"coingecko_status": "operational"}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                service="external_apis",
                status="unhealthy",
                response_time=response_time,
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_data,
                process_count=process_count,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                network_io={},
                process_count=0,
                timestamp=datetime.now()
            )
    
    async def health_check_loop(self):
        """Background loop for health checks"""
        while self.is_running:
            try:
                # Run all health checks
                health_checks = await asyncio.gather(
                    self.check_database_health(),
                    self.check_redis_health(),
                    self.check_api_health()
                )
                
                # Store results
                for check in health_checks:
                    self.health_checks[check.service] = check
                    logger.info(f"Health check - {check.service}: {check.status} ({check.response_time:.3f}s)")
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def metrics_collection_loop(self):
        """Background loop for metrics collection"""
        while self.is_running:
            try:
                metrics = await self.collect_system_metrics()
                
                # Store metrics (keep last 24 hours)
                self.metrics_history.append(metrics)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                logger.info(f"System metrics - CPU: {metrics.cpu_percent}%, Memory: {metrics.memory_percent}%, Disk: {metrics.disk_percent}%")
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    async def alert_check_loop(self):
        """Background loop for checking alert conditions"""
        while self.is_running:
            try:
                await self.check_alert_conditions()
            except Exception as e:
                logger.error(f"Error in alert check loop: {e}")
            
            await asyncio.sleep(self.check_interval * 2)  # Check every minute
    
    async def check_alert_conditions(self):
        """Check if any alert conditions are met"""
        alerts_to_send = []
        
        # Check system metrics
        if self.metrics_history:
            latest_metrics = self.metrics_history[-1]
            
            if latest_metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
                alerts_to_send.append({
                    "title": "High CPU Usage Alert",
                    "message": f"CPU usage is {latest_metrics.cpu_percent}% (threshold: {self.alert_thresholds['cpu_percent']}%)",
                    "severity": "warning"
                })
            
            if latest_metrics.memory_percent > self.alert_thresholds["memory_percent"]:
                alerts_to_send.append({
                    "title": "High Memory Usage Alert",
                    "message": f"Memory usage is {latest_metrics.memory_percent}% (threshold: {self.alert_thresholds['memory_percent']}%)",
                    "severity": "warning"
                })
            
            if latest_metrics.disk_percent > self.alert_thresholds["disk_percent"]:
                alerts_to_send.append({
                    "title": "High Disk Usage Alert",
                    "message": f"Disk usage is {latest_metrics.disk_percent}% (threshold: {self.alert_thresholds['disk_percent']}%)",
                    "severity": "critical"
                })
        
        # Check health status
        for service, check in self.health_checks.items():
            if check.status == "unhealthy":
                alerts_to_send.append({
                    "title": f"Service Health Alert - {service}",
                    "message": f"Service {service} is unhealthy: {check.details.get('error', 'Unknown error')}",
                    "severity": "critical"
                })
            
            if check.response_time > self.alert_thresholds["response_time"]:
                alerts_to_send.append({
                    "title": f"Slow Response Alert - {service}",
                    "message": f"Service {service} response time is {check.response_time:.2f}s (threshold: {self.alert_thresholds['response_time']}s)",
                    "severity": "warning"
                })
        
        # Send alerts
        for alert in alerts_to_send:
            await self.send_alert(alert)
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert via configured channels"""
        try:
            alert_user(
                title=alert["title"],
                message=alert["message"],
                channel="slack",
                metadata={
                    "severity": alert["severity"],
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Also send email for critical alerts
            if alert["severity"] == "critical":
                alert_user(
                    title=alert["title"],
                    message=alert["message"],
                    channel="email",
                    metadata={
                        "severity": alert["severity"],
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            logger.info(f"Alert sent: {alert['title']}")
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        overall_status = "healthy"
        
        for check in self.health_checks.values():
            if check.status == "unhealthy":
                overall_status = "unhealthy"
                break
            elif check.status == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "services": {
                service: {
                    "status": check.status,
                    "response_time": check.response_time,
                    "last_check": check.timestamp.isoformat(),
                    "details": check.details
                }
                for service, check in self.health_checks.items()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get system metrics summary"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        latest = self.metrics_history[-1]
        
        # Calculate averages over last hour
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > hour_ago]
        
        if recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = avg_disk = 0.0
        
        return {
            "current": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_percent": latest.disk_percent,
                "process_count": latest.process_count,
                "timestamp": latest.timestamp.isoformat()
            },
            "averages_1h": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory,
                "disk_percent": avg_disk
            },
            "thresholds": self.alert_thresholds
        }

# Global monitoring service instance
monitoring_service = MonitoringService()

async def start_monitoring_service():
    """Start the monitoring service"""
    await monitoring_service.start()

async def stop_monitoring_service():
    """Stop the monitoring service"""
    await monitoring_service.stop()

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return monitoring_service.get_health_status()

def get_metrics_summary() -> Dict[str, Any]:
    """Get system metrics summary"""
    return monitoring_service.get_metrics_summary()
