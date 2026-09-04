using Godot;

namespace SpaceRail.Game;

/// <summary>
/// Место под модель из Blender. Если .glb есть, подставляет его и скрывает заглушку.
/// Если нет, оставляет заглушку и пишет предупреждение: greybox остаётся играбельным.
/// </summary>
public partial class ModelSlot : Node3D
{
    private static readonly HashSet<string> Reported = new();

    /// <summary>Один путь к модели. Используется, если ModelPaths пуст.</summary>
    [Export] public string ModelPath { get; set; } = "";

    /// <summary>Несколько вариантов модели: при появлении в сцене берётся случайный.</summary>
    [Export] public string[] ModelPaths { get; set; } = System.Array.Empty<string>();

    public override void _Ready()
    {
        var path = ModelPaths.Length > 0 ? ModelPaths[Random.Shared.Next(ModelPaths.Length)] : ModelPath;
        if (string.IsNullOrEmpty(path)) return;

        var placeholder = GetNodeOrNull<Node3D>("Placeholder");
        if (!ResourceLoader.Exists(path))
        {
            if (Reported.Add(path))
                GD.PushWarning($"ModelSlot: {path} не найден, остаётся заглушка");
            return;
        }

        var scene = ResourceLoader.Load<PackedScene>(path);
        if (scene is null)
        {
            GD.PushWarning($"ModelSlot: {path} не удалось загрузить как PackedScene, остаётся заглушка");
            return;
        }

        AddChild(scene.Instantiate<Node3D>());
        if (placeholder is not null) placeholder.Visible = false;
    }
}
