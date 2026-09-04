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
