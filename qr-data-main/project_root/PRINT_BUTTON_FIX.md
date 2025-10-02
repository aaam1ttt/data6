# Исправление кнопки печати в формах

## Проблема
При нажатии на кнопку "Печать" в формах (ТОРГ-12, Сообщение, Эксплуатация, Транспорт, Произвольная, ENV) не открывалось выпадающее меню с опциями печати (Печать, Печать несколько одинаковых, Добавить в очередь и т.д.).

## Причина
В файле `_print_size_controls.html` была синтаксическая ошибка в массиве `GOST_PRESETS`:
```javascript
AZTEC: [
  ...
]
]  // <-- Лишняя закрывающая скобка
```

Это приводило к ошибке JavaScript, из-за которой функция `initPrintSizeControls` не инициализировалась корректно, и событие `click` на кнопке "Печать" не обрабатывалось.

## Решение

### 1. Исправлена структура GOST_PRESETS
Удалена лишняя закрывающая скобка массива в `_print_size_controls.html`:
```javascript
AZTEC: [
  {gost: 'AZ-S1', px: 177, label: 'AZ-S1: Малый (15×15 мм)', mm: 15, layout: '9×12 на А4'},
  {gost: 'AZ-S2', px: 236, label: 'AZ-S2: Средний (20×20 мм)', mm: 20, layout: '7×9 на А4'},
  {gost: 'AZ-S3', px: 295, label: 'AZ-S3: Большой (25×25 мм)', mm: 25, layout: '6×7 на А4'},
  {gost: 'AZ-S4', px: 354, label: 'AZ-S4: Печатный (30×30 мм)', mm: 30, layout: '5×6 на А4'}
]  // <-- Теперь правильно
};
```

### 2. Улучшена обработка события клика
Добавлен `stopPropagation` для предотвращения конфликтов с другими обработчиками:
```javascript
printBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  togglePrintDropdown();
});
```

### 3. Улучшен внешний вид выпадающего меню
Увеличены размеры и улучшена читаемость:
```html
<div id="printDropdown" class="dropdown-content" style="min-width:260px; ...">
  <div style="padding:12px; ...">
    <label style="margin-bottom:6px;">Размер печати (ГОСТ)</label>
    <select id="printSizeSelect" style="padding:8px; font-size:13px;">
```

## Проверка исправления

Все формы теперь корректно работают с кнопкой печати:

### Тестирование
```bash
python test_form_print_fix.py
```

Результат:
```
[PASS] form_torg12.html is correctly configured
[PASS] form_message.html is correctly configured
[PASS] form_exploitation.html is correctly configured
[PASS] form_transport.html is correctly configured
[PASS] form_custom.html is correctly configured
[PASS] form_env.html is correctly configured

[SUCCESS] All form templates have print button correctly configured
```

## Затронутые файлы
- `app/templates/_print_size_controls.html` - исправлена структура GOST_PRESETS и улучшен UI
- Все формы (ТОРГ-12, Сообщение, Эксплуатация, Транспорт, Произвольная, ENV) используют этот общий компонент

## Функционал кнопки печати
После нажатия на "Печать ▼" теперь открывается выпадающее меню с опциями:
1. **Размер печати (ГОСТ)** - выбор размера кода по ГОСТ стандартам
2. **Печать** - печать одного кода
3. **Печать несколько одинаковых** - печать нескольких копий одного кода
4. **Добавить в очередь** - добавление кода в очередь печати
5. **Печать несколько разных** - печать всей очереди
6. **Посмотреть очередь** - просмотр и управление очередью
7. **Очистить очередь** - очистка всей очереди

Все функции теперь работают корректно во всех формах.
