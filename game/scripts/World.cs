using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Двигает всех детей к игроку по +Z и удаляет тех, кто улетел за спину.</summary>
public partial class World : Node3D
{
    [Export] public float DespawnZ { get; set; } = 10f;

    private GameState _state = null!;

    public override void _Ready() => _state = Session.Of(this).State;

    public override void _Process(double delta)
    {
        var dz = _state.Speed * (float)delta;
        foreach (var child in GetChildren())
        {
            if (child is not Node3D node) continue;
            node.Position += new Vector3(0f, 0f, dz);
            if (node.Position.Z > DespawnZ) node.QueueFree();
        }
    }
}
