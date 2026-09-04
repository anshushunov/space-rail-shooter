using Godot;

namespace SpaceRail.Game;

/// <summary>
/// Место под модель из Blender. Если .glb есть, подставляет его и скрывает заглушку.
/// Если нет, оставляет заглушку и пишет предупреждение: greybox остаётся играбельным.
/// </summary>
public partial class ModelSlot : Node3D
{
    private static readonly HashSet<string> Reported = new();

    [Export] public string ModelPath { get; set; } = "";

    public override void _Ready()
    {
        if (string.IsNullOrEmpty(ModelPath)) return;

        var placeholder = GetNodeOrNull<Node3D>("Placeholder");
        if (!ResourceLoader.Exists(ModelPath))
        {
            if (Reported.Add(ModelPath))
                GD.PushWarning($"ModelSlot: {ModelPath} не найден, остаётся заглушка");
            return;
        }

        var scene = ResourceLoader.Load<PackedScene>(ModelPath);
        if (scene is null)
        {
            GD.PushWarning($"ModelSlot: {ModelPath} не удалось загрузить как PackedScene, остаётся заглушка");
            return;
        }

        AddChild(scene.Instantiate<Node3D>());
        if (placeholder is not null) placeholder.Visible = false;
    }
}
