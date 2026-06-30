# ============================================================
# 工具函数：生成随机/动态测试数据
# ============================================================
# 作用：避免测试数据硬编码，每次执行生成不同的数据
# 好处：防止数据冲突，提高用例稳定性
# 使用场景：
#   - 创建帖子时用 random_name() 生成动态标题
#   - 创建用户时用 random_email() 生成唯一邮箱
# ============================================================

from faker import Faker
import uuid

# 初始化 Faker（中文版）
fake = Faker(locale="zh_CN")

def random_name():
    """生成随机中文姓名"""
    return fake.name()

def random_email():
    """生成随机邮箱地址"""
    return fake.email()

def random_string(length=10):
    """生成指定长度的随机字符串（仅字母）"""
    return fake.pystr(min_chars=length, max_chars=length)

def random_int(min=1, max=100):
    """生成指定范围内的随机整数"""
    return fake.random_int(min=min, max=max)

def unique_id():
    """生成 8 位唯一 ID（用于标识测试数据）"""
    return str(uuid.uuid4())[:8]