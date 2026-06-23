# Monad Engine — local web app

موتور خودتفسیر قرآن: نقشه‌ی شبکه + پنل شاهد. اولین ماژولِ یک سکوی توسعه‌پذیر.

## اجرا

```bash
python3 build/build_evidence_index.py      # یک‌بار: ساخت ایندکس شاهد + گراف
python3 -m app.server.main                 # سرور: http://localhost:8000
```

تست‌ها: `python3 -m pytest tests/ -v`
وارسیِ بازتولیدپذیری ساخت: `python3 build/validate_evidence_index.py`

## افزودن یک ماژول جدید (قرارداد دو-فایلی)

1. **بک‌اند:** `app/server/modules/<name>.py` بساز که `spec()` را با شکلِ
   `{"id","title","icon","routes":[(method, regex, handler)]}` برمی‌گرداند؛ سپس آن را در
   `app/server/modules/__init__.py` به `MODULE_REGISTRY` بیفزای. هندلر امضای
   `handler(match_groupdict) -> (status, payload)` دارد و فقط از `services/*` داده می‌گیرد.
2. **فرانت:** `app/web/src/modules/<name>/index.js` بساز که
   `{id,title,icon,mount(container, api)}` صادر می‌کند؛ آن را در `app/web/src/shell/layout.js`
   `register(...)` کن. پوسته خودکار در نوار کناری نشانش می‌دهد.

هسته (سرور، روتر، پوسته، سرویس‌ها) دست‌نخورده می‌ماند. `tests/test_extensibility.py`
این قرارداد را تضمین می‌کند.

## اصل صداقت

هیچ ترجمه/تفسیر/معنای بیرونی نمایش داده نمی‌شود — تنها متنِ آیات، ریشه‌های مشترک، و
وزنِ رابطه. آیاتِ بی‌شاهد صریحاً «امتناع» علامت می‌خورند.
