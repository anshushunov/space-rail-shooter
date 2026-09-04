namespace SpaceRail.Core;

/// <summary>Единственное место, где меняются HP, счёт и скорость мира.</summary>
public sealed class GameState
{
    private readonly GameConfig _config;

    public GameState(GameConfig config)
    {
        _config = config;
        Hp = config.MaxHp;
        Speed = config.BaseSpeed;
    }

    public int Hp { get; private set; }
    public int Score { get; private set; }
    public float Speed { get; private set; }
    public float ElapsedSeconds { get; private set; }
    public bool IsAlive => Hp > 0;

    /// <summary>Срабатывает после изменения Hp или Score и после Restart. Tick событие не вызывает.</summary>
    public event Action? Changed;

    public void Tick(double delta)
    {
        if (!IsAlive) return;
        ElapsedSeconds += (float)delta;
        Speed = Math.Min(_config.MaxSpeed, _config.BaseSpeed + _config.Acceleration * ElapsedSeconds);
    }

    public void TakeDamage(int amount)
    {
        if (!IsAlive || amount <= 0) return;
        Hp = Math.Max(0, Hp - amount);
        Changed?.Invoke();
    }

    public void AddScore(int points)
    {
        if (!IsAlive || points <= 0) return;
        Score += points;
        Changed?.Invoke();
    }

    public void Restart()
    {
        Hp = _config.MaxHp;
        Score = 0;
        ElapsedSeconds = 0f;
        Speed = _config.BaseSpeed;
        Changed?.Invoke();
    }
}
