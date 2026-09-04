# Space Rail Shooter — план реализации: каркас и greybox

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Играбельный greybox: капсула-корабль летит вперёд, кубы-враги и шары-астероиды летят навстречу, есть стрельба, урон, счёт, HUD и рестарт. Ни одной своей модели ещё нет.

**Architecture:** Godot 4.7 mono, три C#-проекта в одном solution: `SpaceRail.Core` (чистая логика: `GameState`, `SpawnPolicy`, тестируется xUnit), `SpaceRail.Game` (Godot-сцены и ноды), `SpaceRail.Tests`. Корабль стоит у начала координат, мир движется к нему по +Z; вперёд это -Z (стандарт Godot). `GameState` живёт в autoload-ноде `Session`.

**Tech Stack:** Godot 4.7.1 mono (`C:\gamedev\Godot_v4.7.1-stable_mono_win64`), .NET SDK 8.0.424, Godot.NET.Sdk 4.7.1, xUnit 2.5.3, git.

**Scope этого плана:** этапы 1 и 2 спеки `docs/superpowers/specs/2026-09-04-space-rail-shooter-design.md`. Этапы 3–6 (Blender MCP, модели, эффекты, баланс) идут отдельным планом.

## Global Constraints

- Godot-проект лежит в `game/`, `project.godot` там же. Godot-сборка: `Godot.NET.Sdk/4.7.1`, `net8.0`.
- Чистая логика без `using Godot` живёт в `game/core/`, тесты в `game/tests/`. В обеих папках лежит пустой файл `.gdignore`, чтобы Godot их не индексировал.
- Все C#-проекты: `LangVersion 12`, `Nullable enable`, `ImplicitUsings enable`, `TreatWarningsAsErrors true` (через `game/Directory.Build.props`).
- Имя C#-класса скрипта совпадает с именем файла. Пространство имён `SpaceRail.Game` для нод, `SpaceRail.Core` для логики.
- Ось «вперёд» -Z. Спавн на Z = -80, удаление за Z = +10. Коридор игрока: X ∈ [-8, 8], Y ∈ [-4.5, 4.5].
- Слои физики: 1 `player`, 2 `player_bullet`, 3 `enemy`, 4 `enemy_bullet`, 5 `asteroid`. Битовые маски: 1, 2, 4, 8, 16.
- Веса спавна: астероид 50, дрон 35, стрелок 15.
- Коммиты в формате Conventional Commits, без упоминания LLM в авторстве.
- Все команды ниже запускаются из корня репозитория `C:\gamedev\prototype-blender` в Git Bash. Переменная для Godot:
  ```bash
  GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"
  ```
- Проверка Godot-задач: `dotnet build game/SpaceRail.sln`, затем headless-прогон `"$GODOT" --headless --path game --quit-after 120`. В выводе не должно быть строк `ERROR`, `SCRIPT ERROR`, `Unhandled exception`.

---

## Карта файлов

| Файл | Ответственность |
|---|---|
| `.gitignore`, `README.md`, `CLAUDE.md` | Каркас репозитория |
| `docs/style-guide.md` | Правила арта из спеки (для этапа 3, пишется сейчас, чтобы не потерять) |
| `game/Directory.Build.props` | Общие настройки компилятора |
| `game/SpaceRail.sln` | Solution из трёх проектов |
| `game/core/SpaceRail.Core.csproj`, `game/core/.gdignore` | Сборка чистой логики |
| `game/core/GameConfig.cs` | Константы баланса |
| `game/core/GameState.cs` | HP, счёт, скорость, событие изменения |
| `game/core/SpawnPolicy.cs` | Выбор типа спавна по весам, интервал |
| `game/tests/SpaceRail.Tests.csproj`, `game/tests/.gdignore` | Тестовый проект |
| `game/tests/GameStateTests.cs`, `game/tests/SpawnPolicyTests.cs` | Тесты логики |
| `game/project.godot` | Настройки, autoload, InputMap, имена слоёв |
| `game/SpaceRail.Game.csproj` | Godot-сборка, исключает `core/**` и `tests/**` |
| `game/scripts/Session.cs` | Autoload с `GameState` |
| `game/scripts/Main.cs` | Тик состояния, пауза при смерти |
| `game/scripts/World.cs` | Движение мира к игроку, удаление за спиной |
| `game/scripts/Spawner.cs` | Периодический спавн по `SpawnPolicy` |
| `game/scripts/IDamageable.cs` | Интерфейс получения урона |
| `game/scripts/Player.cs` | Движение, крен, стрельба, приём урона |
| `game/scripts/Bullet.cs` | Полёт, время жизни, нанесение урона |
| `game/scripts/Asteroid.cs` | Вращение, HP, столкновение с игроком |
| `game/scripts/Enemy.cs` | Базовый враг: HP, очки, столкновение |
| `game/scripts/EnemyDrone.cs` | Преследует игрока |
| `game/scripts/EnemyShooter.cs` | Держит дистанцию, стреляет |
| `game/scripts/Hud.cs` | HP, счёт, экран смерти, рестарт |
| `game/scripts/ModelSlot.cs` | Подмена заглушки на .glb, если файл есть |
| `game/scenes/*.tscn` | Main, Player, PlayerBullet, EnemyBullet, Asteroid, EnemyDrone, EnemyShooter, Hud |

---

### Task 1: Каркас репозитория

**Files:**
- Create: `.gitignore`, `README.md`, `CLAUDE.md`, `docs/style-guide.md`, `game/Directory.Build.props`

**Interfaces:**
- Produces: правила для всех последующих задач; `Directory.Build.props` применяется ко всем csproj под `game/`.

- [ ] **Step 1: Создать `.gitignore`**

```gitignore
# .NET и Godot
**/bin/
**/obj/
**/.godot/
*.import
*.uid
TestResults/
*.user

# Локальное состояние Claude Code
CLAUDE.local.md
.claude/settings.local.json

# Blender
*.blend1
*.blend2
```

- [ ] **Step 2: Создать `README.md`**

```markdown
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

## Управление

WASD или стрелки: движение. Пробел: огонь. Геймпад: левый стик и кнопка A.
```

- [ ] **Step 3: Создать `CLAUDE.md`**

```markdown
# Space Rail Shooter — правила для агентов

## Что это
Учебный 3D rail shooter на Godot 4.7 mono + C#. Спека:
`docs/superpowers/specs/2026-09-04-space-rail-shooter-design.md`. Планы:
`docs/superpowers/plans/`.

## Структура
- `game/` — Godot-проект. `game/scripts/*.cs` — ноды, `game/scenes/*.tscn` — сцены.
- `game/core/` — чистая логика без Godot (`SpaceRail.Core`), тестируется.
- `game/tests/` — xUnit.
- `art/` — Blender: скрипты генерации, .blend, палитра, экспорт.
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
```

- [ ] **Step 4: Создать `docs/style-guide.md`**

```markdown
# Style guide арта

Референсы: Fur Squadron Phoenix, Whisker Squadron: Survivor. Современный
стилизованный low-poly: гладкие формы, палитровая текстура, эмиссивные детали.

## Геометрия
- Полигонаж (треугольники): корабль игрока 400–800, враги 150–400, астероид 100–200.
- Shading: auto smooth 30°, без запечённых нормалей.
- Масштаб: 1 единица Blender = 1 метр. Корабль игрока около 4 м в длину.
- Нос модели смотрит по -Y в Blender. После экспорта glTF это -Z в Godot.
- Пивот в геометрическом центре. Объект и меш названы одинаково, латиницей, snake_case.

## Цвет
- Одна палитра `art/blender/palette.png`, 8×8 ячеек, 64 цвета.
- Ряды 0–5: основные цвета корпусов и деталей. Ряд 6: эмиссия двигателей.
  Ряд 7: эмиссия оружия и опасности.
- Один материал на все модели, ссылается на палитру. Раскраска через UV в ячейки.

## Экспорт
- Формат glTF binary (.glb), путь `game/assets/models/<name>.glb`.
- Модификаторы применяются при экспорте, трансформации применены (rotation 0, scale 1).
- Имена файлов: `ship.glb`, `asteroid.glb`, `enemy_drone.glb`, `enemy_shooter.glb`.
```

- [ ] **Step 5: Создать `game/Directory.Build.props`**

```xml
<Project>
  <PropertyGroup>
    <LangVersion>12.0</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md CLAUDE.md docs/style-guide.md game/Directory.Build.props
git commit -m "chore: каркас репозитория, style guide, правила для агентов"
```

---

### Task 2: SpaceRail.Core и GameState

**Files:**
- Create: `game/SpaceRail.sln`, `game/core/SpaceRail.Core.csproj`, `game/core/.gdignore`, `game/core/GameConfig.cs`, `game/core/GameState.cs`
- Create: `game/tests/SpaceRail.Tests.csproj`, `game/tests/.gdignore`, `game/tests/GameStateTests.cs`

**Interfaces:**
- Produces:
  ```csharp
  namespace SpaceRail.Core;
  public sealed record GameConfig(int MaxHp = 3, float BaseSpeed = 20f, float MaxSpeed = 45f, float Acceleration = 0.5f);
  public sealed class GameState {
      public GameState(GameConfig config);
      public int Hp { get; }           // текущее HP
      public int Score { get; }
      public float Speed { get; }      // скорость мира, м/с
      public float ElapsedSeconds { get; }
      public bool IsAlive { get; }     // Hp > 0
      public event Action? Changed;    // после любого изменения Hp или Score, и после Restart
      public void Tick(double delta);  // растит время и скорость; игнорируется, если мёртв
      public void TakeDamage(int amount);
      public void AddScore(int points);
      public void Restart();
  }
  ```

- [ ] **Step 1: Создать проекты и solution**

`game/core/SpaceRail.Core.csproj`:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <RootNamespace>SpaceRail.Core</RootNamespace>
  </PropertyGroup>
</Project>
```

`game/tests/SpaceRail.Tests.csproj`:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
    <RootNamespace>SpaceRail.Tests</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="xunit" Version="2.5.3" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\core\SpaceRail.Core.csproj" />
  </ItemGroup>
</Project>
```

Пустые файлы `game/core/.gdignore` и `game/tests/.gdignore`:
```bash
touch game/core/.gdignore game/tests/.gdignore
```

Solution:
```bash
cd game && dotnet new sln -n SpaceRail && dotnet sln SpaceRail.sln add core/SpaceRail.Core.csproj tests/SpaceRail.Tests.csproj && cd ..
```

- [ ] **Step 2: Написать падающие тесты `game/tests/GameStateTests.cs`**

```csharp
using SpaceRail.Core;
using Xunit;

namespace SpaceRail.Tests;

public class GameStateTests
{
    private static GameState NewState() => new(new GameConfig(MaxHp: 3, BaseSpeed: 20f, MaxSpeed: 45f, Acceleration: 0.5f));

    [Fact]
    public void StartsWithMaxHpZeroScoreAndBaseSpeed()
    {
        var s = NewState();
        Assert.Equal(3, s.Hp);
        Assert.Equal(0, s.Score);
        Assert.Equal(20f, s.Speed);
        Assert.True(s.IsAlive);
    }

    [Fact]
    public void TakeDamageReducesHpAndClampsAtZero()
    {
        var s = NewState();
        s.TakeDamage(2);
        Assert.Equal(1, s.Hp);
        s.TakeDamage(5);
        Assert.Equal(0, s.Hp);
        Assert.False(s.IsAlive);
    }

    [Fact]
    public void AddScoreAccumulatesWhileAliveAndIgnoredWhenDead()
    {
        var s = NewState();
        s.AddScore(10);
        s.AddScore(5);
        Assert.Equal(15, s.Score);
        s.TakeDamage(3);
        s.AddScore(100);
        Assert.Equal(15, s.Score);
    }

    [Fact]
    public void TickRaisesSpeedUpToMaxAndStopsWhenDead()
    {
        var s = NewState();
        s.Tick(10.0);
        Assert.Equal(10f, s.ElapsedSeconds, 3);
        Assert.Equal(25f, s.Speed, 3);
        s.Tick(1000.0);
        Assert.Equal(45f, s.Speed, 3);
        s.TakeDamage(3);
        var elapsedAtDeath = s.ElapsedSeconds;
        s.Tick(5.0);
        Assert.Equal(elapsedAtDeath, s.ElapsedSeconds);
    }

    [Fact]
    public void RestartResetsEverything()
    {
        var s = NewState();
        s.AddScore(7);
        s.Tick(30.0);
        s.TakeDamage(3);
        s.Restart();
        Assert.Equal(3, s.Hp);
        Assert.Equal(0, s.Score);
        Assert.Equal(0f, s.ElapsedSeconds);
        Assert.Equal(20f, s.Speed);
        Assert.True(s.IsAlive);
    }

    [Fact]
    public void ChangedFiresOnDamageScoreAndRestartButNotOnTick()
    {
        var s = NewState();
        var count = 0;
        s.Changed += () => count++;
        s.Tick(1.0);
        Assert.Equal(0, count);
        s.TakeDamage(1);
        s.AddScore(1);
        s.Restart();
        Assert.Equal(3, count);
    }
}
```

- [ ] **Step 3: Убедиться, что тесты не компилируются**

Run: `dotnet test game/SpaceRail.sln 2>&1 | tail -5`
Expected: ошибка компиляции, `GameState` и `GameConfig` не найдены.

- [ ] **Step 4: Реализовать `game/core/GameConfig.cs` и `game/core/GameState.cs`**

`GameConfig.cs`:
```csharp
namespace SpaceRail.Core;

/// <summary>Константы баланса. Скорости в метрах в секунду.</summary>
public sealed record GameConfig(
    int MaxHp = 3,
    float BaseSpeed = 20f,
    float MaxSpeed = 45f,
    float Acceleration = 0.5f);
```

`GameState.cs`:
```csharp
namespace SpaceRail.Core;

/// <summary>Единственное место, где меняются HP, счёт и скорость мира.</summary>
public sealed class GameState
{
    private readonly GameConfig _config;

    public GameState(GameConfig config)
    {
        _config = config;
        Hp = config.MaxHp;
        Speed = config.BaseSpeed;
    }

    public int Hp { get; private set; }
    public int Score { get; private set; }
    public float Speed { get; private set; }
    public float ElapsedSeconds { get; private set; }
    public bool IsAlive => Hp > 0;

    /// <summary>Срабатывает после изменения Hp или Score и после Restart. Tick событие не вызывает.</summary>
    public event Action? Changed;

    public void Tick(double delta)
    {
        if (!IsAlive) return;
        ElapsedSeconds += (float)delta;
        Speed = Math.Min(_config.MaxSpeed, _config.BaseSpeed + _config.Acceleration * ElapsedSeconds);
    }

    public void TakeDamage(int amount)
    {
        if (!IsAlive || amount <= 0) return;
        Hp = Math.Max(0, Hp - amount);
        Changed?.Invoke();
    }

    public void AddScore(int points)
    {
        if (!IsAlive || points <= 0) return;
        Score += points;
        Changed?.Invoke();
    }

    public void Restart()
    {
        Hp = _config.MaxHp;
        Score = 0;
        ElapsedSeconds = 0f;
        Speed = _config.BaseSpeed;
        Changed?.Invoke();
    }
}
```

- [ ] **Step 5: Прогнать тесты**

Run: `dotnet test game/SpaceRail.sln 2>&1 | tail -5`
Expected: `Passed! - Failed: 0, Passed: 6`.

- [ ] **Step 6: Commit**

```bash
git add game/SpaceRail.sln game/core game/tests
git commit -m "feat: SpaceRail.Core с GameState и тестами"
```

---

### Task 3: SpawnPolicy

**Files:**
- Create: `game/core/SpawnPolicy.cs`, `game/tests/SpawnPolicyTests.cs`

**Interfaces:**
- Produces:
  ```csharp
  namespace SpaceRail.Core;
  public enum SpawnKind { Asteroid, Drone, Shooter }
  public sealed class SpawnPolicy {
      public SpawnPolicy(Random rng, float startInterval = 1.2f, float minInterval = 0.4f, float decayPerSecond = 0.01f);
      public static IReadOnlyDictionary<SpawnKind, int> Weights { get; } // 50/35/15
      public SpawnKind Choose();
      public float IntervalAt(float elapsedSeconds); // max(minInterval, startInterval - decayPerSecond * elapsed)
  }
  ```

- [ ] **Step 1: Написать падающие тесты `game/tests/SpawnPolicyTests.cs`**

```csharp
using SpaceRail.Core;
using Xunit;

namespace SpaceRail.Tests;

public class SpawnPolicyTests
{
    [Fact]
    public void WeightsMatchSpec()
    {
        Assert.Equal(50, SpawnPolicy.Weights[SpawnKind.Asteroid]);
        Assert.Equal(35, SpawnPolicy.Weights[SpawnKind.Drone]);
        Assert.Equal(15, SpawnPolicy.Weights[SpawnKind.Shooter]);
    }

    [Fact]
    public void ChooseFollowsWeightsWithinTolerance()
    {
        var policy = new SpawnPolicy(new Random(42));
        const int n = 20_000;
        var counts = new Dictionary<SpawnKind, int> { [SpawnKind.Asteroid] = 0, [SpawnKind.Drone] = 0, [SpawnKind.Shooter] = 0 };
        for (var i = 0; i < n; i++) counts[policy.Choose()]++;

        Assert.InRange(counts[SpawnKind.Asteroid] / (double)n, 0.47, 0.53);
        Assert.InRange(counts[SpawnKind.Drone] / (double)n, 0.32, 0.38);
        Assert.InRange(counts[SpawnKind.Shooter] / (double)n, 0.12, 0.18);
    }

    [Fact]
    public void IntervalDecaysLinearlyAndClampsAtMinimum()
    {
        var policy = new SpawnPolicy(new Random(1), startInterval: 1.2f, minInterval: 0.4f, decayPerSecond: 0.01f);
        Assert.Equal(1.2f, policy.IntervalAt(0f), 3);
        Assert.Equal(0.9f, policy.IntervalAt(30f), 3);
        Assert.Equal(0.4f, policy.IntervalAt(80f), 3);
        Assert.Equal(0.4f, policy.IntervalAt(10_000f), 3);
    }
}
```

- [ ] **Step 2: Убедиться, что тесты не компилируются**

Run: `dotnet test game/SpaceRail.sln 2>&1 | tail -5`
Expected: ошибка компиляции, `SpawnPolicy` не найден.

- [ ] **Step 3: Реализовать `game/core/SpawnPolicy.cs`**

```csharp
namespace SpaceRail.Core;

public enum SpawnKind { Asteroid, Drone, Shooter }

/// <summary>Что и как часто спавнить. Без Godot, чтобы тестировать распределение.</summary>
public sealed class SpawnPolicy
{
    private static readonly (SpawnKind Kind, int Weight)[] Table =
    {
        (SpawnKind.Asteroid, 50),
        (SpawnKind.Drone, 35),
        (SpawnKind.Shooter, 15),
    };

    public static IReadOnlyDictionary<SpawnKind, int> Weights { get; } =
        Table.ToDictionary(t => t.Kind, t => t.Weight);

    private static readonly int TotalWeight = Table.Sum(t => t.Weight);

    private readonly Random _rng;
    private readonly float _startInterval;
    private readonly float _minInterval;
    private readonly float _decayPerSecond;

    public SpawnPolicy(Random rng, float startInterval = 1.2f, float minInterval = 0.4f, float decayPerSecond = 0.01f)
    {
        _rng = rng;
        _startInterval = startInterval;
        _minInterval = minInterval;
        _decayPerSecond = decayPerSecond;
    }

    public SpawnKind Choose()
    {
        var roll = _rng.Next(TotalWeight);
        foreach (var (kind, weight) in Table)
        {
            if (roll < weight) return kind;
            roll -= weight;
        }
        return Table[^1].Kind;
    }

    public float IntervalAt(float elapsedSeconds) =>
        Math.Max(_minInterval, _startInterval - _decayPerSecond * elapsedSeconds);
}
```

- [ ] **Step 4: Прогнать тесты**

Run: `dotnet test game/SpaceRail.sln 2>&1 | tail -5`
Expected: `Passed! - Failed: 0, Passed: 9`.

- [ ] **Step 5: Commit**

```bash
git add game/core/SpawnPolicy.cs game/tests/SpawnPolicyTests.cs
git commit -m "feat: SpawnPolicy с весами 50/35/15 и убывающим интервалом"
```

---

### Task 4: Godot-проект, Session и пустая сцена Main

**Files:**
- Create: `game/project.godot`, `game/SpaceRail.Game.csproj`, `game/scripts/Session.cs`, `game/scripts/Main.cs`, `game/scenes/Main.tscn`
- Modify: `game/SpaceRail.sln` (добавить Game-проект)

**Interfaces:**
- Consumes: `SpaceRail.Core.GameState`, `GameConfig`.
- Produces:
  ```csharp
  namespace SpaceRail.Game;
  public partial class Session : Node {
      public GameState State { get; }
      public static Session Of(Node node); // node.GetNode<Session>("/root/Session")
  }
  ```
  Сцена `res://scenes/Main.tscn` с узлами `Main` (Node3D), `Camera3D`, `Sun`, `Env`, `World` (Node3D, пока без скрипта), `Projectiles` (Node3D).

- [ ] **Step 1: Создать `game/SpaceRail.Game.csproj`**

```xml
<Project Sdk="Godot.NET.Sdk/4.7.1">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <RootNamespace>SpaceRail.Game</RootNamespace>
    <EnableDynamicLoading>true</EnableDynamicLoading>
  </PropertyGroup>
  <ItemGroup>
    <Compile Remove="core/**;tests/**" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="core\SpaceRail.Core.csproj" />
  </ItemGroup>
</Project>
```

Добавить в solution:
```bash
dotnet sln game/SpaceRail.sln add game/SpaceRail.Game.csproj
```

- [ ] **Step 2: Создать `game/project.godot`**

```ini
; Engine configuration file.
config_version=5

[application]

config/name="Space Rail Shooter"
run/main_scene="res://scenes/Main.tscn"
config/features=PackedStringArray("4.7", "C#", "Forward Plus")

[autoload]

Session="*res://scripts/Session.cs"

[display]

window/size/viewport_width=1280
window/size/viewport_height=720

[dotnet]

project/assembly_name="SpaceRail.Game"

[input]

move_left={
"deadzone": 0.2,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":65,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194319,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":-1,"axis":0,"axis_value":-1.0,"script":null)
]
}
move_right={
"deadzone": 0.2,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":68,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194321,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":-1,"axis":0,"axis_value":1.0,"script":null)
]
}
move_up={
"deadzone": 0.2,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":87,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194320,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":-1,"axis":1,"axis_value":-1.0,"script":null)
]
}
move_down={
"deadzone": 0.2,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":83,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194322,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadMotion,"resource_local_to_scene":false,"resource_name":"","device":-1,"axis":1,"axis_value":1.0,"script":null)
]
}
fire={
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":32,"key_label":0,"unicode":0,"location":0,"echo":false,"script":null)
, Object(InputEventJoypadButton,"resource_local_to_scene":false,"resource_name":"","device":-1,"button_index":0,"pressure":0.0,"pressed":false,"script":null)
]
}

[layer_names]

3d_physics/layer_1="player"
3d_physics/layer_2="player_bullet"
3d_physics/layer_3="enemy"
3d_physics/layer_4="enemy_bullet"
3d_physics/layer_5="asteroid"

[rendering]

renderer/rendering_method="forward_plus"
```

Коды клавиш: A=65, D=68, W=87, S=83, пробел=32, стрелки влево/вверх/вправо/вниз = 4194319/4194320/4194321/4194322.

- [ ] **Step 3: Создать `game/scripts/Session.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Autoload. Держит GameState, который переживает перезагрузку сцены.</summary>
public partial class Session : Node
{
    public GameState State { get; } = new(new GameConfig());

    public static Session Of(Node node) => node.GetNode<Session>("/root/Session");
}
```

- [ ] **Step 4: Создать `game/scripts/Main.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Корневая сцена: тикает состояние и ставит игру на паузу при смерти.</summary>
public partial class Main : Node3D
{
    private GameState _state = null!;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _state.Changed += OnStateChanged;
    }

    public override void _ExitTree() => _state.Changed -= OnStateChanged;

    public override void _Process(double delta) => _state.Tick(delta);

    private void OnStateChanged()
    {
        if (!_state.IsAlive && !GetTree().Paused)
            GetTree().Paused = true;
    }
}
```

- [ ] **Step 5: Создать `game/scenes/Main.tscn`**

```
[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/Main.cs" id="1_main"]

[sub_resource type="Environment" id="Environment_space"]
background_mode = 1
background_color = Color(0.02, 0.02, 0.05, 1)
ambient_light_source = 2
ambient_light_color = Color(0.45, 0.45, 0.6, 1)
ambient_light_energy = 0.7

[node name="Main" type="Node3D"]
script = ExtResource("1_main")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.985, -0.174, 0, 0.174, 0.985, 0, 3, 12)
fov = 70.0

[node name="Sun" type="DirectionalLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.643, -0.766, 0, 0.766, 0.643, 0, 20, 0)
light_energy = 1.2

[node name="Env" type="WorldEnvironment" parent="."]
environment = SubResource("Environment_space")

[node name="World" type="Node3D" parent="."]

[node name="Projectiles" type="Node3D" parent="."]
```

Камера стоит на (0, 3, 12) и наклонена вниз на 10°, смотрит вдоль -Z. Свет наклонён на 50° вниз.

- [ ] **Step 6: Собрать и прогнать headless**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
GODOT="/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64_console.exe"
"$GODOT" --headless --path game --import 2>&1 | tail -5
"$GODOT" --headless --path game --quit-after 120 2>&1 | tail -20
```
Expected: сборка `0 Error(s)`, прогон завершается без `ERROR`, `SCRIPT ERROR`, `Unhandled exception`. Если Godot ругается на отсутствие сборки, проверить, что `dotnet build` положил dll в `game/.godot/mono/temp/bin/Debug/`.

- [ ] **Step 7: Commit**

```bash
git add game/project.godot game/SpaceRail.Game.csproj game/SpaceRail.sln game/scripts/Session.cs game/scripts/Main.cs game/scenes/Main.tscn
git commit -m "feat: Godot-проект, autoload Session и пустая сцена Main"
```

---

### Task 5: World, Spawner и астероиды-заглушки летят навстречу

**Files:**
- Create: `game/scripts/World.cs`, `game/scripts/Spawner.cs`, `game/scripts/IDamageable.cs`, `game/scripts/Asteroid.cs`, `game/scenes/Asteroid.tscn`
- Modify: `game/scenes/Main.tscn`

**Interfaces:**
- Consumes: `Session.Of(node).State`, `SpawnPolicy`, `SpawnKind`.
- Produces:
  ```csharp
  public interface IDamageable { void TakeHit(int damage); }
  public partial class World : Node3D { [Export] public float DespawnZ; }
  public partial class Spawner : Node {
      [Export] public PackedScene? AsteroidScene; [Export] public PackedScene? DroneScene; [Export] public PackedScene? ShooterScene;
  }
  public partial class Asteroid : Area3D, IDamageable { [Export] public int Hp; [Export] public int ScoreValue; }
  ```
  Столкновение астероида с игроком реализуется в Task 8, когда появится `Player.TakeHit`.

- [ ] **Step 1: Создать `game/scripts/IDamageable.cs`**

```csharp
namespace SpaceRail.Game;

/// <summary>Всё, во что можно попасть пулей.</summary>
public interface IDamageable
{
    void TakeHit(int damage);
}
```

- [ ] **Step 2: Создать `game/scripts/World.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Двигает всех детей к игроку по +Z и удаляет тех, кто улетел за спину.</summary>
public partial class World : Node3D
{
    [Export] public float DespawnZ { get; set; } = 10f;

    private GameState _state = null!;

    public override void _Ready() => _state = Session.Of(this).State;

    public override void _Process(double delta)
    {
        var dz = _state.Speed * (float)delta;
        foreach (var child in GetChildren())
        {
            if (child is not Node3D node) continue;
            node.Position += new Vector3(0f, 0f, dz);
            if (node.Position.Z > DespawnZ) node.QueueFree();
        }
    }
}
```

- [ ] **Step 3: Создать `game/scripts/Spawner.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Раз в интервал из SpawnPolicy добавляет в World новый объект впереди игрока.</summary>
public partial class Spawner : Node
{
    [Export] public PackedScene? AsteroidScene { get; set; }
    [Export] public PackedScene? DroneScene { get; set; }
    [Export] public PackedScene? ShooterScene { get; set; }
    [Export] public float SpawnZ { get; set; } = -80f;
    [Export] public float HalfWidth { get; set; } = 8f;
    [Export] public float HalfHeight { get; set; } = 4.5f;

    private readonly Random _rng = new();
    private SpawnPolicy _policy = null!;
    private GameState _state = null!;
    private Node3D _world = null!;
    private float _timer;

    public override void _Ready()
    {
        _policy = new SpawnPolicy(_rng);
        _state = Session.Of(this).State;
        _world = GetNode<Node3D>("../World");
        _timer = _policy.IntervalAt(0f);
    }

    public override void _Process(double delta)
    {
        if (!_state.IsAlive) return;
        _timer -= (float)delta;
        if (_timer > 0f) return;
        Spawn(_policy.Choose());
        _timer = _policy.IntervalAt(_state.ElapsedSeconds);
    }

    private void Spawn(SpawnKind kind)
    {
        var scene = kind switch
        {
            SpawnKind.Asteroid => AsteroidScene,
            SpawnKind.Drone => DroneScene,
            SpawnKind.Shooter => ShooterScene,
            _ => null,
        };
        if (scene is null) return;

        var node = scene.Instantiate<Node3D>();
        node.Position = new Vector3(
            (float)(_rng.NextDouble() * 2 - 1) * HalfWidth,
            (float)(_rng.NextDouble() * 2 - 1) * HalfHeight,
            SpawnZ);
        _world.AddChild(node);
    }
}
```

- [ ] **Step 4: Создать `game/scripts/Asteroid.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Препятствие: медленно вращается, разрушается с трёх попаданий.</summary>
public partial class Asteroid : Area3D, IDamageable
{
    [Export] public int Hp { get; set; } = 3;
    [Export] public int ScoreValue { get; set; } = 10;

    private GameState _state = null!;
    private Vector3 _spin;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        var rng = new Random();
        _spin = new Vector3(Rand(rng), Rand(rng), Rand(rng));
    }

    public override void _Process(double delta) => Rotation += _spin * (float)delta;

    public void TakeHit(int damage)
    {
        Hp -= damage;
        if (Hp > 0) return;
        _state.AddScore(ScoreValue);
        QueueFree();
    }

    private static float Rand(Random rng) => (float)(rng.NextDouble() * 2 - 1);
}
```

- [ ] **Step 5: Создать `game/scenes/Asteroid.tscn`**

```
[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Asteroid.cs" id="1_asteroid"]

[sub_resource type="SphereMesh" id="SphereMesh_rock"]
radius = 1.5
height = 3.0
radial_segments = 8
rings = 4

[sub_resource type="StandardMaterial3D" id="Mat_rock"]
albedo_color = Color(0.45, 0.38, 0.32, 1)

[sub_resource type="SphereShape3D" id="Shape_rock"]
radius = 1.5

[node name="Asteroid" type="Area3D"]
collision_layer = 16
collision_mask = 1
script = ExtResource("1_asteroid")

[node name="Placeholder" type="MeshInstance3D" parent="."]
mesh = SubResource("SphereMesh_rock")
surface_material_override/0 = SubResource("Mat_rock")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("Shape_rock")
```

- [ ] **Step 6: Подключить World, Spawner и Asteroid в `game/scenes/Main.tscn`**

Заменить содержимое файла:
```
[gd_scene load_steps=6 format=3]

[ext_resource type="Script" path="res://scripts/Main.cs" id="1_main"]
[ext_resource type="Script" path="res://scripts/World.cs" id="2_world"]
[ext_resource type="Script" path="res://scripts/Spawner.cs" id="3_spawner"]
[ext_resource type="PackedScene" path="res://scenes/Asteroid.tscn" id="4_asteroid"]

[sub_resource type="Environment" id="Environment_space"]
background_mode = 1
background_color = Color(0.02, 0.02, 0.05, 1)
ambient_light_source = 2
ambient_light_color = Color(0.45, 0.45, 0.6, 1)
ambient_light_energy = 0.7

[node name="Main" type="Node3D"]
script = ExtResource("1_main")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.985, -0.174, 0, 0.174, 0.985, 0, 3, 12)
fov = 70.0

[node name="Sun" type="DirectionalLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.643, -0.766, 0, 0.766, 0.643, 0, 20, 0)
light_energy = 1.2

[node name="Env" type="WorldEnvironment" parent="."]
environment = SubResource("Environment_space")

[node name="World" type="Node3D" parent="."]
script = ExtResource("2_world")

[node name="Projectiles" type="Node3D" parent="."]

[node name="Spawner" type="Node" parent="."]
script = ExtResource("3_spawner")
AsteroidScene = ExtResource("4_asteroid")
```

- [ ] **Step 7: Собрать, прогнать headless, посмотреть глазами**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 300 2>&1 | tail -20
```
Expected: без ошибок. Затем запуск с окном `"$GODOT" --path game`: шары летят на камеру и исчезают за ней, со временем чаще.

- [ ] **Step 8: Commit**

```bash
git add game/scripts/World.cs game/scripts/Spawner.cs game/scripts/IDamageable.cs game/scripts/Asteroid.cs game/scenes/Asteroid.tscn game/scenes/Main.tscn
git commit -m "feat: движение мира, спавн и астероиды-заглушки"
```

---

### Task 6: Игрок двигается и кренится

**Files:**
- Create: `game/scripts/Player.cs`, `game/scenes/Player.tscn`
- Modify: `game/scenes/Main.tscn`

**Interfaces:**
- Produces:
  ```csharp
  public partial class Player : CharacterBody3D {
      [Export] public float MoveSpeed; [Export] public float HalfWidth; [Export] public float HalfHeight;
      [Export] public float BankDegrees; [Export] public float FireCooldown; [Export] public PackedScene? BulletScene;
      public void TakeHit(int damage); // -> GameState.TakeDamage
  }
  ```
  Узел `Player` в группе `player`. Дочерние узлы: `Model` (Node3D, кренится), `Model/Placeholder` (MeshInstance3D), `CollisionShape3D`, `MuzzleLeft`, `MuzzleRight` (Marker3D). Стрельба добавляется в Task 7, здесь `BulletScene` только объявлен.

- [ ] **Step 1: Создать `game/scripts/Player.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Корабль игрока: двигается в плоскости экрана, кренится, стреляет.</summary>
public partial class Player : CharacterBody3D
{
    [Export] public float MoveSpeed { get; set; } = 14f;
    [Export] public float HalfWidth { get; set; } = 8f;
    [Export] public float HalfHeight { get; set; } = 4.5f;
    [Export] public float BankDegrees { get; set; } = 35f;
    [Export] public float FireCooldown { get; set; } = 0.15f;
    [Export] public PackedScene? BulletScene { get; set; }

    private GameState _state = null!;
    private Node3D _model = null!;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _model = GetNode<Node3D>("Model");
    }

    public override void _Process(double delta)
    {
        if (!_state.IsAlive) return;
        var dt = (float)delta;

        var input = Input.GetVector("move_left", "move_right", "move_down", "move_up");
        var p = Position + new Vector3(input.X, input.Y, 0f) * MoveSpeed * dt;
        p.X = Mathf.Clamp(p.X, -HalfWidth, HalfWidth);
        p.Y = Mathf.Clamp(p.Y, -HalfHeight, HalfHeight);
        p.Z = 0f;
        Position = p;

        var targetBank = -input.X * Mathf.DegToRad(BankDegrees);
        var bank = Mathf.LerpAngle(_model.Rotation.Z, targetBank, 10f * dt);
        _model.Rotation = new Vector3(0f, 0f, bank);
    }

    public void TakeHit(int damage) => _state.TakeDamage(damage);
}
```

- [ ] **Step 2: Создать `game/scenes/Player.tscn`**

```
[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Player.cs" id="1_player"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_ship"]
radius = 0.6
height = 3.0

[sub_resource type="StandardMaterial3D" id="Mat_ship"]
albedo_color = Color(0.3, 0.8, 1, 1)

[sub_resource type="CapsuleShape3D" id="Shape_ship"]
radius = 0.6
height = 3.0

[node name="Player" type="CharacterBody3D" groups=["player"]]
collision_layer = 1
collision_mask = 0
script = ExtResource("1_player")

[node name="Model" type="Node3D" parent="."]

[node name="Placeholder" type="MeshInstance3D" parent="Model"]
transform = Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0)
mesh = SubResource("CapsuleMesh_ship")
surface_material_override/0 = SubResource("Mat_ship")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0)
shape = SubResource("Shape_ship")

[node name="MuzzleLeft" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -0.8, 0, -1.5)

[node name="MuzzleRight" type="Marker3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.8, 0, -1.5)
```

Капсула по умолчанию вытянута вдоль Y, трансформ поворачивает её на 90° вокруг X, чтобы лежала вдоль Z.

- [ ] **Step 3: Добавить игрока в `game/scenes/Main.tscn`**

В заголовке `load_steps=6` заменить на `load_steps=7`. После строки с `4_asteroid` добавить:
```
[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="5_player"]
```
После узла `Projectiles` добавить:
```
[node name="Player" parent="." instance=ExtResource("5_player")]
```

- [ ] **Step 4: Собрать, прогнать headless, поиграть**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 120 2>&1 | tail -20
```
Expected: без ошибок. С окном: капсула двигается WASD или стрелками в пределах коридора, кренится при боковом движении.

- [ ] **Step 5: Commit**

```bash
git add game/scripts/Player.cs game/scenes/Player.tscn game/scenes/Main.tscn
git commit -m "feat: корабль игрока с движением и креном"
```

---

### Task 7: Пули игрока разрушают астероиды

**Files:**
- Create: `game/scripts/Bullet.cs`, `game/scenes/PlayerBullet.tscn`
- Modify: `game/scripts/Player.cs`, `game/scenes/Player.tscn`

**Interfaces:**
- Consumes: `IDamageable`, `Player.TakeHit`.
- Produces:
  ```csharp
  public partial class Bullet : Area3D {
      [Export] public Vector3 Direction; [Export] public float Speed; [Export] public int Damage; [Export] public float Lifetime;
  }
  ```
  `PlayerBullet.tscn`: слой 2, маска 20 (enemy | asteroid). Сцена `EnemyBullet.tscn` на этом же скрипте появится в Task 10.

- [ ] **Step 1: Создать `game/scripts/Bullet.cs`**

```csharp
using Godot;

namespace SpaceRail.Game;

/// <summary>Снаряд. Летит по прямой, живёт ограниченное время, бьёт первое, что задел.</summary>
public partial class Bullet : Area3D
{
    [Export] public Vector3 Direction { get; set; } = Vector3.Forward;
    [Export] public float Speed { get; set; } = 60f;
    [Export] public int Damage { get; set; } = 1;
    [Export] public float Lifetime { get; set; } = 2f;

    private bool _spent;

    public override void _Ready()
    {
        AreaEntered += OnAreaEntered;
        BodyEntered += OnBodyEntered;
    }

    public override void _Process(double delta)
    {
        var dt = (float)delta;
        Position += Direction * Speed * dt;
        Lifetime -= dt;
        if (Lifetime <= 0f) QueueFree();
    }

    private void OnAreaEntered(Area3D area)
    {
        if (_spent || area is not IDamageable target) return;
        _spent = true;
        target.TakeHit(Damage);
        QueueFree();
    }

    private void OnBodyEntered(Node3D body)
    {
        if (_spent || body is not Player player) return;
        _spent = true;
        player.TakeHit(Damage);
        QueueFree();
    }
}
```

- [ ] **Step 2: Создать `game/scenes/PlayerBullet.tscn`**

```
[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Bullet.cs" id="1_bullet"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_bullet"]
radius = 0.1
height = 1.0

[sub_resource type="StandardMaterial3D" id="Mat_bullet"]
albedo_color = Color(1, 0.9, 0.3, 1)
emission_enabled = true
emission = Color(1, 0.9, 0.3, 1)
emission_energy_multiplier = 2.0

[sub_resource type="SphereShape3D" id="Shape_bullet"]
radius = 0.25

[node name="PlayerBullet" type="Area3D"]
collision_layer = 2
collision_mask = 20
monitorable = false
script = ExtResource("1_bullet")
Direction = Vector3(0, 0, -1)
Speed = 60.0

[node name="Mesh" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0, 1, 0, -1, 0, 0, 0, 0)
mesh = SubResource("CapsuleMesh_bullet")
surface_material_override/0 = SubResource("Mat_bullet")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("Shape_bullet")
```

- [ ] **Step 3: Добавить стрельбу в `game/scripts/Player.cs`**

Добавить поля после `_model`:
```csharp
    private Node _projectiles = null!;
    private Marker3D _muzzleLeft = null!;
    private Marker3D _muzzleRight = null!;
    private float _cooldown;
```

В `_Ready` после `_model = ...` добавить:
```csharp
        _projectiles = GetNode("../Projectiles");
        _muzzleLeft = GetNode<Marker3D>("MuzzleLeft");
        _muzzleRight = GetNode<Marker3D>("MuzzleRight");
```

В конец `_Process` (после установки крена) добавить:
```csharp
        _cooldown -= dt;
        if (Input.IsActionPressed("fire") && _cooldown <= 0f)
        {
            Fire();
            _cooldown = FireCooldown;
        }
```

Добавить метод перед `TakeHit`:
```csharp
    private void Fire()
    {
        if (BulletScene is null) return;
        foreach (var muzzle in new[] { _muzzleLeft, _muzzleRight })
        {
            var bullet = BulletScene.Instantiate<Bullet>();
            _projectiles.AddChild(bullet);
            bullet.GlobalPosition = muzzle.GlobalPosition;
        }
    }
```

- [ ] **Step 4: Привязать сцену пули в `game/scenes/Player.tscn`**

В заголовке `load_steps=5` заменить на `load_steps=6`. После строки `1_player` добавить:
```
[ext_resource type="PackedScene" path="res://scenes/PlayerBullet.tscn" id="2_bullet"]
```
В узле `Player` после `script = ExtResource("1_player")` добавить:
```
BulletScene = ExtResource("2_bullet")
```

- [ ] **Step 5: Собрать, прогнать headless, поиграть**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 120 2>&1 | tail -20
```
Expected: без ошибок. С окном: пробел выпускает две жёлтые пули, астероид исчезает с третьего попадания.

- [ ] **Step 6: Commit**

```bash
git add game/scripts/Bullet.cs game/scenes/PlayerBullet.tscn game/scripts/Player.cs game/scenes/Player.tscn
git commit -m "feat: стрельба игрока и разрушение астероидов"
```

---

### Task 8: Урон игроку, HUD, смерть и рестарт

**Files:**
- Create: `game/scripts/Hud.cs`, `game/scenes/Hud.tscn`
- Modify: `game/scripts/Asteroid.cs`, `game/scenes/Main.tscn`

**Interfaces:**
- Consumes: `GameState.Changed`, `Player.TakeHit`.
- Produces: `Hud : CanvasLayer` с узлами `HpLabel`, `ScoreLabel`, `GameOver/VBox/FinalScore`, `GameOver/VBox/RestartButton`.

- [ ] **Step 1: Астероид бьёт игрока при касании — `game/scripts/Asteroid.cs`**

В `_Ready` первой строкой добавить:
```csharp
        BodyEntered += OnBodyEntered;
```
Добавить метод перед `Rand`:
```csharp
    private void OnBodyEntered(Node3D body)
    {
        if (body is not Player player) return;
        player.TakeHit(1);
        QueueFree();
    }
```

- [ ] **Step 2: Создать `game/scripts/Hud.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>HP, счёт и экран смерти. Работает на паузе, чтобы кнопка рестарта жила.</summary>
public partial class Hud : CanvasLayer
{
    private GameState _state = null!;
    private Label _hp = null!;
    private Label _score = null!;
    private Label _finalScore = null!;
    private Control _gameOver = null!;
    private Button _restart = null!;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _hp = GetNode<Label>("HpLabel");
        _score = GetNode<Label>("ScoreLabel");
        _gameOver = GetNode<Control>("GameOver");
        _finalScore = GetNode<Label>("GameOver/VBox/FinalScore");
        _restart = GetNode<Button>("GameOver/VBox/RestartButton");

        _state.Changed += Refresh;
        _restart.Pressed += OnRestartPressed;
        Refresh();
    }

    public override void _ExitTree()
    {
        _state.Changed -= Refresh;
        _restart.Pressed -= OnRestartPressed;
    }

    private void Refresh()
    {
        _hp.Text = $"HP {_state.Hp}";
        _score.Text = _state.Score.ToString();
        _finalScore.Text = $"Счёт: {_state.Score}";
        _gameOver.Visible = !_state.IsAlive;
    }

    private void OnRestartPressed()
    {
        _state.Restart();
        GetTree().Paused = false;
        GetTree().ReloadCurrentScene();
    }
}
```

- [ ] **Step 3: Создать `game/scenes/Hud.tscn`**

```
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/Hud.cs" id="1_hud"]

[node name="Hud" type="CanvasLayer"]
process_mode = 3
script = ExtResource("1_hud")

[node name="HpLabel" type="Label" parent="."]
offset_left = 16.0
offset_top = 16.0
offset_right = 200.0
offset_bottom = 48.0
theme_override_font_sizes/font_size = 24
text = "HP 3"

[node name="ScoreLabel" type="Label" parent="."]
anchors_preset = 1
anchor_left = 1.0
anchor_right = 1.0
offset_left = -216.0
offset_top = 16.0
offset_right = -16.0
offset_bottom = 48.0
grow_horizontal = 0
theme_override_font_sizes/font_size = 24
text = "0"
horizontal_alignment = 2

[node name="GameOver" type="CenterContainer" parent="."]
visible = false
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="VBox" type="VBoxContainer" parent="GameOver"]
layout_mode = 2
theme_override_constants/separation = 16

[node name="Title" type="Label" parent="GameOver/VBox"]
layout_mode = 2
theme_override_font_sizes/font_size = 48
text = "Корабль уничтожен"
horizontal_alignment = 1

[node name="FinalScore" type="Label" parent="GameOver/VBox"]
layout_mode = 2
theme_override_font_sizes/font_size = 28
text = "Счёт: 0"
horizontal_alignment = 1

[node name="RestartButton" type="Button" parent="GameOver/VBox"]
layout_mode = 2
theme_override_font_sizes/font_size = 28
text = "Ещё раз"
```

`process_mode = 3` это `PROCESS_MODE_ALWAYS`: HUD обрабатывает ввод, пока дерево на паузе.

- [ ] **Step 4: Добавить HUD в `game/scenes/Main.tscn`**

В заголовке `load_steps=7` заменить на `load_steps=8`. После строки `5_player` добавить:
```
[ext_resource type="PackedScene" path="res://scenes/Hud.tscn" id="6_hud"]
```
В конец файла добавить:
```
[node name="Hud" parent="." instance=ExtResource("6_hud")]
```

- [ ] **Step 5: Собрать, прогнать headless, поиграть**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 120 2>&1 | tail -20
```
Expected: без ошибок. С окном: HP и счёт видны, три столкновения с астероидами останавливают игру и показывают экран с кнопкой «Ещё раз», кнопка начинает игру заново с HP 3 и счётом 0.

- [ ] **Step 6: Commit**

```bash
git add game/scripts/Asteroid.cs game/scripts/Hud.cs game/scenes/Hud.tscn game/scenes/Main.tscn
git commit -m "feat: урон игроку, HUD, экран смерти и рестарт"
```

---

### Task 9: Враг-дрон преследует игрока

**Files:**
- Create: `game/scripts/Enemy.cs`, `game/scripts/EnemyDrone.cs`, `game/scenes/EnemyDrone.tscn`
- Modify: `game/scenes/Main.tscn`

**Interfaces:**
- Consumes: `IDamageable`, `Player.TakeHit`, `Spawner.DroneScene`.
- Produces:
  ```csharp
  public abstract partial class Enemy : Area3D, IDamageable {
      [Export] public int Hp; [Export] public int ScoreValue;
      protected GameState State { get; }
      protected Player? FindPlayer();   // первый узел группы "player"
      protected void Die();              // очки и QueueFree
  }
  public partial class EnemyDrone : Enemy { [Export] public float SeekSpeed; [Export] public float ForwardSpeed; }
  ```

- [ ] **Step 1: Создать `game/scripts/Enemy.cs`**

```csharp
using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Общее для врагов: HP, очки, столкновение с игроком.</summary>
public abstract partial class Enemy : Area3D, IDamageable
{
    [Export] public int Hp { get; set; } = 1;
    [Export] public int ScoreValue { get; set; } = 25;

    protected GameState State { get; private set; } = null!;

    public override void _Ready()
    {
        State = Session.Of(this).State;
        BodyEntered += OnBodyEntered;
    }

    public void TakeHit(int damage)
    {
        Hp -= damage;
        if (Hp <= 0) Die();
    }

    protected Player? FindPlayer() => GetTree().GetFirstNodeInGroup("player") as Player;

    protected void Die()
    {
        State.AddScore(ScoreValue);
        QueueFree();
    }

    private void OnBodyEntered(Node3D body)
    {
        if (body is not Player player) return;
        player.TakeHit(1);
        QueueFree();
    }
}
```

- [ ] **Step 2: Создать `game/scripts/EnemyDrone.cs`**

```csharp
using Godot;

namespace SpaceRail.Game;

/// <summary>Летит на игрока, подстраиваясь по X и Y. Один удар и он мёртв.</summary>
public partial class EnemyDrone : Enemy
{
    [Export] public float SeekSpeed { get; set; } = 5f;
    [Export] public float ForwardSpeed { get; set; } = 12f;

    public override void _Process(double delta)
    {
        var dt = (float)delta;
        var target = FindPlayer();
        var p = Position;
        if (target is not null)
        {
            p.X = Mathf.MoveToward(p.X, target.Position.X, SeekSpeed * dt);
            p.Y = Mathf.MoveToward(p.Y, target.Position.Y, SeekSpeed * dt);
        }
        p.Z += ForwardSpeed * dt;
        Position = p;
    }
}
```

- [ ] **Step 3: Создать `game/scenes/EnemyDrone.tscn`**

```
[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/EnemyDrone.cs" id="1_drone"]

[sub_resource type="BoxMesh" id="BoxMesh_drone"]
size = Vector3(1.6, 0.6, 1.6)

[sub_resource type="StandardMaterial3D" id="Mat_drone"]
albedo_color = Color(0.9, 0.25, 0.2, 1)

[sub_resource type="BoxShape3D" id="Shape_drone"]
size = Vector3(1.6, 0.6, 1.6)

[node name="EnemyDrone" type="Area3D"]
collision_layer = 4
collision_mask = 1
script = ExtResource("1_drone")
Hp = 1
ScoreValue = 25

[node name="Placeholder" type="MeshInstance3D" parent="."]
mesh = SubResource("BoxMesh_drone")
surface_material_override/0 = SubResource("Mat_drone")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("Shape_drone")
```

- [ ] **Step 4: Подключить дрона к спавнеру в `game/scenes/Main.tscn`**

В заголовке `load_steps=8` заменить на `load_steps=9`. После строки `6_hud` добавить:
```
[ext_resource type="PackedScene" path="res://scenes/EnemyDrone.tscn" id="7_drone"]
```
В узле `Spawner` после `AsteroidScene = ...` добавить:
```
DroneScene = ExtResource("7_drone")
```

- [ ] **Step 5: Собрать, прогнать headless, поиграть**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 300 2>&1 | tail -20
```
Expected: без ошибок. С окном: красные плоские кубы сдвигаются к кораблю и умирают с одного попадания, давая 25 очков.

- [ ] **Step 6: Commit**

```bash
git add game/scripts/Enemy.cs game/scripts/EnemyDrone.cs game/scenes/EnemyDrone.tscn game/scenes/Main.tscn
git commit -m "feat: враг-дрон преследует игрока"
```

---

### Task 10: Враг-стрелок держит дистанцию и стреляет

**Files:**
- Create: `game/scripts/EnemyShooter.cs`, `game/scenes/EnemyShooter.tscn`, `game/scenes/EnemyBullet.tscn`
- Modify: `game/scenes/Main.tscn`

**Interfaces:**
- Consumes: `Enemy`, `Bullet`, `Spawner.ShooterScene`.
- Produces:
  ```csharp
  public partial class EnemyShooter : Enemy {
      [Export] public float HoldZ; [Export] public float ApproachSpeed; [Export] public float HoldSeconds;
      [Export] public float FireInterval; [Export] public float BulletSpeed; [Export] public PackedScene? BulletScene;
  }
  ```
  `EnemyBullet.tscn`: слой 8, маска 1 (player).

- [ ] **Step 1: Создать `game/scenes/EnemyBullet.tscn`**

```
[gd_scene load_steps=5 format=3]

[ext_resource type="Script" path="res://scripts/Bullet.cs" id="1_bullet"]

[sub_resource type="SphereMesh" id="SphereMesh_ebullet"]
radius = 0.25
height = 0.5

[sub_resource type="StandardMaterial3D" id="Mat_ebullet"]
albedo_color = Color(1, 0.35, 0.2, 1)
emission_enabled = true
emission = Color(1, 0.35, 0.2, 1)
emission_energy_multiplier = 2.0

[sub_resource type="SphereShape3D" id="Shape_ebullet"]
radius = 0.3

[node name="EnemyBullet" type="Area3D"]
collision_layer = 8
collision_mask = 1
monitorable = false
script = ExtResource("1_bullet")
Direction = Vector3(0, 0, 1)
Speed = 30.0
Lifetime = 4.0

[node name="Mesh" type="MeshInstance3D" parent="."]
mesh = SubResource("SphereMesh_ebullet")
surface_material_override/0 = SubResource("Mat_ebullet")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("Shape_ebullet")
```

- [ ] **Step 2: Создать `game/scripts/EnemyShooter.cs`**

```csharp
using Godot;

namespace SpaceRail.Game;

/// <summary>
/// Подлетает до HoldZ, держит дистанцию и стреляет в игрока, потом отпускает
/// позицию и уносится мимо. Пока держит дистанцию, гасит дрейф мира.
/// </summary>
public partial class EnemyShooter : Enemy
{
    [Export] public float HoldZ { get; set; } = -35f;
    [Export] public float ApproachSpeed { get; set; } = 25f;
    [Export] public float HoldSeconds { get; set; } = 6f;
    [Export] public float FireInterval { get; set; } = 1.4f;
    [Export] public float BulletSpeed { get; set; } = 30f;
    [Export] public PackedScene? BulletScene { get; set; }

    private float _holdLeft;
    private float _fireTimer;
    private bool _released;

    public override void _Ready()
    {
        base._Ready();
        _holdLeft = HoldSeconds;
        _fireTimer = FireInterval;
    }

    public override void _Process(double delta)
    {
        if (_released) return;
        var dt = (float)delta;

        // World каждый кадр добавляет State.Speed * dt по Z. Пока держим дистанцию, вычитаем это обратно.
        var p = Position;
        p.Z -= State.Speed * dt;
        p.Z = Mathf.MoveToward(p.Z, HoldZ, ApproachSpeed * dt);
        Position = p;

        if (Mathf.Abs(p.Z - HoldZ) > 0.01f) return;

        _holdLeft -= dt;
        if (_holdLeft <= 0f)
        {
            _released = true;
            return;
        }

        _fireTimer -= dt;
        if (_fireTimer <= 0f)
        {
            Fire();
            _fireTimer = FireInterval;
        }
    }

    private void Fire()
    {
        var player = FindPlayer();
        if (BulletScene is null || player is null) return;

        var bullet = BulletScene.Instantiate<Bullet>();
        bullet.Direction = (player.GlobalPosition - GlobalPosition).Normalized();
        bullet.Speed = BulletSpeed;
        GetTree().CurrentScene.GetNode("Projectiles").AddChild(bullet);
        bullet.GlobalPosition = GlobalPosition;
    }
}
```

- [ ] **Step 3: Создать `game/scenes/EnemyShooter.tscn`**

```
[gd_scene load_steps=6 format=3]

[ext_resource type="Script" path="res://scripts/EnemyShooter.cs" id="1_shooter"]
[ext_resource type="PackedScene" path="res://scenes/EnemyBullet.tscn" id="2_ebullet"]

[sub_resource type="PrismMesh" id="PrismMesh_shooter"]
size = Vector3(2, 1, 2)

[sub_resource type="StandardMaterial3D" id="Mat_shooter"]
albedo_color = Color(0.7, 0.3, 0.9, 1)

[sub_resource type="BoxShape3D" id="Shape_shooter"]
size = Vector3(2, 1, 2)

[node name="EnemyShooter" type="Area3D"]
collision_layer = 4
collision_mask = 1
script = ExtResource("1_shooter")
Hp = 3
ScoreValue = 60
BulletScene = ExtResource("2_ebullet")

[node name="Placeholder" type="MeshInstance3D" parent="."]
mesh = SubResource("PrismMesh_shooter")
surface_material_override/0 = SubResource("Mat_shooter")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("Shape_shooter")
```

- [ ] **Step 4: Подключить стрелка к спавнеру в `game/scenes/Main.tscn`**

В заголовке `load_steps=9` заменить на `load_steps=10`. После строки `7_drone` добавить:
```
[ext_resource type="PackedScene" path="res://scenes/EnemyShooter.tscn" id="8_shooter"]
```
В узле `Spawner` после `DroneScene = ...` добавить:
```
ShooterScene = ExtResource("8_shooter")
```

- [ ] **Step 5: Собрать, прогнать headless, поиграть**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 600 2>&1 | tail -20
```
Expected: без ошибок. С окном: фиолетовая призма подлетает, зависает впереди, стреляет красными шарами в сторону корабля, через 6 секунд улетает мимо. Умирает с трёх попаданий, 60 очков. Попадание красного шара снимает 1 HP.

- [ ] **Step 6: Commit**

```bash
git add game/scripts/EnemyShooter.cs game/scenes/EnemyShooter.tscn game/scenes/EnemyBullet.tscn game/scenes/Main.tscn
git commit -m "feat: враг-стрелок держит дистанцию и стреляет"
```

---

### Task 11: ModelSlot: подмена заглушек на .glb, когда они появятся

**Files:**
- Create: `game/scripts/ModelSlot.cs`, `game/assets/models/.gitkeep`
- Modify: `game/scenes/Player.tscn`, `game/scenes/Asteroid.tscn`, `game/scenes/EnemyDrone.tscn`, `game/scenes/EnemyShooter.tscn`

**Interfaces:**
- Produces:
  ```csharp
  public partial class ModelSlot : Node3D { [Export] public string ModelPath; }
  ```
  Контракт: дочерний узел `Placeholder` скрывается, если по `ModelPath` есть ресурс. Иначе предупреждение в лог, заглушка остаётся. Это точка входа для этапа 3 (Blender).

- [ ] **Step 1: Создать `game/scripts/ModelSlot.cs`**

```csharp
using Godot;

namespace SpaceRail.Game;

/// <summary>
/// Место под модель из Blender. Если .glb есть, подставляет его и скрывает заглушку.
/// Если нет, оставляет заглушку и пишет предупреждение: greybox остаётся играбельным.
/// </summary>
public partial class ModelSlot : Node3D
{
    [Export] public string ModelPath { get; set; } = "";

    public override void _Ready()
    {
        if (string.IsNullOrEmpty(ModelPath)) return;

        var placeholder = GetNodeOrNull<Node3D>("Placeholder");
        if (!ResourceLoader.Exists(ModelPath))
        {
            GD.PushWarning($"ModelSlot: {ModelPath} не найден, остаётся заглушка");
            return;
        }

        var scene = ResourceLoader.Load<PackedScene>(ModelPath);
        AddChild(scene.Instantiate<Node3D>());
        if (placeholder is not null) placeholder.Visible = false;
    }
}
```

- [ ] **Step 2: Повесить ModelSlot на игрока — `game/scenes/Player.tscn`**

В заголовке `load_steps=6` заменить на `load_steps=7`. После строки `2_bullet` добавить:
```
[ext_resource type="Script" path="res://scripts/ModelSlot.cs" id="3_slot"]
```
Узел `Model` заменить на:
```
[node name="Model" type="Node3D" parent="."]
script = ExtResource("3_slot")
ModelPath = "res://assets/models/ship.glb"
```

- [ ] **Step 3: Повесить ModelSlot на астероид и врагов**

В каждой из трёх сцен `Asteroid.tscn`, `EnemyDrone.tscn`, `EnemyShooter.tscn`:

1. Увеличить `load_steps` на 1.
2. После первой строки `ext_resource` добавить строку (id уникален в пределах файла):
   ```
   [ext_resource type="Script" path="res://scripts/ModelSlot.cs" id="9_slot"]
   ```
3. Перед узлом `Placeholder` вставить узел `Model`, а у `Placeholder` сменить `parent="."` на `parent="Model"`:
   ```
   [node name="Model" type="Node3D" parent="."]
   script = ExtResource("9_slot")
   ModelPath = "res://assets/models/asteroid.glb"

   [node name="Placeholder" type="MeshInstance3D" parent="Model"]
   ```
   Пути моделей: `asteroid.glb`, `enemy_drone.glb`, `enemy_shooter.glb`.

Создать `game/assets/models/.gitkeep` пустым файлом.

- [ ] **Step 4: Собрать, прогнать headless, убедиться в предупреждениях**

```bash
dotnet build game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 300 2>&1 | tail -30
```
Expected: сборка без ошибок. В выводе `WARNING: ModelSlot: res://assets/models/ship.glb не найден` и аналогичные для остальных, но без `ERROR`. С окном: игра выглядит и играется так же, как после Task 10.

- [ ] **Step 5: Commit**

```bash
git add game/scripts/ModelSlot.cs game/assets/models/.gitkeep game/scenes/Player.tscn game/scenes/Asteroid.tscn game/scenes/EnemyDrone.tscn game/scenes/EnemyShooter.tscn
git commit -m "feat: ModelSlot подменяет заглушки на .glb, когда они появятся"
```

---

### Task 12: Плейтест greybox и фиксация результата

**Files:**
- Create: `docs/playtests/2026-09-XX-greybox.md` (дата фактического плейтеста)

**Interfaces:**
- Consumes: всё выше.
- Produces: решение владельца CONTINUE или ADJUST для перехода к этапу 3 (Blender).

- [ ] **Step 1: Финальная проверка всего**

```bash
dotnet test game/SpaceRail.sln 2>&1 | tail -3
"$GODOT" --headless --path game --quit-after 600 2>&1 | tail -20
git status --short
```
Expected: 9 тестов пройдены, headless без ошибок, рабочая копия чистая.

- [ ] **Step 2: Запустить с окном и передать владельцу**

```bash
"/c/gamedev/Godot_v4.7.1-stable_mono_win64/Godot_v4.7.1-stable_mono_win64.exe" --path game
```

Вопросы владельцу после 2–3 минут игры (по одному, из спеки раздел 6):
1. Ощущается ли скорость полёта?
2. Успеваешь ли уворачиваться от астероидов и пуль стрелка при HP 3?
3. Что раздражает сильнее всего?

- [ ] **Step 3: Записать ответы в `docs/playtests/2026-09-XX-greybox.md`**

```markdown
# Плейтест greybox

Дата: (заполнить). Сборка: коммит (заполнить `git rev-parse --short HEAD`).

## Ответы владельца
1. Скорость: (ответ)
2. Уворачивание: (ответ)
3. Раздражает: (ответ)

## Решение
CONTINUE / ADJUST. Если ADJUST: какие параметры менять (MoveSpeed, BaseSpeed,
интервал спавна, HP) и на сколько.

## Следующий этап
План этапа 3: подключение Blender MCP и модель корабля.
```

- [ ] **Step 4: Commit**

```bash
git add docs/playtests
git commit -m "docs: результаты плейтеста greybox"
git push
```

---

## Самопроверка плана

**Покрытие спеки.** Раздел 3 (структура): Task 1, 2, 4. Раздел 4: GameState и Session (Task 2, 4), Player (6, 7), Bullet (7, 10), EnemyDrone и EnemyShooter (9, 10), Asteroid (5, 8), Spawner и SpawnPolicy (3, 5), World (5), HUD (8), управление (4), отказоустойчивость через заглушки (11). Раздел 6, автотесты: Task 2, 3. Раздел 7, этапы 1 и 2: закрыты Task 1–12. Проверка арта и этапы 3–6 вне этого плана, это ожидаемо.

**Согласованность типов.** `Session.Of(node).State` используется одинаково во всех нодах. `IDamageable.TakeHit(int)` реализуют `Asteroid` и `Enemy`, вызывает `Bullet`. `Player.TakeHit(int)` вызывают `Bullet`, `Asteroid`, `Enemy`. `Spawner` ждёт `AsteroidScene`, `DroneScene`, `ShooterScene`, сцены подключаются в Task 5, 9, 10. Узел `Projectiles` ищется игроком как `../Projectiles`, а стрелком через `GetTree().CurrentScene.GetNode("Projectiles")`; оба пути ведут к одному узлу сцены `Main`.
