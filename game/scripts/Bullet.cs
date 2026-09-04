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
