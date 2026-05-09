# План работ по дизайну анимаций (аналитик)

## 1. Входные ограничения
- Целевой экран: RGB `128x160`.
- Требуются анимации персонажа авокадо: `happy`, `neutral`, `sad`.
- Требуется независимый фоновый слой: смена дня/ночи и смена сезонов/погоды.
- Артефакты сохраняются в `design/`.
- Явных ограничений по RAM/flash/FPS не предоставлено.

## 2. Решение по маршрутизации агентов
- Вызывается только `pixel_animator`.
- `menu_designer` не требуется, так как задача не про структуру меню или навигацию экранов.

## 3. Порядок запуска
1. `pixel_animator`

## 4. Риски и блокеры
- Блокирующих вопросов нет.
- Риск: отсутствие лимитов производительности компенсируется консервативными параметрами (низкое число кадров, умеренный fps).

## 5. Контекст для pixel_animator
- `screen_sizes`: `128x160` (RGB).
- `state_list`: `happy`, `neutral`, `sad`, а также фоновые состояния `day/night` и `seasonal_weather`.
- `timing_limits`: рекомендованный диапазон `6-12 fps` для плавности и экономии ресурсов.
- `export_format`: `png sprite sheets`, `json atlas metadata`, `gif previews`.

```json
{
  "work_plan_file": "design/work_plan.md",
  "agents_to_call": ["pixel_animator"],
  "execution_order": ["pixel_animator"],
  "context_map": {
    "pixel_animator": ["screen_sizes", "state_list", "timing_limits", "export_format"]
  },
  "blocking_questions": [],
  "assumptions": [
    "Используется послойный рендер: background + character + fx.",
    "Целевая частота обновления анимаций ограничена диапазоном 6-12 fps."
  ]
}
```
