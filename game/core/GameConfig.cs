namespace SpaceRail.Core;

/// <summary>Константы баланса. Скорости в метрах в секунду.</summary>
public sealed record GameConfig(
    int MaxHp = 3,
    float BaseSpeed = 20f,
    float MaxSpeed = 45f,
    float Acceleration = 0.5f);
