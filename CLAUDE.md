# Space Rail Shooter — правила для агентов

## Что это
Учебный 3D rail shooter на Godot 4.7 mono + C#. Спека:
`docs/superpowers/specs/2026-09-04-space-rail-shooter-design.md`. Планы:
`docs/superpowers/plans/`.

## Структура
- `game/` — Godot-проект. `game/scripts/*.cs` — ноды, `game/scenes/*.tscn` — сцены.
- `game/core/` — чистая логика без Godot (`SpaceRail.Core`), тестируется.
- `game/tests/` — xUnit.
- `art/` — Blender: скрипты генерации, .blend, палитра, экспорт (появится на этапе 3).
- `docs/style-guide.md` — правила арта.

## Команды
```bash
GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"
dotnet build game/SpaceRail.sln
dotnet test game/SpaceRail.sln
"$GODOT" --headless --path game --quit-after 120   # smoke-прогон без окна
"$GODOT" --path game                                # запуск с окном
```

## Конвенции
- Вперёд это -Z. Мир едет к игроку по +Z. Игрок стоит у начала координат.
- `GameState` меняется только через свои методы; ноды его читают.
- Логика, которую можно тестировать без Godot, идёт в `game/core/`.
- Слои физики: 1 player, 2 player_bullet, 3 enemy, 4 enemy_bullet, 5 asteroid.
- В `game/assets/models` только экспорт из Blender, руками не править.
- Коммиты Conventional Commits, без упоминания LLM в авторстве.
