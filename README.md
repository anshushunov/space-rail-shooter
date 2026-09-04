# Space Rail Shooter

Учебный 3D rail shooter: корабль летит вперёд по космосу и стреляет во врагов.
Godot 4.7 + C#, модели в Blender. Дизайн: `docs/superpowers/specs/`.

## Запуск

```bash
dotnet build game/SpaceRail.sln
"/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64.exe" --path game
```

## Тесты

```bash
dotnet test game/SpaceRail.sln
```

## Арт

Модели строятся Python-скриптами в Blender 5.2 и экспортируются в `game/assets/models/*.glb`.
Команды: `scripts/art.sh {test|make-palette|ship|export|check|import|shot}`. Подробности в `CLAUDE.md`.

## Управление

WASD или стрелки: движение. Пробел: огонь. Геймпад: левый стик и кнопка A.
