namespace SpaceRail.Game;

/// <summary>Всё, во что можно попасть пулей.</summary>
public interface IDamageable
{
    void TakeHit(int damage);
}
