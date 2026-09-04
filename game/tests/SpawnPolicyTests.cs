using SpaceRail.Core;
using Xunit;

namespace SpaceRail.Tests;

public class SpawnPolicyTests
{
    [Fact]
    public void WeightsMatchSpec()
    {
        Assert.Equal(50, SpawnPolicy.Weights[SpawnKind.Asteroid]);
        Assert.Equal(35, SpawnPolicy.Weights[SpawnKind.Drone]);
        Assert.Equal(15, SpawnPolicy.Weights[SpawnKind.Shooter]);
    }

    [Fact]
    public void ChooseFollowsWeightsWithinTolerance()
    {
        var policy = new SpawnPolicy(new Random(42));
        const int n = 20_000;
        var counts = new Dictionary<SpawnKind, int> { [SpawnKind.Asteroid] = 0, [SpawnKind.Drone] = 0, [SpawnKind.Shooter] = 0 };
        for (var i = 0; i < n; i++) counts[policy.Choose()]++;

        Assert.InRange(counts[SpawnKind.Asteroid] / (double)n, 0.47, 0.53);
        Assert.InRange(counts[SpawnKind.Drone] / (double)n, 0.32, 0.38);
        Assert.InRange(counts[SpawnKind.Shooter] / (double)n, 0.12, 0.18);
    }

    [Fact]
    public void IntervalDecaysLinearlyAndClampsAtMinimum()
    {
        var policy = new SpawnPolicy(new Random(1), startInterval: 1.2f, minInterval: 0.4f, decayPerSecond: 0.01f);
        Assert.Equal(1.2f, policy.IntervalAt(0f), 3);
        Assert.Equal(0.9f, policy.IntervalAt(30f), 3);
        Assert.Equal(0.4f, policy.IntervalAt(80f), 3);
        Assert.Equal(0.4f, policy.IntervalAt(10_000f), 3);
    }
}
