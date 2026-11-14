document.documentElement.classList.add('js');

const arabic = window.WOW_AR_TRANSLATIONS || {};
let currentLanguage = 'en';
const localizedText = [];
const textWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
while (textWalker.nextNode()) {
  const node = textWalker.currentNode;
  const english = node.nodeValue.trim();
  const translation = node.parentElement?.dataset.ar || arabic[english];
  if (english && translation) localizedText.push({ node, original: node.nodeValue, english, translation });
}
const localizedLabels = [...document.querySelectorAll('[aria-label]')]
  .filter(el => !el.classList.contains('menu-toggle') && !el.classList.contains('language-switch'))
  .map(el => ({ el, original: el.getAttribute('aria-label') }));
const localizedImages = [...document.querySelectorAll('img[data-alt-ar]')]
  .map(el => ({ el, english: el.alt, arabic: el.dataset.altAr }));
const labelTranslations = {
  'WowTech Solution, back to top': 'WowTech Solution، العودة للأعلى',
  'WowTech Solution, back to home': 'WowTech Solution، العودة للرئيسية',
  'Chat with WowTech Solution on WhatsApp': 'تواصل مع WowTech Solution عبر واتساب',
  'WowTech Solution on Instagram': 'حساب WowTech Solution على إنستغرام',
  'Main navigation': 'التنقل الرئيسي',
  'Mobile navigation': 'التنقل على الهاتف',
  'Footer navigation': 'التنقل أسفل الصفحة',
  'Connected technology systems visualization': 'تصوّر للأنظمة التقنية المترابطة',
};
const englishTitle = document.title;
const description = document.querySelector('meta[name="description"]');
const ogTitle = document.querySelector('meta[property="og:title"]');
const ogDescription = document.querySelector('meta[property="og:description"]');
const englishDescription = description?.content;
const englishOgDescription = ogDescription?.content;
const whatsappLinks = [...document.querySelectorAll('a[href^="https://wa.me/"]')]
  .map(el => ({ el, original: el.href }));
const languageButtons = [...document.querySelectorAll('[data-language]')];

function menuLabel(open = false) {
  if (currentLanguage === 'ar') return open ? 'إغلاق القائمة' : 'فتح القائمة';
  return open ? 'Close menu' : 'Open menu';
}

function setLanguage(language) {
  currentLanguage = language === 'ar' ? 'ar' : 'en';
  const isArabic = currentLanguage === 'ar';
  document.documentElement.lang = currentLanguage;
  document.documentElement.dir = isArabic ? 'rtl' : 'ltr';
  localizedText.forEach(({ node, original, english, translation }) => {
    node.nodeValue = isArabic ? original.replace(english, translation) : original;
  });
  localizedLabels.forEach(({ el, original }) => {
    el.setAttribute('aria-label', isArabic ? (labelTranslations[original] || original) : original);
  });
  localizedImages.forEach(({ el, english, arabic }) => { el.alt = isArabic ? arabic : english; });
  document.title = isArabic ? (document.documentElement.dataset.titleAr || englishTitle) : englishTitle;
  if (description) description.content = isArabic
    ? (description.dataset.arContent || englishDescription)
    : englishDescription;
  if (ogTitle) ogTitle.content = document.title;
  if (ogDescription) ogDescription.content = isArabic
    ? (ogDescription.dataset.arContent || englishOgDescription)
    : englishOgDescription;
  const arabicMessage = 'مرحباً WowTech Solution، أود الحصول على استشارة مجانية حول احتياجات شركتي التقنية.';
  whatsappLinks.forEach(({ el, original }) => {
    el.href = isArabic ? `https://wa.me/971521961007?text=${encodeURIComponent(arabicMessage)}` : original;
  });
  languageButtons.forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.language === currentLanguage));
  });
  const menu = document.querySelector('.menu-toggle');
  if (menu) menu.setAttribute('aria-label', menuLabel(menu.getAttribute('aria-expanded') === 'true'));
  try { localStorage.setItem('wow-language', currentLanguage); } catch { /* Storage may be unavailable. */ }
}

languageButtons.forEach(button => button.addEventListener('click', () => setLanguage(button.dataset.language)));
let savedLanguage;
try { savedLanguage = localStorage.getItem('wow-language'); } catch { /* Storage may be unavailable. */ }
setLanguage(savedLanguage || (navigator.language?.toLowerCase().startsWith('ar') ? 'ar' : 'en'));

const menuButton = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('#mobile-nav');
if (menuButton && mobileNav) {
  const closeMenu = () => {
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', menuLabel());
    mobileNav.hidden = true;
  };
  menuButton.addEventListener('click', () => {
    const opening = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(opening));
    menuButton.setAttribute('aria-label', menuLabel(opening));
    mobileNav.hidden = !opening;
  });
  mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeMenu();
  });
  matchMedia('(min-width: 801px)').addEventListener('change', event => {
    if (event.matches) closeMenu();
  });
}

const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const revealed = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !reducedMotion.matches) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .08, rootMargin: '0px 0px 70px 0px' });
  revealed.forEach(el => observer.observe(el));
} else {
  revealed.forEach(el => el.classList.add('is-visible'));
}

const hero = document.querySelector('.hero-shell');
const scene = document.querySelector('.scene-depth');
if (hero && scene && !reducedMotion.matches) {
  hero.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch') return;
    const rect = hero.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - .5;
    const y = (event.clientY - rect.top) / rect.height - .5;
    scene.style.setProperty('--rx', `${-y * 10 + 2}deg`);
    scene.style.setProperty('--ry', `${x * 14 - 8}deg`);
  }, { passive: true });
  hero.addEventListener('pointerleave', () => {
    scene.style.setProperty('--rx', '2deg');
    scene.style.setProperty('--ry', '-8deg');
  });
}

const canvas = document.querySelector('#network-canvas');
if (canvas?.getContext) {
  const context = canvas.getContext('2d');
  let width = 0, height = 0, frame = 0, animation;
  let visible = true;
  const cols = 12, rows = 7;
  function resize() {
    const bounds = canvas.getBoundingClientRect();
    width = bounds.width;
    height = bounds.height;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    draw();
  }
  function point(c, r, tick) {
    return {
      x: width * (.13 + c * .087) + Math.sin(tick * .00035 + r * .8 + c * .37) * 7,
      y: height * (.08 + r * .14) + Math.cos(tick * .00042 + c * .47 + r * .3) * 7
    };
  }
  function draw(tick = 0) {
    if (!width || !height) return;
    context.clearRect(0, 0, width, height);
    const nodes = Array.from({ length: rows }, (_, r) =>
      Array.from({ length: cols }, (_, c) => point(c, r, tick)));
    context.lineWidth = 1;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const origin = nodes[r][c];
        [[r, c + 1], [r + 1, c], [r + 1, c + (r % 2 ? 1 : -1)]].forEach(([nr, nc]) => {
          if (!nodes[nr]?.[nc]) return;
          const next = nodes[nr][nc];
          context.strokeStyle = c < 4 ? 'rgba(168,240,195,.055)' : 'rgba(167,243,197,.11)';
          context.beginPath();context.moveTo(origin.x, origin.y);context.lineTo(next.x, next.y);context.stroke();
        });
        if (c > 4 && (c * 7 + r * 11) % 5 === 0) {
          context.fillStyle = 'rgba(182,251,204,.3)';
          context.beginPath();context.arc(origin.x, origin.y, 1.5, 0, Math.PI * 2);context.fill();
        }
      }
    }
    for (let i = 0; i < 9; i++) {
      const r = (i * 3) % (rows - 1), c = 4 + (i * 5) % (cols - 5);
      const start = nodes[r][c], end = nodes[r][c + 1];
      const t = (tick * .00016 + i * .227) % 1;
      const x = start.x + (end.x - start.x) * t, y = start.y + (end.y - start.y) * t;
      const glow = context.createRadialGradient(x, y, 0, x, y, 10);
      glow.addColorStop(0, 'rgba(186,255,209,.7)');
      glow.addColorStop(1, 'rgba(186,255,209,0)');
      context.fillStyle = glow;context.beginPath();context.arc(x, y, 10, 0, Math.PI * 2);context.fill();
      context.fillStyle = '#c6ffdb';context.beginPath();context.arc(x, y, 1.5, 0, Math.PI * 2);context.fill();
    }
  }
  function animate(tick) {
    if (!visible || document.hidden || reducedMotion.matches) return;
    if (++frame % 2 === 0) draw(tick);
    animation = requestAnimationFrame(animate);
  }
  new ResizeObserver(resize).observe(canvas);
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (visible && !reducedMotion.matches) {
      cancelAnimationFrame(animation);
      animation = requestAnimationFrame(animate);
    } else cancelAnimationFrame(animation);
  }).observe(canvas);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && visible && !reducedMotion.matches) animation = requestAnimationFrame(animate);
  });
  reducedMotion.addEventListener('change', () => {
    cancelAnimationFrame(animation);
    draw();
    if (!reducedMotion.matches && visible) animation = requestAnimationFrame(animate);
  });
}
