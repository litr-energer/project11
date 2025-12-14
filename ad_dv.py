# import_all_products_full.py
import sys
import os
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.models.products import ProductModel

# ВСЕ 50 ПРОДУКТОВ ИЗ js.js
ALL_PRODUCTS = [
    {
        "title": "Dota 2 — Полный гид и тактики (eBook)",
        "description": "Подробные тактики, сборки и разбор ролей — eBook для игроков всех уровней.",
        "price": Decimal("499.00"),
        "category": "dota2",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
        "popularity": 95,
        "is_active": True
    },
    {
        "title": "Five Nights at Freddy's — Анализ и путеводитель (eBook)",
        "description": "Критический разбор серии, история создания и тайны — электронная книга.",
        "price": Decimal("299.00"),
        "category": "fnaf",
        "image_url": "https://avatars.mds.yandex.net/i?id=a766a89ca074b8947d85daae5bb5a330005afab5-4479100-images-thumbs&n=13",
        "popularity": 85,
        "is_active": True
    },
    {
        "title": "Half-Life 2 — История разработки и геймдизайн (eBook)",
        "description": "Электронная книга о создании Half-Life 2, дизайне уровней и влиянии на индустрию.",
        "price": Decimal("299.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/220/header.jpg",
        "popularity": 80,
        "is_active": True
    },
    {
        "title": "BioShock Infinite — Сюжетный анализ и артбук (eBook)",
        "description": "Разбор сюжета, символики и иллюстрации — цифровой артбук.",
        "price": Decimal("399.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/8870/header.jpg",
        "popularity": 75,
        "is_active": True
    },
    {
        "title": "Resident Evil 2 — Полный разбор сюжета и стратегии (eBook)",
        "description": "Сюжетный разбор, советы по выживанию и коллекционные заметки.",
        "price": Decimal("499.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/883710/header.jpg",
        "popularity": 88,
        "is_active": True
    },
    {
        "title": "CS:GO — Тактики, карты и экономия (eBook)",
        "description": "Практические руководства по картам, экономике и стрельбе.",
        "price": Decimal("399.00"),
        "category": "guides",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
        "popularity": 90,
        "is_active": True
    },
    {
        "title": "Мульти-игровые эссе: Анализ механик (eBook)",
        "description": "Сборник статей о дизайне и механиках популярных игр.",
        "price": Decimal("299.00"),
        "category": "guides",
        "image_url": "https://www.ixbt.com/img/n1/news/2023/4/3/100-best-games-hp-b_large.jpg",
        "popularity": 70,
        "is_active": True
    },
    {
        "title": "Devil May Cry 5 — Комбат-гайд и артбуки (eBook)",
        "description": "Комбат-гайд, приёмы и сборник концепт-артов.",
        "price": Decimal("399.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/601150/header.jpg",
        "popularity": 82,
        "is_active": True
    },
    {
        "title": "Among Us — Психология и стратегии (eBook)",
        "description": "Стратегии для экипажа и предателя, советы для командной игры.",
        "price": Decimal("149.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/945360/header.jpg",
        "popularity": 85,
        "is_active": True
    },
    {
        "title": "Hitman — Стелс-проекты и прохождения (eBook)",
        "description": "Полные прохождения и креативные способы завершения контрактов.",
        "price": Decimal("299.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/236870/header.jpg",
        "popularity": 78,
        "is_active": True
    },
    {
        "title": "Dark Souls — Руководство по боссам и билдам (eBook)",
        "description": "Стратегии для победы над боссами и оптимальные сборки.",
        "price": Decimal("349.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/570940/header.jpg",
        "popularity": 87,
        "is_active": True
    },
    {
        "title": "Silent Hill 2 — Исследование тем и символов (eBook)",
        "description": "Глубокий анализ тем, символики и интерпретаций Silent Hill 2.",
        "price": Decimal("249.00"),
        "category": "classic",
        "image_url": "https://avatars.mds.yandex.net/i?id=a559f5b60ae74cc430b91a9d9137ad9f261a2d9c-12421307-images-thumbs&n=13",
        "popularity": 83,
        "is_active": True
    },
    {
        "title": "Devil May Cry 3 — Мастерство боя (eBook)",
        "description": "Гайды по комбинациям, стилям и сложностям.",
        "price": Decimal("199.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/490820/header.jpg",
        "popularity": 76,
        "is_active": True
    },
    {
        "title": "Hitman 2 — Карты и оптимальные маршруты (eBook)",
        "description": "Разбор карт и лучших маршрутов для целей.",
        "price": Decimal("249.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/863550/header.jpg",
        "popularity": 79,
        "is_active": True
    },
    {
        "title": "Dark Souls III — Гид по билдам и тактикам (eBook)",
        "description": "Тактики и билды для продвинутых игроков.",
        "price": Decimal("349.00"),
        "category": "classic",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/374320/header.jpg",
        "popularity": 88,
        "is_active": True
    },
    {
        "title": "Civilization VI — Полный стратегический гид (eBook)",
        "description": "Гайд по цивилизациям, победным стратегиям и оптимальным маршрутам развития.",
        "price": Decimal("399.00"),
        "category": "strategy",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/289070/header.jpg",
        "popularity": 84,
        "is_active": True
    },
    {
        "title": "Stellaris — Имперская стратегия и экономика (eBook)",
        "description": "Углублённый разбор управления империей, экономики и дипломатии.",
        "price": Decimal("349.00"),
        "category": "strategy",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/281990/header.jpg",
        "popularity": 81,
        "is_active": True
    },
    {
        "title": "The Witcher 3 — Лор, квесты и билд-гайд (eBook)",
        "description": "Подробный разбор сюжета, заданий и советов по построению персонажа.",
        "price": Decimal("499.00"),
        "category": "rpg",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg",
        "popularity": 92,
        "is_active": True
    },
    {
        "title": "Honkai: Star Rail — Сюжетный разбор и лор (eBook)",
        "description": "Глубокий разбор истории мира, персонажей и скрытых связей — для поклонников Honkai: Star Rail.",
        "price": Decimal("349.00"),
        "category": "lore",
        "image_url": "https://www.goha.ru/s/E:Mn/sn/vTJS8VZtDK.jpg",
        "popularity": 82,
        "is_active": True
    },
    {
        "title": "Genshin Impact — Исследование сюжета и персонажей (eBook)",
        "description": "Аналитические эссе по основным сюжетным линиям, архетипам персонажей и теории мира Teyvat.",
        "price": Decimal("399.00"),
        "category": "analysis",
        "image_url": "https://ir.ozone.ru/s3/multimedia-p/6383185753.jpg",
        "popularity": 86,
        "is_active": True
    },
    {
        "title": "Factorio — Автоматизация и оптимизация (eBook)",
        "description": "Руководство по автоматическим фабрикам, балансировке и логистике.",
        "price": Decimal("299.00"),
        "category": "simulation",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/427520/header.jpg",
        "popularity": 77,
        "is_active": True
    },
    {
        "title": "Portal — Решение головоломок и механики (eBook)",
        "description": "Разбор механик порталов и пошаговые решения для сложных комнат.",
        "price": Decimal("199.00"),
        "category": "puzzle",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/400/header.jpg",
        "popularity": 74,
        "is_active": True
    },
    {
        "title": "Hollow Knight — Руководство по лору и картам (eBook)",
        "description": "Анализ мира, карты и советы по изучению глубин королевства.",
        "price": Decimal("249.00"),
        "category": "indie",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/367520/header.jpg",
        "popularity": 83,
        "is_active": True
    },
    {
        "title": "Kingdom Builder — Тактики и экономические стратегии (eBook)",
        "description": "Тактики экономического развития и роста королевства.",
        "price": Decimal("279.00"),
        "category": "strategy",
        "image_url": "https://i.pinimg.com/736x/de/49/5c/de495c9f0ef6d94efdbf288a3afca1d3.jpg",
        "popularity": 68,
        "is_active": True
    },
    {
        "title": "RimWorld — Выживание и управление колонией (eBook)",
        "description": "Советы по планированию базы, управлению ресурсами и модулям.",
        "price": Decimal("319.00"),
        "category": "simulation",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/294100/header.jpg",
        "popularity": 79,
        "is_active": True
    },
    {
        "title": "Disco Elysium — Наратив и дизайн персонажей (eBook)",
        "description": "Аналитические эссе о письме, диалогах и построении мира.",
        "price": Decimal("299.00"),
        "category": "rpg",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/632470/header.jpg",
        "popularity": 85,
        "is_active": True
    },
    {
        "title": "Celeste — Платформинг и тренировка навыков (eBook)",
        "description": "Практические советы по оттачиванию трюков и улучшению скорости.",
        "price": Decimal("149.00"),
        "category": "indie",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/504230/header.jpg",
        "popularity": 76,
        "is_active": True
    },
    {
        "title": "Slay the Spire — Карточные стратегии и билды (eBook)",
        "description": "Сборники билдов, маршрутов и сочетаний карт для победы.",
        "price": Decimal("199.00"),
        "category": "strategy",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/646570/header.jpg",
        "popularity": 80,
        "is_active": True
    },
    {
        "title": "Stardew Valley — Фермерство и гайд по экономике (eBook)",
        "description": "Пошаговые руководства по фермерству, оптимизации и расписанию.",
        "price": Decimal("179.00"),
        "category": "simulation",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/413150/header.jpg",
        "popularity": 82,
        "is_active": True
    },
    {
        "title": "Tetris — Архитектура скоростей и техники (eBook)",
        "description": "Техники позиционирования, скорости и улучшения реакций.",
        "price": Decimal("99.00"),
        "category": "puzzle",
        "image_url": "https://avatars.mds.yandex.net/i?id=587e0f82f6e8524c184911ad9906cfce_l-5008975-images-thumbs&n=13",
        "popularity": 65,
        "is_active": True
    },
    {
        "title": "Pokemon — Командные сборки и соревнования (eBook)",
        "description": "Метагейм, построение команд и советы для турниров.",
        "price": Decimal("249.00"),
        "category": "rpg",
        "image_url": "https://avatars.mds.yandex.net/i?id=253b13385ef0243a9829c3927ba30051_l-5239905-images-thumbs&n=13",
        "popularity": 73,
        "is_active": True
    },
    {
        "title": "Cyberpunk 2077 — Практический гид и квесты (eBook)",
        "description": "Подробные прохождения квестов, билды и оптимизация персонажа.",
        "price": Decimal("349.00"),
        "category": "rpg",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
        "popularity": 84,
        "is_active": True
    },
    {
        "title": "Elden Ring — Тактики боссов и билды (eBook)",
        "description": "Разбор механик боссов, оптимальные билды и маршруты по локациям.",
        "price": Decimal("399.00"),
        "category": "rpg",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/1248130/header.jpg",
        "popularity": 91,
        "is_active": True
    },
    {
        "title": "Zelda: Breath of the Wild — Исследовательский гид (eBook)",
        "description": "Маршруты, секреты и советы по выживанию в открытом мире Hyrule.",
        "price": Decimal("299.00"),
        "category": "adventure",
        "image_url": "https://static0.srcdn.com/wordpress/wp-content/uploads/2023/5/tears-of-the-kingdom-legend-of-zelda.jpg?w=1200&h=675&fit=crop",
        "popularity": 87,
        "is_active": True
    },
    {
        "title": "Persona 5 — Наративный разбор и тактики (eBook)",
        "description": "Разбор персонажей, сюжетных выборов и оптимизации расписания.",
        "price": Decimal("249.00"),
        "category": "rpg",
        "image_url": "https://avatars.mds.yandex.net/i?id=474ed74995c77dec5e73c333e8451b40_l-7025550-images-thumbs&n=13",
        "popularity": 79,
        "is_active": True
    },
    {
        "title": "Hades — Комбат, боевые сборки и прохождения (eBook)",
        "description": "Советы по сборкам, использованию благ и эффективным маршрутам в пекле.",
        "price": Decimal("179.00"),
        "category": "indie",
        "image_url": "https://avatars.mds.yandex.net/i?id=c46f21409d91663d3286e332bff16b15_l-4055806-images-thumbs&n=13",
        "popularity": 85,
        "is_active": True
    },
    {
        "title": "FIFA — Тактики и менеджмент команды (eBook)",
        "description": "Построение состава, тактические схемы и советы для управления клубом.",
        "price": Decimal("179.00"),
        "category": "sports",
        "image_url": "https://avatars.mds.yandex.net/i?id=1b21347ace9ad0a12941c731178ae94e_l-12762283-images-thumbs&n=13",
        "popularity": 72,
        "is_active": True
    },
    {
        "title": "Forza Horizon — Тюнинг и оптимизация машин (eBook)",
        "description": "Руководство по тюнингу, балансировке и подбору настроек для гонок.",
        "price": Decimal("219.00"),
        "category": "simulation",
        "image_url": "https://avatars.mds.yandex.net/i?id=7b439515c8eb2e85e06ee271ecf6bf74bba6856c-10555755-images-thumbs&n=13",
        "popularity": 74,
        "is_active": True
    },
    {
        "title": "Minecraft — Редстоун, фабрики и автоматизация (eBook)",
        "description": "Пошаговые схемы редстоуна, автоматизация ферм и полезные проекты.",
        "price": Decimal("159.00"),
        "category": "creative",
        "image_url": "https://avatars.mds.yandex.net/i?id=046e39d96ff55340caa9233088af1798_l-4593530-images-thumbs&n=13",
        "popularity": 88,
        "is_active": True
    },
    {
        "title": "Skyrim — Создание модов и улучшение геймплея (eBook)",
        "description": "Как создавать моды, пользоваться инструментами и улучшать игру.",
        "price": Decimal("199.00"),
        "category": "rpg",
        "image_url": "https://avatars.mds.yandex.net/i?id=a559f5b60ae74cc430b91a9d9137ad9f261a2d9c-12421307-images-thumbs&n=13",
        "popularity": 77,
        "is_active": True
    },
    {
        "title": "Subnautica — Выживание и постройки под водой (eBook)",
        "description": "Советы по выживанию, постройке базы и исследованию глубин.",
        "price": Decimal("189.00"),
        "category": "survival",
        "image_url": "https://cdn1.epicgames.com/offer/jaguar/SN_EpicLandscape_2560x1440-68271847bd0a1a7adac3992f9d2a996a_2560x1440-984d9943bcc436738c44220778d4407d",
        "popularity": 81,
        "is_active": True
    },
    {
        "title": "Planet Zoo — Менеджмент парка и животные (eBook)",
        "description": "Проектирование вольеров, забота о животных и экономика парка.",
        "price": Decimal("229.00"),
        "category": "management",
        "image_url": "https://avatars.mds.yandex.net/i?id=c8d0195be1f63968ad498ad07d8d08c9_l-5220454-images-thumbs&n=13",
        "popularity": 69,
        "is_active": True
    },
    {
        "title": "Ori and the Blind Forest — Платформинг и приёмы (eBook)",
        "description": "Приёмы, трюки и техника для сложных платформенных участков.",
        "price": Decimal("129.00"),
        "category": "platformer",
        "image_url": "https://cdn.wccftech.com/wp-content/uploads/2015/4/Ori-and-the-Blind-Forest-5.jpg",
        "popularity": 75,
        "is_active": True
    },
    {
        "title": "The Long Dark — Холод и выживание в дикой природе (eBook)",
        "description": "Гайды по выживанию, управлению ресурсами и планированию путешествий.",
        "price": Decimal("169.00"),
        "category": "survival",
        "image_url": "https://digital-basket-01.wbbasket.ru/vol4/564/970318f6cff57e4507f82144399504a8/1920.jpg",
        "popularity": 73,
        "is_active": True
    },
    {
        "title": "Mortal Kombat 11 — Комбо и матчи высокого уровня (eBook)",
        "description": "Сборник проверенных комбо, фрейм-дата и стратегий против популярных персонажей.",
        "price": Decimal("199.00"),
        "category": "fighting",
        "image_url": "https://avatars.mds.yandex.net/i?id=d602140b3affa6dc0d7b1a4c4062310c32174cbf-5334917-images-thumbs&n=13",
        "popularity": 76,
        "is_active": True
    },
    {
        "title": "Football Tactics — Тактики и построения (eBook)",
        "description": "Построения, тактические замены и тренировки для онлайн-матчей.",
        "price": Decimal("129.00"),
        "category": "sports",
        "image_url": "https://avatars.mds.yandex.net/i?id=6d9f8acc47df7c51c6451f3eb9452814c3af8ffa-3766334-images-thumbs&n=13",
        "popularity": 68,
        "is_active": True
    },
    {
        "title": "XCOM — Тактика против инопланетян (eBook)",
        "description": "Планирование миссий, прокачка солдат и управление ресурсами.",
        "price": Decimal("269.00"),
        "category": "strategy",
        "image_url": "https://cdn.cloudflare.steamstatic.com/steam/apps/200510/header.jpg",
        "popularity": 78,
        "is_active": True
    },
    {
        "title": "Noita — Механики и экспериментальные сборники (eBook)",
        "description": "Тактики по оптимизации процессов на кухне и секреты рецептов.",
        "price": Decimal("179.00"),
        "category": "indie",
        "image_url": "https://avatars.mds.yandex.net/i?id=c0fc7922c16fcf6b9db43bd4fdfc4e40a2f03cef-2390381-images-thumbs&n=13",
        "popularity": 71,
        "is_active": True
    },
    {
        "title": "RPG Photography — Съёмка и композиция в играх (eBook)",
        "description": "Советы по съемке скриншотов, композиции и постобработке.",
        "price": Decimal("149.00"),
        "category": "creative",
        "image_url": "https://img.freepik.com/premium-photo/fantastic-epic-magical-landscape-mountains-summer-nature-mystic-forest-gaming-rpg-background_636456-2552.jpg",
        "popularity": 64,
        "is_active": True
    }
]

def import_all_products():
    """Импортирует ВСЕ 50 продуктов в базу данных"""
    
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("ИМПОРТ ВСЕХ 50 ПРОДУКТОВ ИЗ js.js")
        print("=" * 60)
        
        # Сначала очистим таблицу (опционально)
        from sqlalchemy.sql import text
        db.execute(text("DELETE FROM products"))
        print("✅ Таблица products очищена")
        
        # Импортируем все продукты
        imported_count = 0
        for product_data in ALL_PRODUCTS:
            product = ProductModel(**product_data)
            db.add(product)
            imported_count += 1
            print(f"  [{imported_count:2d}] {product_data['title'][:40]}...")
        
        db.commit()
        
        print("=" * 60)
        print(f"✅ УСПЕШНО ИМПОРТИРОВАНО: {imported_count} ПРОДУКТОВ!")
        print("=" * 60)
        
        # Проверяем результат
        total_count = db.query(ProductModel).count()
        print(f"\n📊 Всего продуктов в БД: {total_count}")
        
        # Статистика по категориям
        print("\n📈 Распределение по категориям:")
        categories = {}
        for product in ALL_PRODUCTS:
            cat = product['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} товаров")
        
        # Показываем несколько примеров
        print("\n🔍 Примеры добавленных товаров:")
        sample_products = db.query(ProductModel).order_by(ProductModel.id.desc()).limit(5).all()
        for p in sample_products:
            print(f"  • {p.title} - {p.price} руб.")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def check_current_data():
    """Проверяет текущие данные в БД"""
    db = SessionLocal()
    
    try:
        count = db.query(ProductModel).count()
        print(f"\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ БАЗЫ:")
        print(f"   Всего продуктов: {count}")
        
        if count > 0:
            print("\n   Последние 5 продуктов:")
            products = db.query(ProductModel).order_by(ProductModel.id.desc()).limit(5).all()
            for p in products:
                print(f"   • {p.id}: {p.title}")
    finally:
        db.close()

if __name__ == "__main__":
    # Показываем текущее состояние
    check_current_data()
    
    # Спрашиваем подтверждение
    print("\n" + "=" * 60)
    response = input("Загрузить ВСЕ 50 продуктов в базу данных? (y/n): ").strip().lower()
    
    if response == 'y':
        import_all_products()
        print("\n🎉 ИМПОРТ ЗАВЕРШЕН!")
        print("\nТеперь проверьте API:")
        print("  http://localhost:8000/products/")
        print("  http://localhost:8000/products/?skip=0&limit=10")
        
        # Быстрая проверка
        check_current_data()
    else:
        print("Импорт отменен.")