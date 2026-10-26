# ТЗ — AutoParts Intelligence (lead brief)

См. также **`docs/PRODUCT_TZ_V2.md`**.

## Цель
Полноценный **сервис поиска запчастей** для рынков **UA · MD · RO**.

## Рынки (только эти)
| Страна | Источники |
|--------|-----------|
| UA | `olx_ua`, `prom_ua`, `flagma_ua` |
| MD | `nine99_md`, `prom_md` |
| RO | `olx_ro` |

PL/BG/PT/Bazar и прочее — **вне продукта** (см. `docs/ACCESS_PATHS.md`).

## Продуктовые требования
1. **Vehicle Search** — главный экран.
2. Запрос из Make/Model/Generation/Year/Part/OEM.
3. Параллельный live-поиск (GraphQL / JSON-LD), без CAPTCHA-bypass.
4. Карточка: фото, title, цена, источник, страна, View.
5. **Свежесть:** не показывать объявления старше **30 дней**, если дата известна.
6. Сортировка: cheaper first; без цены — в конец.
7. Честные бейджи: title-heuristic ≠ VERIFIED_EXACT.

## Критерий готовности
- UI = рабочий поиск, рынки только UA/MD/RO
- Live search возвращает свежие офферы
- Задеплоено на Vercel
