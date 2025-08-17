"""
Analytics service for tracking queries, user behavior, and system performance.
"""
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import os
from pathlib import Path

class AnalyticsService:
    def __init__(self, data_dir: str = "data/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.query_log_file = self.data_dir / "query_log.jsonl"
        self.performance_file = self.data_dir / "performance.json"
        self.user_stats_file = self.data_dir / "user_stats.json"
        
        # In-memory cache for real-time stats
        self._query_cache = []
        self._performance_cache = {
            "total_queries": 0,
            "avg_response_time": 0.0,
            "success_rate": 1.0,
            "agent_usage": defaultdict(int),
            "popular_queries": Counter(),
            "error_count": 0
        }
    
    def log_query(self, query: str, location: Optional[str], crop: Optional[str], 
                  response_time: float, success: bool, agent_used: Optional[str] = None,
                  confidence: float = 0.0, error: Optional[str] = None):
        """Log a query with metadata"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "query": query,
            "location": location,
            "crop": crop,
            "response_time": response_time,
            "success": success,
            "agent_used": agent_used,
            "confidence": confidence,
            "error": error
        }
        
        # Write to file
        with open(self.query_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Update cache
        self._query_cache.append(log_entry)
        self._performance_cache["total_queries"] += 1
        
        if success:
            # Update average response time
            total_time = self._performance_cache["avg_response_time"] * (self._performance_cache["total_queries"] - 1)
            self._performance_cache["avg_response_time"] = (total_time + response_time) / self._performance_cache["total_queries"]
        else:
            self._performance_cache["error_count"] += 1
        
        # Update success rate
        self._performance_cache["success_rate"] = (
            (self._performance_cache["total_queries"] - self._performance_cache["error_count"]) / 
            self._performance_cache["total_queries"]
        )
        
        # Update agent usage
        if agent_used:
            self._performance_cache["agent_usage"][agent_used] += 1
        
        # Update popular queries (simplified)
        query_key = query.lower()[:50]  # First 50 chars
        self._performance_cache["popular_queries"][query_key] += 1
        
        # Keep cache size manageable
        if len(self._query_cache) > 1000:
            self._query_cache = self._query_cache[-500:]
    
    def get_performance_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter recent queries
        recent_queries = [
            q for q in self._query_cache 
            if datetime.fromisoformat(q["timestamp"]) > cutoff_time
        ]
        
        if not recent_queries:
            return self._performance_cache
        
        # Calculate recent stats
        recent_response_times = [q["response_time"] for q in recent_queries if q["success"]]
        recent_success_rate = sum(1 for q in recent_queries if q["success"]) / len(recent_queries)
        
        recent_agent_usage = defaultdict(int)
        for q in recent_queries:
            if q.get("agent_used"):
                recent_agent_usage[q["agent_used"]] += 1
        
        return {
            "period_hours": hours,
            "total_queries": len(recent_queries),
            "avg_response_time": sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0,
            "success_rate": recent_success_rate,
            "agent_usage": dict(recent_agent_usage),
            "popular_queries": dict(Counter(q["query"][:30] for q in recent_queries).most_common(10)),
            "error_count": sum(1 for q in recent_queries if not q["success"])
        }
    
    def get_user_insights(self, hours: int = 24) -> Dict[str, Any]:
        """Get user behavior insights"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_queries = [
            q for q in self._query_cache 
            if datetime.fromisoformat(q["timestamp"]) > cutoff_time
        ]
        
        if not recent_queries:
            return {"message": "No recent queries"}
        
        # Location analysis
        locations = [q["location"] for q in recent_queries if q["location"]]
        popular_locations = Counter(locations).most_common(5)
        
        # Crop analysis
        crops = [q["crop"] for q in recent_queries if q["crop"]]
        popular_crops = Counter(crops).most_common(5)
        
        # Query patterns
        query_types = []
        for q in recent_queries:
            query_lower = q["query"].lower()
            if any(word in query_lower for word in ["price", "market", "cost"]):
                query_types.append("market")
            elif any(word in query_lower for word in ["weather", "rain", "temperature"]):
                query_types.append("weather")
            elif any(word in query_lower for word in ["disease", "pest", "fertilizer"]):
                query_types.append("crop_management")
            elif any(word in query_lower for word in ["scheme", "subsidy", "government"]):
                query_types.append("policy")
            else:
                query_types.append("general")
        
        query_type_distribution = Counter(query_types)
        
        return {
            "popular_locations": popular_locations,
            "popular_crops": popular_crops,
            "query_type_distribution": dict(query_type_distribution),
            "avg_confidence": sum(q["confidence"] for q in recent_queries) / len(recent_queries),
            "total_users": len(set(q.get("user_id", "anonymous") for q in recent_queries))
        }
    
    def export_data(self, format: str = "json") -> str:
        """Export analytics data"""
        if format == "json":
            data = {
                "performance": self.get_performance_stats(),
                "user_insights": self.get_user_insights(),
                "recent_queries": self._query_cache[-100:]  # Last 100 queries
            }
            export_file = self.data_dir / f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return str(export_file)
        
        return "Unsupported format"
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old analytics data"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Clean up query cache
        self._query_cache = [
            q for q in self._query_cache 
            if datetime.fromisoformat(q["timestamp"]) > cutoff_time
        ]
        
        # Clean up log file (keep only recent entries)
        if self.query_log_file.exists():
            temp_file = self.data_dir / "temp_log.jsonl"
            with open(self.query_log_file, "r", encoding="utf-8") as f_in:
                with open(temp_file, "w", encoding="utf-8") as f_out:
                    for line in f_in:
                        try:
                            entry = json.loads(line.strip())
                            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time:
                                f_out.write(line)
                        except:
                            continue
            
            temp_file.replace(self.query_log_file)

