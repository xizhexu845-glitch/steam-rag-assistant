import json
import os
import steam_crawler.steam_crawler_fuc as sc
from typing import List, Union, Dict, Any
from tqdm import tqdm


def load_json(file_path: str) -> Union[List[Dict[str, Any]], List[int]]:
    """
    加载 JSON 文件。
    返回字典列表（游戏详情）或数字列表（steamid列表），或空列表。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print(f"⚠️ 期望列表，但文件 {file_path} 中数据类型为 {type(data)}，返回空列表。")
                return []
            return data
    except FileNotFoundError:
        print(f"⚠️ 文件未找到: {file_path}，将返回空列表。")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ 无法解析 JSON 文件 {file_path}：{e}")
        return []

def load_category_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(f"⚠️ 期望字典，但文件 {file_path} 中数据类型为 {type(data)}，返回空字典。")
                return {}
            return data
    except Exception as e:
        print(f"❌ 加载分类文件失败: {e}")
        return {}



def save_json(file_path: str, data: Any) -> None:
    """保存数据到 JSON 文件，格式美观"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 写入文件失败 {file_path}：{e}")


def extract_steamids(json_data: List[Union[Dict[str, Any], int, str]]) -> List[Union[int, str]]:
    """
    从传入的列表中提取 steamid。
    - 如果元素是 dict，且含 'steamid' 字段，取字段值
    - 如果元素是数字或字符串，直接当 steamid
    返回 steamid 列表
    """
    steam_ids = []
    for item in json_data:
        if isinstance(item, dict) and 'steamid' in item:
            steam_ids.append(item['steamid'])
        elif isinstance(item, (int, str)):
            steam_ids.append(item)
        else:
            print(f"⚠️ 跳过无效数据项：{item}")
    return steam_ids



def get_updated_data(Update_all: bool = False,
                     each_category_num: int = 30,
                     category_num: int = 20,
                     base_path: str = "data_base") -> None:
    """
    更新 steamapp 数据：
    - old_data 是 steamid 列表
    - categories 是 steam 分类字典
    - Update_all: 是否重新获取所有数据
    """

    old_data_path = os.path.join(base_path, "steamapp.json")
    update_data_path = os.path.join(base_path, "steamapp_update.json")
    category_path = os.path.join(base_path, "steam_category.json")

    old_data = load_json(old_data_path)
    old_steam_ids = extract_steamids(old_data)

    categories = load_category_json(category_path)
    if not categories:
        print("❌ 分类文件为空或加载失败，无法继续。")
        return

    selected_categories = list(categories.keys())[:category_num]

    all_new_ids = set()
    updated_data = []

    # 收集所有分类的新 steamid
    for category in tqdm(selected_categories, desc="获取分类游戏列表"):
        try:
            steam_ids = sc.get_steamapp_list(category, each_category_num)
            all_new_ids.update(steam_ids)
        except Exception as e:
            print(f"⚠️ 分类 {category} 获取失败：{e}")

    if Update_all:
        all_new_ids.update(old_steam_ids)

    print(f"🔍 正在获取 {len(all_new_ids)} 个 Steam 应用的详细信息...")

    to_remove = set()  # 收集 info 为空的 steamid

    for steamid in tqdm(all_new_ids, desc="获取游戏详情进度"):
        if Update_all or steamid not in old_steam_ids:
            try:
                app_info = sc.get_steamid_information(steamid)
                if app_info:
                    info = app_info.get("info")
                    if isinstance(info, dict) and any(info.values()):
                        updated_data.append(app_info)
                    else:
                        print(f"⚠️ SteamID {steamid} 的 info 为空，已标记删除")
                        to_remove.add(steamid)
            except Exception as e:
                print(f"❌ 获取 SteamID {steamid} 时出错：{e}")

    # 删除 info 为空的 steamid
    all_new_ids.difference_update(to_remove)

    # 保存更新的详细信息文件
    save_json(update_data_path, updated_data)
    save_json(old_data_path, list(all_new_ids.union(old_steam_ids)))

    print(f"✅ 更新完成，共获取游戏详情数量：{len(updated_data)}")
