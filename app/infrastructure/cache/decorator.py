import json
import functools
from typing import Callable, Any, Optional
from app.infrastructure.cache.redis_client import get_redis

def cached(key_pattern: str, expire: int = 3600):
    """
    Decorator to cache async function results in Redis.
    
    :param key_pattern: String pattern for key. format() will be called with *args and **kwargs.
                        Example: "media:{media_id}"
    :param expire: Expiration time in seconds.
    """
    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Construct key
            # Simple approach: try to format the string with function arguments
            # Note: This is a basic implementation. For complex args, this needs robustness.
            # We assume the first arg is 'self' (Service), so we skip it for formatting if needed,
            # or users must name args in pattern.
            
            # Helper to bind arguments to signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            try:
                cache_key = key_pattern.format(**bound_args.arguments)
            except KeyError:
                 # Fallback or error if pattern doesn't match args
                 # For safety, let's just proceed without cache if we can't key it, or raise error
                 return await func(*args, **kwargs)

            redis = await get_redis()
            cached_data = await redis.get(cache_key)
            
            if cached_data:
                # Cache Hit
                try:
                    data = json.loads(cached_data)
                    # If the function expects objects, we might need a way to deserialize.
                    # This decorator returns Dicts. The Service must handle Dict -> Object conversion
                    # OR we cache Pydantic models using .model_dump() and .model_validate()
                    return data
                except:
                    pass

            # Cache Miss
            result = await func(*args, **kwargs)
            
            if result:
                # Attempt to serialize
                # If result is list of objects, or object
                data_to_store = None
                if hasattr(result, "__dict__"):
                    data_to_store = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
                elif isinstance(result, list):
                    data_to_store = [
                         {k: v for k, v in item.__dict__.items() if not k.startswith('_')} 
                         if hasattr(item, "__dict__") else item
                         for item in result
                    ]
                else:
                    data_to_store = result

                await redis.set(cache_key, json.dumps(data_to_store), ex=expire)
            
            return result
        return wrapper
    return decorator
