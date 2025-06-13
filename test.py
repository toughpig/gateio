#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略输入模块测试脚本

本脚本用于测试strategy_input.py模块的各项功能：
1. 配置文件加载测试
2. 市场数据收集测试
3. 账户数据收集测试
4. 订单数据收集测试
5. 数据清洗和验证测试
6. 完整流程测试
"""

import os
import sys
import time
import json
import logging
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv

# 导入策略输入模块
from strategy_input import (
    ConfigManager,
    create_strategy_input_manager_from_config,
    create_strategy_input_manager,
    StrategyInputManager
)

# 加载环境变量
load_dotenv()

# 导入Gate.io API
import gate_api

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_strategy_input.log')
        ]
    )

def print_separator(title: str):
    """打印分隔符"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def print_subsection(title: str):
    """打印子章节标题"""
    print(f"\n--- {title} ---")

def test_config_loading():
    """测试配置文件加载"""
    print_separator("配置文件加载测试")
    
    try:
        config_manager = ConfigManager("config.ini")
        
        print_subsection("交易对配置")
        trading_pairs = config_manager.get_trading_pairs()
        print(f"配置的交易对数量: {len(trading_pairs)}")
        print(f"交易对列表: {trading_pairs}")
        
        print_subsection("时间间隔配置")
        intervals = config_manager.get_intervals()
        print(f"配置的时间间隔: {intervals}")
        
        print_subsection("策略配置")
        strategy_config = config_manager.get_strategy_config()
        print(f"策略名称: {strategy_config['strategy_name']}")
        print(f"策略版本: {strategy_config['strategy_version']}")
        print(f"基础货币: {strategy_config['base_currency']}")
        print(f"最大仓位: {strategy_config['max_position_size']}")
        print(f"策略参数: {strategy_config['strategy_params']}")
        
        print_subsection("数据收集配置")
        data_config = config_manager.get_data_collection_config()
        print(f"订单簿深度: {data_config['orderbook_depth']}")
        print(f"历史成交数量: {data_config['trades_limit']}")
        print(f"K线数据数量: {data_config['candles_limit']}")
        
        print_subsection("环境配置")
        env_config = config_manager.get_environment_config()
        print(f"运行环境: {env_config['trading_env']}")
        print(f"调试模式: {env_config['debug_mode']}")
        print(f"启用交易: {env_config['enable_trading']}")
        
        print("✅ 配置文件加载测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件加载测试失败: {e}")
        return False

def test_api_connection():
    """测试API连接"""
    print_separator("API连接测试")
    
    try:
        # 检查环境变量
        api_key = os.getenv("GATEIO_API_KEY")
        api_secret = os.getenv("GATEIO_API_SECRET")
        
        if not api_key or not api_secret:
            print("⚠️  警告: 未找到API密钥，将只能测试公开API")
            return False
        
        print(f"API Key: {api_key[:10]}***")
        print("✅ API密钥配置正常")
        return True
        
    except Exception as e:
        print(f"❌ API连接测试失败: {e}")
        return False

def test_market_data_collection():
    """测试市场数据收集"""
    print_separator("市场数据收集测试")
    
    try:
        # 创建管理器
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager()
        
        # 获取配置
        trading_pairs = config_manager.get_trading_pairs() # 只测试前3个交易对
        intervals = config_manager.get_intervals()[:3]  # 只测试前3个时间间隔
        
        print(f"测试交易对: {trading_pairs}")
        print(f"测试时间间隔: {intervals}")
        
        print_subsection("行情数据测试")
        tickers = manager.market_collector.get_ticker_data(trading_pairs)
        print(f"获取到 {len(tickers)} 个交易对的行情数据")
        for pair, ticker in tickers.items():
            print(f"{pair}: 价格={ticker.last_price}, 24h涨跌={ticker.change_24h:.2%}")
        
        print_subsection("订单簿数据测试")
        orderbooks = manager.market_collector.get_orderbook_data(trading_pairs)  # 只测试前2个
        print(f"获取到 {len(orderbooks)} 个交易对的订单簿数据")
        for pair, orderbook in orderbooks.items():
            print(f"{pair}: 买单数量={len(orderbook.bids)}, 卖单数量={len(orderbook.asks)}")
            if orderbook.bids and orderbook.asks:
                print(f"  最佳买价: {orderbook.bids[0].price}")
                print(f"  最佳卖价: {orderbook.asks[0].price}")
        
        print_subsection("成交记录测试")
        trades = manager.market_collector.get_recent_trades(trading_pairs)
        print(f"获取到成交记录的交易对数量: {len(trades)}")
        for pair, trade_list in trades.items():
            print(f"{pair}: 成交记录数量={len(trade_list)}")
            if trade_list:
                latest_trade = trade_list[0]
                print(f"  最新成交: 价格={latest_trade.price}, 数量={latest_trade.volume}")
        
        print_subsection("K线数据测试")
        candles = manager.market_collector.get_candle_data(trading_pairs, intervals)
        print(f"获取到K线数据的交易对数量: {len(candles)}")
        for pair, intervals_data in candles.items():
            print(f"{pair}:")
            for interval, candle_list in intervals_data.items():
                print(f"  {interval}: {len(candle_list)} 根K线")
                if candle_list:
                    latest_candle = candle_list[-1]
                    print(f"    最新K线: 开={latest_candle.open_price}, 高={latest_candle.high_price}, "
                          f"低={latest_candle.low_price}, 收={latest_candle.close_price}")
        
        print("✅ 市场数据收集测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 市场数据收集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_account_data_collection():
    """测试账户数据收集"""
    print_separator("账户数据收集测试")
    
    # 检查是否有API密钥
    if not os.getenv("GATEIO_API_KEY"):
        print("⚠️  跳过账户数据测试（需要API密钥）")
        return True
    
    try:
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager()
        trading_pairs = config_manager.get_trading_pairs()
        
        print_subsection("现货余额测试")
        balances = manager.account_collector.get_spot_balances()
        print(f"获取到 {len(balances)} 种币的余额信息")
        for currency, balance in balances.items():
            if balance.total > 0:
                print(f"{currency}: 可用={balance.available}, 冻结={balance.locked}, 总计={balance.total}")
        
        print_subsection("交易费率测试")
        fees = manager.account_collector.get_trading_fees(trading_pairs)
        print(f"获取到 {len(fees)} 个交易对的费率信息")
        for pair, fee in fees.items():
            print(f"{pair}: Maker费率={fee.maker_fee}, Taker费率={fee.taker_fee}")
        
        print_subsection("账户数据汇总测试")
        account_data = manager.account_collector.collect_account_data(trading_pairs)
        print(f"总权益: {account_data.total_equity} USDT")
        print(f"可用保证金: {account_data.available_margin} USDT")
        print(f"风险等级: {account_data.risk_level}")
        print(f"数据更新时间: {account_data.update_timestamp}")
        
        print("✅ 账户数据收集测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 账户数据收集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_data_collection():
    """测试订单数据收集"""
    print_separator("订单数据收集测试")
    
    # 检查是否有API密钥
    if not os.getenv("GATEIO_API_KEY"):
        print("⚠️  跳过订单数据测试（需要API密钥）")
        return True
    
    try:
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager()
        trading_pairs = config_manager.get_trading_pairs()
        
        print_subsection("活跃订单测试")
        active_orders = manager.order_collector.get_active_orders(trading_pairs)
        print(f"获取到 {len(active_orders)} 个活跃订单")
        for order_id, order in active_orders.items():
            print(f"订单ID: {order_id}, 交易对: {order.currency_pair}, "
                  f"方向: {order.side}, 状态: {order.status}")
        
        print_subsection("历史订单测试")
        recent_orders = manager.order_collector.get_recent_orders(trading_pairs, limit=10)
        print(f"获取到 {len(recent_orders)} 个历史订单")
        for order in recent_orders[:5]:  # 只显示前5个
            print(f"订单ID: {order.order_id}, 交易对: {order.currency_pair}, "
                  f"方向: {order.side}, 状态: {order.status}")
        
        print_subsection("成交历史测试")
        trade_history = manager.order_collector.get_trade_history(trading_pairs, limit=10)
        print(f"获取到 {len(trade_history)} 个成交记录")
        for trade in trade_history[:5]:  # 只显示前5个
            print(f"成交ID: {trade.trade_id}, 交易对: {trade.currency_pair}, "
                  f"方向: {trade.side}, 价格: {trade.price}, 数量: {trade.amount}")
        
        print_subsection("订单数据汇总测试")
        order_data = manager.order_collector.collect_order_data(trading_pairs)
        print(f"活跃订单数: {len(order_data.active_orders)}")
        print(f"历史订单数: {len(order_data.recent_orders)}")
        print(f"成交记录数: {len(order_data.trade_history)}")
        print(f"订单统计: {order_data.order_stats}")
        
        print("✅ 订单数据收集测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 订单数据收集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_strategy_input():
    """测试完整的策略输入收集"""
    print_separator("完整策略输入收集测试")
    
    try:
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager()
        intervals = config_manager.get_intervals()[:3]  # 限制测试数据量
        
        print("开始收集完整的策略输入数据...")
        start_time = time.time()
        
        # 收集完整输入
        strategy_input = manager.collect_strategy_input(intervals)
        
        end_time = time.time()
        collection_duration = end_time - start_time
        
        print(f"数据收集完成，耗时: {collection_duration:.2f} 秒")
        
        print_subsection("输入数据概览")
        print(f"输入ID: {strategy_input.input_id}")
        print(f"收集开始时间: {strategy_input.collection_start_time}")
        print(f"收集结束时间: {strategy_input.collection_end_time}")
        print(f"数据完整性: {strategy_input.data_completeness}")
        
        print_subsection("市场数据概览")
        market_data = strategy_input.market_data
        print(f"行情数据: {len(market_data.tickers)} 个交易对")
        print(f"订单簿数据: {len(market_data.orderbooks)} 个交易对")
        print(f"成交记录: {len(market_data.recent_trades)} 个交易对")
        print(f"K线数据: {len(market_data.candles)} 个交易对")
        print(f"数据来源: {market_data.data_source}")
        
        print_subsection("账户数据概览")
        account_data = strategy_input.account_data
        print(f"现货余额: {len(account_data.spot_balances)} 种币")
        print(f"交易费率: {len(account_data.trading_fees)} 个交易对")
        print(f"总权益: {account_data.total_equity}")
        print(f"风险等级: {account_data.risk_level}")
        
        print_subsection("外部信号概览")
        signals = strategy_input.external_signals
        print(f"技术信号: {len(signals.technical_signals)} 个")
        print(f"市场信号: {len(signals.market_signals)} 个")
        
        # 清洗和验证数据
        print_subsection("数据清洗验证测试")
        clean_input = manager.clean_and_validate_input(strategy_input)
        print("数据清洗验证完成")
        
        # 生成质量报告
        print_subsection("数据质量报告")
        quality_report = manager.get_data_quality_report(clean_input)
        print(f"收集耗时: {quality_report['collection_duration']:.2f} 秒")
        print(f"数据完整性: {quality_report['data_completeness']}")
        print(f"市场数据质量: {quality_report['data_quality']['market_data']}")
        print(f"账户数据质量: {quality_report['data_quality']['account_data']}")
        print(f"订单数据质量: {quality_report['data_quality']['order_data']}")
        
        print("✅ 完整策略输入收集测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 完整策略输入收集测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_persistence():
    """测试数据持久化"""
    print_separator("数据持久化测试")
    
    try:
        manager = create_strategy_input_manager_from_config()
        strategy_input = manager.collect_strategy_input(['1m'])
        
        # 将数据转换为JSON进行序列化测试
        print_subsection("数据序列化测试")
        
        # 测试基本数据结构的序列化
        test_data = {
            'input_id': strategy_input.input_id,
            'collection_time': strategy_input.collection_end_time.isoformat(),
            'trading_pairs': len(strategy_input.market_data.tickers),
            'data_completeness': {k: float(v) for k, v in strategy_input.data_completeness.items()}
        }
        
        json_data = json.dumps(test_data, indent=2, ensure_ascii=False)
        print("数据序列化为JSON格式:")
        print(json_data)
        
        # 测试数据反序列化
        restored_data = json.loads(json_data)
        print(f"反序列化成功，输入ID: {restored_data['input_id']}")
        
        print("✅ 数据持久化测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据持久化测试失败: {e}")
        return False

def run_performance_test():
    """运行性能测试"""
    print_separator("性能测试")
    
    try:
        manager = create_strategy_input_manager_from_config()
        
        # 测试多次数据收集的性能
        iterations = 3
        durations = []
        
        print(f"进行 {iterations} 次数据收集性能测试...")
        
        for i in range(iterations):
            print(f"第 {i+1} 次测试...")
            start_time = time.time()
            
            strategy_input = manager.collect_strategy_input(['1m'])
            
            end_time = time.time()
            duration = end_time - start_time
            durations.append(duration)
            
            print(f"  耗时: {duration:.2f} 秒")
            time.sleep(1)  # 避免API频率限制
        
        # 性能统计
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        
        print_subsection("性能统计")
        print(f"平均耗时: {avg_duration:.2f} 秒")
        print(f"最短耗时: {min_duration:.2f} 秒")
        print(f"最长耗时: {max_duration:.2f} 秒")
        
        if avg_duration < 10:
            print("✅ 性能测试通过（平均耗时 < 10秒）")
            return True
        else:
            print("⚠️  性能警告（平均耗时 >= 10秒）")
            return False
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def update_trading_pairs_from_holdings():
    """
    从用户持有的代币更新交易对列表
    
    功能：
    1. 获取用户现货账户余额
    2. 提取持有的代币（数量>0）
    3. 与USDT组成交易对
    4. 验证交易对的有效性
    5. 更新配置文件中的交易对列表
    """
    print_separator("从持有代币更新交易对列表")
    
    # 检查是否有API密钥
    if not os.getenv("GATEIO_API_KEY"):
        print("❌ 需要API密钥才能获取账户余额信息")
        return False
    
    try:
        # 创建管理器和配置管理器
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager("config.ini")
        
        print_subsection("获取账户余额")
        
        # 获取现货余额
        balances = manager.account_collector.get_spot_balances()
        print(f"获取到 {len(balances)} 种币的余额信息")
        
        # 提取持有的代币（余额>0，排除USDT）
        held_currencies = []
        for currency, balance in balances.items():
            if balance.total > 0 and currency != 'USDT':
                held_currencies.append(currency)
                print(f"持有 {currency}: {balance.total}")
        
        if not held_currencies:
            print("未发现除USDT外的其他持仓")
            return True
        
        print(f"\n发现持有的代币: {held_currencies}")
        
        print_subsection("构建交易对列表")
        
        # 构建与USDT的交易对
        potential_pairs = [f"{currency}_USDT" for currency in held_currencies]
        print(f"潜在交易对: {potential_pairs}")
        
        # 验证交易对的有效性
        valid_pairs = []
        invalid_pairs = []
        
        print("验证交易对有效性...")
        for pair in potential_pairs:
            try:
                # 尝试获取该交易对的行情数据来验证有效性
                tickers = manager.market_collector.spot_api.list_tickers(currency_pair=pair)
                if tickers and len(tickers) > 0 and tickers[0].last:
                    ticker = tickers[0]
                    valid_pairs.append(pair)
                    print(f"✅ {pair} - 当前价格: {ticker.last}")
                else:
                    invalid_pairs.append(pair)
                    print(f"❌ {pair} - 无效交易对")
            except Exception as e:
                invalid_pairs.append(pair)
                print(f"❌ {pair} - 验证失败: {str(e)[:50]}")
            
            time.sleep(0.1)  # 避免API频率限制
        
        if not valid_pairs:
            print("没有找到有效的交易对")
            return False
        
        print_subsection("更新配置文件")
        
        # 获取当前配置的交易对
        current_pairs = set(config_manager.get_trading_pairs())
        print(f"当前配置的交易对: {current_pairs}")
        
        # 合并交易对（去重）
        all_pairs = current_pairs.union(set(valid_pairs))
        new_pairs = set(valid_pairs) - current_pairs
        
        print(f"新增交易对: {new_pairs}")
        print(f"更新后交易对总数: {len(all_pairs)}")
        
        if new_pairs:
            # 更新配置文件
            pairs_str = ", ".join(sorted(all_pairs))
            config_manager.update_config('trading', 'trading_pairs', pairs_str)
            config_manager.save_config()
            print(f"✅ 配置文件已更新")
            print(f"最终交易对列表: {sorted(all_pairs)}")
        else:
            print("所有持有的代币交易对都已在配置中，无需更新")
        
        print_subsection("更新结果汇总")
        print(f"持有的代币数量: {len(held_currencies)}")
        print(f"有效交易对数量: {len(valid_pairs)}")
        print(f"无效交易对数量: {len(invalid_pairs)}")
        print(f"新增交易对数量: {len(new_pairs)}")
        print(f"最终配置交易对数量: {len(all_pairs)}")
        
        if invalid_pairs:
            print(f"\n⚠️  以下交易对无效或不存在:")
            for pair in invalid_pairs:
                print(f"  - {pair}")
        
        print("✅ 从持有代币更新交易对列表完成")
        return True
        
    except Exception as e:
        print(f"❌ 从持有代币更新交易对列表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_holdings_summary():
    """
    获取持仓摘要信息
    
    功能：
    1. 显示所有持有的代币及数量
    2. 显示对应的USDT交易对状态
    3. 提供持仓价值估算（如果可能）
    """
    print_separator("持仓摘要")
    
    # 检查是否有API密钥
    if not os.getenv("GATEIO_API_KEY"):
        print("❌ 需要API密钥才能获取账户余额信息")
        return False
    
    try:
        manager = create_strategy_input_manager_from_config()
        config_manager = ConfigManager("config.ini")
        
        print_subsection("账户余额详情")
        
        # 获取现货余额
        balances = manager.account_collector.get_spot_balances()
        
        # 分类显示
        usdt_balance = None
        other_holdings = {}
        
        for currency, balance in balances.items():
            if balance.total > 0:
                if currency == 'USDT':
                    usdt_balance = balance
                else:
                    other_holdings[currency] = balance
        
        # 显示USDT余额
        if usdt_balance:
            print(f"💰 USDT余额: {usdt_balance.total}")
            print(f"   可用: {usdt_balance.available}")
            print(f"   冻结: {usdt_balance.locked}")
        else:
            print("💰 USDT余额: 0")
        
        # 显示其他代币持仓
        if other_holdings:
            print(f"\n🪙 其他代币持仓 ({len(other_holdings)} 种):")
            
            # 获取当前配置的交易对
            current_pairs = set(config_manager.get_trading_pairs())
            
            for currency, balance in sorted(other_holdings.items()):
                pair = f"{currency}_USDT"
                in_config = "✅" if pair in current_pairs else "❌"
                
                print(f"   {currency}:")
                print(f"     数量: {balance.total}")
                print(f"     可用: {balance.available}")
                print(f"     冻结: {balance.locked}")
                print(f"     交易对: {pair} {in_config}")
                
                # 尝试获取当前价格
                try:
                    tickers = manager.market_collector.spot_api.list_tickers(currency_pair=pair)
                    if tickers and len(tickers) > 0 and tickers[0].last:
                        price = float(tickers[0].last)
                        value = float(balance.total) * price
                        print(f"     当前价格: {price} USDT")
                        print(f"     估值: {value:.2f} USDT")
                    else:
                        print(f"     当前价格: 无法获取")
                except:
                    print(f"     当前价格: 无法获取")
                
                print()
        else:
            print("\n🪙 无其他代币持仓")
        
        print_subsection("配置状态")
        current_pairs = config_manager.get_trading_pairs()
        print(f"当前配置的交易对数量: {len(current_pairs)}")
        print(f"配置的交易对: {current_pairs}")
        
        # 检查配置中的交易对是否都有对应持仓
        configured_currencies = set()
        for pair in current_pairs:
            if '_USDT' in pair:
                currency = pair.replace('_USDT', '')
                configured_currencies.add(currency)
        
        held_currencies = set(other_holdings.keys())
        
        only_configured = configured_currencies - held_currencies
        only_held = held_currencies - configured_currencies
        
        if only_configured:
            print(f"\n⚠️  配置中但未持有的币种: {only_configured}")
        
        if only_held:
            print(f"\n💡 持有但未配置的币种: {only_held}")
            print("   可以运行 '更新交易对列表' 功能来自动添加")
        
        print("✅ 持仓摘要获取完成")
        return True
        
    except Exception as e:
        print(f"❌ 获取持仓摘要失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_menu():
    """打印测试菜单"""
    print("\n" + "="*60)
    print(" Strategy Input 模块测试菜单")
    print("="*60)
    print("1. 配置文件加载测试")
    print("2. API连接测试")
    print("3. 市场数据收集测试")
    print("4. 账户数据收集测试")
    print("5. 订单数据收集测试")
    print("6. 完整策略输入收集测试")
    print("7. 数据持久化测试")
    print("8. 性能测试")
    print("9. 从持有代币更新交易对列表")
    print("10. 获取持仓摘要")
    print("11. 运行所有测试")
    print("0. 退出")
    print("="*60)

def run_all_tests():
    """运行所有测试"""
    print_separator("运行所有测试")
    
    tests = [
        ("配置文件加载测试", test_config_loading),
        ("API连接测试", test_api_connection),
        ("市场数据收集测试", test_market_data_collection),
        ("账户数据收集测试", test_account_data_collection),
        ("订单数据收集测试", test_order_data_collection),
        ("完整策略输入收集测试", test_complete_strategy_input),
        ("数据持久化测试", test_data_persistence),
        ("性能测试", run_performance_test),
        ("从持有代币更新交易对列表", update_trading_pairs_from_holdings),
        ("获取持仓摘要", get_holdings_summary)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n开始执行: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 避免API频率限制
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # 汇总结果
    print_separator("测试结果汇总")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过数量: {passed}")
    print(f"失败数量: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    print(f"总耗时: {total_duration:.2f} 秒")
    
    print("\n详细结果:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")

def main():
    """主函数"""
    setup_logging()
    
    # 检查配置文件
    if not os.path.exists("config.ini"):
        print("❌ 配置文件 config.ini 不存在，请先创建配置文件")
        return
    
    # 检查环境变量
    if not os.path.exists(".env"):
        print("⚠️  警告: .env 文件不存在，请确保已设置API密钥环境变量")
    
    while True:
        print_menu()
        choice = input("\n请选择测试项目 (0-11): ").strip()
        
        if choice == "0":
            print("退出测试程序")
            break
        elif choice == "1":
            test_config_loading()
        elif choice == "2":
            test_api_connection()
        elif choice == "3":
            test_market_data_collection()
        elif choice == "4":
            test_account_data_collection()
        elif choice == "5":
            test_order_data_collection()
        elif choice == "6":
            test_complete_strategy_input()
        elif choice == "7":
            test_data_persistence()
        elif choice == "8":
            run_performance_test()
        elif choice == "9":
            update_trading_pairs_from_holdings()
        elif choice == "10":
            get_holdings_summary()
        elif choice == "11":
            run_all_tests()
        else:
            print("❌ 无效选择，请输入 0-11")
        
        if choice != "0":
            input("\n按回车键继续...")

if __name__ == "__main__":
    main() 