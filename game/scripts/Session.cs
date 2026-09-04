using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>Autoload. Держит GameState, который переживает перезагрузку сцены.</summary>
public partial class Session : Node
{
    public GameState State { get; } = new(new GameConfig());

    public static Session Of(Node node) => node.GetNode<Session>("/root/Session");
}
