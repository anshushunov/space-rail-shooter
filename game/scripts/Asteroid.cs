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
        BodyEntered += OnBodyEntered;
        _state = Session.Of(this).State;
        var rng = new Random();
        _spin = new Vector3(Rand(rng), Rand(rng), Rand(rng));
    }

    public override void _Process(double delta) => Rotation += _spin * (float)delta;

    public void TakeHit(int damage)
    {
        if (Hp <= 0) return;
        Hp -= damage;
        if (Hp > 0) return;
        _state.AddScore(ScoreValue);
        QueueFree();
    }

    private void OnBodyEntered(Node3D body)
    {
        if (Hp <= 0) return;
        if (body is not Player player) return;
        player.TakeHit(1);
        QueueFree();
    }

    private static float Rand(Random rng) => (float)(rng.NextDouble() * 2 - 1);
}
