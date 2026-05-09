# Архитектура анимаций: независимые фон и персонаж

## Цель
Обеспечить независимое обновление:
- фона (день/ночь, сезон, погода),
- персонажа (эмоциональные состояния),
без взаимного редактирования ассетов.

## Слои рендера
1. `BackgroundLayer` (`128x160`)
   - Отвечает за время суток и сезонно-погодный пресет.
2. `CharacterLayer` (`80x80`)
   - Отвечает только за персонажа и его настроение.
3. `FxLayer` (`128x160`, опционально)
   - Поверхностные эффекты: частицы дождя/снега, блики.
4. `UiOverlayLayer` (опционально)
   - Иконки, часы, HUD (вне рамок текущей задачи).

## Контракт между модулями

### 1) Контракт Background System
- Вход:
  - `timeOfDay`: `day | evening | night | dawn`
  - `season`: `spring | summer | autumn | winter`
  - `weather`: `clear | rain | snow | cloudy`
- Выход:
  - `background_animation_id`
  - `fx_preset` (например, `rain_light`, `snow_light`)

### 2) Контракт Character Animator
- Вход:
  - `mood`: `happy | neutral | sad`
  - `state_time_ms` (время в текущем mood)
- Выход:
  - `character_animation_id`
  - `anchor`: `{x, y}` точки привязки слоя

### 3) Композитор кадра
- Получает `background_animation_id` и `character_animation_id`.
- Рендерит в фиксированном порядке слоев.
- Не хранит логики выбора персонажа или погоды.

## Маппинг состояний
- Персонаж (пример для `avocado`):
  - `happy -> avocado_happy_idle`
  - `neutral -> avocado_neutral_idle`
  - `sad -> avocado_sad_idle`
- Персонаж (пример для `pear`):
  - `happy -> pear_happy_idle`
  - `neutral -> pear_neutral_idle`
  - `sad -> pear_sad_idle`
- Фон:
  - `day/night` и сезонные пресеты выбираются независимо от mood.

## Замена персонажа без изменения фона
Для нового персонажа (например, `pear` или `cactus`):
1. Создать новые анимации `cactus_happy_idle`, `cactus_neutral_idle`, `cactus_sad_idle`.
2. Обновить только таблицу маппинга в Character Animator.
3. `BackgroundLayer` и его наборы day/night + season/weather не трогаются.

## Рекомендации по интеграции
- Вынести выбор анимации в два независимых автомата:
  - `BackgroundStateMachine`
  - `CharacterStateMachine`
- Хранить manifest по слоям:
  - `manifest.background.*`
  - `manifest.character.*`
- Поддерживать fallback:
  - если нет нужного mood-ассета, использовать `neutral`;
  - если нет погодного пресета, использовать `clear`.
