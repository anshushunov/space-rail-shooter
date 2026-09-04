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
    private Node _projectiles = null!;
    private Marker3D _muzzleLeft = null!;
    private Marker3D _muzzleRight = null!;
    private float _cooldown;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _model = GetNode<Node3D>("Model");
        _projectiles = GetNode("../Projectiles");
        _muzzleLeft = GetNode<Marker3D>("MuzzleLeft");
        _muzzleRight = GetNode<Marker3D>("MuzzleRight");
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

        _cooldown -= dt;
        if (Input.IsActionPressed("fire") && _cooldown <= 0f)
        {
            Fire();
            _cooldown = FireCooldown;
        }
    }

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

    public void TakeHit(int damage) => _state.TakeDamage(damage);
}
