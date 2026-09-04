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
