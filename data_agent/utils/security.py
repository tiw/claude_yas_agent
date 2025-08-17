import hashlib
import hmac
from typing import Optional
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

class SecurityManager:
    """安全管理器"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.access_log = []
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data: str) -> str:
        """数据哈希"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def generate_signature(self, data: str, secret: str) -> str:
        """生成签名"""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_signature(self, data: str, signature: str, secret: str) -> bool:
        """验证签名"""
        expected_signature = self.generate_signature(data, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    def log_access(self, user_id: str, action: str, resource: str):
        """记录访问日志"""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource
        })
    
    def check_rate_limit(self, user_id: str, max_requests: int = 100) -> bool:
        """检查速率限制"""
        now = datetime.now()
        recent_access = [
            log for log in self.access_log
            if log["user_id"] == user_id and
            datetime.fromisoformat(log["timestamp"]) > now - timedelta(minutes=1)
        ]
        return len(recent_access) < max_requests