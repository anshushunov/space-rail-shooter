using Godot;
using SpaceRail.Core;

namespace SpaceRail.Game;

/// <summary>HP, счёт и экран смерти. Работает на паузе, чтобы кнопка рестарта жила.</summary>
public partial class Hud : CanvasLayer
{
    private GameState _state = null!;
    private Label _hp = null!;
    private Label _score = null!;
    private Label _finalScore = null!;
    private Control _gameOver = null!;
    private Button _restart = null!;

    public override void _Ready()
    {
        _state = Session.Of(this).State;
        _hp = GetNode<Label>("HpLabel");
        _score = GetNode<Label>("ScoreLabel");
        _gameOver = GetNode<Control>("GameOver");
        _finalScore = GetNode<Label>("GameOver/VBox/FinalScore");
        _restart = GetNode<Button>("GameOver/VBox/RestartButton");

        _state.Changed += Refresh;
        _restart.Pressed += OnRestartPressed;
        Refresh();
    }

    public override void _ExitTree()
    {
        _state.Changed -= Refresh;
        _restart.Pressed -= OnRestartPressed;
    }

    private void Refresh()
    {
        _hp.Text = $"HP {_state.Hp}";
        _score.Text = _state.Score.ToString();
        _finalScore.Text = $"Счёт: {_state.Score}";
        _gameOver.Visible = !_state.IsAlive;
        if (_gameOver.Visible) _restart.GrabFocus();
    }

    private void OnRestartPressed()
    {
        _state.Restart();
        GetTree().Paused = false;
        GetTree().ReloadCurrentScene();
    }
}
