#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gate.io API Demo Script
功能:
1. 通过.env配置连接账户，提供查询当前账户资产的所有币种信息，所有的订单簿信息
2. 针对现货交易，对于某个币种，提供实时订单簿查询，历史成交记录查询
3. 针对现货交易，提供某个币种的创建订单簿接口，取消订单簿接口
4. 实时订单簿成交反馈接口
"""

import os
import time
import pprint
from dotenv import load_dotenv
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# 加载环境变量
load_dotenv()

# 配置API客户端
def get_api_client(with_credentials=False):
    """
    创建API客户端
    
    Args:
        with_credentials (bool): 是否使用API凭证
        
    Returns:
        gate_api.ApiClient: 配置好的API客户端
    """
    # 初始化配置
    configuration = gate_api.Configuration(
        host="https://api.gateio.ws/api/v4"
    )
    
    # 添加API凭证（如果需要）
    if with_credentials:
        # 从环境变量加载API密钥
        configuration.key = os.getenv("GATEIO_API_KEY")
        configuration.secret = os.getenv("GATEIO_API_SECRET")
    
    # 创建API客户端
    api_client = gate_api.ApiClient(configuration)
    return api_client

def get_account_balances():
    """查询账户资产的所有币种信息"""
    print("\n=== 账户资产信息 ===\n")
    
    # 创建带认证的API客户端
    api_client = get_api_client(with_credentials=True)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取现货账户余额
        print("获取现货账户余额...")
        spot_balances = spot_api.list_spot_accounts()
        
        print(f"总币种数: {len(spot_balances)}")
        
        # 显示非零余额
        print("\n非零余额币种:")
        for balance in spot_balances:
            # 只显示有可用或锁定金额的币种
            if float(balance.available) > 0 or float(balance.locked) > 0:
                print(f"币种: {balance.currency}, 可用: {balance.available}, 锁定: {balance.locked}")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def get_all_tickers():
    """获取所有交易对的行情信息"""
    print("\n=== 所有交易对行情 ===\n")
    
    # 创建API客户端（不需要认证）
    api_client = get_api_client(with_credentials=False)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取所有交易对的行情
        print("获取所有交易对行情...")
        tickers = spot_api.list_tickers()
        
        print(f"总交易对数: {len(tickers)}")
        
        # 显示部分交易对信息（前5个）
        print("\n部分交易对行情 (前5个):")
        for ticker in tickers[:5]:
            print(f"交易对: {ticker.currency_pair}, 最新价: {ticker.last}, 24h涨跌幅: {ticker.change_percentage}%")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def list_order_book(currency_pair="ETH_USDT", depth=10):
    """
    查询特定交易对的订单簿
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        depth (int): 订单簿深度，1-100之间
    """
    print(f"\n=== {currency_pair} 订单簿 ===\n")
    
    # 创建API客户端（不需要认证）
    api_client = get_api_client(with_credentials=False)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取订单簿
        print(f"获取 {currency_pair} 订单簿 (深度: {depth})...")
        order_book = spot_api.list_order_book(currency_pair, limit=depth)
        
        # 显示卖单（从低到高）
        print("\n卖单 (价格从低到高):")
        for ask in reversed(order_book.asks[-depth:]):
            print(f"价格: {ask[0]}, 数量: {ask[1]}")
        
        # 显示当前时间戳
        if hasattr(order_book, 'current'):
            print(f"\n当前时间戳: {order_book.current}")
        
        # 显示买单（从高到低）
        print("\n买单 (价格从高到低):")
        for bid in order_book.bids[:depth]:
            print(f"价格: {bid[0]}, 数量: {bid[1]}")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def format_timestamp(timestamp, is_ms=False):
    """
    将时间戳转换为人类可读的格式
    
    Args:
        timestamp (int/float): Unix时间戳
        is_ms (bool): 时间戳是否为毫秒级
    
    Returns:
        str: 格式化的时间字符串，格式为 'YYYY-MM-DD HH:MM:SS'
    """
    if timestamp is None:
        return 'N/A'
    
    try:
        # 如果是毫秒级时间戳，转换为秒级
        if is_ms:
            timestamp = int(timestamp) / 1000
        # 转换时间戳为本地时间
        time_struct = time.localtime(int(timestamp))
        # 格式化时间字符串
        return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
    except (ValueError, TypeError):
        return 'Invalid timestamp'

def get_market_trades(currency_pair="ETH_USDT", limit=20):
    """
    查询特定交易对的历史成交记录
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        limit (int): 返回记录数量，默认20条
    """
    print(f"\n=== {currency_pair} 历史成交记录 ===\n")
    
    # 创建API客户端（不需要认证）
    api_client = get_api_client(with_credentials=False)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取市场交易历史
        print(f"获取 {currency_pair} 历史成交记录...")
        trades = spot_api.list_trades(currency_pair, limit=limit)
        
        print(f"总成交记录数: {len(trades)}")
        
        # 显示成交记录
        print("\n成交记录:")
        for trade in trades:
            side = "买入" if trade.side == "buy" else "卖出"
            create_time = format_timestamp(trade.create_time_ms, is_ms=True)
            print(f"ID: {trade.id}, 方向: {side}, 价格: {trade.price}, "
                  f"数量: {trade.amount}, 时间: {create_time}")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def get_personal_trades(currency_pair="ETH_USDT", limit=10):
    """
    查询特定交易对的个人成交历史
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        limit (int): 返回记录数量，默认10条
    """
    print(f"\n=== {currency_pair} 个人成交历史 ===\n")
    
    # 创建带认证的API客户端
    api_client = get_api_client(with_credentials=True)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取个人交易历史
        print(f"获取 {currency_pair} 个人成交历史...")
        my_trades = spot_api.list_my_trades(currency_pair=currency_pair, limit=limit)
        
        print(f"总成交记录数: {len(my_trades)}")
        
        # 显示成交记录
        if my_trades:
            print("\n个人成交记录:")
            for trade in my_trades:
                side = "买入" if trade.side == "buy" else "卖出"
                create_time = format_timestamp(trade.create_time)
                print(f"订单ID: {trade.order_id}, 方向: {side}, 价格: {trade.price}, "
                      f"数量: {trade.amount}, 手续费: {trade.fee}, 时间: {create_time}")
        else:
            print(f"在 {currency_pair} 没有个人成交记录")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def create_order(currency_pair="ETH_USDT", side="buy", amount="0.001", price=None, order_type="limit"):
    """
    创建订单
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        side (str): 订单方向，'buy' 或 'sell'
        amount (str): 数量
        price (str, optional): 价格，限价单必填，市价单不填
        order_type (str): 订单类型，'limit' 或 'market'
    
    Returns:
        order: 创建的订单信息
    """
    print(f"\n=== 创建{currency_pair}订单 ===\n")
    
    # 创建带认证的API客户端
    api_client = get_api_client(with_credentials=True)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    # 设置订单参数
    order = gate_api.Order(
        currency_pair=currency_pair,
        side=side,
        amount=amount,
        price=price,
        type=order_type
    )
    
    try:
        # 创建订单
        if order_type == "limit":
            print(f"创建限价单: {side} {amount} {currency_pair} @ {price}")
        else:
            print(f"创建市价单: {side} {amount} {currency_pair}")
            
        # 安全询问
        confirm = input("确认创建订单? (y/n): ")
        if confirm.lower() != 'y':
            print("取消创建订单")
            return None
        
        # 提交订单
        created_order = spot_api.create_order(order)
        
        # 显示订单信息
        print("\n订单创建成功:")
        print(f"订单ID: {created_order.id}")
        print(f"交易对: {created_order.currency_pair}")
        print(f"类型: {created_order.type}")
        print(f"方向: {created_order.side}")
        print(f"数量: {created_order.amount}")
        if created_order.price:
            print(f"价格: {created_order.price}")
        print(f"创建时间: {format_timestamp(created_order.create_time)}")
        print(f"状态: {created_order.status}")
        
        return created_order
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")
    
    return None

def cancel_order(currency_pair, order_id):
    """
    取消订单
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        order_id (str): 要取消的订单ID
    """
    print(f"\n=== 取消订单 ===\n")
    
    # 创建带认证的API客户端
    api_client = get_api_client(with_credentials=True)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取订单详情
        print(f"获取订单 {order_id} 详情...")
        order = spot_api.get_order(order_id, currency_pair)
        
        print("\n当前订单信息:")
        print(f"订单ID: {order.id}")
        print(f"交易对: {order.currency_pair}")
        print(f"类型: {order.type}")
        print(f"方向: {order.side}")
        print(f"数量: {order.amount}")
        if order.price:
            print(f"价格: {order.price}")
        print(f"状态: {order.status}")
        
        # 安全询问
        confirm = input(f"确认取消订单 {order_id}? (y/n): ")
        if confirm.lower() != 'y':
            print("取消操作")
            return
        
        # 取消订单
        print(f"取消订单 {order_id}...")
        cancelled_order = spot_api.cancel_order(order_id, currency_pair)
        
        # 显示取消的订单信息
        print("\n订单已取消:")
        print(f"订单ID: {cancelled_order.id}")
        print(f"交易对: {cancelled_order.currency_pair}")
        print(f"方向: {cancelled_order.side}")
        print(f"状态: {cancelled_order.status}")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def list_open_orders(currency_pair=None):
    """
    查询当前未完成订单
    
    Args:
        currency_pair (str, optional): 交易对，如 ETH_USDT，为None时查询所有交易对
    """
    print("\n=== 当前未完成订单 ===\n")
    
    # 创建带认证的API客户端
    api_client = get_api_client(with_credentials=True)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    try:
        # 获取未完成订单
        if currency_pair:
            print(f"获取 {currency_pair} 未完成订单...")
            # 如果指定了交易对，使用list_orders查询特定交易对的订单
            open_orders = spot_api.list_orders(currency_pair, status="open")
            total_orders = len(open_orders)
            
            print(f"未完成订单数: {total_orders}")
            
            # 显示未完成订单
            if open_orders:
                print("\n未完成订单列表:")
                for order in open_orders:
                    create_time = format_timestamp(order.create_time)
                    print(f"订单ID: {order.id}, 交易对: {order.currency_pair}, "
                          f"方向: {order.side}, 数量: {order.amount}, "
                          f"价格: {order.price}, 创建时间: {create_time}")
            else:
                print(f"在 {currency_pair} 没有未完成的订单")
        else:
            print("获取所有交易对的未完成订单...")
            # 否则使用list_all_open_orders查询所有交易对的未完成订单
            all_open_orders = spot_api.list_all_open_orders()
            
            total_orders = sum(pair_orders.total for pair_orders in all_open_orders)
            print(f"未完成订单总数: {total_orders}")
            
            # 显示每个交易对的未完成订单
            if all_open_orders:
                print("\n未完成订单列表:")
                for pair_orders in all_open_orders:
                    print(f"\n交易对 {pair_orders.currency_pair} 的订单 (共 {pair_orders.total} 个):")
                    for order in pair_orders.orders:
                        create_time = format_timestamp(order.create_time)
                        print(f"订单ID: {order.id}, 方向: {order.side}, "
                              f"数量: {order.amount}, 价格: {order.price}, "
                              f"创建时间: {create_time}")
            else:
                print("没有未完成的订单")
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")

def monitor_order_book_changes(currency_pair="ETH_USDT", interval=5, iterations=3):
    """
    监控订单簿变化
    
    Args:
        currency_pair (str): 交易对，如 ETH_USDT
        interval (int): 刷新间隔（秒）
        iterations (int): 监控次数
    """
    print(f"\n=== 监控 {currency_pair} 订单簿变化 ===\n")
    
    # 创建API客户端（不需要认证）
    api_client = get_api_client(with_credentials=False)
    
    # 初始化SpotApi实例
    spot_api = gate_api.SpotApi(api_client)
    
    # 保存上一次的订单簿
    last_book = None
    
    try:
        for i in range(iterations):
            print(f"\n第 {i+1}/{iterations} 次查询:")
            # 获取当前订单簿
            order_book = spot_api.list_order_book(currency_pair, limit=5)
            
            # 显示当前买一卖一价格
            best_ask = order_book.asks[0] if order_book.asks else None
            best_bid = order_book.bids[0] if order_book.bids else None
            
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"时间: {current_time}")
            if best_ask:
                print(f"卖一: 价格 {best_ask[0]}, 数量 {best_ask[1]}")
            if best_bid:
                print(f"买一: 价格 {best_bid[0]}, 数量 {best_bid[1]}")
            
            # 如果有上一次的订单簿，比较变化
            if last_book is not None:
                # 检查最佳卖价变化
                last_best_ask = last_book.asks[0] if last_book.asks else None
                if best_ask and last_best_ask and best_ask[0] != last_best_ask[0]:
                    direction = "上涨" if float(best_ask[0]) > float(last_best_ask[0]) else "下跌"
                    change = abs(float(best_ask[0]) - float(last_best_ask[0]))
                    print(f"卖一价格{direction}: {change}")
                
                # 检查最佳买价变化
                last_best_bid = last_book.bids[0] if last_book.bids else None
                if best_bid and last_best_bid and best_bid[0] != last_best_bid[0]:
                    direction = "上涨" if float(best_bid[0]) > float(last_best_bid[0]) else "下跌"
                    change = abs(float(best_bid[0]) - float(last_best_bid[0]))
                    print(f"买一价格{direction}: {change}")
            
            # 更新上一次的订单簿
            last_book = order_book
            
            # 如果不是最后一次，等待一段时间
            if i < iterations - 1:
                print(f"等待 {interval} 秒...")
                time.sleep(interval)
    
    except GateApiException as ex:
        print(f"Gate API异常, 标签: {ex.label}, 消息: {ex.message}")
    except ApiException as e:
        print(f"调用SpotApi时出现异常: {e}")
    except KeyboardInterrupt:
        print("监控被用户中断")

def print_menu():
    """打印菜单"""
    print("\n=== Gate.io API 示例 ===")
    print("1. 查询账户资产")
    print("2. 获取所有交易对行情")
    print("3. 查询特定交易对订单簿")
    print("4. 查询市场成交历史")
    print("5. 查询个人成交历史")
    print("6. 创建订单")
    print("7. 取消订单")
    print("8. 查询未完成订单")
    print("9. 监控订单簿变化")
    print("0. 退出")
    return input("请选择功能: ")

def main():
    """主函数"""
    # 检查API凭证是否设置
    if not os.getenv("GATEIO_API_KEY") or not os.getenv("GATEIO_API_SECRET"):
        print("错误: API凭证未设置。请在.env文件中配置GATEIO_API_KEY和GATEIO_API_SECRET。")
        return
    
    # 菜单循环
    while True:
        choice = print_menu()
        
        if choice == '1':
            get_account_balances()
        elif choice == '2':
            get_all_tickers()
        elif choice == '3':
            pair = input("请输入交易对 (默认: ETH_USDT): ") or "ETH_USDT"
            depth = int(input("请输入深度 (1-100, 默认: 10): ") or 10)
            list_order_book(pair, depth)
        elif choice == '4':
            pair = input("请输入交易对 (默认: ETH_USDT): ") or "ETH_USDT"
            limit = int(input("请输入记录数量 (默认: 20): ") or 20)
            get_market_trades(pair, limit)
        elif choice == '5':
            pair = input("请输入交易对 (默认: ETH_USDT): ") or "ETH_USDT"
            get_personal_trades(pair)
        elif choice == '6':
            pair = input("请输入交易对 (默认: ETH_USDT): ") or "ETH_USDT"
            side = input("请输入交易方向 (buy/sell, 默认: buy): ") or "buy"
            order_type = input("请输入订单类型 (limit/market, 默认: limit): ") or "limit"
            amount = input("请输入数量: ")
            price = None if order_type == "market" else input("请输入价格: ")
            create_order(pair, side, amount, price, order_type)
        elif choice == '7':
            pair = input("请输入交易对: ")
            order_id = input("请输入订单ID: ")
            cancel_order(pair, order_id)
        elif choice == '8':
            pair = input("请输入交易对 (直接回车查询所有交易对): ")
            if not pair:
                list_open_orders()
            else:
                list_open_orders(pair)
        elif choice == '9':
            pair = input("请输入交易对 (默认: ETH_USDT): ") or "ETH_USDT"
            interval = int(input("请输入刷新间隔秒数 (默认: 5): ") or 5)
            iterations = int(input("请输入监控次数 (默认: 3): ") or 3)
            monitor_order_book_changes(pair, interval, iterations)
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    main() 