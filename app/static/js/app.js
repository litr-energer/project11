const PRODUCTS = [
  {
    id: "dota2-guide",
    title: "Dota 2 — Полный гид и тактики (eBook)",
    category: "dota2",
    price: 499,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
    tag: "Гид",
    desc: "Подробные тактики, сборки и разбор ролей — eBook для игроков всех уровней."
  },
  {
    id: "fnaf-ebook",
    title: "Five Nights at Freddy's — Анализ и путеводитель (eBook)",
    category: "fnaf",
    price: 299,
    thumb: "https://static.wikia.nocookie.net/fnaf/images/7/71/FNAF_Logo.png",
    tag: "Анализ",
    desc: "Критический разбор серии, история создания и тайны — электронная книга."
  },
  {
    id: "hl2",
    title: "Half-Life 2 — История разработки и геймдизайн (eBook)",
    category: "classic",
    price: 299,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/220/header.jpg",
    tag: "История",
    desc: "Электронная книга о создании Half-Life 2, дизайне уровней и влиянии на индустрию."
  },
  {
    id: "bioshock-inf",
    title: "BioShock Infinite — Сюжетный анализ и артбук (eBook)",
    category: "classic",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/8870/header.jpg",
    tag: "Артбук",
    desc: "Разбор сюжета, символики и иллюстрации — цифровой артбук."
  },
  {
    id: "resident-evil-2",
    title: "Resident Evil 2 — Полный разбор сюжета и стратегии (eBook)",
    category: "classic",
    price: 499,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/883710/header.jpg",
    tag: "Гайд",
    desc: "Сюжетный разбор, советы по выживанию и коллекционные заметки."
  },

  // New account-type products (CS:GO accounts and similar)
  {
    id: "csgo-guide",
    title: "CS:GO — Тактики, карты и экономия (eBook)",
    category: "guides",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
    tag: "Гайд",
    desc: "Практические руководства по картам, экономике и стрельбе."
  },
  {
    id: "multigame-essay",
    title: "Мульти-игровые эссе: Анализ механик (eBook)",
    category: "guides",
    price: 299,
    thumb: "https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/570/570_header.jpg",
    tag: "Анализ",
    desc: "Сборник статей о дизайне и механиках популярных игр."
  },

  // Additional requested game product entries
  {
    id: "devil-may-cry5",
    title: "Devil May Cry 5 — Комбат-гайд и артбуки (eBook)",
    category: "classic",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/601150/header.jpg",
    tag: "Гайд",
    desc: "Комбат-гайд, приёмы и сборник концепт-артов."
  },
  {
    id: "among-us",
    title: "Among Us — Психология и стратегии (eBook)",
    category: "classic",
    price: 149,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/945360/header.jpg",
    tag: "Стратегии",
    desc: "Стратегии для экипажа и предателя, советы для командной игры."
  },
  {
    id: "hitman-2016",
    title: "Hitman — Стелс-проекты и прохождения (eBook)",
    category: "classic",
    price: 299,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/236870/header.jpg",
    tag: "Гайд",
    desc: "Полные прохождения и креативные способы завершения контрактов."
  },
  {
    id: "dark-souls",
    title: "Dark Souls — Руководство по боссам и билдам (eBook)",
    category: "classic",
    price: 349,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570940/header.jpg",
    tag: "Гайд",
    desc: "Стратегии для победы над боссами и оптимальные сборки."
  },
  {
    id: "silent-hill-2",
    title: "Silent Hill 2 — Исследование тем и символов (eBook)",
    category: "classic",
    price: 249,
    thumb: "https://via.placeholder.com/600x200?text=Silent+Hill+2",
    tag: "Анализ",
    desc: "Глубокий анализ тем, символики и интерпретаций Silent Hill 2."
  },
  {
    id: "devil-may-cry-3",
    title: "Devil May Cry 3 — Мастерство боя (eBook)",
    category: "classic",
    price: 199,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/490820/header.jpg",
    tag: "Гайд",
    desc: "Гайды по комбинациям, стилям и сложностям."
  },
  {
    id: "hitman-2",
    title: "Hitman 2 — Карты и оптимальные маршруты (eBook)",
    category: "classic",
    price: 249,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/863550/header.jpg",
    tag: "Гайд",
    desc: "Разбор карт и лучших маршрутов для целей."
  },
  {
    id: "dark-souls-3",
    title: "Dark Souls III — Гид по билдам и тактикам (eBook)",
    category: "classic",
    price: 349,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/374320/header.jpg",
    tag: "Гайд",
    desc: "Тактики и билды для продвинутых игроков."
  },

  // Replaced previous horror entries with non-horror titles (strategy, RPG, simulation, puzzles, indie)
  {
    id: "civ6-strategy",
    title: "Civilization VI — Полный стратегический гид (eBook)",
    category: "strategy",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/289070/header.jpg",
    tag: "Стратегия",
    desc: "Гайд по цивилизациям, победным стратегиям и оптимальным маршрутам развития."
  },
  {
    id: "stellaris-analytics",
    title: "Stellaris — Имперская стратегия и экономика (eBook)",
    category: "strategy",
    price: 349,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/281990/header.jpg",
    tag: "Гайд",
    desc: "Углублённый разбор управления империей, экономики и дипломатии."
  },
  {
    id: "witcher3-lore",
    title: "The Witcher 3 — Лор, квесты и билд-гайд (eBook)",
    category: "rpg",
    price: 499,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/header.jpg",
    tag: "Лор",
    desc: "Подробный разбор сюжета, заданий и советов по построению персонажа."
  },

  // New story/analysis additions
  {
    id: "honkai-star-rail-lore",
    title: "Honkai: Star Rail — Сюжетный разбор и лор (eBook)",
    category: "lore",
    price: 349,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/1669000/header.jpg",
    tag: "Лор",
    desc: "Глубокий разбор истории мира, персонажей и скрытых связей — для поклонников Honkai: Star Rail."
  },
  {
    id: "genshin-story-analysis",
    title: "Genshin Impact — Исследование сюжета и персонажей (eBook)",
    category: "analysis",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/1330720/header.jpg",
    tag: "Анализ",
    desc: "Аналитические эссе по основным сюжетным линиям, архетипам персонажей и теории мира Teyvat."
  },

  {
    id: "factorio-guide",
    title: "Factorio — Автоматизация и оптимизация (eBook)",
    category: "simulation",
    price: 299,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/427520/header.jpg",
    tag: "Авто",
    desc: "Руководство по автоматическим фабрикам, балансировке и логистике."
  },
  {
    id: "portal-puzzles",
    title: "Portal — Решение головоломок и механики (eBook)",
    category: "puzzle",
    price: 199,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/400/header.jpg",
    tag: "Пазлы",
    desc: "Разбор механик порталов и пошаговые решения для сложных комнат."
  },
  {
    id: "hollow-knight-lore",
    title: "Hollow Knight — Руководство по лору и картам (eBook)",
    category: "indie",
    price: 249,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/367520/header.jpg",
    tag: "Инди",
    desc: "Анализ мира, карты и советы по изучению глубин королевства."
  },
  {
    id: "kingdoms-andquests",
    title: "Kingdom Builder — Тактики и экономические стратегии (eBook)",
    category: "strategy",
    price: 279,
    thumb: "https://via.placeholder.com/600x200?text=Kingdom+Guide",
    tag: "Стратегия",
    desc: "Тактики экономического развития и роста королевства."
  },
  {
    id: "rimworld-survival",
    title: "RimWorld — Выживание и управление колонией (eBook)",
    category: "simulation",
    price: 319,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/294100/header.jpg",
    tag: "Выживание",
    desc: "Советы по планированию базы, управлению ресурсами и модулям."
  },
  {
    id: "disco-elysium-essays",
    title: "Disco Elysium — Наратив и дизайн персонажей (eBook)",
    category: "rpg",
    price: 299,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/632470/header.jpg",
    tag: "Наратив",
    desc: "Аналитические эссе о письме, диалогах и построении мира."
  },
  {
    id: "celeste-guide",
    title: "Celeste — Платформинг и тренировка навыков (eBook)",
    category: "indie",
    price: 149,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/504230/header.jpg",
    tag: "Платформер",
    desc: "Практические советы по оттачиванию трюков и улучшению скорости."
  },
  {
    id: "slay-the-spire",
    title: "Slay the Spire — Карточные стратегии и билды (eBook)",
    category: "strategy",
    price: 199,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/646570/header.jpg",
    tag: "Карточная",
    desc: "Сборники билдов, маршрутов и сочетаний карт для победы."
  },
  {
    id: "stardew-farming",
    title: "Stardew Valley — Фермерство и гайд по экономике (eBook)",
    category: "simulation",
    price: 179,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/413150/header.jpg",
    tag: "Ферма",
    desc: "Пошаговые руководства по фермерству, оптимизации и расписанию."
  },
  {
    id: "tetris-architecture",
    title: "Tetris — Архитектура скоростей и техники (eBook)",
    category: "puzzle",
    price: 99,
    thumb: "https://via.placeholder.com/600x200?text=Tetris+Guide",
    tag: "Пазлы",
    desc: "Техники позиционирования, скорости и улучшения реакций."
  },

  // New non-horror additions
  {
    id: "pokemon-competitive",
    title: "Pokemon — Командные сборки и соревнования (eBook)",
    category: "rpg",
    price: 249,
    thumb: "https://via.placeholder.com/600x200?text=Pokemon+Guide",
    tag: "Команды",
    desc: "Метагейм, построение команд и советы для турниров."
  },
  {
    id: "cyberpunk-2077-guide",
    title: "Cyberpunk 2077 — Практический гид и квесты (eBook)",
    category: "rpg",
    price: 349,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
    tag: "Гайд",
    desc: "Подробные прохождения квестов, билды и оптимизация персонажа."
  },
  {
    id: "elden-ring-bosses",
    title: "Elden Ring — Тактики боссов и билды (eBook)",
    category: "rpg",
    price: 399,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/1248130/header.jpg",
    tag: "Гайд",
    desc: "Разбор механик боссов, оптимальные билды и маршруты по локациям."
  },
  {
    id: "zelda-botw-explorer",
    title: "Zelda: Breath of the Wild — Исследовательский гид (eBook)",
    category: "adventure",
    price: 299,
    thumb: "https://via.placeholder.com/600x200?text=Zelda+Guide",
    tag: "Путеводитель",
    desc: "Маршруты, секреты и советы по выживанию в открытoм мире Hyrule."
  },
  {
    id: "persona5-analysis",
    title: "Persona 5 — Наративный разбор и тактики (eBook)",
    category: "rpg",
    price: 249,
    thumb: "https://via.placeholder.com/600x200?text=Persona+5",
    tag: "Анализ",
    desc: "Разбор персонажей, сюжетных выборов и оптимизации расписания."
  },
  {
    id: "hades-combat-guide",
    title: "Hades — Комбат, боевые сборки и прохождения (eBook)",
    category: "indie",
    price: 179,
    thumb: "https://via.placeholder.com/600x200?text=Hades+Guide",
    tag: "Гайд",
    desc: "Советы по сборкам, использованию благ и эффективным маршрутам в пекле."
  },
  {
    id: "fifa-tactics",
    title: "FIFA — Тактики и менеджмент команды (eBook)",
    category: "sports",
    price: 179,
    thumb: "https://via.placeholder.com/600x200?text=FIFA+Tactics",
    tag: "Спорт",
    desc: "Построение состава, тактические схемы и советы для управления клубом."
  },
  {
    id: "forza-tuning",
    title: "Forza Horizon — Тюнинг и оптимизация машин (eBook)",
    category: "simulation",
    price: 219,
    thumb: "https://via.placeholder.com/600x200?text=Forza+Tuning",
    tag: "Авто",
    desc: "Руководство по тюнингу, балансировке и подбору настроек для гонок."
  },
  {
    id: "minecraft-redstone",
    title: "Minecraft — Редстоун, фабрики и автоматизация (eBook)",
    category: "creative",
    price: 159,
    thumb: "https://via.placeholder.com/600x200?text=Minecraft+Redstone",
    tag: "Авто",
    desc: "Пошаговые схемы редстоуна, автоматизация ферм и полезные проекты."
  },
  {
    id: "skyrim-modding",
    title: "Skyrim — Создание модов и улучшение геймплея (eBook)",
    category: "rpg",
    price: 199,
    thumb: "https://via.placeholder.com/600x200?text=Skyrim+Modding",
    tag: "Моддинг",
    desc: "Как создавать моды, пользоваться инструментами и улучшать игру."
  },
  {
    id: "subnautica-survival",
    title: "Subnautica — Выживание и постройки под водой (eBook)",
    category: "survival",
    price: 189,
    thumb: "https://via.placeholder.com/600x200?text=Subnautica+Guide",
    tag: "Выживание",
    desc: "Советы по выживанию, постройке базы и исследованию глубин."
  },
  {
    id: "planet-zoo-management",
    title: "Planet Zoo — Менеджмент парка и животные (eBook)",
    category: "management",
    price: 229,
    thumb: "https://via.placeholder.com/600x200?text=Planet+Zoo",
    tag: "Менеджмент",
    desc: "Проектирование вольеров, забота о животных и экономика парка."
  },
  {
    id: "ori-platforming",
    title: "Ori and the Blind Forest — Платформинг и приёмы (eBook)",
    category: "platformer",
    price: 129,
    thumb: "https://via.placeholder.com/600x200?text=Ori+Guide",
    tag: "Платформер",
    desc: "Приёмы, трюки и техника для сложных платформенных участков."
  },
  {
    id: "the-long-dark",
    title: "The Long Dark — Холод и выживание в дикой природе (eBook)",
    category: "survival",
    price: 169,
    thumb: "https://via.placeholder.com/600x200?text=The+Long+Dark",
    tag: "Выживание",
    desc: "Гайды по выживанию, управлению ресурсами и планированию путешествий."
  },

  {
    id: "mk11-combo-guide",
    title: "Mortal Kombat 11 — Комбо и матчи высокого уровня (eBook)",
    category: "fighting",
    price: 199,
    thumb: "https://via.placeholder.com/600x200?text=MK11+Guide",
    tag: "Файтинг",
    desc: "Сборник проверенных комбо, фрейм-дата и стратегий против популярных персонажей."
  },
  {
    id: "efootball-tactics",
    title: "Football Tactics — Тактики и построения (eBook)",
    category: "sports",
    price: 129,
    thumb: "https://via.placeholder.com/600x200?text=Football+Tactics",
    tag: "Спорт",
    desc: "Построения, тактические замены и тренировки для онлайн-матчей."
  },
  {
    id: "xcom-strategy",
    title: "XCOM — Тактика против инопланетян (eBook)",
    category: "strategy",
    price: 269,
    thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/200510/header.jpg",
    tag: "Тактика",
    desc: "Планирование миссий, прокачка солдат и управление ресурсами."
  },
  {
    id: "noita-mechanics",
    title: "Noita — Механики и экспериментальные сборники (eBook)",
    category: "indie",
    price: 179,
    thumb: "https://via.placeholder.com/600x200?text=Noita+Guide",
    tag: "Инди",
    desc: "Тактики по оптимизации процессов на кухне и секреты рецептов."
  },
  {
    id: "rpg-camera-techniques",
    title: "RPG Photography — Съёмка и композиция в играх (eBook)",
    category: "creative",
    price: 149,
    thumb: "https://via.placeholder.com/600x200?text=Game+Photography",
    tag: "Креатив",
    desc: "Советы по съемке скриншотов, композиции и постобработке."
  }
];

const state = {
  products: PRODUCTS.slice(),
  cart: JSON.parse(localStorage.getItem('kv_cart')||'{}'),
  query: "",
  category: "all",
  sort: "popular",
  marketListings: [
    // example listing
    {
      id: "lst-1",
      title: "AWP | Истории коллекционеров (eBook)",
      game: "CS:GO",
      price: 399,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
      seller: "Игрок123"
    },
    {
      id: "lst-2",
      title: "Rare Courier — Истории предметов (eBook)",
      game: "Dota 2",
      price: 349,
      thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
      seller: "MarketPro"
    }
  ],
  accountListings: [
    // repurposed to author/indie publications
    { id: "acc-1", title: "Авторское издание: Истории CS:GO", games: "CS:GO", price: 249, thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg", seller: "MarketUser" },
    { id: "acc-2", title: "Авторское издание: Курьеры Dota 2", games: "Dota 2", price: 299, thumb: "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg", seller: "SellerPro" }
  ],
  reviews: [
    { id:1, name:"Алексей", text:"Купил гайдовую книгу по Dota 2 — всё подробно и понятно.", rating:5 },
    { id:2, name:"Мария", text:"Поддержка помогла с загрузкой eBook, спасибо!", rating:5 },
    { id:3, name:"Иван", text:"Качественные материалы, много полезных схем.", rating:5 },
    { id:4, name:"Ольга", text:"Найденный гид по Silent Hill превзошёл ожидания.", rating:5 },
    { id:5, name:"Дмитрий", text:"Удобная биржа и понятный интерфейс магазина.", rating:4 },
    { id:6, name:"Светлана", text:"Обложки и превью хорошие, хотелось бы больше демо-страниц.", rating:4 },
    { id:7, name:"Роман", text:"Авторские издания отличные — поддержал одного инди-автора.", rating:5 },
    { id:8, name:"Екатерина", text:"Быстро получила ссылку после оплаты, всё работает.", rating:5 },
    { id:9, name:"Павел", text:"Хорошие цены на тематические сборники.", rating:4 },
    { id:11, name:"Никита", text:"Купил гайд по CS:GO — полезные карты и советы.", rating:5 },
    { id:12, name:"Алина", text:"Интерфейс приятный, мобильная версия удобна.", rating:4 },
    { id:14, name:"Марина", text:"Были небольшие задержки с публикацией, но поддержка решила.", rating:4 },
    { id:15, name:"Сергей", text:"Качество PDF на уровне, рекомендую магазин.", rating:5 },
    { id:16, name:"Людмила", text:"Отличные руководства по стратегии — многое стало понятнее.", rating:5 },
    { id:17, name:"Влад", text:"Нашёл редкую книгу по моддингу Skyrim, всё прошло быстро.", rating:4 }
  ],
  user: JSON.parse(localStorage.getItem('kv_user')||'null'),
  chat: {
    messages: [
      // sample system message
      { id: 'sys-1', author: 'bot', text: 'Здравствуйте! Чем можем помочь?' }
    ]
  },
  favorites: JSON.parse(localStorage.getItem('kv_favs')||'[]') // added favorites state
};

const el = selector => document.querySelector(selector);
const els = selector => Array.from(document.querySelectorAll(selector));

function formatPrice(p){
  return (p === 0) ? "Free" : `${p.toLocaleString('ru-RU')} ₽`;
}

/* Render products */
function renderProducts(){
  const container = el('#products');
  container.innerHTML = '';
  let list = state.products.filter(p => {
    if(state.category !== 'all' && p.category !== state.category) return false;
    if(state.query && !`${p.title} ${p.desc} ${p.tag}`.toLowerCase().includes(state.query.toLowerCase())) return false;
    return true;
  });

  if(state.sort === 'price-asc') list.sort((a,b)=>(a.price - b.price));
  if(state.sort === 'price-desc') list.sort((a,b)=>(b.price - a.price));
  if(state.sort === 'popular') list.sort((a,b)=> a.title.localeCompare(b.title));

  list.forEach(p => {
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.pid = p.id; // added dataset to enable 'go to product' from cart
    const isFav = state.favorites.includes(p.id);
    card.innerHTML = `
      <div class="media" role="img" aria-label="${p.title}">
        <img src="${p.thumb}" alt="${p.title}" style="width:100%;height:100%;object-fit:cover">
      </div>
      <div>
        <h3>${p.title}</h3>
        <div class="meta"><span class="tag-pill">${p.tag}</span><span class="price">${formatPrice(p.price)}</span></div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">${p.desc}</p>
      </div>
      <div class="actions">
        <div style="display:flex;gap:8px;flex:1">
          <button class="btn" data-id="${p.id}">Добавить</button>
          <button class="btn ghost buy" data-id="${p.id}">Купить</button>
        </div>
        <button class="btn ghost fav" data-id="${p.id}" aria-label="Избранное">${isFav ? '★' : '☆'}</button>
      </div>
    `;
    container.appendChild(card);
  });
}

/* Render marketplace listings */
function renderMarketplace(){
  const wrap = el('#marketGrid');
  if(!wrap) return;
  wrap.innerHTML = '';
  state.marketListings.forEach(l=>{
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="media" role="img" aria-label="${l.title}">
        <img src="${l.thumb}" alt="${l.title}" style="width:100%;height:100%;object-fit:cover">
      </div>
      <div>
        <h3>${l.title}</h3>
        <div class="meta"><span class="tag-pill">#${l.game}</span><span class="price">${formatPrice(l.price)}</span></div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">Автор: ${l.seller}</p>
      </div>
      <div class="actions">
        <button class="btn primary buy-listing" data-id="${l.id}">Купить</button>
        <button class="btn ghost" data-id="${l.id}" aria-label="Добавить в корзину">Добавить в корзину</button>
      </div>
    `;
    wrap.appendChild(card);
  });
}

/* Render accounts marketplace */
function renderAccountsMarketplace(){
  const wrap = el('#accMarketGrid');
  if(!wrap) return;
  wrap.innerHTML = '';
  state.accountListings.forEach(l=>{
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="media" role="img" aria-label="${l.title}">
        <img src="${l.thumb}" alt="${l.title}" style="width:100%;height:100%;object-fit:cover">
      </div>
      <div>
        <h3>${l.title}</h3>
        <div class="meta"><span class="tag-pill">${l.games}</span><span class="price">${formatPrice(l.price)}</span></div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">Автор: ${l.seller}</p>
      </div>
      <div class="actions">
        <button class="btn primary buy-acc" data-id="${l.id}">Купить</button>
        <button class="btn ghost add-acc" data-id="${l.id}">Добавить в корзину</button>
      </div>
    `;
    wrap.appendChild(card);
  });
}

/* Add account listing to cart */
function addAccountToCart(accId, qty=1){
  const a = state.accountListings.find(x=>x.id===accId);
  if(!a) return;
  const key = `account-${a.id}`;
  state.cart[key] = state.cart[key] || { id: key, title: `${a.title}`, price: a.price, price_display: formatPrice(a.price), thumb: a.thumb, tag: 'Издание', desc: `Автор: ${a.seller}`, qty:0 };
  state.cart[key].qty += qty;
  updateCartUI();
  showToast(`Добавлено: ${a.title}`);
}

/* Add listing item into cart (market listing -> cart item) */
function addListingToCart(listId, qty=1){
  const l = state.marketListings.find(x=>x.id===listId);
  if(!l) return;
  // create cart entry shaped like product
  const key = `listing-${l.id}`;
  state.cart[key] = state.cart[key] || { ...l, qty:0 };
  state.cart[key].qty += qty;
  updateCartUI();
  showToast(`Добавлено: ${l.title}`);
}

/* Render reviews */
function renderReviews(){
  const wrap = el('#reviewsGrid');
  if(!wrap) return;
  wrap.innerHTML = '';
  state.reviews.forEach(r=>{
    const node = document.createElement('div');
    node.className = 'card';
    node.style.padding = '10px';
    node.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
        <div class="profile-avatar" style="width:36px;height:36px;border-radius:8px;font-size:14px">${r.name[0].toUpperCase()}</div>
        <div>
          <strong style="display:block">${r.name}</strong>
          <div style="font-size:12px;color:var(--muted)">${'★'.repeat(r.rating)}${'☆'.repeat(5-r.rating)}</div>
        </div>
      </div>
      <div style="color:var(--muted);font-size:13px">${r.text}</div>
    `;
    wrap.appendChild(node);
  });
}

// Chat rendering and logic
function renderChat(){
  const body = el('#chatBody');
  if(!body) return;
  body.innerHTML = '';
  state.chat.messages.forEach(m=>{
    const msg = document.createElement('div');
    msg.style.maxWidth = '80%';
    msg.style.padding = '8px 10px';
    msg.style.borderRadius = '10px';
    msg.style.fontSize = '13px';
    if(m.author === 'user'){
      msg.style.marginLeft = 'auto';
      msg.style.background = 'linear-gradient(90deg,var(--accent-1),var(--accent-2))';
      msg.style.color = '#fff';
    } else {
      msg.style.background = 'rgba(255,255,255,0.03)';
      msg.style.color = 'var(--text)';
    }
    msg.textContent = m.text;
    body.appendChild(msg);
  });
  body.scrollTop = body.scrollHeight;
}

function sendChatMessage(text){
  if(!text) return;
  const id = 'm-' + Date.now();
  state.chat.messages.push({ id, author: 'user', text });
  renderChat();
  showToast('Сообщение отправлено', 1400);

  // simulate bot reply
  setTimeout(()=>{
    const replyId = 'bot-' + Date.now();
    const replyText = generateBotReply(text);
    state.chat.messages.push({ id: replyId, author: 'bot', text: replyText });
    renderChat();
  }, 800 + Math.random()*900);
}

function generateBotReply(userText){
  const lt = userText.toLowerCase();
  if(lt.includes('оплат') || lt.includes('покуп')) return 'Оплата прошла успешно? Если нет — пришлите номер заказа, мы проверим.';
  if(lt.includes('ссылка') || lt.includes('скач')) return 'Ссылки обычно приходят на почту. Хотите повторно отправить ссылку на текущий email?';
  if(lt.includes('проблем') || lt.includes('не работает')) return 'Опишите пожалуйста проблему коротко: что именно не работает и на каком устройстве.';
  return 'Спасибо за сообщение! Мы свяжемся с вами в ближайшее время, уточните, пожалуйста, ваш email или ник.';
}

/* Cart logic */
function addToCart(id, qty=1){
  const prod = PRODUCTS.find(p=>p.id===id);
  if(!prod) return;
  state.cart[id] = state.cart[id] || { ...prod, qty: 0 };
  state.cart[id].qty += qty;
  updateCartUI();
  showToast(`Добавлено: ${prod.title}`);
}

function removeFromCart(id){
  delete state.cart[id];
  updateCartUI();
}

function changeQty(id, delta){
  if(!state.cart[id]) return;
  state.cart[id].qty += delta;
  if(state.cart[id].qty <= 0) removeFromCart(id);
  updateCartUI();
}

function clearCart(){
  state.cart = {};
  updateCartUI();
}

/* Update cart UI and modal contents */
function updateCartUI(){
  el('#cartCount').textContent = Object.values(state.cart).reduce((s,i)=>s+i.qty,0);
  const itemsWrap = el('#cartItems');
  itemsWrap.innerHTML = '';
  let total = 0;
  Object.values(state.cart).forEach(it=>{
    total += it.price * it.qty;
    const node = document.createElement('div');
    node.className = 'cart-item';
    node.innerHTML = `
      <div class="thumb"><img src="${it.thumb}" alt="${it.title}" style="width:100%;height:100%;object-fit:cover;border-radius:6px"></div>
      <div class="item-info">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <strong>${it.title}</strong>
          <span style="color:var(--muted)">${formatPrice(it.price)}</span>
        </div>
        <div class="qty">
          <button class="btn" data-act="dec" data-id="${it.id}">−</button>
          <div style="padding:6px 10px;border-radius:6px;background:rgba(255,255,255,0.02)">${it.qty}</div>
          <button class="btn" data-act="inc" data-id="${it.id}">+</button>
          <button class="btn ghost" data-act="rm" data-id="${it.id}" style="margin-left:auto">Удалить</button>
        </div>
        <div style="margin-top:8px;display:flex;gap:8px">
          <button class="btn ghost" data-act="goto" data-ref="${it.id}">Оформить товар</button>
        </div>
      </div>
    `;
    itemsWrap.appendChild(node);
  });
  el('#cartTotal').textContent = formatPrice(total);
  // persist cart to localStorage so separate pages can read it
  try { localStorage.setItem('kv_cart', JSON.stringify(state.cart)); } catch(e){}
}

/* Simple toast */
let toastTimer;
function showToast(text, ms=2200){
  const t = el('#toast');
  t.textContent = text;
  t.style.display = 'block';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>t.style.display='none', ms);
}

/* Modal helpers */
function openCart(){
  // Navigate to cart page instead of opening modal
  window.location.href = 'cart.html';
}
function closeCart(){ el('#cartModal').setAttribute('aria-hidden','true'); }

function openChat(){
  // Navigate to chat page instead of opening chat modal
  window.location.href = 'chat.html';
}
function closeChat(){ el('#chatModal').setAttribute('aria-hidden','true'); }

/* Checkout simulation */
function checkout(){
  // redirect to cart/checkout page for full checkout flow
  if(Object.keys(state.cart).length === 0){
    showToast('Корзина пуста');
    return;
  }
  window.location.href = 'cart.html#checkout';
}

/* New: finalize payment / validate and process */
function finalizePayment(){
  const name = el('#checkoutName').value.trim();
  const email = el('#checkoutEmail').value.trim();
  const method = el('#paymentMethod').value;
  const pdata = el('#paymentData').value.trim();

  if(!name || !email){
    showToast('Введите имя и email');
    return;
  }
  // simple method-specific validation (light)
  if(method !== 'cod' && pdata.length < 4){
    showToast('Введите корректные данные оплаты');
    return;
  }

  // simulate processing
  showToast('Оплата проходит... подождите', 1400);
  setTimeout(()=>{
    showToast('Заказ оплачен. Ссылки отправлены на ' + email, 2800);

    // create order record and persist to localStorage
    try{
      const cartItems = Object.values(state.cart).map(it=>({
        id: it.id,
        title: it.title,
        price: it.price,
        qty: it.qty || 1,
        thumb: it.thumb
      }));
      const orders = JSON.parse(localStorage.getItem('kv_orders')||'[]');
      const user = state.user || JSON.parse(localStorage.getItem('kv_user')||'null') || { name: name };
      const order = {
        id: 'ord-' + Date.now(),
        user: user.name || 'guest',
        name,
        email,
        method,
        items: cartItems,
        total: cartItems.reduce((s,i)=>s + (i.price||0)*(i.qty||1),0),
        created_at: new Date().toISOString()
      };
      orders.unshift(order);
      localStorage.setItem('kv_orders', JSON.stringify(orders));
    }catch(e){ console.warn('order save failed', e); }

    // clear cart, hide form, reset inputs
    clearCart();
    el('#checkoutForm').style.display = 'none';
    el('#checkoutName').value=''; el('#checkoutEmail').value=''; el('#paymentData').value='';
    closeCart();
  }, 1000 + Math.random()*900);
}

/* Auth functions */
function saveUser(){
  localStorage.setItem('kv_user', JSON.stringify(state.user));
  renderAuthArea();
}

function logout(){
  state.user = null;
  saveUser();
  showToast('Вы вышли');
}

function renderAuthArea(){
  const area = el('#authArea');
  area.innerHTML = '';
  if(state.user){
    const btn = document.createElement('button');
    btn.className = 'profile-btn';
    btn.id = 'profileBtn';
    btn.innerHTML = `<div class="profile-avatar">${(state.user.name||'U')[0].toUpperCase()}</div><div class="auth-mini">${state.user.name}</div>`;
    area.appendChild(btn);

    const menu = document.createElement('div');
    menu.style.display='none';
    menu.id='profileMenu';
    // added "Мой аккаунт" button which navigates to account page
    menu.innerHTML = `<div style="margin-top:6px;display:flex;flex-direction:column;gap:8px"><button id="myAccountBtn" class="btn">Мой аккаунт</button><button id="logoutBtn" class="btn ghost">Выйти</button></div>`;
    area.appendChild(menu);
  } else {
    area.innerHTML = `<button id="authBtn" class="btn ghost">Войти</button>`;
  }
}

function openAuth(mode='login'){
  // Navigate to dedicated auth page; mode passed via query param
  const m = encodeURIComponent(mode);
  window.location.href = `auth.html?mode=${m}`;
}

function closeAuth(){ el('#authModal').setAttribute('aria-hidden','true'); }

/* Favorites utilities */
function saveFavs(){ localStorage.setItem('kv_favs', JSON.stringify(state.favorites)); }
function toggleFavorite(prodId){
  const idx = state.favorites.indexOf(prodId);
  if(idx === -1) state.favorites.push(prodId);
  else state.favorites.splice(idx,1);
  saveFavs();
  renderProducts();
  renderFavoritesModal(); // refresh modal if open
  showToast(state.favorites.includes(prodId) ? 'Добавлено в избранное' : 'Удалено из избранного',1000);
}

function updateFavoritesHeader(){
  const elCount = el('#favCount');
  if(elCount) elCount.textContent = state.favorites.length;
}

/* Favorites modal rendering/injection */
function ensureFavoritesUI(){
  if(el('#favBtn')) {
    updateFavoritesHeader();
    return;
  }
  // floating button (kept for convenience)
  const btn = document.createElement('button');
  btn.id = 'favBtn';
  btn.className = 'btn';
  btn.style.position = 'fixed';
  btn.style.right = '18px';
  btn.style.bottom = '86px';
  btn.style.zIndex = 80;
  btn.style.borderRadius = '999px';
  btn.style.padding = '10px 12px';
  btn.textContent = 'Избранное';
  document.body.appendChild(btn);

  // modal
  const modal = document.createElement('div');
  modal.id = 'favModal';
  modal.className = 'modal';
  modal.setAttribute('aria-hidden','true');
  modal.innerHTML = `
    <div class="modal-panel" style="max-width:700px">
      <header class="modal-header">
        <h3>Избранное</h3>
        <button id="closeFav" class="btn icon">×</button>
      </header>
      <div class="modal-body" id="favBody" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px"></div>
    </div>
  `;
  document.body.appendChild(modal);

  // bindings
  btn.addEventListener('click', ()=> {
    // open favorites page instead of modal
    window.location.href = 'favorites.html';
  });
  modal.addEventListener('click', (ev)=>{ if(ev.target === modal) modal.setAttribute('aria-hidden','true'); });
  document.body.addEventListener('click', (e)=>{
    if(e.target.closest('#closeFav')) el('#favModal').setAttribute('aria-hidden','true');
  });

  updateFavoritesHeader();
}

function renderFavoritesModal(){
  const wrap = el('#favBody');
  if(!wrap) return;
  wrap.innerHTML = '';
  if(state.favorites.length === 0){
    wrap.innerHTML = '<div style="color:var(--muted);padding:12px">Нет избранных товаров</div>';
    return;
  }
  state.favorites.forEach(fid=>{
    const p = state.products.find(x=>x.id===fid) || state.marketListings.find(x=>x.id===fid) || state.accountListings.find(x=>x.id===fid);
    if(!p) return;
    const card = document.createElement('article');
    card.className = 'card';
    card.innerHTML = `
      <div class="media"><img src="${p.thumb}" alt="${p.title}" style="width:100%;height:100%;object-fit:cover"></div>
      <div>
        <h3>${p.title}</h3>
        <div class="meta"><span class="tag-pill">${p.tag||p.game||p.games||''}</span><span class="price">${formatPrice(p.price)}</span></div>
        <p style="margin:8px 0 0;color:var(--muted);font-size:13px">${p.desc||''}</p>
      </div>
      <div class="actions">
        <button class="btn primary buy" data-id="${p.id}">Купить</button>
        <button class="btn ghost remove-fav" data-id="${p.id}">Удалить</button>
      </div>
    `;
    wrap.appendChild(card);
  });
}

/* Event bindings */
function bind(){
  ensureFavoritesUI(); // inject favorites UI

  // Search input — debounced live search
  const searchInput = el('#search');
  if(searchInput){
    let searchTimer = null;
    searchInput.addEventListener('input', (ev)=>{
      clearTimeout(searchTimer);
      searchTimer = setTimeout(()=>{
        state.query = ev.target.value.trim();
        renderProducts();
      }, 220);
    });
    // support Enter to jump to results (optional)
    searchInput.addEventListener('keydown', (e)=>{
      if(e.key === 'Enter'){
        e.preventDefault();
        state.query = searchInput.value.trim();
        renderProducts();
      }
    });
  }

  // Product actions
  document.body.addEventListener('click', (e)=>{
    const buy = e.target.closest('button.buy');
    if(buy){
      addToCart(buy.dataset.id, 1);
      return;
    }
    const favBtn = e.target.closest('button.fav');
    if(favBtn){
      toggleFavorite(favBtn.dataset.id);
      updateFavoritesHeader();
      return;
    }
    const addBtn = e.target.closest('button[data-id]');
    if(addBtn && !addBtn.classList.contains('buy') && !addBtn.classList.contains('fav')){
      addToCart(addBtn.dataset.id, 1);
      return;
    }

    // Marketplace: buy listing
    const buyList = e.target.closest('button.buy-listing');
    if(buyList){
      addListingToCart(buyList.dataset.id, 1);
      return;
    }

    // Marketplace: add listing to cart (same data-id)
    const addListBtn = e.target.closest('#marketGrid .btn[data-id]');
    if(addListBtn && !addListBtn.classList.contains('buy-listing')){
      addListingToCart(addListBtn.dataset.id, 1);
      return;
    }

    const cartBtn = e.target.closest('#cartBtn');
    if(cartBtn){ openCart(); return; }

    const favHeader = e.target.closest('#favHeaderBtn');
    if(favHeader){
      // open favorites page instead of modal
      window.location.href = 'favorites.html';
      return;
    }

    const close = e.target.closest('#closeCart');
    if(close){ closeCart(); return; }

    const clearBtn = e.target.closest('#clearCart');
    if(clearBtn){ clearCart(); return; }

    const checkoutBtn = e.target.closest('#checkoutBtn');
    if(checkoutBtn){ checkout(); return; }

    const confirmPay = e.target.closest('#confirmPayment');
    if(confirmPay){ finalizePayment(); return; }

    const cancelPay = e.target.closest('#cancelCheckout');
    if(cancelPay){ el('#checkoutForm').style.display = 'none'; return; }

    // Cart item controls
    const cartControl = e.target.closest('[data-act]');
    if(cartControl){
      const act = cartControl.dataset.act;
      const id = cartControl.dataset.id;
      if(act === 'inc') changeQty(id, 1);
      if(act === 'dec') changeQty(id, -1);
      if(act === 'rm') removeFromCart(id);
      if(act === 'goto'){
        // "Оформить товар" - scroll to product card if exists
        const ref = cartControl.dataset.ref;
        // try product id as stored in cart keys; if key like 'listing-...' or 'account-...' map to underlying id
        let pid = ref;
        if(ref.startsWith('listing-')) pid = ref.replace('listing-','');
        if(ref.startsWith('account-')) pid = ref.replace('account-','');
        // try find product card by dataset.pid
        const target = document.querySelector(`[data-pid="${pid}"]`);
        if(target){
          target.scrollIntoView({behavior:'smooth',block:'center'});
          // flash highlight
          target.style.boxShadow = '0 8px 30px rgba(123,97,255,0.18)';
          setTimeout(()=> target.style.boxShadow = "", 1200);
          // close cart to let user view/complete
          closeCart();
        } else {
          showToast('Товар не найден на странице',1400);
        }
      }
    }
  });

  // Accounts marketplace form toggles and creation
  el('#openAccListForm').addEventListener('click', ()=>{
    el('#accListingForm').style.display = 'block';
    window.scrollTo({top: el('#accListingForm').offsetTop - 20, behavior:'smooth'});
  });
  el('#cancelAccListing').addEventListener('click', ()=>{
    el('#accListingForm').style.display = 'none';
  });
  el('#createAccListing').addEventListener('click', ()=>{
    const title = el('#accListTitle').value.trim();
    const price = Number(el('#accListPrice').value) || 0;
    const games = el('#accListGames').value.trim() || 'General';
    const thumb = el('#accListThumb').value.trim() || 'https://via.placeholder.com/400x200?text=Cover';
    if(!title || price <= 0){ showToast('Введите корректное название и цену'); return; }
    const id = 'acc-'+(Date.now());
    state.accountListings.unshift({ id, title, games, price, thumb, seller: 'Вы' });
    el('#accListingForm').style.display = 'none';
    el('#accListTitle').value=''; el('#accListPrice').value=''; el('#accListGames').value=''; el('#accListThumb').value='';
    renderAccountsMarketplace();
    showToast('Издание опубликовано');
  });

  // Account purchase/add to cart handlers (delegated)
  document.body.addEventListener('click', (e)=>{
    const buyAcc = e.target.closest('button.buy-acc');
    if(buyAcc){ addAccountToCart(buyAcc.dataset.id,1); return; }
    const addAcc = e.target.closest('button.add-acc');
    if(addAcc){ addAccountToCart(addAcc.dataset.id,1); return; }
  });

  // additional delegated handlers for fav modal actions and remove from fav
  document.body.addEventListener('click', (e)=>{
    const rem = e.target.closest('.remove-fav');
    if(rem){
      toggleFavorite(rem.dataset.id);
      renderFavoritesModal();
      updateFavoritesHeader();
      return;
    }
  });

  // Auth bindings
  document.body.addEventListener('click', (e)=>{
    if(e.target.closest('#authBtn')){ openAuth('login'); return; }
    if(e.target.closest('#toRegister')){ 
      const mode = el('#authTitle').textContent === 'Войти' ? 'register' : 'login';
      openAuth(mode === 'register' ? 'register' : 'login'); return;
    }
    if(e.target.closest('#submitAuth')){
      const name = el('#authName').value.trim();
      const pass = el('#authPass').value;
      if(!name || !pass){ showToast('Введите имя и пароль'); return; }
      // Simple register/login logic (no real auth) — register if not exists
      const stored = JSON.parse(localStorage.getItem('kv_users')||'{}');
      if(el('#authTitle').textContent === 'Регистрация'){
        if(stored[name]){ showToast('Пользователь уже существует'); return; }
        stored[name] = { name, pass };
        localStorage.setItem('kv_users', JSON.stringify(stored));
        state.user = { name }; saveUser();
        showToast('Регистрация успешна');
        closeAuth(); return;
      } else {
        if(stored[name] && stored[name].pass === pass){
          state.user = { name }; saveUser();
          showToast('Вход успешен');
          closeAuth(); return;
        } else { showToast('Неверные данные'); return; }
      }
    }
    if(e.target.closest('#closeAuth')){ closeAuth(); return; }
    if(e.target.closest('#profileBtn')){
      const menu = el('#profileMenu');
      if(menu) menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
      return;
    }
    if(e.target.closest('#myAccountBtn')){
      window.location.href = 'account.html';
      return;
    }
    if(e.target.closest('#logoutBtn')){ logout(); return; }
  });

  // Category toolbar (chips)
  const catToolbar = el('#categoryToolbar');
  if(catToolbar){
    catToolbar.addEventListener('click', (ev)=>{
      const btn = ev.target.closest('button.chip');
      if(!btn) return;
      const cat = btn.dataset.cat;
      state.category = cat;
      // update pressed states
      els('#categoryToolbar button.chip').forEach(b=>{ b.setAttribute('aria-pressed','false'); b.classList.remove('active-chip'); });
      btn.setAttribute('aria-pressed','true'); btn.classList.add('active-chip');
      renderProducts();
      if(state.category === 'market') setTimeout(()=> el('#marketplace').scrollIntoView({behavior:'smooth'}), 100);
    });
  }

  // Sort menu (chips)
  const sortMenu = el('#sortMenu');
  if(sortMenu){
    sortMenu.addEventListener('click', (ev)=>{
      const btn = ev.target.closest('button.chip');
      if(!btn) return;
      const s = btn.dataset.sort;
      state.sort = s;
      els('#sortMenu button.chip').forEach(b=>{ b.setAttribute('aria-pressed','false'); b.classList.remove('active-chip'); });
      btn.setAttribute('aria-pressed','true'); btn.classList.add('active-chip');
      renderProducts();
    });
  }

  // Marketplace form toggles and creation
  el('#openListForm').addEventListener('click', ()=>{
    el('#listingForm').style.display = 'block';
    window.scrollTo({top: el('#listingForm').offsetTop - 20, behavior:'smooth'});
  });
  el('#cancelListing').addEventListener('click', ()=>{
    el('#listingForm').style.display = 'none';
  });
  el('#createListing').addEventListener('click', ()=>{
    const title = el('#listTitle').value.trim();
    const price = Number(el('#listPrice').value) || 0;
    const game = el('#listGame').value.trim() || 'Unknown';
    const thumb = el('#listThumb').value.trim() || 'https://via.placeholder.com/400x200?text=Cover';
    if(!title || price <= 0){ showToast('Введите корректное название и цену'); return; }
    const id = 'lst-'+(Date.now());
    state.marketListings.unshift({ id, title, game, price, thumb, seller: 'Вы' });
    el('#listingForm').style.display = 'none';
    el('#listTitle').value = ''; el('#listPrice').value=''; el('#listGame').value=''; el('#listThumb').value='';
    renderMarketplace();
    showToast('Книга опубликована');
  });

  // Accounts / author listing creation (repurposed)
  // Accounts marketplace form toggles and creation
  el('#openAccListForm').addEventListener('click', ()=>{
    el('#accListingForm').style.display = 'block';
    window.scrollTo({top: el('#accListingForm').offsetTop - 20, behavior:'smooth'});
  });
  el('#cancelAccListing').addEventListener('click', ()=>{
    el('#accListingForm').style.display = 'none';
  });
  el('#createAccListing').addEventListener('click', ()=>{
    const title = el('#accListTitle').value.trim();
    const price = Number(el('#accListPrice').value) || 0;
    const games = el('#accListGames').value.trim() || 'General';
    const thumb = el('#accListThumb').value.trim() || 'https://via.placeholder.com/400x200?text=Cover';
    if(!title || price <= 0){ showToast('Введите корректное название и цену'); return; }
    const id = 'acc-'+(Date.now());
    state.accountListings.unshift({ id, title, games, price, thumb, seller: 'Вы' });
    el('#accListingForm').style.display = 'none';
    el('#accListTitle').value=''; el('#accListPrice').value=''; el('#accListGames').value=''; el('#accListThumb').value='';
    renderAccountsMarketplace();
    showToast('Издание опубликовано');
  });

  // Close modal on background click
  el('#cartModal').addEventListener('click', (ev)=>{
    if(ev.target === el('#cartModal')) closeCart();
  });

  // Close auth modal on background click
  el('#authModal').addEventListener('click', (ev)=>{
    if(ev.target === el('#authModal')) closeAuth();
  });

  // keyboard: Esc closes modal
  document.addEventListener('keydown', (ev)=>{
    if(ev.key === 'Escape') {
      if(el('#cartModal').getAttribute('aria-hidden') !== 'false') closeCart();
      if(el('#authModal').getAttribute('aria-hidden') !== 'false') closeAuth();
    }
  });

  // Chat bindings
  el('#chatBtn').addEventListener('click', ()=> openChat());
  el('#closeChat').addEventListener('click', ()=> closeChat());
  el('#sendChat').addEventListener('click', ()=>{
    const txt = el('#chatInput').value.trim();
    if(!txt) return;
    el('#chatInput').value = '';
    sendChatMessage(txt);
  });
  el('#chatInput').addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      const txt = el('#chatInput').value.trim();
      if(!txt) return;
      el('#chatInput').value = '';
      sendChatMessage(txt);
    }
  });

  // Close chat modal on background click
  el('#chatModal').addEventListener('click', (ev)=>{
    if(ev.target === el('#chatModal')) closeChat();
  });
}

/* Init */
function init(){
  renderProducts();
  renderMarketplace();
  renderAccountsMarketplace();
  renderReviews();
  renderAuthArea();
  bind();

  // friendly hint
  showToast('Добро пожаловать в KeyVault', 1800);
  ensureFavoritesUI(); // ensure favorites UI present on load
  updateFavoritesHeader();
}

init();