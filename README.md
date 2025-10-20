# grid-economy

格子状のマス目で社会をシミュレートするための枠組み

## 概要 (Overview)

2次元空間の各マス目についてイベントを実行し、更新する時間を持つような世界をシミュレートするシステムです。

A simulation system for a 2D grid-based world where each cell can execute events and update over time.

## 機能 (Features)

### エージェント (Agents)

- **有機エージェント (Organic Agents)**:
  - 近くの財Xを消費し財Yを生み出す
  - 財Xがないと死ぬ
  - 十分な財Xがあれば子エージェントを生み出す
  - 新たに生まれるときは親エージェントの形質を引き継ぐが確率的に変異する
  - 自身の生存を優位にするために無機エージェントを生成することがある

- **無機エージェント (Inorganic Agents)**:
  - 近くの財Xを消費し財Yを生み出す
  - 近くに財Xがなければ変換を停止するが、死なない
  - 自己複製は行わない
  - 親エージェントの形質によらずランダムな変換機構を持つ

### 財 (Goods)

- 複数の種類が存在する
- 新しいエージェントが発生するときに確率的に新種の財が発生しうる
- 財ごとの特徴を後付けできる実装

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### 基本的な例 (Basic Example)

```python
from grid_economy import Good, OrganicAgent, InorganicAgent, World

# 財を作成
food = Good("food", {"nutritional": True})
energy = Good("energy")

# 世界を作成
world = World(width=20, height=20)

# 有機エージェントを追加
agent = OrganicAgent(
    position=(10, 10),
    consumes=food,
    produces=energy,
    consumption_rate=1.0,
    production_rate=1.5,
    search_radius=2
)
world.add_agent(agent)

# 財を配置
world.add_good((10, 10), food, 100.0)

# シミュレーションを実行
for _ in range(100):
    world.step()

# 統計を取得
stats = world.get_statistics()
print(f"Agents: {stats['total_agents']}")
print(f"Good types: {stats['good_types']}")
```

### デモの実行 (Running the Demo)

```bash
python example.py
```

## テスト (Testing)

```bash
pytest tests/
```

## アーキテクチャ (Architecture)

### クラス構成 (Class Structure)

- **Good**: 財の種類を表すクラス
  - 一意のID
  - 特徴を追加可能な辞書

- **Agent**: エージェントの基底クラス
  - 位置
  - 消費する財と生産する財
  - 変換レート

- **OrganicAgent**: 有機エージェント
  - 死と再生産のメカニズム
  - 形質の継承と変異
  - 無機エージェントの生成

- **InorganicAgent**: 無機エージェント
  - 死なない
  - 再生産しない
  - ランダムな変換機構

- **World**: 2Dグリッド世界
  - エージェントと財の管理
  - 時間ステップの実行
  - 統計情報の提供

## ライセンス (License)

MIT License
