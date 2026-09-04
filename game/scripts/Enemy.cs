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
        if (Hp <= 0) return;
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
        if (Hp <= 0) return;
        if (body is not Player player) return;
        player.TakeHit(1);
        QueueFree();
    }
}
