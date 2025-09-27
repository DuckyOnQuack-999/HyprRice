"""
Performance monitoring and optimization utilities for HyprRice
"""

import time
import psutil
import threading
import gc
import weakref
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
from functools import wraps, lru_cache
from collections import defaultdict
import asyncio


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    io_read_mb: float = 0.0
    io_write_mb: float = 0.0
    thread_count: int = 0
    file_descriptors: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class FunctionProfile:
    """Function execution profile."""
    name: str
    total_calls: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float('inf')
    last_called: float = 0.0


class MemoryTracker:
    """Track memory usage and detect leaks."""
    
    def __init__(self, threshold_mb: float = 100.0):
        self.threshold_mb = threshold_mb
        self.logger = logging.getLogger(__name__)
        self.snapshots = []
        self.object_refs = weakref.WeakSet()
        self.tracked_objects = defaultdict(int)
        
    def take_snapshot(self) -> PerformanceMetrics:
        """Take a memory usage snapshot."""
        process = psutil.Process()
        
        metrics = PerformanceMetrics(
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            memory_percent=process.memory_percent(),
            io_read_mb=process.io_counters().read_bytes / 1024 / 1024,
            io_write_mb=process.io_counters().write_bytes / 1024 / 1024,
            thread_count=process.num_threads(),
            file_descriptors=process.num_fds() if hasattr(process, 'num_fds') else 0
        )
        
        self.snapshots.append(metrics)
        
        # Keep only last 100 snapshots
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-100:]
        
        # Check for memory leaks
        if metrics.memory_mb > self.threshold_mb:
            self.logger.warning(f"High memory usage detected: {metrics.memory_mb:.1f}MB")
            self._analyze_memory_usage()
        
        return metrics
    
    def track_object(self, obj: Any, name: str = None):
        """Track an object for memory leak detection."""
        obj_type = type(obj).__name__
        if name:
            obj_type = f"{obj_type}({name})"
        
        self.tracked_objects[obj_type] += 1
        
        try:
            self.object_refs.add(obj)
        except TypeError:
            # Object is not weakly referenceable
            pass
    
    def _analyze_memory_usage(self):
        """Analyze current memory usage."""
        # Force garbage collection
        collected = gc.collect()
        if collected > 0:
            self.logger.info(f"Garbage collected {collected} objects")
        
        # Log tracked object counts
        if self.tracked_objects:
            self.logger.info("Tracked object counts:")
            for obj_type, count in self.tracked_objects.most_common(10):
                self.logger.info(f"  {obj_type}: {count}")
    
    def get_memory_trend(self, window: int = 10) -> Optional[float]:
        """Get memory usage trend over recent snapshots."""
        if len(self.snapshots) < window:
            return None
        
        recent_snapshots = self.snapshots[-window:]
        memory_values = [s.memory_mb for s in recent_snapshots]
        
        # Simple linear trend calculation
        n = len(memory_values)
        sum_x = sum(range(n))
        sum_y = sum(memory_values)
        sum_xy = sum(i * memory_values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        trend = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return trend


class FunctionProfiler:
    """Profile function execution times."""
    
    def __init__(self):
        self.profiles = {}
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
    
    def profile(self, func_name: str = None):
        """Decorator to profile function execution."""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.perf_counter()
                    execution_time = end_time - start_time
                    self._record_execution(name, execution_time)
            
            return wrapper
        return decorator
    
    def _record_execution(self, func_name: str, execution_time: float):
        """Record function execution time."""
        with self.lock:
            if func_name not in self.profiles:
                self.profiles[func_name] = FunctionProfile(name=func_name)
            
            profile = self.profiles[func_name]
            profile.total_calls += 1
            profile.total_time += execution_time
            profile.avg_time = profile.total_time / profile.total_calls
            profile.max_time = max(profile.max_time, execution_time)
            profile.min_time = min(profile.min_time, execution_time)
            profile.last_called = time.time()
    
    def get_profile(self, func_name: str) -> Optional[FunctionProfile]:
        """Get profile for a specific function."""
        return self.profiles.get(func_name)
    
    def get_top_functions(self, by: str = 'total_time', limit: int = 10) -> List[FunctionProfile]:
        """Get top functions by specified metric."""
        if by not in ['total_time', 'avg_time', 'max_time', 'total_calls']:
            raise ValueError(f"Invalid sort key: {by}")
        
        return sorted(
            self.profiles.values(),
            key=lambda p: getattr(p, by),
            reverse=True
        )[:limit]
    
    def reset_profiles(self):
        """Reset all profiles."""
        with self.lock:
            self.profiles.clear()


class CacheManager:
    """Manage various caches with TTL and size limits."""
    
    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.caches = {}
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
    
    def create_cache(self, name: str, ttl: float = None, max_size: int = None) -> 'TTLCache':
        """Create a new TTL cache."""
        with self.lock:
            cache = TTLCache(
                ttl=ttl or self.default_ttl,
                max_size=max_size or self.max_size
            )
            self.caches[name] = cache
            return cache
    
    def get_cache(self, name: str) -> Optional['TTLCache']:
        """Get existing cache by name."""
        return self.caches.get(name)
    
    def clear_cache(self, name: str = None):
        """Clear specific cache or all caches."""
        with self.lock:
            if name:
                if name in self.caches:
                    self.caches[name].clear()
            else:
                for cache in self.caches.values():
                    cache.clear()
    
    def cleanup_expired(self):
        """Clean up expired entries in all caches."""
        with self.lock:
            total_removed = 0
            for name, cache in self.caches.items():
                removed = cache.cleanup_expired()
                total_removed += removed
            
            if total_removed > 0:
                self.logger.debug(f"Cleaned up {total_removed} expired cache entries")


class TTLCache:
    """Time-to-live cache implementation."""
    
    def __init__(self, ttl: float = 300.0, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        self.lock = threading.RLock()
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                return default
            
            # Check if expired
            if time.time() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return default
            
            return self.cache[key]
    
    def set(self, key: Any, value: Any):
        """Set value in cache."""
        with self.lock:
            # Remove oldest entries if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_oldest()
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    def delete(self, key: Any):
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
    
    def clear(self):
        """Clear all entries."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, timestamp in self.timestamps.items()
                if current_time - timestamp > self.ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
            
            return len(expired_keys)
    
    def _evict_oldest(self):
        """Evict oldest entry."""
        if not self.timestamps:
            return
        
        oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
        del self.cache[oldest_key]
        del self.timestamps[oldest_key]
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self, monitor_interval: float = 30.0):
        self.monitor_interval = monitor_interval
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.memory_tracker = MemoryTracker()
        self.profiler = FunctionProfiler()
        self.cache_manager = CacheManager()
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        self.lock = threading.Lock()
    
    def start_monitoring(self):
        """Start performance monitoring."""
        with self.lock:
            if self.monitoring_active:
                return
            
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        with self.lock:
            self.monitoring_active = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5.0)
            self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Take memory snapshot
                metrics = self.memory_tracker.take_snapshot()
                
                # Cleanup expired cache entries
                self.cache_manager.cleanup_expired()
                
                # Log performance summary periodically
                if len(self.memory_tracker.snapshots) % 10 == 0:
                    self._log_performance_summary()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.monitor_interval)
    
    def _log_performance_summary(self):
        """Log performance summary."""
        if not self.memory_tracker.snapshots:
            return
        
        latest = self.memory_tracker.snapshots[-1]
        trend = self.memory_tracker.get_memory_trend()
        
        self.logger.info("Performance Summary:")
        self.logger.info(f"  Memory: {latest.memory_mb:.1f}MB ({latest.memory_percent:.1f}%)")
        self.logger.info(f"  CPU: {latest.cpu_percent:.1f}%")
        self.logger.info(f"  Threads: {latest.thread_count}")
        self.logger.info(f"  File Descriptors: {latest.file_descriptors}")
        
        if trend is not None:
            trend_direction = "increasing" if trend > 0 else "decreasing"
            self.logger.info(f"  Memory Trend: {trend_direction} ({trend:.2f}MB/snapshot)")
        
        # Top functions by execution time
        top_functions = self.profiler.get_top_functions(limit=5)
        if top_functions:
            self.logger.info("  Top Functions by Total Time:")
            for func in top_functions:
                self.logger.info(f"    {func.name}: {func.total_time:.3f}s ({func.total_calls} calls)")
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.memory_tracker.take_snapshot()
    
    def profile_function(self, func_name: str = None):
        """Decorator to profile a function."""
        return self.profiler.profile(func_name)
    
    def create_cache(self, name: str, ttl: float = None, max_size: int = None):
        """Create a managed cache."""
        return self.cache_manager.create_cache(name, ttl, max_size)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()

# Flag to control automatic monitoring in tests
_auto_monitoring_enabled = True

def disable_auto_monitoring():
    """Disable automatic performance monitoring (for tests)."""
    global _auto_monitoring_enabled
    _auto_monitoring_enabled = False

def enable_auto_monitoring():
    """Enable automatic performance monitoring."""
    global _auto_monitoring_enabled
    _auto_monitoring_enabled = True


def profile(func_name: str = None):
    """Convenience decorator for profiling functions."""
    return performance_monitor.profile_function(func_name)


def cached(cache_name: str, ttl: float = 300.0, max_size: int = 1000):
    """Decorator for caching function results."""
    def decorator(func):
        cache = performance_monitor.cache_manager.get_cache(cache_name)
        if cache is None:
            cache = performance_monitor.cache_manager.create_cache(cache_name, ttl, max_size)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = (args, tuple(sorted(kwargs.items())))
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator


async def async_profile(func_name: str = None):
    """Decorator for profiling async functions."""
    def decorator(func):
        name = func_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                performance_monitor.profiler._record_execution(name, execution_time)
        
        return wrapper
    return decorator
