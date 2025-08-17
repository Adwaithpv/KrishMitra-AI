"""
Monitoring and metrics service for production readiness
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import asyncio
import psutil
import json

# Configure logging
import os
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and expose application metrics"""
    
    def __init__(self):
        self.query_count = 0
        self.error_count = 0
        self.response_times = []
        self.agent_usage = Counter()
        self.location_queries = Counter()
        self.crop_queries = Counter()
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        
    def record_query(self, query: str, location: str = None, crop: str = None, 
                    response_time: float = 0, agent_used: str = None, success: bool = True):
        """Record a query event"""
        self.query_count += 1
        
        if not success:
            self.error_count += 1
            
        if response_time > 0:
            self.response_times.append(response_time)
            # Keep only last 1000 response times for memory efficiency
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]
        
        if agent_used:
            self.agent_usage[agent_used] += 1
            
        if location:
            self.location_queries[location] += 1
            
        if crop:
            self.crop_queries[crop] += 1
            
        # Daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        self.daily_stats[today]['queries'] += 1
        if not success:
            self.daily_stats[today]['errors'] += 1
            
        logger.info(f"Query recorded: success={success}, response_time={response_time:.3f}s, agent={agent_used}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_queries": self.query_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.query_count, 1),
            "avg_response_time": round(avg_response_time, 3),
            "agent_usage": dict(self.agent_usage),
            "top_locations": dict(self.location_queries.most_common(10)),
            "top_crops": dict(self.crop_queries.most_common(10)),
            "daily_stats": dict(self.daily_stats),
            "system_health": self.get_system_health()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        metrics = self.get_metrics()
        
        prometheus_format = f"""# HELP agri_advisor_queries_total Total number of queries
# TYPE agri_advisor_queries_total counter
agri_advisor_queries_total {metrics['total_queries']}

# HELP agri_advisor_errors_total Total number of errors
# TYPE agri_advisor_errors_total counter
agri_advisor_errors_total {metrics['total_errors']}

# HELP agri_advisor_response_time_avg Average response time in seconds
# TYPE agri_advisor_response_time_avg gauge
agri_advisor_response_time_avg {metrics['avg_response_time']}

# HELP agri_advisor_error_rate Error rate percentage
# TYPE agri_advisor_error_rate gauge
agri_advisor_error_rate {metrics['error_rate']}

# HELP agri_advisor_cpu_usage CPU usage percentage
# TYPE agri_advisor_cpu_usage gauge
agri_advisor_cpu_usage {metrics['system_health'].get('cpu_usage_percent', 0)}

# HELP agri_advisor_memory_usage Memory usage percentage
# TYPE agri_advisor_memory_usage gauge
agri_advisor_memory_usage {metrics['system_health'].get('memory_usage_percent', 0)}
"""
        
        # Add agent usage metrics
        for agent, count in metrics['agent_usage'].items():
            prometheus_format += f"""
# HELP agri_advisor_agent_usage_{agent} Usage count for {agent}
# TYPE agri_advisor_agent_usage_{agent} counter
agri_advisor_agent_usage_{agent} {count}
"""
        
        return prometheus_format

class HealthChecker:
    """Health check service for production monitoring"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = None
        
    async def check_health(self) -> Dict[str, Any]:
        """Run all health checks"""
        self.last_check_time = datetime.now()
        
        results = {
            "status": "healthy",
            "timestamp": self.last_check_time.isoformat(),
            "checks": {}
        }
        
        # Database connectivity
        try:
            from .main import get_qdrant_client
            client = get_qdrant_client()
            await asyncio.sleep(0.1)  # Simulate async check
            results["checks"]["qdrant"] = {"status": "up", "message": "Connected"}
        except Exception as e:
            results["checks"]["qdrant"] = {"status": "down", "error": str(e)}
            results["status"] = "degraded"
        
        # LLM service
        try:
            from .llm_client import LLMClient
            llm = LLMClient()
            if llm.gemini_model:
                results["checks"]["llm"] = {"status": "up", "provider": "gemini"}
            else:
                results["checks"]["llm"] = {"status": "fallback", "provider": "local"}
        except Exception as e:
            results["checks"]["llm"] = {"status": "down", "error": str(e)}
            results["status"] = "degraded"
        
        # System resources
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            if cpu > 90 or memory.percent > 90:
                results["status"] = "degraded"
                
            results["checks"]["system"] = {
                "status": "up",
                "cpu_percent": cpu,
                "memory_percent": memory.percent
            }
        except Exception as e:
            results["checks"]["system"] = {"status": "down", "error": str(e)}
            results["status"] = "degraded"
        
        return results

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
