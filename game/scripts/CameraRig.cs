using Godot;

namespace SpaceRail.Game;

/// <summary>
/// Камера сзади и выше корабля. Поворот фиксирован (горизонт стабилен),
/// позиция мягко следует за кораблём на долю его смещения, чтобы он
/// мог дойти до края кадра, но не покинуть его.
/// </summary>
public partial class CameraRig : Camera3D
{
    [Export] public float FollowFactor { get; set; } = 0.35f;
    [Export] public float Smoothing { get; set; } = 6f;

    private Vector3 _basePosition;
    private Player? _player;

    public override void _Ready() => _basePosition = Position;

    public override void _Process(double delta)
    {
        _player ??= GetTree().GetFirstNodeInGroup("player") as Player;
        if (_player is null) return;

        var offset = new Vector3(_player.Position.X, _player.Position.Y, 0f) * FollowFactor;
        var weight = 1f - Mathf.Exp(-Smoothing * (float)delta);
        Position = Position.Lerp(_basePosition + offset, weight);
    }
}
