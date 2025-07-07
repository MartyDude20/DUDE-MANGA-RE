import redis
import sys

def test_redis_connection():
    """Test Redis connection and provide setup instructions"""
    try:
        # Try to connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        print("✅ Redis connection successful!")
        print("✅ Token blacklisting will work properly.")
        return True
    except redis.ConnectionError:
        print("❌ Redis connection failed!")
        print("\n📋 Redis Setup Instructions:")
        print("=" * 50)
        print("1. Install Redis:")
        print("   Windows: Download from https://github.com/microsoftarchive/redis/releases")
        print("   macOS: brew install redis")
        print("   Linux: sudo apt-get install redis-server")
        print("\n2. Start Redis server:")
        print("   Windows: redis-server")
        print("   macOS/Linux: redis-server")
        print("\n3. Test connection:")
        print("   redis-cli ping")
        print("\n4. Alternative: Use Redis Cloud (free tier available)")
        print("   - Sign up at https://redis.com/")
        print("   - Update REDIS_URL in your .env file")
        print("\n5. For development without Redis:")
        print("   - Comment out Redis imports in auth.py")
        print("   - Remove blacklist checks (less secure)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    test_redis_connection() 