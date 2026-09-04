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
