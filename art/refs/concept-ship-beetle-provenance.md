# Концепт корабля игрока «Жук» — provenance

Статус: концепт для ручного low-poly моделирования, не финальный арт.

Файлы в `art/refs/`:

| Файл | Размер | SHA-256 (первые 16) | Роль |
|---|---|---|---|
| `concept-ship-beetle-main.png` | 1254×1254 | `320a06e2184c84c6` | Основной вид сзади-сверху, как игровая камера |
| `concept-ship-beetle-ortho.png` | 1536×1024 | `fb0876be066ccaac` | Лист трёх проекций: сверху, сбоку, сзади |

## Запись воспроизведения

- Дата: 2026-09-05.
- Исполнитель: Codex CLI 0.147.0, модель `gpt-5.6-sol`, вызван headless через
  скилл `peer` (`ask-peer.sh --mode ask --peer codex`).
- Инструмент генерации: встроенный `image_gen.imagegen` Codex; идентификатор
  модели генератора инструмент не сообщает; качество по умолчанию.
- Изображение 1: запрошено 1024×1024, сохранено 1254×1254.
- Изображение 2: 1536×1024, при генерации использовано изображение 1 как
  референс (`num_last_images_to_include: 1`).
- Исходники на генерирующей машине:
  `~/.codex/generated_images/01a06e42-edf8-75c3-9188-545926859989/`.
- Ручная обработка: нет. Файлы скопированы как есть.

## Замечания к листу проекций

Правая проекция на листе подписана в промпте как «вид спереди», но нарисован
вид сзади (видно кольцо двигателя). Вид сбоку показывает купол кокпита ближе к
корме и маленький оранжевый выступ на брюхе, которого нет на основном виде.
Источник правды для моделирования: основной вид. Лист использовать для
пропорций корпуса и крыльев.

## Бриф исполнителю

`/tmp/peer/ship-concept/brief.md` (временный файл). Суть: два изображения,
дизайн «Жук» из решения владельца 2026-09-05, палитра #F2E9D8 / #F08A3C /
#1E2A4A / #40E0FF / #FFD23F на фоне #0A0B14, стиль Whisker Squadron.

## Точные промпты генератора

### Изображение 1

```text
Use case: stylized-concept
Asset type: player spaceship concept art for manual low-poly Blender modeling

Primary request: Create a polished concept sketch/render of a compact friendly player spaceship named "Beetle" for a modern stylized low-poly 3D space rail shooter.

Scene/backdrop: perfectly uniform solid dark background #0A0B14. No stars, no ground, no scene elements, no gradients, no atmospheric effects.

Subject and construction: one short, plump spacecraft with simple readable volumes and proportions approximately 1 : 0.6 : 0.45 (length : width : height). Rounded chunky main hull. Tiny side wing-stabilizers located near the rear. One large rear engine with a clearly visible brightly glowing cyan ring. Two simple forward-facing blaster antennae at the nose. A small cockpit dome on top. Cartoonish, friendly, compact, appealing "beetle" character.

Style/medium: modern stylized low-poly 3D concept render, clean broad polygonal planes, smooth large shapes, flat palette colors, minimal geometry, designed to be manually modeled in only 400–800 triangles. No tiny greebles, no panel-line clutter, no realistic machinery, no photorealism.

Composition/framing: square 1024×1024. Single ship centered with generous padding. Rear-three-quarter elevated game-camera view: camera is behind and above the ship; the nose points away from the viewer into the depth of the frame. Make the rear engine ring a strong readable focal point while the top cockpit, nose direction, both stabilizers, and both blaster antennae remain legible.

Color palette — use only these colors, no others: cream hull #F2E9D8; orange accents #F08A3C only for hull stripes and wing tips; dark navy #1E2A4A for lower hull, nozzle, mechanical details, and cockpit base; cyan emission #40E0FF only for the engine glow ring; yellow #FFD23F for the blasters; background #0A0B14. Cockpit is dark navy #1E2A4A with a small light highlight derived only from the allowed cream/cyan colors.

Lighting/mood: clean graphic studio-like lighting, bright readable silhouette, friendly energetic arcade tone. Preserve the restricted palette despite lighting; avoid introducing tinted colors.

Constraints: exactly one spacecraft; simple volumes suitable for a 400–800 triangle model; all specified features visible; no text, no labels, no logo, no watermark, no border.

Avoid: extra colors, stars, planets, nebulae, floor planes, scenery, weapons other than the two nose blaster antennae, multiple engines, extra wings, fine details, busy surface noise, photographic textures.
```

### Изображение 2

```text
Use case: stylized-concept
Asset type: orthographic turnaround sheet for manual low-poly Blender modeling

Primary request: Create a clean three-view orthographic concept sheet of the exact same compact friendly "Beetle" player spaceship shown in the provided reference image. Preserve the reference ship's identity, proportions, silhouette, construction, color placement, cockpit, rear engine ring, wing-stabilizers, and twin yellow nose blaster antennae.

Reference image role: design reference for the same ship; reconstruct it consistently in true orthographic views, not as a new variant.

Scene/backdrop: one perfectly uniform solid dark background #0A0B14 across the entire sheet. No stars, no ground, no scene elements, no gradients, no atmospheric effects. No dividers.

Subject and construction: a short, plump spacecraft made from simple readable volumes, proportions approximately 1 : 0.6 : 0.45 (length : width : height). Rounded chunky main hull; tiny side wing-stabilizers near the rear; exactly one large rear engine with a bright cyan ring; exactly two forward-facing blaster antennae at the nose; small cockpit dome on top. Cartoonish, friendly, compact. Geometry must be feasible as a manually built 400–800 triangle low-poly model.

Style/medium: modern stylized low-poly 3D model sheet, clean broad polygonal planes, smooth large forms, flat palette colors, minimal geometry, consistent neutral orthographic rendering. No perspective distortion, no tiny greebles, no panel-line clutter, no realistic machinery, no photorealism.

Composition/framing: horizontal canvas, requested size 1536×1024. Show exactly three separate, non-overlapping, equally scaled orthographic projections of the same ship arranged cleanly on one sheet with generous spacing: top view, side profile view, and front view looking directly at the nose. Keep all three fully visible and centered as a balanced triptych. The orientation and feature placement must agree precisely between projections. No perspective in any view.

Color palette — use only these colors, no others: cream hull #F2E9D8; orange accents #F08A3C only for hull stripes and wing tips; dark navy #1E2A4A for lower hull, nozzle, mechanical details, and cockpit; cyan emission #40E0FF only for the rear engine glow ring where visible; yellow #FFD23F for the two blasters; background #0A0B14. Cockpit is dark navy #1E2A4A with a small light highlight derived only from the allowed cream/cyan colors.

Lighting/mood: flat neutral design-sheet lighting for clear shape readability. Preserve the exact restricted palette despite lighting; no cast shadows and no tinted colors.

Constraints: exactly three projections and exactly one ship per projection; all are the same design and scale; true orthographic top, side, and front views; no labels, no captions, no text, no arrows, no dimensions, no logo, no watermark, no border.

Avoid: perspective views, three-quarter views, mismatched designs, extra colors, stars, planets, nebulae, scenery, floor plane, extra engines, extra wings, extra weapons, fine detail, busy surface noise, photographic textures.
```
