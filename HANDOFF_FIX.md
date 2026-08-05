# HANDOFF — auris-dental-studio (fix продуктивності/надійності)

> Вхід у новий чат: прочитати цей файл + `index.html`. Все під рукою, можна робити одразу.

## Статус
- Сайт задеплоєно й живий: **https://auris-dental-studio.vercel.app**
- GitHub: https://github.com/itprofi78/auris-dental-studio (гілка `main`, авто-деплой Vercel Hobby, team `3d`)
- Локальна папка: `C:\AI-projects\my-business-ai\auris-dental-studio\` (git init, remote origin налаштовано)
- Vercel preset: Other (статичний, один `index.html`), Root `./`

## PageSpeed (5 серп. 2026)
- Десктоп: Performance **99** — не чіпати.
- Мобілка: Performance **69**, LCP **19,2 сек** (червоний), FCP 3,0 с. Решта (TBT 0, CLS 0, SI 3,1) — ок.

## Діагноз
LCP-елемент = hero `<video id="bg-video">` (index.html:729-731). Причини:
1. **Немає `poster`** → браузер чекає завантаження відео, щоб намалювати перший кадр.
2. **Медіа на тимчасових чужих лінках** `labs.google/fx/api/...` (share-ендпоінт Google Flow, НЕ хостинг): hero-відео (1,36 МБ) + 8 фото «до/після» (index.html:811-880). Повільно під throttling + ризик відвалу будь-коли.
3. Фото Unsplash (`images.unsplash.com`) — лишаємо, вони на надійному CDN.

## РІШЕННЯ ВЛАСНИКА (5 серп.): обрано «ПОВНИЙ обсяг», але відкладено ~1,5 год через ліміти.
Повний = poster + перенос УСЬОГО labs.google-медіа (відео + 8 фото «до/після») на Cloudinary. Unsplash не чіпати.

## План fix (робити самому, ~15-20 хв)
1. Скачати hero-відео локально:
   `curl -sL "https://labs.google/fx/api/og-video/shared/9761d795-4f79-4522-930a-9fe7399e469a" -o hero.mp4`
2. ffmpeg (є, v8.1.1) → перший кадр у WebP poster: `ffmpeg -i hero.mp4 -vframes 1 -q:v 80 hero_poster.webp` (цільова вага ~60 КБ).
3. Скачати 8 фото «до/після» з labs.google (URL в index.html:811,814,833,836,855,858,877,880).
4. Залити відео + poster + 8 фото на Cloudinary. Креди: `C:\AI-projects\my-business-ai\ai-prodavec\.env` (той самий акаунт, що forma-3d). Скрипт-зразок: `C:\AI-projects\my-business-ai\3D_сайти\демо_диван\upload_cloudinary.py` (папка на кшталт `3d-saity/auris`).
5. Правки `index.html`:
   - line 729: `<video id="bg-video" ... poster="[cloudinary poster url]" preload="metadata">`
   - line 730: `src` відео → Cloudinary URL
   - lines 811-880: 8 `case-img` src → Cloudinary URLs
6. commit + **push у main (ПРОД — спитати дозвіл перед push)** → авто-редеплой Vercel.
7. Перевірка: перепрогнати PageSpeed мобілка, ціль LCP < 4 c / Performance 85+.

## Інструменти (перевірено, все є)
- ffmpeg 8.1.1 ✓
- Cloudinary креди в ai-prodavec/.env ✓
- gh CLI авторизовано (itprofi78) ✓
