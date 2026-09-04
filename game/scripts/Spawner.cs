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
