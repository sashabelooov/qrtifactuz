(function () {
  const LANGS = ['en', 'ru', 'uz'];

  const T = {
    ru: {
      // Buttons
      'Save': 'Сохранить',
      'Save and continue editing': 'Сохранить и продолжить',
      'Save and add another': 'Сохранить и добавить ещё',
      'Cancel': 'Отмена',
      'Delete': 'Удалить',
      'Export': 'Экспорт',
      'Search': 'Поиск',
      'Reset': 'Сбросить',
      'Submit': 'Отправить',
      'Logout': 'Выйти',
      'Select': 'Выбрать',
      // Page titles / actions
      'List': 'Список',
      'Create': 'Создать',
      'Edit': 'Редактировать',
      'Detail': 'Детали',
      'View': 'Просмотр',
      'Add': 'Добавить',
      'New': 'Новый',
      // Confirmation
      'Are you sure you want to delete this record?': 'Вы уверены, что хотите удалить эту запись?',
      'Yes, delete!': 'Да, удалить!',
      // Pagination
      'of': 'из',
      'items': 'записей',
      'Page': 'Страница',
      // Column labels
      'Active': 'Активен',
      'Admin': 'Администратор',
      'Created': 'Создан',
      'Updated': 'Обновлён',
      'Country': 'Страна',
      'City': 'Город',
      'Museum': 'Музей',
      'Hall': 'Зал',
      'Exhibit': 'Экспонат',
      'Language': 'Язык',
      'Title': 'Заголовок',
      'Description': 'Описание',
      'Type': 'Тип',
      'Cover': 'Обложка',
      'Order': 'Порядок',
      'File': 'Файл',
      'Public URL': 'Публичный URL',
      'Duration (sec)': 'Длительность (сек)',
      'Views': 'Просмотры',
      'Listens': 'Прослушивания',
      'Code': 'Код',
      'Name': 'Название',
      'Slug': 'Слаг',
      'Status': 'Статус',
      'Floor': 'Этаж',
      'Address': 'Адрес',
      'Logo URL': 'URL логотипа',
      'Email': 'Эл. почта',
      // Sidebar model names
      'Users': 'Пользователи',
      'Countries': 'Страны',
      'Cities': 'Города',
      'Museums': 'Музеи',
      'Halls': 'Залы',
      'Exhibits': 'Экспонаты',
      'Translations': 'Переводы',
      'Audio Tracks': 'Аудиодорожки',
      'Exhibit Media': 'Медиа экспонатов',
      // Status values
      'draft': 'черновик',
      'published': 'опубликован',
      'archived': 'в архиве',
    },
    uz: {
      // Buttons
      'Save': 'Saqlash',
      'Save and continue editing': 'Saqlash va tahrirlashni davom ettirish',
      'Save and add another': 'Saqlash va yangi qo\'shish',
      'Cancel': 'Bekor qilish',
      'Delete': 'O\'chirish',
      'Export': 'Eksport',
      'Search': 'Qidirish',
      'Reset': 'Qayta o\'rnatish',
      'Submit': 'Yuborish',
      'Logout': 'Chiqish',
      'Select': 'Tanlash',
      // Page titles / actions
      'List': 'Ro\'yxat',
      'Create': 'Yaratish',
      'Edit': 'Tahrirlash',
      'Detail': 'Tafsilot',
      'View': 'Ko\'rish',
      'Add': 'Qo\'shish',
      'New': 'Yangi',
      // Confirmation
      'Are you sure you want to delete this record?': 'Ushbu yozuvni o\'chirishni xohlaysizmi?',
      'Yes, delete!': 'Ha, o\'chirish!',
      // Pagination
      'of': 'dan',
      'items': 'ta yozuv',
      'Page': 'Sahifa',
      // Column labels
      'Active': 'Faol',
      'Admin': 'Administrator',
      'Created': 'Yaratilgan',
      'Updated': 'Yangilangan',
      'Country': 'Mamlakat',
      'City': 'Shahar',
      'Museum': 'Muzey',
      'Hall': 'Zal',
      'Exhibit': 'Eksponat',
      'Language': 'Til',
      'Title': 'Sarlavha',
      'Description': 'Tavsif',
      'Type': 'Tur',
      'Cover': 'Muqova',
      'Order': 'Tartib',
      'File': 'Fayl',
      'Public URL': 'Ochiq URL',
      'Duration (sec)': 'Davomiylik (sek)',
      'Views': 'Ko\'rishlar',
      'Listens': 'Tinglanishlar',
      'Code': 'Kod',
      'Name': 'Nomi',
      'Slug': 'Slug',
      'Status': 'Holat',
      'Floor': 'Qavat',
      'Address': 'Manzil',
      'Logo URL': 'Logo URL',
      'Email': 'Elektron pochta',
      // Sidebar model names
      'Users': 'Foydalanuvchilar',
      'Countries': 'Mamlakatlar',
      'Cities': 'Shaharlar',
      'Museums': 'Muzeylar',
      'Halls': 'Zallar',
      'Exhibits': 'Eksponatlar',
      'Translations': 'Tarjimalar',
      'Audio Tracks': 'Audio treklar',
      'Exhibit Media': 'Eksponat media',
      // Status values
      'draft': 'qoralama',
      'published': 'nashr etilgan',
      'archived': 'arxivlangan',
    },
  };

  // ── Language state ────────────────────────────────────────────────
  let currentLang = localStorage.getItem('adminLang') || 'en';

  // ── Translate all matching text nodes ────────────────────────────
  function translateNode(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const raw = node.textContent;
      const trimmed = raw.trim();
      if (!trimmed) return;
      const dict = T[currentLang];
      if (dict && dict[trimmed] !== undefined) {
        node.textContent = raw.replace(trimmed, dict[trimmed]);
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      // Skip script/style nodes
      if (['SCRIPT', 'STYLE', 'INPUT', 'TEXTAREA'].includes(node.tagName)) return;
      node.childNodes.forEach(translateNode);
    }
  }

  function translatePage() {
    if (currentLang === 'en') return;
    document.body.childNodes.forEach(translateNode);
  }

  // ── Inject language dropdown fixed at top-right ──────────────────
  function injectDropdown() {
    const flags = { en: '🇬🇧 EN', ru: '🇷🇺 RU', uz: '🇺🇿 UZ' };

    const wrapper = document.createElement('div');
    wrapper.id = 'adminLangSwitcher';
    wrapper.style.cssText = `
      position: fixed;
      top: 14px;
      right: 20px;
      z-index: 99999;
    `;

    const btn = document.createElement('button');
    btn.textContent = flags[currentLang];
    btn.style.cssText = `
      background: #1e293b;
      color: #fff;
      border: 1px solid rgba(255,255,255,0.25);
      border-radius: 8px;
      padding: 6px 14px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 2px 8px rgba(0,0,0,0.25);
      letter-spacing: 0.5px;
    `;

    const menu = document.createElement('div');
    menu.style.cssText = `
      display: none;
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
      overflow: hidden;
      min-width: 120px;
    `;

    LANGS.forEach(lang => {
      const item = document.createElement('button');
      item.textContent = flags[lang];
      item.style.cssText = `
        display: block;
        width: 100%;
        padding: 10px 18px;
        background: ${lang === currentLang ? '#f0f4ff' : 'white'};
        color: #1e293b;
        border: none;
        text-align: left;
        cursor: pointer;
        font-size: 13px;
        font-weight: ${lang === currentLang ? '700' : '400'};
        transition: background 0.15s;
      `;
      item.addEventListener('mouseenter', () => { if (lang !== currentLang) item.style.background = '#f8fafc'; });
      item.addEventListener('mouseleave', () => { if (lang !== currentLang) item.style.background = 'white'; });
      item.addEventListener('click', () => {
        currentLang = lang;
        localStorage.setItem('adminLang', lang);
        window.location.reload();
      });
      menu.appendChild(item);
    });

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    });

    document.addEventListener('click', () => { menu.style.display = 'none'; });

    wrapper.appendChild(btn);
    wrapper.appendChild(menu);
    document.body.appendChild(wrapper);
  }

  // ── Slug auto-fill ────────────────────────────────────────────────
  function toSlug(text) {
    return text.toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9-]/g, '')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  function initSlugAutofill() {
    const nameInput = document.querySelector('input[name="name"]');
    const slugInput = document.querySelector('input[name="slug"]');
    if (!nameInput || !slugInput) return;
    let userEditedSlug = slugInput.value.length > 0;
    slugInput.addEventListener('input', () => { userEditedSlug = true; });
    nameInput.addEventListener('input', () => {
      if (!userEditedSlug) slugInput.value = toSlug(nameInput.value);
    });
  }

  // ── Mobile CSS fixes ─────────────────────────────────────────────
  function injectMobileStyles() {
    const style = document.createElement('style');
    style.textContent = `
      @media (max-width: 768px) {
        /* Scrollable tables */
        .table-responsive, .card-table { overflow-x: auto; -webkit-overflow-scrolling: touch; }
        table { min-width: 500px; }

        /* Full-width form fields */
        .form-control, .form-select, .tom-select { font-size: 16px !important; }
        .col-md-6, .col-md-4, .col-md-8 { width: 100% !important; max-width: 100% !important; }

        /* Bigger tap targets for buttons */
        .btn { min-height: 40px; padding: 8px 16px; }

        /* Fix lang switcher position on mobile */
        #adminLangSwitcher { top: 10px; right: 10px; }

        /* Page header stacking */
        .page-header { flex-direction: column; gap: 8px; }
        .page-header .ms-auto { margin-left: 0 !important; }

        /* Card padding */
        .card-body { padding: 12px; }

        /* Pagination on mobile */
        .pagination { flex-wrap: wrap; gap: 4px; }

        /* Left drawer sidebar */
        .navbar-collapse {
          position: fixed !important;
          top: 0 !important;
          left: -280px !important;
          width: 280px !important;
          height: 100vh !important;
          background: #1e293b !important;
          z-index: 99990 !important;
          overflow-y: auto !important;
          transition: left 0.3s ease !important;
          padding: 20px 0 !important;
          flex-direction: column !important;
          align-items: flex-start !important;
        }
        .navbar-collapse.show {
          left: 0 !important;
        }
        .navbar-collapse .navbar-nav {
          width: 100% !important;
          flex-direction: column !important;
          padding: 0 12px !important;
        }
        .navbar-collapse .nav-link {
          color: #cbd5e1 !important;
          padding: 12px 16px !important;
          border-radius: 8px !important;
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          font-size: 15px !important;
        }
        .navbar-collapse .nav-link:hover {
          background: rgba(255,255,255,0.1) !important;
          color: #fff !important;
        }

        /* Backdrop */
        #mobileBackdrop {
          display: none;
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.5);
          z-index: 99980;
        }
        #mobileBackdrop.show { display: block; }
      }
    `;
    document.head.appendChild(style);
  }

  // ── Mobile left drawer ────────────────────────────────────────────
  function initMobileDrawer() {
    if (window.innerWidth > 768) return;

    const style = document.createElement('style');
    style.textContent = `
      @media (max-width: 768px) {
        /* Hide entire original navbar */
        .navbar { display: none !important; }

        /* Hamburger button fixed top-left */
        #mobileMenuBtn {
          position: fixed;
          top: 12px;
          left: 12px;
          z-index: 99999;
          background: #1e293b;
          border: none;
          border-radius: 8px;
          width: 42px;
          height: 42px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          gap: 5px;
          cursor: pointer;
          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        #mobileMenuBtn span {
          display: block;
          width: 22px;
          height: 2px;
          background: #fff;
          border-radius: 2px;
        }

        /* Drawer */
        #mobileDrawer {
          position: fixed;
          top: 0;
          left: -290px;
          width: 270px;
          height: 100vh;
          background: #1e293b;
          z-index: 99990;
          overflow-y: auto;
          transition: left 0.3s ease;
          padding: 20px 12px;
          display: flex;
          flex-direction: column;
        }
        #mobileDrawer.open { left: 0; }
        #mobileDrawer .drawer-title {
          color: #fff;
          font-size: 18px;
          font-weight: 700;
          padding: 10px 16px 20px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
          margin-bottom: 10px;
        }
        #mobileDrawer a {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          color: #cbd5e1;
          text-decoration: none;
          border-radius: 8px;
          font-size: 15px;
          margin-bottom: 2px;
        }
        #mobileDrawer a:hover, #mobileDrawer a.active {
          background: rgba(255,255,255,0.1);
          color: #fff;
        }
        #mobileDrawer a svg, #mobileDrawer a i { width: 20px; flex-shrink: 0; }
        #mobileDrawer .drawer-logout {
          margin-top: auto;
          border-top: 1px solid rgba(255,255,255,0.1);
          padding-top: 10px;
        }
        #mobileDrawer .drawer-logout a { color: #f87171; }
        #mobileDrawer .drawer-logout a:hover { background: rgba(248,113,113,0.15); }

        /* Backdrop */
        #mobileBackdrop {
          display: none;
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.5);
          z-index: 99980;
        }
        #mobileBackdrop.show { display: block; }

        /* Push page content down so it's not under the hamburger */
        .page-wrapper { padding-top: 60px !important; }
      }
    `;
    document.head.appendChild(style);

    // Build drawer
    const drawer = document.createElement('div');
    drawer.id = 'mobileDrawer';

    const title = document.createElement('div');
    title.className = 'drawer-title';
    title.textContent = 'Admin';
    drawer.appendChild(title);

    // Nav links
    const navLinks = document.querySelectorAll('.navbar-collapse .nav-link, .navbar-collapse a');
    const seen = new Set();
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      const text = link.textContent.trim();
      if (!text || seen.has(href) || href === '/admin/logout') return;
      seen.add(href);
      const a = document.createElement('a');
      a.href = href || '#';
      a.innerHTML = link.innerHTML;
      if (window.location.pathname.startsWith(href)) a.classList.add('active');
      drawer.appendChild(a);
    });

    // Logout at bottom
    const logoutSection = document.createElement('div');
    logoutSection.className = 'drawer-logout';
    const logoutLink = document.createElement('a');
    logoutLink.href = '/admin/logout';
    logoutLink.innerHTML = '<i class="fa-solid fa-right-from-bracket"></i> Logout';
    logoutSection.appendChild(logoutLink);
    drawer.appendChild(logoutSection);

    // Backdrop & button
    const backdrop = document.createElement('div');
    backdrop.id = 'mobileBackdrop';

    const btn = document.createElement('button');
    btn.id = 'mobileMenuBtn';
    btn.setAttribute('aria-label', 'Menu');
    btn.innerHTML = '<span></span><span></span><span></span>';

    function openDrawer() { drawer.classList.add('open'); backdrop.classList.add('show'); }
    function closeDrawer() { drawer.classList.remove('open'); backdrop.classList.remove('show'); }

    btn.addEventListener('click', () => drawer.classList.contains('open') ? closeDrawer() : openDrawer());
    backdrop.addEventListener('click', closeDrawer);

    document.body.appendChild(drawer);
    document.body.appendChild(backdrop);
    document.body.appendChild(btn);
  }

  // ── Boot ──────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    const isLoginPage = window.location.pathname.includes('/login');
    injectMobileStyles();
    if (!isLoginPage) {
      injectDropdown();
      initMobileDrawer();
    }
    translatePage();
    initSlugAutofill();
  });
})();
