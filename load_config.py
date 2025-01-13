import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConfigError(Exception):
    """配置文件操作相关的自定义异常"""
    pass


def get_file_path(filename: str) -> Path:
    """
    获取配置文件的完整路径

    Args:
        filename: 配置文件名

    Returns:
        Path: 配置文件的完整路径
    """
    return Path(__file__).parent / filename


def read_json_file(filename: str) -> Any:
    """
    读取JSON文件

    Args:
        filename: 要读取的文件名

    Returns:
        解析后的JSON数据

    Raises:
        ConfigError: 当文件读取或解析失败时
    """
    try:
        file_path = get_file_path(filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ConfigError(f"Error reading {filename}: {str(e)}")


def write_json_file(filename: str, data: Any) -> None:
    """
    写入JSON文件

    Args:
        filename: 要写入的文件名
        data: 要写入的数据

    Raises:
        ConfigError: 当文件写入失败时
    """
    try:
        file_path = get_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ConfigError(f"Error writing {filename}: {str(e)}")


def load_config() -> Optional[Dict]:
    """
    加载主配置文件

    Returns:
        Dict: 配置数据，如果加载失败则返回None
    """
    try:
        return read_json_file('config.json')
    except ConfigError as e:
        print(f"Error loading config: {str(e)}")
        return None


def load_recent() -> Optional[List]:
    """
    加载最近记录文件

    Returns:
        List: 最近记录数据，如果加载失败则返回None
    """
    try:
        return read_json_file('recent.json')
    except ConfigError as e:
        print(f"Error loading recent data: {str(e)}")
        return None


def add_new_entry(new_entry: Dict) -> bool:
    """
    添加新记录

    Args:
        new_entry: 要添加的新记录

    Returns:
        bool: 操作是否成功
    """
    try:
        config = load_recent()
        if config is None:
            return False

        config.append(new_entry)
        write_json_file('recent.json', config)
        return True
    except ConfigError as e:
        print(f"Error adding new entry: {str(e)}")
        return False


def update_count() -> bool:
    """
    更新计数器

    Returns:
        bool: 操作是否成功
    """
    try:
        config = load_config()
        print('从cofig.json加载',config['count'])
        if config is None:
            return False

        config["count"] += 1
        write_json_file('config.json', config)
        return True
    except ConfigError as e:
        print(f"Error updating count: {str(e)}")
        return False


def update_file_status(index: int, read: Optional[bool] = None,
                       statue: Optional[str] = None) -> bool:
    """
    更新文件状态

    Args:
        index: 要更新的记录索引
        read: 是否已读
        statue: 状态值

    Returns:config = load_config.load_config()
        bool: 操作是否成功
    """
    try:
        data = read_json_file('recent.json')

        for item in data:
            if item['index'] == index:
                if read is not None:
                    item['read'] = read
                if statue is not None:
                    item['statue'] = statue
                break

        write_json_file('recent.json', data)
        return True
    except ConfigError as e:
        print(f"Error updating file status: {str(e)}")
        return False


def delete_entry(index: int) -> bool:
    """
    删除指定索引的记录及对应的文件，支持不同的文件扩展名

    Args:
        index: 要删除的记录索引

    Returns:
        bool: 操作是否成功
    """
    try:
        data = read_json_file('recent.json')
        print(f"读取到的数据: {data}")

        # 找到要删除的记录
        target_entry = None
        for item in data:
            if item['index'] == index:
                target_entry = item
                break

        if target_entry:
            print(f"找到目标记录: {target_entry}")

            # 删除原始文件（保持原始扩展名）
            original_file = os.path.join('static', 'original', target_entry['name'])
            print(f"原始文件路径: {original_file}")
            # if os.path.exists(original_file):
            #     os.remove(original_file)
            #     print(f"成功删除原始文件: {original_file}")
            # else:
            #     print(f"原始文件不存在: {original_file}")

            # 删除翻译后的文件（始终使用.pdf扩展名）
            filename_without_ext = os.path.splitext(target_entry['name'])[0]
            target_file = os.path.join('static', 'target',
                                       f"{filename_without_ext}_{target_entry['target_language']}.pdf")
            print(f"目标文件路径: {target_file}")
            if os.path.exists(target_file):
                os.remove(target_file)
                print(f"成功删除目标文件: {target_file}")
            else:
                print(f"目标文件不存在: {target_file}")

        # 从数据中删除记录
        data = [item for item in data if item['index'] != index]
        write_json_file('recent.json', data)
        return True
    except Exception as e:
        print(f"Error deleting entry: {str(e)}")
        return False


if __name__ == "__main__":
    # 确保目录存在
    os.makedirs('static/original', exist_ok=True)
    os.makedirs('static/target', exist_ok=True)

    # 创建测试用的 recent.json
    test_data = [
        {
            "index": 1,
            "name": "g2.epub",  # 注意这里是.epub
            "target_language": "zh",
            "status": "completed",
            "timestamp": "2024-01-20 12:00:00"
        }
    ]
    write_json_file('recent.json', test_data)

    # 在删除之前先检查文件是否存在
    print("检查初始状态...")
    print(f"原始文件(.epub)是否存在: {os.path.exists('static/original/g2.epub')}")
    print(f"目标文件(.pdf)是否存在: {os.path.exists('static/target/g2_zh.pdf')}")

    print("\n开始测试删除功能...")
    result = delete_entry(1)
    print(f"删除操作结果: {result}")

    print("\n检查最终状态...")
    print(f"原始文件(.epub)是否存在: {os.path.exists('static/original/g2.epub')}")
    print(f"目标文件(.pdf)是否存在: {os.path.exists('static/target/g2_zh.pdf')}")


def decrease_count() -> bool:
    """
    减少计数器值

    Returns:
        bool: 操作是否成功
    """
    try:
        config = load_config()
        if config is None:
            return False

        config["count"] -= 1
        write_json_file('config.json', config)
        return True
    except ConfigError as e:
        print(f"Error decreasing count: {str(e)}")
        return False
def update_default_services(translation: Optional[bool] = None,
                          translation_service: Optional[str] = None,
                          ocr_modle: Optional[bool] = None) -> bool:
    """
    更新默认服务配置

    Args:
        translation: 是否启用翻译
        translation_service: 翻译服务提供商
        ocr_modle: 是否启用OCR模块

    Returns:
        bool: 操作是否成功
    """
    try:
        config = load_config()
        if config is None:
            return False

        # 只更新提供的参数
        if translation is not None:
            config["default_services"]["translation"] = str(translation).lower() == 'true'
        if translation_service is not None:
            config["default_services"]["translation_service"] = translation_service
        if ocr_modle is not None:
            config["default_services"]["ocr_modle"] = str(ocr_modle).lower() == 'true'

        write_json_file('config.json', config)
        return True
    except ConfigError as e:
        print(f"Error updating default services: {str(e)}")
        return False


def get_default_services() -> Optional[Dict]:
    """
    获取默认服务配置值

    Returns:
        Dict: 包含default_services的所有配置值的字典,格式为:
        {
            "translation": bool,
            "translation_service": str,
            "ocr_modle": bool
        }
        如果获取失败则返回None
    """
    try:
        config = load_config()
        if config is None:
            return None

        return {
            "translation": config["default_services"]["translation"],
            "translation_service": config["default_services"]["translation_service"],
            "ocr_modle": config["default_services"]["ocr_modle"],
            "count": config["count"],
        }
    except ConfigError as e:
        print(f"Error getting default services: {str(e)}")
        return None
# if __name__ == "__main__":
#     # 确保目录存在
#     os.makedirs('static/original', exist_ok=True)
#     os.makedirs('static/target', exist_ok=True)
#
#     # 创建测试用的 recent.json
#     test_data = [
#         {
#             "index": 1,
#             "name": "g2.pdf",
#             "target_language": "zh",
#             "status": "completed",
#             "timestamp": "2024-01-20 12:00:00"
#         }
#     ]
#     write_json_file('recent.json', test_data)
#
#     # 测试删除功能
#     print("开始测试删除功能...")
#     result = delete_entry(1)
#     print(f"删除操作结果: {result}")
#
#     # 验证文件是否还存在
#     original_exists = os.path.exists('static/original/g2.pdf')
#     target_exists = os.path.exists('static/target/g2_zh.pdf')
#     print(f"原始文件是否存在: {original_exists}")
#     print(f"目标文件是否存在: {target_exists}")
