"""Seed 70 realistic-looking TikTok Shop US products into the products table.

Why this exists:
    Until we wire up Apify (PRD Week 3), we use hand-curated data so the
    LLM has meaningful candidates to reason over. Numbers are calibrated to
    match real TikTok Shop US 14-day windows observed in early 2026.

Usage (from apps/api/, with venv active):
    python scripts/seed_products.py

Re-running is safe — uses ON CONFLICT DO UPDATE to refresh existing rows.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

# Make `app` importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects.postgresql import insert  # noqa: E402

from app.core.db import AsyncSessionLocal, engine  # noqa: E402
from app.models.product import Product  # noqa: E402

# ============================================================
# Products organized by category. Numbers are realistic for a
# 14-day window on TikTok Shop US (mid-tier sellers, $1k-100k GMV).
# ============================================================

PRODUCTS: list[dict] = [

    # ---------- Home / 家居 ----------
    {"id": "home_001", "title": "LED 便携小夜灯（触控款）", "category": "Home", "price_usd": 19.99,
     "gmv_14d": 58600, "growth_14d": 342, "shop_count": 23, "creator_count": 47,
     "review_count": 2180, "avg_rating": 4.6, "tags": ["light", "bedroom", "portable"]},
    {"id": "home_002", "title": "静音加湿器 300ml USB", "category": "Home", "price_usd": 24.99,
     "gmv_14d": 42100, "growth_14d": 218, "shop_count": 41, "creator_count": 32,
     "review_count": 1560, "avg_rating": 4.5, "tags": ["humidifier", "desktop"]},
    {"id": "home_003", "title": "可折叠收纳篮 3 件套", "category": "Home", "price_usd": 15.99,
     "gmv_14d": 35200, "growth_14d": 185, "shop_count": 18, "creator_count": 25,
     "review_count": 980, "avg_rating": 4.7, "tags": ["storage", "foldable"]},
    {"id": "home_004", "title": "门缝密封条防风条", "category": "Home", "price_usd": 8.99,
     "gmv_14d": 12400, "growth_14d": 67, "shop_count": 67, "creator_count": 8,
     "review_count": 4210, "avg_rating": 4.4, "tags": ["draft-stopper", "energy-saving"]},
    {"id": "home_005", "title": "香薰扩香机 200ml 七彩", "category": "Home", "price_usd": 29.99,
     "gmv_14d": 28900, "growth_14d": 132, "shop_count": 52, "creator_count": 28,
     "review_count": 1820, "avg_rating": 4.5, "tags": ["aroma", "diffuser"]},
    {"id": "home_006", "title": "化妆镜 LED 三色光", "category": "Home", "price_usd": 32.50,
     "gmv_14d": 47800, "growth_14d": 256, "shop_count": 29, "creator_count": 56,
     "review_count": 2340, "avg_rating": 4.6, "tags": ["mirror", "makeup", "led"]},
    {"id": "home_007", "title": "墙贴 自粘式星空", "category": "Home", "price_usd": 6.99,
     "gmv_14d": 8900, "growth_14d": -12, "shop_count": 89, "creator_count": 5,
     "review_count": 3450, "avg_rating": 4.2, "tags": ["wall-sticker", "kids-room"]},
    {"id": "home_008", "title": "床头收纳挂袋 沙发边", "category": "Home", "price_usd": 12.99,
     "gmv_14d": 18600, "growth_14d": 89, "shop_count": 34, "creator_count": 14,
     "review_count": 1230, "avg_rating": 4.5, "tags": ["organizer", "bedside"]},
    {"id": "home_009", "title": "USB 桌面小风扇 三档", "category": "Home", "price_usd": 16.99,
     "gmv_14d": 22300, "growth_14d": 178, "shop_count": 45, "creator_count": 22,
     "review_count": 1670, "avg_rating": 4.4, "tags": ["fan", "desk"]},
    {"id": "home_010", "title": "硅胶抽屉分隔板", "category": "Home", "price_usd": 11.50,
     "gmv_14d": 14800, "growth_14d": 95, "shop_count": 26, "creator_count": 18,
     "review_count": 890, "avg_rating": 4.6, "tags": ["divider", "drawer"]},

    # ---------- Pet Supplies / 宠物 ----------
    {"id": "pet_001", "title": "猫咪自助按摩刷 壁挂", "category": "Pet", "price_usd": 18.99,
     "gmv_14d": 67400, "growth_14d": 412, "shop_count": 15, "creator_count": 78,
     "review_count": 3210, "avg_rating": 4.8, "tags": ["cat", "grooming", "viral"]},
    {"id": "pet_002", "title": "狗狗降温垫 凝胶冰感", "category": "Pet", "price_usd": 26.99,
     "gmv_14d": 38500, "growth_14d": 198, "shop_count": 28, "creator_count": 41,
     "review_count": 1890, "avg_rating": 4.5, "tags": ["dog", "cooling"]},
    {"id": "pet_003", "title": "宠物自动喂食器 mini 200ml", "category": "Pet", "price_usd": 24.99,
     "gmv_14d": 51200, "growth_14d": 188, "shop_count": 22, "creator_count": 38,
     "review_count": 2240, "avg_rating": 4.6, "tags": ["feeder", "mini", "smart"]},
    {"id": "pet_004", "title": "宠物毛发清理器 双面", "category": "Pet", "price_usd": 12.99,
     "gmv_14d": 19800, "growth_14d": 76, "shop_count": 71, "creator_count": 12,
     "review_count": 5210, "avg_rating": 4.3, "tags": ["lint", "remover"]},
    {"id": "pet_005", "title": "猫咪逗猫棒电动 USB 充电", "category": "Pet", "price_usd": 15.99,
     "gmv_14d": 24600, "growth_14d": 145, "shop_count": 33, "creator_count": 29,
     "review_count": 1450, "avg_rating": 4.5, "tags": ["cat", "toy", "interactive"]},
    {"id": "pet_006", "title": "狗绳 LED 反光夜跑", "category": "Pet", "price_usd": 19.50,
     "gmv_14d": 21300, "growth_14d": 102, "shop_count": 47, "creator_count": 19,
     "review_count": 1110, "avg_rating": 4.4, "tags": ["leash", "led", "safety"]},
    {"id": "pet_007", "title": "猫砂垫 双层防漏", "category": "Pet", "price_usd": 14.99,
     "gmv_14d": 16400, "growth_14d": 58, "shop_count": 56, "creator_count": 11,
     "review_count": 2890, "avg_rating": 4.4, "tags": ["litter-mat", "cat"]},
    {"id": "pet_008", "title": "宠物饮水机 静音流动", "category": "Pet", "price_usd": 36.99,
     "gmv_14d": 44800, "growth_14d": 167, "shop_count": 19, "creator_count": 34,
     "review_count": 1620, "avg_rating": 4.6, "tags": ["fountain", "filtered"]},
    {"id": "pet_009", "title": "狗狗指甲剪 带 LED 灯", "category": "Pet", "price_usd": 13.99,
     "gmv_14d": 11200, "growth_14d": 34, "shop_count": 62, "creator_count": 7,
     "review_count": 1980, "avg_rating": 4.5, "tags": ["grooming", "nail-clipper"]},
    {"id": "pet_010", "title": "猫咪隧道玩具 折叠 S 形", "category": "Pet", "price_usd": 17.99,
     "gmv_14d": 28700, "growth_14d": 224, "shop_count": 24, "creator_count": 31,
     "review_count": 1380, "avg_rating": 4.7, "tags": ["cat", "tunnel", "toy"]},

    # ---------- Beauty / 美妆 ----------
    {"id": "beauty_001", "title": "唇部去角质磨砂膏 樱桃味", "category": "Beauty", "price_usd": 9.99,
     "gmv_14d": 31200, "growth_14d": 287, "shop_count": 18, "creator_count": 44,
     "review_count": 2150, "avg_rating": 4.5, "tags": ["lip", "scrub"]},
    {"id": "beauty_002", "title": "丝巾发圈 缎面不打结", "category": "Beauty", "price_usd": 7.99,
     "gmv_14d": 18900, "growth_14d": 156, "shop_count": 38, "creator_count": 28,
     "review_count": 3420, "avg_rating": 4.6, "tags": ["scrunchie", "silk"]},
    {"id": "beauty_003", "title": "迷你卷发棒 USB 充电式", "category": "Beauty", "price_usd": 28.99,
     "gmv_14d": 52600, "growth_14d": 234, "shop_count": 27, "creator_count": 51,
     "review_count": 1870, "avg_rating": 4.4, "tags": ["curler", "portable"]},
    {"id": "beauty_004", "title": "电动眉毛修剪器 女士用", "category": "Beauty", "price_usd": 14.50,
     "gmv_14d": 22400, "growth_14d": 123, "shop_count": 42, "creator_count": 21,
     "review_count": 1340, "avg_rating": 4.3, "tags": ["eyebrow", "trimmer"]},
    {"id": "beauty_005", "title": "重复使用眼贴 硅胶款 8 对", "category": "Beauty", "price_usd": 11.99,
     "gmv_14d": 16800, "growth_14d": 89, "shop_count": 49, "creator_count": 17,
     "review_count": 2240, "avg_rating": 4.4, "tags": ["eye-patch", "reusable"]},
    {"id": "beauty_006", "title": "面部按摩冰球 玫瑰石英", "category": "Beauty", "price_usd": 19.99,
     "gmv_14d": 26900, "growth_14d": 178, "shop_count": 31, "creator_count": 39,
     "review_count": 1290, "avg_rating": 4.6, "tags": ["face-roller", "quartz"]},
    {"id": "beauty_007", "title": "无热量卷发器 缎带款", "category": "Beauty", "price_usd": 13.99,
     "gmv_14d": 35400, "growth_14d": 312, "shop_count": 25, "creator_count": 67,
     "review_count": 2780, "avg_rating": 4.5, "tags": ["heatless", "curlers", "viral"]},
    {"id": "beauty_008", "title": "发际线粉填充笔 棕色", "category": "Beauty", "price_usd": 12.50,
     "gmv_14d": 14200, "growth_14d": 67, "shop_count": 58, "creator_count": 13,
     "review_count": 1890, "avg_rating": 4.2, "tags": ["hair", "concealer"]},
    {"id": "beauty_009", "title": "指甲油干燥喷雾 速干", "category": "Beauty", "price_usd": 8.99,
     "gmv_14d": 9800, "growth_14d": -8, "shop_count": 73, "creator_count": 6,
     "review_count": 2110, "avg_rating": 4.3, "tags": ["nail", "spray"]},
    {"id": "beauty_010", "title": "化妆海绵收纳架 透气", "category": "Beauty", "price_usd": 6.50,
     "gmv_14d": 7400, "growth_14d": 45, "shop_count": 64, "creator_count": 9,
     "review_count": 1650, "avg_rating": 4.4, "tags": ["sponge", "holder"]},

    # ---------- Kitchen / 厨房 ----------
    {"id": "kitchen_001", "title": "牛油果切片器 三合一", "category": "Kitchen", "price_usd": 11.99,
     "gmv_14d": 24800, "growth_14d": 198, "shop_count": 36, "creator_count": 42,
     "review_count": 1820, "avg_rating": 4.5, "tags": ["avocado", "slicer"]},
    {"id": "kitchen_002", "title": "旋转大蒜切碎器 手动", "category": "Kitchen", "price_usd": 9.99,
     "gmv_14d": 31600, "growth_14d": 245, "shop_count": 28, "creator_count": 58,
     "review_count": 2890, "avg_rating": 4.6, "tags": ["garlic", "chopper", "viral"]},
    {"id": "kitchen_003", "title": "硅胶冰格 球形 4 件套", "category": "Kitchen", "price_usd": 13.50,
     "gmv_14d": 18900, "growth_14d": 134, "shop_count": 41, "creator_count": 24,
     "review_count": 1560, "avg_rating": 4.7, "tags": ["ice-mold", "silicone"]},
    {"id": "kitchen_004", "title": "不锈钢吸管套装 8 支带刷", "category": "Kitchen", "price_usd": 8.99,
     "gmv_14d": 14200, "growth_14d": 78, "shop_count": 67, "creator_count": 12,
     "review_count": 4210, "avg_rating": 4.4, "tags": ["straw", "reusable"]},
    {"id": "kitchen_005", "title": "旋转调料架 360 度", "category": "Kitchen", "price_usd": 22.99,
     "gmv_14d": 38700, "growth_14d": 187, "shop_count": 34, "creator_count": 36,
     "review_count": 1980, "avg_rating": 4.5, "tags": ["spice-rack", "rotating"]},
    {"id": "kitchen_006", "title": "锅盖架 抽屉式分隔器", "category": "Kitchen", "price_usd": 17.50,
     "gmv_14d": 21300, "growth_14d": 112, "shop_count": 39, "creator_count": 19,
     "review_count": 1340, "avg_rating": 4.5, "tags": ["pan-organizer"]},
    {"id": "kitchen_007", "title": "鸡蛋开壳器 手动按压", "category": "Kitchen", "price_usd": 7.99,
     "gmv_14d": 12100, "growth_14d": 56, "shop_count": 53, "creator_count": 11,
     "review_count": 2340, "avg_rating": 4.3, "tags": ["egg-cracker"]},
    {"id": "kitchen_008", "title": "蔬菜削皮器 多功能 Y 形", "category": "Kitchen", "price_usd": 6.99,
     "gmv_14d": 9800, "growth_14d": 23, "shop_count": 78, "creator_count": 6,
     "review_count": 3120, "avg_rating": 4.5, "tags": ["peeler"]},
    {"id": "kitchen_009", "title": "面团擀面杖 立体压花款", "category": "Kitchen", "price_usd": 14.99,
     "gmv_14d": 19600, "growth_14d": 167, "shop_count": 22, "creator_count": 33,
     "review_count": 1230, "avg_rating": 4.6, "tags": ["rolling-pin", "pattern"]},
    {"id": "kitchen_010", "title": "蜂蜜分配器 玻璃滴管", "category": "Kitchen", "price_usd": 10.50,
     "gmv_14d": 11800, "growth_14d": 89, "shop_count": 47, "creator_count": 14,
     "review_count": 1090, "avg_rating": 4.5, "tags": ["honey", "dipper"]},

    # ---------- Outdoor / 户外 ----------
    {"id": "outdoor_001", "title": "可折叠野营椅 超轻便携", "category": "Outdoor", "price_usd": 39.99,
     "gmv_14d": 48700, "growth_14d": 156, "shop_count": 21, "creator_count": 36,
     "review_count": 1670, "avg_rating": 4.5, "tags": ["camping", "chair", "foldable"]},
    {"id": "outdoor_002", "title": "USB 露营灯 LED 吊挂式", "category": "Outdoor", "price_usd": 18.99,
     "gmv_14d": 32400, "growth_14d": 198, "shop_count": 29, "creator_count": 41,
     "review_count": 1890, "avg_rating": 4.6, "tags": ["lantern", "led", "rechargeable"]},
    {"id": "outdoor_003", "title": "驱蚊手环 儿童户外 5 只装", "category": "Outdoor", "price_usd": 9.99,
     "gmv_14d": 14600, "growth_14d": 89, "shop_count": 56, "creator_count": 13,
     "review_count": 2340, "avg_rating": 4.3, "tags": ["mosquito", "bracelet"]},
    {"id": "outdoor_004", "title": "弹出式遮阳沙滩帐篷 1-2 人", "category": "Outdoor", "price_usd": 45.99,
     "gmv_14d": 37800, "growth_14d": 213, "shop_count": 24, "creator_count": 28,
     "review_count": 1240, "avg_rating": 4.4, "tags": ["tent", "popup", "beach"]},
    {"id": "outdoor_005", "title": "充气旅行枕 U 型颈枕", "category": "Outdoor", "price_usd": 12.99,
     "gmv_14d": 19200, "growth_14d": 67, "shop_count": 48, "creator_count": 16,
     "review_count": 2890, "avg_rating": 4.4, "tags": ["travel-pillow"]},
    {"id": "outdoor_006", "title": "太阳能户外串灯 30LED", "category": "Outdoor", "price_usd": 16.50,
     "gmv_14d": 28100, "growth_14d": 178, "shop_count": 32, "creator_count": 27,
     "review_count": 1560, "avg_rating": 4.5, "tags": ["string-lights", "solar"]},
    {"id": "outdoor_007", "title": "自行车手机支架 防震硅胶", "category": "Outdoor", "price_usd": 14.99,
     "gmv_14d": 16400, "growth_14d": 78, "shop_count": 53, "creator_count": 14,
     "review_count": 1980, "avg_rating": 4.4, "tags": ["bike", "phone-mount"]},
    {"id": "outdoor_008", "title": "便携净水器 户外徒步用", "category": "Outdoor", "price_usd": 32.99,
     "gmv_14d": 24800, "growth_14d": 134, "shop_count": 19, "creator_count": 22,
     "review_count": 890, "avg_rating": 4.5, "tags": ["water-filter", "hiking"]},
    {"id": "outdoor_009", "title": "狗狗伸缩牵引绳 5 米", "category": "Outdoor", "price_usd": 18.99,
     "gmv_14d": 22300, "growth_14d": 112, "shop_count": 41, "creator_count": 19,
     "review_count": 1450, "avg_rating": 4.5, "tags": ["dog-leash", "retractable"]},
    {"id": "outdoor_010", "title": "登山头灯 USB 充电感应款", "category": "Outdoor", "price_usd": 21.50,
     "gmv_14d": 17900, "growth_14d": 67, "shop_count": 38, "creator_count": 11,
     "review_count": 1120, "avg_rating": 4.4, "tags": ["headlamp", "rechargeable"]},

    # ---------- Kids / 儿童 ----------
    {"id": "kids_001", "title": "磁力积木 64 片儿童益智", "category": "Kids", "price_usd": 34.99,
     "gmv_14d": 56800, "growth_14d": 256, "shop_count": 19, "creator_count": 48,
     "review_count": 2340, "avg_rating": 4.7, "tags": ["magnetic", "blocks", "stem"]},
    {"id": "kids_002", "title": "儿童感统玩具 减压硅胶", "category": "Kids", "price_usd": 11.99,
     "gmv_14d": 28400, "growth_14d": 198, "shop_count": 47, "creator_count": 32,
     "review_count": 3120, "avg_rating": 4.5, "tags": ["sensory", "fidget"]},
    {"id": "kids_003", "title": "宝宝牙胶 食品级硅胶 4 件", "category": "Kids", "price_usd": 9.99,
     "gmv_14d": 16700, "growth_14d": 89, "shop_count": 58, "creator_count": 18,
     "review_count": 2890, "avg_rating": 4.6, "tags": ["teether", "baby"]},
    {"id": "kids_004", "title": "夜光星星贴纸 200 片", "category": "Kids", "price_usd": 8.50,
     "gmv_14d": 12300, "growth_14d": 45, "shop_count": 71, "creator_count": 9,
     "review_count": 4210, "avg_rating": 4.4, "tags": ["glow", "stars", "kids-room"]},
    {"id": "kids_005", "title": "儿童画板 LCD 8.5 寸彩色", "category": "Kids", "price_usd": 17.99,
     "gmv_14d": 31900, "growth_14d": 178, "shop_count": 34, "creator_count": 29,
     "review_count": 1890, "avg_rating": 4.5, "tags": ["drawing-tablet", "lcd"]},
    {"id": "kids_006", "title": "宝宝洗澡玩具 喷水鸭子", "category": "Kids", "price_usd": 13.99,
     "gmv_14d": 19800, "growth_14d": 134, "shop_count": 42, "creator_count": 24,
     "review_count": 2110, "avg_rating": 4.6, "tags": ["bath", "toy"]},
    {"id": "kids_007", "title": "故事方块骰子 11 个", "category": "Kids", "price_usd": 14.50,
     "gmv_14d": 22100, "growth_14d": 156, "shop_count": 28, "creator_count": 33,
     "review_count": 1340, "avg_rating": 4.7, "tags": ["story-cubes", "creative"]},
    {"id": "kids_008", "title": "儿童袜子收纳挂袋 24 格", "category": "Kids", "price_usd": 12.99,
     "gmv_14d": 11800, "growth_14d": 67, "shop_count": 49, "creator_count": 12,
     "review_count": 1560, "avg_rating": 4.4, "tags": ["organizer", "socks"]},
    {"id": "kids_009", "title": "毛绒动物枕头 30cm 海豚", "category": "Kids", "price_usd": 22.99,
     "gmv_14d": 24600, "growth_14d": 198, "shop_count": 31, "creator_count": 38,
     "review_count": 1450, "avg_rating": 4.6, "tags": ["plush", "pillow"]},
    {"id": "kids_010", "title": "字母数字识字地毯 防滑", "category": "Kids", "price_usd": 27.99,
     "gmv_14d": 18900, "growth_14d": 89, "shop_count": 36, "creator_count": 17,
     "review_count": 980, "avg_rating": 4.5, "tags": ["educational", "rug"]},

    # ---------- Tech accessories / 数码周边 ----------
    {"id": "tech_001", "title": "手机三脚架 LED 补光环", "category": "Tech", "price_usd": 26.99,
     "gmv_14d": 47800, "growth_14d": 234, "shop_count": 25, "creator_count": 52,
     "review_count": 2180, "avg_rating": 4.6, "tags": ["tripod", "ring-light"]},
    {"id": "tech_002", "title": "无线充电板 15W 快充", "category": "Tech", "price_usd": 18.99,
     "gmv_14d": 32100, "growth_14d": 145, "shop_count": 56, "creator_count": 24,
     "review_count": 2890, "avg_rating": 4.4, "tags": ["wireless-charger", "qi"]},
    {"id": "tech_003", "title": "数据线收纳盒 桌面理线器", "category": "Tech", "price_usd": 14.99,
     "gmv_14d": 21300, "growth_14d": 112, "shop_count": 41, "creator_count": 18,
     "review_count": 1670, "avg_rating": 4.5, "tags": ["cable", "organizer"]},
    {"id": "tech_004", "title": "USB 集线器 7 口带开关", "category": "Tech", "price_usd": 22.50,
     "gmv_14d": 18700, "growth_14d": 78, "shop_count": 47, "creator_count": 11,
     "review_count": 1340, "avg_rating": 4.4, "tags": ["usb-hub"]},
    {"id": "tech_005", "title": "笔记本支架 折叠便携铝合金", "category": "Tech", "price_usd": 32.99,
     "gmv_14d": 38900, "growth_14d": 167, "shop_count": 29, "creator_count": 28,
     "review_count": 1890, "avg_rating": 4.6, "tags": ["laptop-stand"]},
    {"id": "tech_006", "title": "迷你充电宝 10000mAh 快充", "category": "Tech", "price_usd": 24.99,
     "gmv_14d": 41200, "growth_14d": 198, "shop_count": 38, "creator_count": 31,
     "review_count": 2340, "avg_rating": 4.5, "tags": ["powerbank", "mini"]},
    {"id": "tech_007", "title": "AirPods 保护套 卡通硅胶", "category": "Tech", "price_usd": 8.99,
     "gmv_14d": 15400, "growth_14d": 89, "shop_count": 87, "creator_count": 14,
     "review_count": 4210, "avg_rating": 4.3, "tags": ["airpods-case"]},
    {"id": "tech_008", "title": "摄像头滑盖遮挡片 6 片装", "category": "Tech", "price_usd": 6.99,
     "gmv_14d": 8900, "growth_14d": 34, "shop_count": 64, "creator_count": 7,
     "review_count": 2110, "avg_rating": 4.5, "tags": ["webcam-cover", "privacy"]},
    {"id": "tech_009", "title": "鼠标垫 加大办公桌垫 80x40", "category": "Tech", "price_usd": 16.99,
     "gmv_14d": 23800, "growth_14d": 134, "shop_count": 51, "creator_count": 19,
     "review_count": 1890, "avg_rating": 4.5, "tags": ["mousepad", "desk-mat"]},
    {"id": "tech_010", "title": "手机屏幕放大器 12 寸 3D", "category": "Tech", "price_usd": 12.99,
     "gmv_14d": 10800, "growth_14d": -8, "shop_count": 73, "creator_count": 9,
     "review_count": 1670, "avg_rating": 4.1, "tags": ["screen-magnifier"]},
]


async def seed() -> int:
    """Upsert all products. Returns count inserted/updated."""
    now = datetime.now(UTC)
    count = 0

    async with AsyncSessionLocal() as session:
        for p in PRODUCTS:
            raw = {
                "shop_count": p["shop_count"],
                "creator_count": p["creator_count"],
                "review_count": p["review_count"],
                "avg_rating": p["avg_rating"],
                "tags": p["tags"],
            }
            stmt = (
                insert(Product)
                .values(
                    platform="tiktok_shop_us",
                    platform_id=p["id"],
                    title=p["title"],
                    category=p["category"],
                    price_usd=p["price_usd"],
                    gmv_14d=p["gmv_14d"],
                    growth_14d=p["growth_14d"],
                    raw=raw,
                    last_synced_at=now,
                )
                .on_conflict_do_update(
                    index_elements=["platform", "platform_id"],
                    set_={
                        "title": p["title"],
                        "category": p["category"],
                        "price_usd": p["price_usd"],
                        "gmv_14d": p["gmv_14d"],
                        "growth_14d": p["growth_14d"],
                        "raw": raw,
                        "last_synced_at": now,
                    },
                )
            )
            await session.execute(stmt)
            count += 1
        await session.commit()

    return count


async def main() -> None:
    n = await seed()
    print(f"✓ Seeded {n} products into `products` table.")
    print("  Categories: Home(10) · Pet(10) · Beauty(10) · Kitchen(10) · Outdoor(10) · Kids(10) · Tech(10)")
    print("  Try a query like: '给我 3 个美区 30 美金以内、宠物类、增速最快的品'")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
