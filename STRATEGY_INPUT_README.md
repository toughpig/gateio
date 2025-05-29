# 策略输入模块 (Strategy Input) 使用指南

## 概述

策略输入模块是 Gate.io 自动化交易系统的核心数据收集组件，负责从 Gate.io API 获取、清洗、验证和整理交易策略所需的各类数据。

## 功能特性

### 核心功能
- ✅ **市场数据收集**: 实时行情、订单簿、成交记录、K线数据
- ✅ **账户数据管理**: 余额查询、费率信息、风险评估
- ✅ **订单数据跟踪**: 活跃订单、历史订单、成交记录
- ✅ **配置文件支持**: 灵活的INI配置文件管理
- ✅ **数据清洗验证**: 自动数据质量检查和清洗
- ✅ **错误处理**: 完善的异常处理和日志记录

### 设计优势
- 🔄 **标准化接口**: 统一的数据结构和接口设计
- 🛡️ **数据安全**: 使用高精度Decimal类型避免浮点误差
- 📊 **质量评估**: 内置数据质量评分和可靠性检查
- ⚡ **高性能**: 优化的API调用和数据处理流程
- 🔧 **易于扩展**: 模块化设计，便于添加新功能

## 项目结构

```
gateio/
├── strategy_input.py      # 核心模块文件
├── config.ini            # 配置文件
├── test.py               # 完整测试脚本
├── quick_test.py         # 快速测试脚本
├── example_usage.py      # 使用示例脚本
└── STRATEGY_INPUT_README.md  # 本说明文档
```

## 快速开始

### 1. 环境配置

确保已安装必要的依赖：
```bash
pip install gate-api python-dotenv
```

创建 `.env` 文件配置API密钥：
```env
GATEIO_API_KEY=your_api_key_here
GATEIO_API_SECRET=your_api_secret_here
```

### 2. 配置文件

编辑 `config.ini` 配置您感兴趣的交易对和策略参数：

```ini
[trading]
trading_pairs = ETH_USDT, BTC_USDT, SOL_USDT, BNB_USDT
base_currency = USDT
intervals = 1m, 5m, 15m, 1h, 1d

[strategy]
strategy_name = my_strategy
max_position_size = 0.1
min_order_size = 10
```

### 3. 基本使用

```python
from strategy_input import create_strategy_input_manager_from_config

# 创建管理器
manager = create_strategy_input_manager_from_config()

# 收集策略输入数据
strategy_input = manager.collect_strategy_input(['1m', '5m', '1h'])

# 访问市场数据
for pair, ticker in strategy_input.market_data.tickers.items():
    print(f"{pair}: {ticker.last_price}")

# 访问账户数据
print(f"总权益: {strategy_input.account_data.total_equity} USDT")
```

## 测试验证

### 快速测试
```bash
python quick_test.py
```

### 完整测试
```bash
python test.py
```
选择测试项目：
- 1: 配置文件加载测试
- 2: API连接测试
- 3: 市场数据收集测试
- 4: 账户数据收集测试
- 5: 订单数据收集测试
- 6: 完整策略输入收集测试
- 7: 数据持久化测试
- 8: 性能测试
- 9: 运行所有测试

### 使用示例
```bash
python example_usage.py
```

## 数据结构说明

### 策略输入 (StrategyInput)
```python
@dataclass
class StrategyInput:
    market_data: MarketDataInput      # 市场数据
    account_data: AccountDataInput    # 账户数据
    order_data: OrderDataInput        # 订单数据
    config: ConfigInput               # 配置数据
    external_signals: ExternalSignalInput  # 外部信号
    input_id: str                     # 输入唯一ID
    collection_start_time: datetime   # 收集开始时间
    collection_end_time: datetime     # 收集结束时间
    data_completeness: Dict[str, Decimal]  # 数据完整性评分
```

### 市场数据 (MarketDataInput)
- **tickers**: 实时行情数据
- **orderbooks**: 订单簿数据
- **recent_trades**: 最近成交记录
- **candles**: K线数据（多时间周期）
- **data_reliability**: 数据可靠性评分

### 账户数据 (AccountDataInput)
- **spot_balances**: 现货余额
- **trading_fees**: 交易费率
- **total_equity**: 总权益
- **risk_level**: 风险等级

## 配置说明

### 交易配置 [trading]
- `trading_pairs`: 监控的交易对列表
- `base_currency`: 基础货币（通常为USDT）
- `intervals`: K线时间间隔

### 策略配置 [strategy]
- `strategy_name`: 策略名称
- `max_position_size`: 最大仓位比例
- `min_order_size`: 最小订单金额
- `decision_interval`: 决策间隔（秒）

### 风险管理 [risk_management]
- `max_daily_loss`: 最大日损失
- `max_positions`: 最大同时持仓数
- `max_order_amount`: 单笔最大订单金额

## API 接口说明

### 主要类

#### ConfigManager
配置文件管理器
```python
config_manager = ConfigManager("config.ini")
trading_pairs = config_manager.get_trading_pairs()
strategy_config = config_manager.get_strategy_config()
```

#### StrategyInputManager
策略输入管理器
```python
manager = create_strategy_input_manager_from_config()
strategy_input = manager.collect_strategy_input(['1m', '5m'])
clean_input = manager.clean_and_validate_input(strategy_input)
quality_report = manager.get_data_quality_report(clean_input)
```

### 数据收集器

#### MarketDataCollector
- `get_ticker_data()`: 获取行情数据
- `get_orderbook_data()`: 获取订单簿数据
- `get_recent_trades()`: 获取成交记录
- `get_candle_data()`: 获取K线数据

#### AccountDataCollector
- `get_spot_balances()`: 获取现货余额
- `get_trading_fees()`: 获取交易费率
- `collect_account_data()`: 收集完整账户数据

#### OrderDataCollector
- `get_active_orders()`: 获取活跃订单
- `get_recent_orders()`: 获取历史订单
- `get_trade_history()`: 获取成交历史

## 错误处理

模块内置完善的错误处理机制：

### 网络错误
- 自动重试机制
- API限频处理
- 连接超时处理

### 数据错误
- 无效数据过滤
- 数据类型验证
- 精度转换保护

### 配置错误
- 配置文件验证
- 默认值回退
- 参数类型检查

## 性能优化

### 数据收集优化
- 并行API调用
- 数据缓存机制
- 增量更新支持

### 内存优化
- 数据结构优化
- 及时释放资源
- 批量处理机制

## 最佳实践

### 1. 配置管理
- 使用合理的交易对数量（建议10个以内）
- 根据策略需求选择时间间隔
- 定期检查和更新配置

### 2. 错误处理
- 监控日志输出
- 检查数据质量报告
- 设置合理的重试机制

### 3. 性能优化
- 避免频繁的完整数据收集
- 使用增量更新
- 监控API调用频率

### 4. 数据验证
- 定期运行测试脚本
- 检查数据完整性评分
- 验证数据时效性

## 故障排查

### 常见问题

#### 1. API密钥错误
```
❌ API连接测试失败
```
**解决方案**: 检查 `.env` 文件中的API密钥配置

#### 2. 交易对无效
```
WARNING - Ticker data not found for MATIC_USDT
```
**解决方案**: 在 `config.ini` 中更新交易对列表

#### 3. 数据质量低
```
data_reliability: 0.3
```
**解决方案**: 检查网络连接，重新收集数据

### 调试模式

启用调试模式获取详细日志：
```ini
[environment]
debug_mode = true
log_level = DEBUG
```

## 扩展开发

### 添加新的数据源
1. 继承相应的收集器基类
2. 实现数据获取方法
3. 添加数据验证逻辑
4. 更新配置文件结构

### 自定义数据处理
1. 创建新的数据结构
2. 实现数据转换逻辑
3. 添加质量评估方法
4. 集成到主流程中

## 版本历史

- **v1.0.0**: 初始版本，基础功能完整
- 支持配置文件管理
- 完整的数据收集功能
- 数据清洗和验证
- 测试脚本和使用示例

## 联系支持

如遇到问题或需要功能建议，请：
1. 查看日志文件了解详细错误信息
2. 运行测试脚本进行诊断
3. 检查配置文件设置
4. 参考使用示例和最佳实践

---

**注意**: 本模块用于教育和研究目的。实际交易时请充分了解风险，谨慎操作。 