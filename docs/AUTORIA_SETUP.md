# AUTO.RIA — отложено (не в MVP)

Коннектор есть в коде (`autoparts_core/connectors/autoria.py`), но **по умолчанию выключен**.

Причины отсева:
- нужен бесплатный ключ с регистрации;
- лимит ~30 запросов/час;
- API про авто/доноров, не про каталог запчастей.

Если всё же нужно:

```bash
ENABLE_AUTORIA=true
AUTORIA_API_KEY=...
```

Ключ: https://developers.ria.com → Мій профіль.  
ToS: ссылка на https://auto.ria.com.
