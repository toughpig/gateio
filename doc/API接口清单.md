# Gate.io API 接口清单

## 概述

本文档详细列出了项目中已实现的所有 Gate.io API 接口，按功能模块进行分类。

## 1. 现货交易 API (Spot API)

### 1.1 市场数据接口（公开）

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取所有交易对 | `spot_api.list_currency_pairs()` | 获取平台支持的所有现货交易对 | 无 |
| 获取行情数据 | `spot_api.list_tickers()` | 获取所有或指定交易对的24小时行情 | currency_pair (可选) |
| 获取订单簿 | `spot_api.list_order_book()` | 获取指定交易对的买卖单深度 | currency_pair, limit |
| 获取市场交易记录 | `spot_api.list_trades()` | 获取指定交易对的最新成交记录 | currency_pair, limit |
| 获取K线数据 | `spot_api.list_candlesticks()` | 获取指定交易对的K线/蜡烛图数据 | currency_pair, interval, limit |
| 获取币种信息 | `spot_api.list_currencies()` | 获取平台支持的所有币种信息 | 无 |
| 获取单个币种信息 | `spot_api.get_currency()` | 获取指定币种的详细信息 | currency |

### 1.2 账户接口（私有）

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取现货余额 | `spot_api.list_spot_accounts()` | 获取现货账户所有币种余额 | currency (可选) |
| 获取交易费率 | `spot_api.get_fee()` | 获取当前用户的交易费率 | currency_pair (可选) |
| 获取账户变动记录 | `spot_api.list_spot_account_book()` | 获取现货账户资金变动记录 | limit, currency |

### 1.3 交易接口（私有）

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 创建订单 | `spot_api.create_order()` | 创建买入或卖出订单 | Order对象 |
| 取消订单 | `spot_api.cancel_order()` | 取消指定的未完成订单 | order_id, currency_pair |
| 获取订单详情 | `spot_api.get_order()` | 获取指定订单的详细信息 | order_id, currency_pair |
| 查询订单列表 | `spot_api.list_orders()` | 查询订单历史或未完成订单 | currency_pair, status, limit |
| 查询所有未完成订单 | `spot_api.list_all_open_orders()` | 查询所有交易对的未完成订单 | 无 |
| 获取个人交易记录 | `spot_api.list_my_trades()` | 获取个人成交历史 | currency_pair, limit |

## 2. 账户管理 API (Account API)

### 2.1 账户信息接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取账户详情 | `account_api.get_account_detail()` | 获取用户账户基本信息 | 无 |

## 3. 钱包管理 API (Wallet API)

### 3.1 充值相关接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取充值地址 | `wallet_api.get_deposit_address()` | 获取指定币种的充值地址 | currency |
| 获取充值记录 | `wallet_api.list_deposits()` | 获取充值历史记录 | currency, limit |

### 3.2 提现相关接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取提现记录 | `wallet_api.list_withdrawals()` | 获取提现历史记录 | currency, limit |

### 3.3 转账相关接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 子账户转账记录 | `wallet_api.list_sub_account_transfers()` | 获取子账户间转账记录 | limit |
| UID转账记录 | `wallet_api.list_push_orders()` | 获取UID转账记录 | limit |

### 3.4 余额相关接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取总余额 | `wallet_api.get_total_balance()` | 获取账户总余额（BTC/USD计价） | 无 |
| 获取子账户余额 | `wallet_api.list_sub_account_balances()` | 获取所有子账户余额 | 无 |
| 获取小额余额 | `wallet_api.list_small_balance()` | 获取小额余额列表 | 无 |
| 小额余额转换历史 | `wallet_api.list_small_balance_history()` | 获取小额余额转换记录 | 无 |

### 3.5 地址管理接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取保存地址 | `wallet_api.list_saved_address()` | 获取已保存的提现地址 | currency |
| 获取币种链信息 | `wallet_api.list_currency_chains()` | 获取币种支持的区块链信息 | currency |

### 3.6 费率接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取交易费率 | `wallet_api.get_trade_fee()` | 获取交易费率信息 | currency_pair (可选) |

## 4. 期货交易 API (Futures API)

### 4.1 期货市场数据接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取期货合约 | `futures_api.list_futures_contracts()` | 获取所有期货合约信息 | settle |
| 获取期货订单簿 | `futures_api.list_futures_order_book()` | 获取期货订单簿 | settle, contract, limit |
| 获取期货K线 | `futures_api.list_futures_candlesticks()` | 获取期货K线数据 | settle, contract, interval, limit |
| 获取期货行情 | `futures_api.list_futures_tickers()` | 获取期货行情数据 | settle, contract |

### 4.2 期货账户接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取期货账户 | `futures_api.list_futures_accounts()` | 获取期货账户信息 | settle |

## 5. 杠杆交易 API (Margin API)

### 5.1 杠杆账户接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取杠杆账户 | `margin_api.list_margin_accounts()` | 获取杠杆交易账户信息 | currency_pair (可选) |
| 获取全仓杠杆账户 | `margin_api.get_cross_margin_account()` | 获取全仓杠杆账户信息 | 无 |
| 获取全仓杠杆币种 | `margin_api.list_cross_margin_currencies()` | 获取支持全仓杠杆的币种 | 无 |
| 获取资金账户 | `margin_api.list_funding_accounts()` | 获取资金账户信息 | currency (可选) |

## 6. 子账户管理 API (SubAccount API)

### 6.1 子账户接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 获取子账户列表 | `sub_account_api.list_sub_accounts()` | 获取所有子账户信息 | 无 |

## 7. 提现管理 API (Withdrawal API)

### 7.1 提现操作接口

| 接口名称 | 函数实现 | 描述 | 参数 |
|---------|---------|------|------|
| 取消提现 | `withdrawal_api.cancel_withdrawal()` | 取消指定的提现申请 | withdrawal_id |

## 接口使用说明

### 认证要求
- **公开接口**: 不需要API密钥，可直接调用
- **私有接口**: 需要API密钥和签名认证

### 通用参数说明
- `currency`: 币种代码，如 BTC, USDT
- `currency_pair`: 交易对，如 BTC_USDT, ETH_USDT
- `limit`: 返回结果数量限制
- `settle`: 结算币种，期货接口使用，如 usdt, btc
- `contract`: 合约名称，期货接口使用

### 错误处理
所有接口调用都包含异常处理：
- `GateApiException`: Gate.io API特定异常
- `ApiException`: 通用API异常

### 配置要求
需要在环境变量中配置：
```
GATEIO_API_KEY=your_api_key
GATEIO_API_SECRET=your_api_secret
```

## 注意事项

1. **API限制**: 部分接口有调用频率限制，请参考官方文档
2. **权限要求**: 不同接口需要不同的API权限，请确保API密钥有相应权限
3. **测试环境**: 建议先在测试环境验证功能后再用于生产环境
4. **数据格式**: 价格和数量通常以字符串格式返回，避免浮点数精度问题
5. **时间戳**: 部分接口返回时间戳，注意区分秒级和毫秒级 