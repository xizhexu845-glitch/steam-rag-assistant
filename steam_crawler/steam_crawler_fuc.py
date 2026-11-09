import re
import requests
from bs4 import BeautifulSoup
import time

def get_steamcategory(url, category_num=20):
    """
    Extract the Steam categories from a given URL.
    :param url: The URL to extract the Steam categories from.
    :param category_num: Number of categories to return.
    :return: A dictionary with category name as key and category url as value.
    """
    category_url = {}

    try:
        res = requests.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        # Steam 分类一般在页面左侧的类别列表里，寻找含类别链接的a标签
        # 以"Browse by category"为标识寻找分类列表，或直接找class="blockbg" 里带分类的a标签
        # 这里用class="popup_menu_item"作为示例，因为Steam分类菜单类名较为固定
        categories = soup.select('a.popup_menu_item')

        count = 0
        for c in categories:
            name = c.get_text(strip=True)
            href = c.get('href')
            if name and href and href.startswith('https://store.steampowered.com/'):
                category_url[name] = href
                count += 1
                if count >= category_num:
                    break
    except Exception as e:
        print(f"Error fetching or parsing URL: {e}")

    return category_url


def get_steamapp_id(url):
    m = re.search(r'/app/(\d+)', url)
    if m:
        return int(m.group(1))
    return None


# 用于从 HTML 提取 appid
def extract_appids_from_html(html):
    return list({int(m) for m in re.findall(r'/app/(\d+)/', html)})

def get_steamapp_list(tag_id, num=30):
    """
    通过标签 ID 获取某类型下的 Steam app IDs。
    :param tag_id: Steam 标签 ID，对应游戏类型
    :param num: 要获取的 app 数量
    :return: App ID 列表
    """
    appids = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for start in range(0, num, 50):
        count = min(50, num - len(appids))
        url = (
            f"https://store.steampowered.com/search/results/"
            f"?query&tags={tag_id}&start={start}&count={count}"
            f"&cc=CN&l=schinese&supportedlang=schinese&filter=popular&infinite=1"
        )
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            html = data.get("results_html", "")
            ids = extract_appids_from_html(html)
            appids.extend(ids)

            if not ids:
                break  # 没有更多数据时退出

        except Exception as e:
            print(f"Error fetching tag_id={tag_id}: {e}")
            break

    return appids[:num]


def get_steamid_information(steamid):
    steam_info = {}

    # 1. 获取基础信息（包含价格，类型，中文名）
    api_url = f"https://store.steampowered.com/api/appdetails?appids={steamid}&l=schinese"
    try:
        r = requests.get(api_url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data[str(steamid)]['success']:
            return {"steamid": steamid, "info": {}, "error": "App not found"}
        appdata = data[str(steamid)]['data']

        # 名称（中文）
        name = appdata.get('name')

        # 价格（人民币）
        price_info = appdata.get("price_overview")
        price = price_info.get("final_formatted") if price_info else "免费或无价格信息"

        # 类型 / 标签
        genres = [g['description'] for g in appdata.get("genres", [])] if appdata.get("genres") else []
        categories = [c['description'] for c in appdata.get("categories", [])] if appdata.get("categories") else []

        # 开发商、发行商
        developers = appdata.get("developers", [])
        publishers = appdata.get("publishers", [])

        # 平台支持
        platforms = appdata.get("platforms", {})

        # 评分数据（Metacritic）
        metacritic = appdata.get("metacritic", {})


        steam_info.update({
            "name": name,
            "price": price,
            "genres": genres,
            "categories": categories,
            "developers": developers,
            "publishers": publishers,
            "platforms": platforms,
            "metacritic": metacritic
        })
    except Exception as e:
        return {"steamid": steamid, "info": {}, "error": f"API error: {e}"}

    # 2. 爬取完整中文简介（从游戏页面）
    detail_url = f"https://store.steampowered.com/app/{steamid}/?l=schinese"
    try:
        r = requests.get(detail_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # 完整中文简介一般在id="game_area_description"中
        full_desc_tag = soup.find(id="game_area_description")
        full_description = full_desc_tag.get_text(strip=True) if full_desc_tag else ""

        # 其他详情：标签（页面右侧可见）
        tag_elements = soup.select('a.app_tag')
        tags = [t.get_text(strip=True) for t in tag_elements] if tag_elements else []

        steam_info["full_description"] = full_description
        steam_info["tags"] = tags
    except Exception as e:
        steam_info["full_description"] = ""
        steam_info["tags"] = []
        steam_info["description_error"] = str(e)

    # 3. 获取用户评价（第一页，含具体评论内容）
    # Steam 评论API文档没有公开，这里用官方页面的ajax接口抓取示例
    # https://store.steampowered.com/appreviews/{appid}?json=1&language=schinese&num_per_page=10
    review_api_url = f"https://store.steampowered.com/appreviews/{steamid}?json=1&language=schinese&num_per_page=10"
    try:
        r = requests.get(review_api_url, timeout=10)
        r.raise_for_status()
        reviews_json = r.json()

        # 解析评论
        reviews = []
        if "reviews" in reviews_json:
            for rev in reviews_json["reviews"]:
                review_text = rev.get("review")
                author = rev.get("author", {}).get("steamid")
                votes_up = rev.get("votes_up")
                voted_down = rev.get("voted_down")
                reviews.append({
                    "author_steamid": author,
                    "review": review_text,
                    "votes_up": votes_up,
                    "voted_down": voted_down
                })
        steam_info["user_reviews"] = reviews
    except Exception as e:
        steam_info["user_reviews"] = []
        steam_info["reviews_error"] = str(e)

    return {"steamid": steamid, "info": steam_info}

