using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Корневая сцена: тикает состояние и ставит игру на паузу при смерти.</summary>
public partial class Main : Node3D
{
    private GameState _state = null!;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _state.Changed += OnStateChanged;
    }

    public override void _ExitTree() => _state.Changed -= OnStateChanged;

    public override void _Process(double delta) => _state.Tick(delta);

    private void OnStateChanged()
    {
        if (!_state.IsAlive && !GetTree().Paused)
            GetTree().Paused = true;
    }
}
