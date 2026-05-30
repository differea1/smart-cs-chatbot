"""知识库种子数据初始化脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db, SessionLocal
from app.models.knowledge import KnowledgeCategory, KnowledgeItem
from app.models.admin import AdminUser
from app.core.security import hash_password
from app.services.rag_service import RAGService


CATEGORIES = [
    {"id": 1, "name": "产品信息", "parent_id": None, "sort_order": 1},
    {"id": 2, "name": "智能投影仪系列", "parent_id": 1, "sort_order": 1},
    {"id": 3, "name": "智能音箱系列", "parent_id": 1, "sort_order": 2},
    {"id": 4, "name": "智能灯具系列", "parent_id": 1, "sort_order": 3},
    {"id": 5, "name": "售后政策", "parent_id": None, "sort_order": 2},
    {"id": 6, "name": "退换货政策", "parent_id": 5, "sort_order": 1},
    {"id": 7, "name": "保修条款", "parent_id": 5, "sort_order": 2},
    {"id": 8, "name": "订单与物流", "parent_id": None, "sort_order": 3},
    {"id": 9, "name": "故障排查", "parent_id": None, "sort_order": 4},
    {"id": 10, "name": "投影仪故障", "parent_id": 9, "sort_order": 1},
    {"id": 11, "name": "音箱故障", "parent_id": 9, "sort_order": 2},
    {"id": 12, "name": "品牌与活动", "parent_id": None, "sort_order": 5},
]

KNOWLEDGE_ITEMS = [
    # 投影仪产品信息
    {
        "category_id": 2, "type": "qa",
        "title": "X1 Pro 的亮度和分辨率是多少？",
        "keywords": "X1 Pro,亮度,流明,分辨率,参数,规格",
        "content": "极米 X1 Pro 的亮度为 2200 ANSI 流明，支持 4K 分辨率（3840×2160），对比度 5000:1。适用于 30-200 英寸的投影画面，建议在环境光较暗时使用以获得最佳效果。",
    },
    {
        "category_id": 2, "type": "qa",
        "title": "X1 Pro 支持哪些连接方式？",
        "keywords": "X1 Pro,连接,WiFi,蓝牙,HDMI,接口",
        "content": "X1 Pro 支持以下连接方式：WiFi 6（2.4G/5G双频）、蓝牙 5.2、HDMI 2.1×2、USB 3.0×2、3.5mm音频输出。支持无线投屏（AirPlay、Miracast、DLNA）。",
    },
    {
        "category_id": 2, "type": "qa",
        "title": "X3 Max 与 X1 Pro 有什么区别？",
        "keywords": "X3 Max,X1 Pro,对比,区别,参数",
        "content": "X3 Max 是旗舰型号，相比 X1 Pro：亮度提升至 3200 ANSI 流明，内置哈曼卡顿音响（20W×2），支持自动对焦和梯形校正，内存升级为 4GB+128GB。价格方面 X3 Max 为 ¥4,999，X1 Pro 为 ¥2,999。",
    },
    {
        "category_id": 3, "type": "qa",
        "title": "S1 智能音箱参数",
        "keywords": "S1,音箱,参数,功率,驱动单元",
        "content": "极米 S1 智能音箱参数：输出功率 30W（15W×2），驱动单元 2.25英寸全频×2 + 被动辐射器，支持 WiFi 6 / 蓝牙 5.2 / AirPlay 2，内置小爱同学，语音远场拾音距离 5 米。",
    },
    # 售后政策
    {
        "category_id": 6, "type": "qa",
        "title": "退货有什么条件和时间限制？",
        "keywords": "退货,退款,退换,7天,条件,政策",
        "content": "极米科技支持 7 天无理由退货、15 天内质量问题免费换货。\n\n1. 7天无理由退货：自签收之日起7个自然日内，商品完好、配件齐全、不影响二次销售，可申请退货退款。退回运费由买家承担。\n\n2. 15天质量问题换货：自签收之日起15个自然日内，出现非人为损坏的质量问题，可申请免费换新，运费由我们承担。\n\n3. 不适用情形：已激活使用的软件类产品、人为损坏（进水、摔落等）、已超出退换期限。",
    },
    {
        "category_id": 6, "type": "qa",
        "title": "退货流程怎么操作？",
        "keywords": "退货流程,步骤,怎么退,操作",
        "content": "退货流程：1. 联系客服或在线申请退货 → 2. 获取退货地址和 RMA 编号 → 3. 将商品及完整配件使用原包装寄回 → 4. 我们收到退货后 1-3 个工作日内完成检测 → 5. 符合条件则原路退款。请务必保留原包装和所有配件，建议拍照保留商品状态。",
    },
    {
        "category_id": 7, "type": "qa",
        "title": "保修期限和范围是什么？",
        "keywords": "保修,期限,保修期,质保,范围",
        "content": "极米科技保修政策：1年整机保修（含机身、电源适配器、遥控器等），3年核心部件保修（含光机、主板）。保修期内非人为损坏免费维修或换新，人为损坏收取维修成本费。需提供购买凭证（发票或订单截图）方可享受保修服务。",
    },
    # 订单物流
    {
        "category_id": 8, "type": "qa",
        "title": "如何查询订单物流状态？",
        "keywords": "订单查询,物流,快递,发货,到哪了",
        "content": "您可以通过以下方式查询订单物流：1. 提供订单号或购买手机号，我帮您实时查询；2. 访问极米官网 → 我的订单 → 查看物流；3. 下载极米 App → 我的 → 我的订单。通常情况下，发货后 1-3 天可送达（省内），3-7 天（跨省）。",
    },
    {
        "category_id": 8, "type": "qa",
        "title": "发货时间和修改订单",
        "keywords": "发货,发货时间,修改订单,取消订单",
        "content": "下单后正常 24 小时内发货（工作日），大促期间 48 小时内发货。修改订单：未发货状态下可修改收货地址或取消订单；已发货状态需联系客服拦截或拒收后重新下单。",
    },
    # 故障排查
    {
        "category_id": 10, "type": "faq",
        "title": "投影仪无法开机怎么办？",
        "keywords": "无法开机,不开机,没反应,电源,故障",
        "content": "如果投影仪无法开机，请按以下步骤逐一排查：\n\n步骤一：检查电源连接。确认电源线两端（插座端和机身端）是否插紧，尝试更换一个已知正常的插座。\n\n步骤二：检查指示灯状态。电源指示灯完全不亮→可能是电源适配器故障，请联系售后更换；红色闪烁→设备处于待机/保护状态，长按机身电源键10秒强制重启；白色但屏幕无画面→进入步骤三。\n\n步骤三：检查散热状态。触摸机身是否异常发热，如果过热拔掉电源冷却30分钟后再尝试，检查散热口是否有灰尘堵塞。\n\n如果以上步骤均无法解决，请提供订单号和设备序列号（机身底部），我们将安排售后检测。",
    },
    {
        "category_id": 10, "type": "faq",
        "title": "投影画面模糊/偏色怎么调整？",
        "keywords": "画面模糊,偏色,不清晰,对焦,梯形校正",
        "content": "画面模糊/偏色调整步骤：\n\n1. 清洁镜头：用干净软布轻轻擦拭镜头表面。\n\n2. 调整对焦：使用遥控器上的对焦按钮或机身对焦环调整至清晰。\n\n3. 梯形校正：按遥控器梯形校正键自动或手动调整画面形状。\n\n4. 检查投影距离：X1 Pro 最佳投影距离为 1.5-4 米（对应 50-150 英寸）。\n\n5. 图像设置：进入设置→图像模式，根据环境选择合适的模式（标准/影院/高亮）。\n\n如果仍无法解决，可能是光机模组问题，建议联系售后检测。",
    },
    {
        "category_id": 10, "type": "faq",
        "title": "投影仪无法连接WiFi",
        "keywords": "WiFi,连不上,网络,无线,wifi",
        "content": "WiFi 连接问题排查：\n\n1. 重启路由器和投影仪。\n2. 确认 WiFi 密码正确（注意大小写）。\n3. 检查路由器是否开启了 MAC 地址过滤。\n4. 尝试切换 2.4G 和 5G 频段（部分设备对 5G 兼容性较差）。\n5. 进入设置→网络→重置网络设置后重新连接。\n6. 如果仍无法连接，可尝试手机热点测试是否为路由器兼容性问题。",
    },
    {
        "category_id": 10, "type": "faq",
        "title": "遥控器失灵解决方法",
        "keywords": "遥控器,失灵,没反应,遥控",
        "content": "遥控器失灵解决方法：\n\n1. 更换电池（使用两节 AAA 电池）。\n2. 清洁遥控器前端红外/蓝牙发射窗口。\n3. 重新配对：同时按住[主页]+[菜单]键 5 秒，待指示灯闪烁后靠近投影仪。\n4. 手机替代：下载极米 App 使用虚拟遥控器功能。\n5. 如仍无法使用，可能是遥控器硬件故障，请联系售后购买替换遥控器（¥49/个）。",
    },
    {
        "category_id": 10, "type": "faq",
        "title": "风扇噪音大怎么办？",
        "keywords": "风扇,噪音,声音大,异响",
        "content": "风扇噪音排查：\n\n1. 正常现象：投影仪运行时风扇会有一定声音（<35dB 正常范围）。\n2. 散热需求：环境温度高或长时间运行会导致风扇加速，属于正常保护机制。\n3. 灰尘清理：用吸尘器从散热口轻轻吸出灰尘（不要向内部吹气）。\n4. 摆放环境：确保投影仪四周有 15cm 以上的散热空间。\n5. 如果噪音异常大或有咔嗒异响，可能是风扇轴承损坏，建议售后检测。",
    },
    {
        "category_id": 11, "type": "faq",
        "title": "音箱蓝牙配对失败",
        "keywords": "音箱,蓝牙,配对,连不上",
        "content": "蓝牙配对问题：\n\n1. 确保音箱处于配对模式（长按蓝牙键 3 秒，指示灯蓝白交替闪烁）。\n2. 关闭手机蓝牙后重新打开。\n3. 清除音箱已配对设备：同时按音量+和音量-键 5 秒。\n4. 确保手机距离音箱在 1 米以内。\n5. 尝试用其他手机测试是否为手机兼容问题。",
    },
    # 品牌活动
    {
        "category_id": 12, "type": "qa",
        "title": "极米会员有什么权益？",
        "keywords": "会员,权益,vip,积分",
        "content": "极米会员分为三个等级：\n\n普通会员（免费注册）：享受 1 年质保、产品更新通知。\n\n银卡会员（年消费≥¥2,000）：享受 2 年质保、专属客服通道、生日礼券。\n\n金卡会员（年消费≥¥5,000）：享受 3 年质保、免费上门安装、新品优先体验、VIP 专属客服。\n\n积分规则：每消费 1 元积 1 分，100 积分抵 1 元使用。",
    },
]


def main():
    print("Initializing database...")
    init_db()
    db = SessionLocal()

    print("Seeding categories...")
    for cat in CATEGORIES:
        existing = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == cat["id"]).first()
        if not existing:
            db.add(KnowledgeCategory(**cat))
    db.commit()

    # Create default admin
    existing_admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    if not existing_admin:
        db.add(AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),
            role="super_admin",
        ))
        db.commit()
        print("Created admin user: admin / admin123")

    print("Seeding knowledge items + ChromaDB vectors...")
    rag = RAGService()

    for item_data in KNOWLEDGE_ITEMS:
        existing = db.query(KnowledgeItem).filter(
            KnowledgeItem.title == item_data["title"]
        ).first()
        if not existing:
            item = KnowledgeItem(**item_data)
            db.add(item)
            db.commit()
            db.refresh(item)

            # Add to ChromaDB
            search_text = f"[{item.title}] {item.keywords}\n{item.content}"
            embedding_id = f"kb_{item.id}"
            try:
                rag.add_document(doc_id=embedding_id, content=search_text, metadata={
                    "category_id": str(item.category_id),
                    "type": item.type,
                })
                item.embedding_id = embedding_id
                db.commit()
                print(f"  Added: {item.title} (ChromaDB: {embedding_id})")
            except Exception as e:
                print(f"  Warning: ChromaDB add failed for {item.title}: {e}")

    db.close()
    print(f"Done! Categories: {len(CATEGORIES)}, Items: {len(KNOWLEDGE_ITEMS)}")
    print(f"ChromaDB collection size: {rag.count()}")


if __name__ == "__main__":
    main()
