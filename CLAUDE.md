# Space Rail Shooter — правила для агентов

## Что это
Учебный 3D rail shooter на Godot 4.7 mono + C#. Спека:
`docs/superpowers/specs/2026-09-04-space-rail-shooter-design.md`. Планы:
`docs/superpowers/plans/`.

## Структура
- `game/` — Godot-проект. `game/scripts/*.cs` — ноды, `game/scenes/*.tscn` — сцены.
- `game/core/` — чистая логика без Godot (`SpaceRail.Core`), тестируется.
- `game/tests/` — xUnit.
- `art/blender/lib/` — bpy-библиотека (палитра, материалы, сборка, экспорт). `art/blender/scripts/` — генераторы моделей. `art/blender/*.blend` — источник правды после ручных правок. `art/refs/` — концепты и превью.
- `docs/style-guide.md` — правила арта.

## Команды
```bash
GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"
dotnet build game/SpaceRail.sln
dotnet test game/SpaceRail.sln
"$GODOT" --headless --path game --quit-after 120   # smoke-прогон без окна
"$GODOT" --path game                                # запуск с окном
```

Арт-пайплайн (Blender 5.2 headless, точка входа `scripts/art.sh`):
```bash
scripts/art.sh test           # unittest палитры (обычный Python)
scripts/art.sh make-palette   # art/blender/palette.png + копия в game/assets/textures
scripts/art.sh ship           # строит корабль: ship.blend, ship.glb, превью
ART_OVERWRITE=1 scripts/art.sh ship   # пересборка с нуля перезаписывает ship.blend; после ручных правок использовать export
scripts/art.sh export         # переэкспорт всех .blend после ручных правок
scripts/art.sh check          # лимиты полигонажа и габаритов .glb, код 1 при нарушении
scripts/art.sh import         # Godot --import, чтобы ModelSlot увидел новые .glb
scripts/art.sh shot 2.5 res://../docs/playtests/shot.png   # скриншот игры
```

## Конвенции
- Вперёд это -Z. Мир едет к игроку по +Z. Игрок стоит у начала координат.
- `GameState` меняется только через свои методы; ноды его читают.
- Логика, которую можно тестировать без Godot, идёт в `game/core/`.
- Слои физики: 1 player, 2 player_bullet, 3 enemy, 4 enemy_bullet, 5 asteroid.
- В `game/assets/models` только экспорт из Blender, руками не править.
- Коммиты Conventional Commits, без упоминания LLM в авторстве.
- Нос модели по +Y в Blender (экспортёр glTF даёт −Z в Godot). Проверять скриншотом, не арифметикой: `.tscn` пишет строки базиса.
- После любого нового .glb обязателен `scripts/art.sh import`, иначе `ResourceLoader.Exists` не видит файл и остаётся заглушка.
- Модели красятся UV в центры ячеек палитры; материалы `palette` и `palette_emit`, других не заводить.
