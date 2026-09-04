using SpaceRail.Core;
using Xunit;

namespace SpaceRail.Tests;

public class GameStateTests
{
    private static GameState NewState() => new(new GameConfig(MaxHp: 3, BaseSpeed: 20f, MaxSpeed: 45f, Acceleration: 0.5f));

    [Fact]
    public void StartsWithMaxHpZeroScoreAndBaseSpeed()
    {
        var s = NewState();
        Assert.Equal(3, s.Hp);
        Assert.Equal(0, s.Score);
        Assert.Equal(20f, s.Speed);
        Assert.True(s.IsAlive);
    }

    [Fact]
    public void TakeDamageReducesHpAndClampsAtZero()
    {
        var s = NewState();
        s.TakeDamage(2);
        Assert.Equal(1, s.Hp);
        s.TakeDamage(5);
        Assert.Equal(0, s.Hp);
        Assert.False(s.IsAlive);
    }

    [Fact]
    public void AddScoreAccumulatesWhileAliveAndIgnoredWhenDead()
    {
        var s = NewState();
        s.AddScore(10);
        s.AddScore(5);
        Assert.Equal(15, s.Score);
        s.TakeDamage(3);
        s.AddScore(100);
        Assert.Equal(15, s.Score);
    }

    [Fact]
    public void TickRaisesSpeedUpToMaxAndStopsWhenDead()
    {
        var s = NewState();
        s.Tick(10.0);
        Assert.Equal(10f, s.ElapsedSeconds, 3);
        Assert.Equal(25f, s.Speed, 3);
        s.Tick(1000.0);
        Assert.Equal(45f, s.Speed, 3);
        s.TakeDamage(3);
        var elapsedAtDeath = s.ElapsedSeconds;
        s.Tick(5.0);
        Assert.Equal(elapsedAtDeath, s.ElapsedSeconds);
    }

    [Fact]
    public void RestartResetsEverything()
    {
        var s = NewState();
        s.AddScore(7);
        s.Tick(30.0);
        s.TakeDamage(3);
        s.Restart();
        Assert.Equal(3, s.Hp);
        Assert.Equal(0, s.Score);
        Assert.Equal(0f, s.ElapsedSeconds);
        Assert.Equal(20f, s.Speed);
        Assert.True(s.IsAlive);
    }

    [Fact]
    public void ChangedFiresOnDamageScoreAndRestartButNotOnTick()
    {
        var s = NewState();
        var count = 0;
        s.Changed += () => count++;
        s.Tick(1.0);
        Assert.Equal(0, count);
        s.TakeDamage(1);
        s.AddScore(1);
        s.Restart();
        Assert.Equal(3, count);
    }
}
