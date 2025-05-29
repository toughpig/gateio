#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
策略输入数据获取、清洗和整理模块

本模块负责：
1. 从Gate.io API获取原始数据
2. 数据清洗和验证
3. 数据标准化和格式转换
4. 聚合为策略模块标准输入
"""

import os
import time
import logging
import configparser
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
import gate_api
from gate_api.exceptions import ApiException, GateApiException

# ===== 数据结构定义 =====

@dataclass
class TickerData:
    """行情数据"""
    currency_pair: str
    last_price: Decimal
    bid_price: Decimal
    ask_price: Decimal
    bid_volume: Decimal
    ask_volume: Decimal
    high_24h: Decimal
    low_24h: Decimal
    volume_24h: Decimal
    volume_24h_quote: Decimal
    change_24h: Decimal
    timestamp: datetime

@dataclass
class OrderBookLevel:
    """订单簿单级数据"""
    price: Decimal
    volume: Decimal

@dataclass
class OrderBookData:
    """订单簿数据"""
    currency_pair: str
    asks: List[OrderBookLevel]
    bids: List[OrderBookLevel]
    timestamp: datetime
    sequence: int

@dataclass
class TradeData:
    """成交记录"""
    trade_id: str
    currency_pair: str
    price: Decimal
    volume: Decimal
    side: str
    timestamp: datetime

@dataclass
class CandleData:
    """K线数据"""
    currency_pair: str
    interval: str
    open_time: datetime
    close_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal
    trade_count: int

@dataclass
class MarketDataInput:
    """市场数据输入集合"""
    tickers: Dict[str, TickerData]
    orderbooks: Dict[str, OrderBookData]
    recent_trades: Dict[str, List[TradeData]]
    candles: Dict[str, Dict[str, List[CandleData]]]
    data_freshness: Dict[str, datetime]
    data_reliability: Dict[str, float]
    collection_timestamp: datetime
    data_source: str

@dataclass
class BalanceInfo:
    """余额信息"""
    currency: str
    available: Decimal
    locked: Decimal
    total: Decimal
    btc_value: Decimal
    usd_value: Decimal

@dataclass
class PositionInfo:
    """持仓信息"""
    currency_pair: str
    side: str
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    unrealized_pnl: Decimal
    margin: Decimal
    leverage: Decimal

@dataclass
class TradingFeeInfo:
    """交易费率信息"""
    currency_pair: str
    maker_fee: Decimal
    taker_fee: Decimal
    volume_tier: str

@dataclass
class AccountDataInput:
    """账户数据输入"""
    spot_balances: Dict[str, BalanceInfo]
    futures_balances: Dict[str, BalanceInfo]
    margin_balances: Dict[str, BalanceInfo]
    positions: Dict[str, PositionInfo]
    trading_fees: Dict[str, TradingFeeInfo]
    total_equity: Decimal
    available_margin: Decimal
    margin_ratio: Decimal
    risk_level: str
    update_timestamp: datetime

@dataclass
class OrderInfo:
    """订单信息"""
    order_id: str
    client_order_id: Optional[str]
    currency_pair: str
    side: str
    type: str
    status: str
    amount: Decimal
    price: Optional[Decimal]
    filled_amount: Decimal
    remaining_amount: Decimal
    average_price: Optional[Decimal]
    fee: Decimal
    fee_currency: str
    create_time: datetime
    update_time: datetime

@dataclass
class TradeHistory:
    """成交历史"""
    trade_id: str
    order_id: str
    currency_pair: str
    side: str
    amount: Decimal
    price: Decimal
    fee: Decimal
    fee_currency: str
    timestamp: datetime

@dataclass
class OrderDataInput:
    """订单数据输入"""
    active_orders: Dict[str, OrderInfo]
    recent_orders: List[OrderInfo]
    trade_history: List[TradeHistory]
    order_stats: Dict[str, Union[int, Decimal]]
    update_timestamp: datetime

@dataclass
class StrategyConfig:
    """策略配置参数"""
    strategy_name: str
    strategy_version: str
    trading_pairs: List[str]
    base_currency: str
    max_position_size: Decimal
    min_order_size: Decimal
    decision_interval: int
    data_window: int
    strategy_params: Dict[str, Union[str, int, float, Decimal]]
    max_drawdown: Decimal
    stop_loss: Optional[Decimal]
    take_profit: Optional[Decimal]

@dataclass
class ConfigInput:
    """配置输入"""
    strategy_config: StrategyConfig
    environment: str
    debug_mode: bool
    logging_level: str
    config_timestamp: datetime

@dataclass
class MarketSignal:
    """市场信号"""
    signal_type: str
    signal_name: str
    value: Union[str, Decimal]
    strength: Decimal
    confidence: Decimal
    timestamp: datetime
    source: str

@dataclass
class ExternalSignalInput:
    """外部信号输入"""
    market_signals: List[MarketSignal]
    news_sentiment: Optional[Decimal]
    technical_signals: Dict[str, Decimal]
    macro_indicators: Dict[str, Decimal]
    update_timestamp: datetime

@dataclass
class StrategyInput:
    """策略模块完整输入"""
    market_data: MarketDataInput
    account_data: AccountDataInput
    order_data: OrderDataInput
    config: ConfigInput
    external_signals: ExternalSignalInput
    input_id: str
    collection_start_time: datetime
    collection_end_time: datetime
    data_completeness: Dict[str, Decimal]

# ===== 数据获取和处理类 =====

class DataValidator:
    """数据验证器"""
    
    @staticmethod
    def safe_decimal(value, default: Decimal = Decimal('0')) -> Decimal:
        """安全转换为Decimal"""
        if value is None:
            return default
        try:
            if isinstance(value, str):
                return Decimal(value) if value.strip() else default
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_datetime(timestamp) -> datetime:
        """安全转换为datetime"""
        if isinstance(timestamp, datetime):
            return timestamp
        try:
            if isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            pass
        return datetime.now()
    
    @staticmethod
    def validate_currency_pair(pair: str) -> bool:
        """验证交易对格式"""
        return isinstance(pair, str) and '_' in pair and len(pair.split('_')) == 2
    
    @staticmethod
    def validate_price_volume(price: Decimal, volume: Decimal) -> bool:
        """验证价格和数量的有效性"""
        return price > 0 and volume >= 0


class MarketDataCollector:
    """市场数据收集器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.spot_api = gate_api.SpotApi(api_client)
        self.logger = logging.getLogger(__name__)
        self.validator = DataValidator()
        
    def get_ticker_data(self, currency_pairs: List[str]) -> Dict[str, TickerData]:
        """获取行情数据"""
        tickers = {}
        
        try:
            # 获取所有交易对的行情
            all_tickers = self.spot_api.list_tickers()
            ticker_dict = {t.currency_pair: t for t in all_tickers}
            
            for pair in currency_pairs:
                if pair in ticker_dict:
                    ticker = ticker_dict[pair]
                    tickers[pair] = TickerData(
                        currency_pair=pair,
                        last_price=self.validator.safe_decimal(ticker.last),
                        bid_price=self.validator.safe_decimal(ticker.highest_bid),
                        ask_price=self.validator.safe_decimal(ticker.lowest_ask),
                        bid_volume=self.validator.safe_decimal(ticker.base_volume),
                        ask_volume=self.validator.safe_decimal(ticker.quote_volume),
                        high_24h=self.validator.safe_decimal(ticker.high_24h),
                        low_24h=self.validator.safe_decimal(ticker.low_24h),
                        volume_24h=self.validator.safe_decimal(ticker.base_volume),
                        volume_24h_quote=self.validator.safe_decimal(ticker.quote_volume),
                        change_24h=self.validator.safe_decimal(ticker.change_percentage, Decimal('0')) / 100,
                        timestamp=datetime.now()
                    )
                else:
                    self.logger.warning(f"Ticker data not found for {pair}")
                    
        except Exception as e:
            self.logger.error(f"Failed to get ticker data: {e}")
            
        return tickers
    
    def get_orderbook_data(self, currency_pairs: List[str], depth: int = 20) -> Dict[str, OrderBookData]:
        """获取订单簿数据"""
        orderbooks = {}
        
        for pair in currency_pairs:
            try:
                orderbook = self.spot_api.list_order_book(pair, limit=depth)
                
                asks = [
                    OrderBookLevel(
                        price=self.validator.safe_decimal(ask[0]),
                        volume=self.validator.safe_decimal(ask[1])
                    ) for ask in orderbook.asks
                ]
                
                bids = [
                    OrderBookLevel(
                        price=self.validator.safe_decimal(bid[0]),
                        volume=self.validator.safe_decimal(bid[1])
                    ) for bid in orderbook.bids
                ]
                
                orderbooks[pair] = OrderBookData(
                    currency_pair=pair,
                    asks=asks,
                    bids=bids,
                    timestamp=datetime.now(),
                    sequence=getattr(orderbook, 'id', 0)
                )
                
            except Exception as e:
                self.logger.error(f"Failed to get orderbook for {pair}: {e}")
                
        return orderbooks
    
    def get_recent_trades(self, currency_pairs: List[str], limit: int = 100) -> Dict[str, List[TradeData]]:
        """获取最近成交记录"""
        trades = {}
        
        for pair in currency_pairs:
            try:
                trade_list = self.spot_api.list_trades(pair, limit=limit)
                
                trades[pair] = [
                    TradeData(
                        trade_id=str(trade.id),
                        currency_pair=pair,
                        price=self.validator.safe_decimal(trade.price),
                        volume=self.validator.safe_decimal(trade.amount),
                        side=trade.side,
                        timestamp=self.validator.safe_datetime(trade.create_time)
                    ) for trade in trade_list
                ]
                
            except Exception as e:
                self.logger.error(f"Failed to get trades for {pair}: {e}")
                trades[pair] = []
                
        return trades
    
    def get_candle_data(self, currency_pairs: List[str], intervals: List[str], limit: int = 200) -> Dict[str, Dict[str, List[CandleData]]]:
        """获取K线数据"""
        candles = {}
        
        for pair in currency_pairs:
            candles[pair] = {}
            
            for interval in intervals:
                try:
                    candle_list = self.spot_api.list_candlesticks(
                        currency_pair=pair,
                        interval=interval,
                        limit=limit
                    )
                    
                    candles[pair][interval] = [
                        CandleData(
                            currency_pair=pair,
                            interval=interval,
                            open_time=self.validator.safe_datetime(int(candle[0])),
                            close_time=self.validator.safe_datetime(int(candle[0]) + self._interval_to_seconds(interval)),
                            open_price=self.validator.safe_decimal(candle[5]),
                            high_price=self.validator.safe_decimal(candle[3]),
                            low_price=self.validator.safe_decimal(candle[4]),
                            close_price=self.validator.safe_decimal(candle[2]),
                            volume=self.validator.safe_decimal(candle[1]),
                            quote_volume=self.validator.safe_decimal(candle[7]),
                            trade_count=int(candle[8]) if len(candle) > 8 else 0
                        ) for candle in candle_list
                    ]
                    
                except Exception as e:
                    self.logger.error(f"Failed to get candles for {pair} {interval}: {e}")
                    candles[pair][interval] = []
                    
        return candles
    
    def _interval_to_seconds(self, interval: str) -> int:
        """将时间间隔转换为秒数"""
        interval_map = {
            '1s': 1, '10s': 10, '1m': 60, '5m': 300, '15m': 900,
            '30m': 1800, '1h': 3600, '4h': 14400, '8h': 28800,
            '1d': 86400, '7d': 604800, '30d': 2592000
        }
        return interval_map.get(interval, 60)
    
    def collect_market_data(self, currency_pairs: List[str], intervals: List[str] = None) -> MarketDataInput:
        """收集完整的市场数据"""
        if intervals is None:
            intervals = ['1m', '5m', '15m', '1h', '1d']
            
        collection_start = datetime.now()
        
        # 获取各类数据
        tickers = self.get_ticker_data(currency_pairs)
        orderbooks = self.get_orderbook_data(currency_pairs)
        recent_trades = self.get_recent_trades(currency_pairs)
        candles = self.get_candle_data(currency_pairs, intervals)
        
        # 计算数据新鲜度
        data_freshness = {pair: datetime.now() for pair in currency_pairs}
        
        # 计算数据可靠性
        data_reliability = {}
        for pair in currency_pairs:
            reliability = 1.0
            if pair not in tickers:
                reliability -= 0.3
            if pair not in orderbooks:
                reliability -= 0.3
            if pair not in recent_trades or not recent_trades[pair]:
                reliability -= 0.2
            if pair not in candles or not any(candles[pair].values()):
                reliability -= 0.2
            data_reliability[pair] = max(0.0, reliability)
        
        return MarketDataInput(
            tickers=tickers,
            orderbooks=orderbooks,
            recent_trades=recent_trades,
            candles=candles,
            data_freshness=data_freshness,
            data_reliability=data_reliability,
            collection_timestamp=datetime.now(),
            data_source="gate.io"
        )


class AccountDataCollector:
    """账户数据收集器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.spot_api = gate_api.SpotApi(api_client)
        self.logger = logging.getLogger(__name__)
        self.validator = DataValidator()
        
    def get_spot_balances(self) -> Dict[str, BalanceInfo]:
        """获取现货余额"""
        balances = {}
        
        try:
            account_balances = self.spot_api.list_spot_accounts()
            
            for balance in account_balances:
                if float(balance.available) > 0 or float(balance.locked) > 0:
                    available = self.validator.safe_decimal(balance.available)
                    locked = self.validator.safe_decimal(balance.locked)
                    total = available + locked
                    
                    balances[balance.currency] = BalanceInfo(
                        currency=balance.currency,
                        available=available,
                        locked=locked,
                        total=total,
                        btc_value=Decimal('0'),  # 需要额外计算
                        usd_value=Decimal('0')   # 需要额外计算
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to get spot balances: {e}")
            
        return balances
    
    def get_trading_fees(self, currency_pairs: List[str]) -> Dict[str, TradingFeeInfo]:
        """获取交易费率"""
        fees = {}
        
        try:
            fee_info = self.spot_api.get_fee()
            
            for pair in currency_pairs:
                fees[pair] = TradingFeeInfo(
                    currency_pair=pair,
                    maker_fee=self.validator.safe_decimal(fee_info.maker_fee),
                    taker_fee=self.validator.safe_decimal(fee_info.taker_fee),
                    volume_tier="default"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to get trading fees: {e}")
            # 使用默认费率
            for pair in currency_pairs:
                fees[pair] = TradingFeeInfo(
                    currency_pair=pair,
                    maker_fee=Decimal('0.002'),
                    taker_fee=Decimal('0.002'),
                    volume_tier="default"
                )
                
        return fees
    
    def calculate_total_equity(self, balances: Dict[str, BalanceInfo]) -> Decimal:
        """计算总权益（简化版）"""
        total_equity = Decimal('0')
        
        # 简化计算，主要考虑USDT价值
        for balance in balances.values():
            if balance.currency == 'USDT':
                total_equity += balance.total
            # 其他币种需要通过价格转换，这里暂时简化处理
                
        return total_equity
    
    def assess_risk_level(self, total_equity: Decimal, margin_ratio: Decimal) -> str:
        """评估风险等级"""
        if margin_ratio > Decimal('0.8'):
            return "high"
        elif margin_ratio > Decimal('0.5'):
            return "medium"
        else:
            return "low"
    
    def collect_account_data(self, currency_pairs: List[str]) -> AccountDataInput:
        """收集完整的账户数据"""
        spot_balances = self.get_spot_balances()
        trading_fees = self.get_trading_fees(currency_pairs)
        
        total_equity = self.calculate_total_equity(spot_balances)
        available_margin = total_equity * Decimal('0.8')  # 简化计算
        margin_ratio = Decimal('0.1')  # 简化设置
        risk_level = self.assess_risk_level(total_equity, margin_ratio)
        
        return AccountDataInput(
            spot_balances=spot_balances,
            futures_balances={},  # 暂时为空
            margin_balances={},   # 暂时为空
            positions={},         # 暂时为空
            trading_fees=trading_fees,
            total_equity=total_equity,
            available_margin=available_margin,
            margin_ratio=margin_ratio,
            risk_level=risk_level,
            update_timestamp=datetime.now()
        )


class OrderDataCollector:
    """订单数据收集器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.spot_api = gate_api.SpotApi(api_client)
        self.logger = logging.getLogger(__name__)
        self.validator = DataValidator()
        
    def get_active_orders(self, currency_pairs: List[str]) -> Dict[str, OrderInfo]:
        """获取活跃订单"""
        active_orders = {}
        
        for pair in currency_pairs:
            try:
                orders = self.spot_api.list_orders(currency_pair=pair, status="open")
                
                for order in orders:
                    order_info = OrderInfo(
                        order_id=order.id,
                        client_order_id=getattr(order, 'text', None),
                        currency_pair=order.currency_pair,
                        side=order.side,
                        type=order.type,
                        status=order.status,
                        amount=self.validator.safe_decimal(order.amount),
                        price=self.validator.safe_decimal(order.price) if order.price else None,
                        filled_amount=self.validator.safe_decimal(order.filled_total),
                        remaining_amount=self.validator.safe_decimal(order.left),
                        average_price=self.validator.safe_decimal(order.avg_deal_price) if hasattr(order, 'avg_deal_price') else None,
                        fee=self.validator.safe_decimal(order.fee),
                        fee_currency=getattr(order, 'fee_currency', 'USDT'),
                        create_time=self.validator.safe_datetime(order.create_time),
                        update_time=self.validator.safe_datetime(order.update_time)
                    )
                    active_orders[order.id] = order_info
                    
            except Exception as e:
                self.logger.error(f"Failed to get active orders for {pair}: {e}")
                
        return active_orders
    
    def get_recent_orders(self, currency_pairs: List[str], limit: int = 100) -> List[OrderInfo]:
        """获取最近的订单历史"""
        recent_orders = []
        
        for pair in currency_pairs:
            try:
                orders = self.spot_api.list_orders(currency_pair=pair, status="finished", limit=limit)
                
                for order in orders[:limit]:  # 限制数量
                    order_info = OrderInfo(
                        order_id=order.id,
                        client_order_id=getattr(order, 'text', None),
                        currency_pair=order.currency_pair,
                        side=order.side,
                        type=order.type,
                        status=order.status,
                        amount=self.validator.safe_decimal(order.amount),
                        price=self.validator.safe_decimal(order.price) if order.price else None,
                        filled_amount=self.validator.safe_decimal(order.filled_total),
                        remaining_amount=self.validator.safe_decimal(order.left),
                        average_price=self.validator.safe_decimal(order.avg_deal_price) if hasattr(order, 'avg_deal_price') else None,
                        fee=self.validator.safe_decimal(order.fee),
                        fee_currency=getattr(order, 'fee_currency', 'USDT'),
                        create_time=self.validator.safe_datetime(order.create_time),
                        update_time=self.validator.safe_datetime(order.update_time)
                    )
                    recent_orders.append(order_info)
                    
            except Exception as e:
                self.logger.error(f"Failed to get recent orders for {pair}: {e}")
                
        # 按时间排序
        recent_orders.sort(key=lambda x: x.create_time, reverse=True)
        return recent_orders[:limit]
    
    def get_trade_history(self, currency_pairs: List[str], limit: int = 100) -> List[TradeHistory]:
        """获取成交历史"""
        trade_history = []
        
        for pair in currency_pairs:
            try:
                trades = self.spot_api.list_my_trades(currency_pair=pair, limit=limit)
                
                for trade in trades:
                    trade_info = TradeHistory(
                        trade_id=str(trade.id),
                        order_id=trade.order_id,
                        currency_pair=pair,
                        side=trade.side,
                        amount=self.validator.safe_decimal(trade.amount),
                        price=self.validator.safe_decimal(trade.price),
                        fee=self.validator.safe_decimal(trade.fee),
                        fee_currency=trade.fee_currency,
                        timestamp=self.validator.safe_datetime(trade.create_time)
                    )
                    trade_history.append(trade_info)
                    
            except Exception as e:
                self.logger.error(f"Failed to get trade history for {pair}: {e}")
                
        # 按时间排序
        trade_history.sort(key=lambda x: x.timestamp, reverse=True)
        return trade_history[:limit]
    
    def calculate_order_stats(self, orders: List[OrderInfo], trades: List[TradeHistory]) -> Dict[str, Union[int, Decimal]]:
        """计算订单统计信息"""
        stats = {
            'total_orders': len(orders),
            'filled_orders': len([o for o in orders if o.status == 'closed']),
            'cancelled_orders': len([o for o in orders if o.status == 'cancelled']),
            'total_trades': len(trades),
            'total_volume': sum(t.amount for t in trades),
            'total_fees': sum(t.fee for t in trades),
        }
        
        if stats['total_orders'] > 0:
            stats['fill_rate'] = Decimal(str(stats['filled_orders'])) / Decimal(str(stats['total_orders']))
        else:
            stats['fill_rate'] = Decimal('0')
            
        return stats
    
    def collect_order_data(self, currency_pairs: List[str]) -> OrderDataInput:
        """收集完整的订单数据"""
        active_orders = self.get_active_orders(currency_pairs)
        recent_orders = self.get_recent_orders(currency_pairs)
        trade_history = self.get_trade_history(currency_pairs)
        order_stats = self.calculate_order_stats(recent_orders, trade_history)
        
        return OrderDataInput(
            active_orders=active_orders,
            recent_orders=recent_orders,
            trade_history=trade_history,
            order_stats=order_stats,
            update_timestamp=datetime.now()
        )


class ExternalSignalCollector:
    """外部信号收集器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def collect_technical_signals(self, market_data: MarketDataInput) -> Dict[str, Decimal]:
        """收集技术指标信号（简化版）"""
        signals = {}
        
        for pair, ticker in market_data.tickers.items():
            # 简单的RSI信号（这里用价格变化模拟）
            if ticker.change_24h > Decimal('0.05'):
                signals[f"{pair}_trend"] = Decimal('0.8')  # 强上涨
            elif ticker.change_24h < Decimal('-0.05'):
                signals[f"{pair}_trend"] = Decimal('0.2')  # 强下跌
            else:
                signals[f"{pair}_trend"] = Decimal('0.5')  # 中性
                
        return signals
    
    def collect_external_signals(self, market_data: MarketDataInput) -> ExternalSignalInput:
        """收集外部信号"""
        market_signals = []
        technical_signals = self.collect_technical_signals(market_data)
        
        # 这里可以添加更多外部信号源
        # 比如新闻API、社交媒体情感分析等
        
        return ExternalSignalInput(
            market_signals=market_signals,
            news_sentiment=None,
            technical_signals=technical_signals,
            macro_indicators={},
            update_timestamp=datetime.now()
        )


class StrategyInputManager:
    """策略输入管理器 - 主要接口类"""
    
    def __init__(self, api_client, strategy_config: Dict):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个收集器
        self.market_collector = MarketDataCollector(api_client)
        self.account_collector = AccountDataCollector(api_client)
        self.order_collector = OrderDataCollector(api_client)
        self.signal_collector = ExternalSignalCollector()
        
        # 策略配置
        self.strategy_config = self._parse_strategy_config(strategy_config)
        
    def _parse_strategy_config(self, config: Dict) -> StrategyConfig:
        """解析策略配置"""
        validator = DataValidator()
        
        return StrategyConfig(
            strategy_name=config.get('strategy_name', 'default'),
            strategy_version=config.get('strategy_version', '1.0.0'),
            trading_pairs=config.get('trading_pairs', []),
            base_currency=config.get('base_currency', 'USDT'),
            max_position_size=validator.safe_decimal(config.get('max_position_size', '0.1')),
            min_order_size=validator.safe_decimal(config.get('min_order_size', '10')),
            decision_interval=config.get('decision_interval', 60),
            data_window=config.get('data_window', 100),
            strategy_params=config.get('strategy_params', {}),
            max_drawdown=validator.safe_decimal(config.get('max_drawdown', '0.1')),
            stop_loss=validator.safe_decimal(config.get('stop_loss')) if config.get('stop_loss') else None,
            take_profit=validator.safe_decimal(config.get('take_profit')) if config.get('take_profit') else None
        )
    
    def validate_data_completeness(self, strategy_input: StrategyInput) -> Dict[str, Decimal]:
        """验证数据完整性"""
        completeness = {}
        
        # 市场数据完整性
        market_score = Decimal('0')
        if strategy_input.market_data.tickers:
            market_score += Decimal('0.3')
        if strategy_input.market_data.orderbooks:
            market_score += Decimal('0.3')
        if strategy_input.market_data.recent_trades:
            market_score += Decimal('0.2')
        if strategy_input.market_data.candles:
            market_score += Decimal('0.2')
        completeness['market_data'] = market_score
        
        # 账户数据完整性
        account_score = Decimal('1.0') if strategy_input.account_data.spot_balances else Decimal('0.5')
        completeness['account_data'] = account_score
        
        # 订单数据完整性
        order_score = Decimal('1.0')  # 订单数据可以为空
        completeness['order_data'] = order_score
        
        # 外部信号完整性
        signal_score = Decimal('0.5') if strategy_input.external_signals.technical_signals else Decimal('0.3')
        completeness['external_signals'] = signal_score
        
        return completeness
    
    def collect_strategy_input(self, intervals: List[str] = None) -> StrategyInput:
        """收集完整的策略输入数据"""
        input_id = f"input_{int(time.time())}"
        collection_start = datetime.now()
        
        self.logger.info(f"Starting data collection for strategy input: {input_id}")
        
        try:
            # 收集各类数据
            market_data = self.market_collector.collect_market_data(
                self.strategy_config.trading_pairs, intervals
            )
            
            account_data = self.account_collector.collect_account_data(
                self.strategy_config.trading_pairs
            )
            
            order_data = self.order_collector.collect_order_data(
                self.strategy_config.trading_pairs
            )
            
            external_signals = self.signal_collector.collect_external_signals(market_data)
            
            # 配置数据
            config_input = ConfigInput(
                strategy_config=self.strategy_config,
                environment=os.getenv('TRADING_ENV', 'test'),
                debug_mode=os.getenv('DEBUG_MODE', 'true').lower() == 'true',
                logging_level=os.getenv('LOG_LEVEL', 'INFO'),
                config_timestamp=datetime.now()
            )
            
            collection_end = datetime.now()
            
            # 构建策略输入
            strategy_input = StrategyInput(
                market_data=market_data,
                account_data=account_data,
                order_data=order_data,
                config=config_input,
                external_signals=external_signals,
                input_id=input_id,
                collection_start_time=collection_start,
                collection_end_time=collection_end,
                data_completeness={}
            )
            
            # 验证数据完整性
            strategy_input.data_completeness = self.validate_data_completeness(strategy_input)
            
            self.logger.info(f"Data collection completed: {input_id}, duration: {(collection_end - collection_start).total_seconds():.2f}s")
            
            return strategy_input
            
        except Exception as e:
            self.logger.error(f"Failed to collect strategy input: {e}")
            raise
    
    def clean_and_validate_input(self, strategy_input: StrategyInput) -> StrategyInput:
        """清洗和验证输入数据"""
        self.logger.info("Cleaning and validating strategy input data")
        
        # 清洗市场数据
        cleaned_tickers = {}
        for pair, ticker in strategy_input.market_data.tickers.items():
            if (ticker.last_price > 0 and 
                ticker.bid_price > 0 and 
                ticker.ask_price > 0 and
                ticker.bid_price <= ticker.last_price <= ticker.ask_price):
                cleaned_tickers[pair] = ticker
            else:
                self.logger.warning(f"Invalid ticker data for {pair}")
        
        strategy_input.market_data.tickers = cleaned_tickers
        
        # 清洗订单簿数据
        cleaned_orderbooks = {}
        for pair, orderbook in strategy_input.market_data.orderbooks.items():
            valid_asks = [ask for ask in orderbook.asks if ask.price > 0 and ask.volume > 0]
            valid_bids = [bid for bid in orderbook.bids if bid.price > 0 and bid.volume > 0]
            
            if valid_asks and valid_bids:
                orderbook.asks = valid_asks
                orderbook.bids = valid_bids
                cleaned_orderbooks[pair] = orderbook
            else:
                self.logger.warning(f"Invalid orderbook data for {pair}")
        
        strategy_input.market_data.orderbooks = cleaned_orderbooks
        
        return strategy_input
    
    def get_data_quality_report(self, strategy_input: StrategyInput) -> Dict:
        """生成数据质量报告"""
        report = {
            'input_id': strategy_input.input_id,
            'collection_time': strategy_input.collection_end_time.isoformat(),
            'collection_duration': (strategy_input.collection_end_time - strategy_input.collection_start_time).total_seconds(),
            'data_completeness': {k: float(v) for k, v in strategy_input.data_completeness.items()},
            'data_quality': {}
        }
        
        # 市场数据质量
        market_quality = {
            'trading_pairs_coverage': len(strategy_input.market_data.tickers) / len(self.strategy_config.trading_pairs),
            'average_reliability': sum(strategy_input.market_data.data_reliability.values()) / len(strategy_input.market_data.data_reliability) if strategy_input.market_data.data_reliability else 0,
            'data_freshness': min((datetime.now() - ts).total_seconds() for ts in strategy_input.market_data.data_freshness.values()) if strategy_input.market_data.data_freshness else 0
        }
        report['data_quality']['market_data'] = market_quality
        
        # 账户数据质量
        account_quality = {
            'balance_currencies': len(strategy_input.account_data.spot_balances),
            'total_equity': float(strategy_input.account_data.total_equity),
            'risk_level': strategy_input.account_data.risk_level
        }
        report['data_quality']['account_data'] = account_quality
        
        # 订单数据质量
        order_quality = {
            'active_orders': len(strategy_input.order_data.active_orders),
            'recent_orders': len(strategy_input.order_data.recent_orders),
            'trade_history': len(strategy_input.order_data.trade_history)
        }
        report['data_quality']['order_data'] = order_quality
        
        return report


# ===== 配置文件管理 =====

class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件不存在: {self.config_file}")
            
        self.config.read(self.config_file, encoding='utf-8')
        
    def get_trading_pairs(self) -> List[str]:
        """获取交易对列表"""
        pairs_str = self.config.get('trading', 'trading_pairs', fallback='BTC_USDT,ETH_USDT')
        return [pair.strip() for pair in pairs_str.split(',')]
        
    def get_intervals(self) -> List[str]:
        """获取K线时间间隔列表"""
        intervals_str = self.config.get('trading', 'intervals', fallback='1m,5m,1h')
        return [interval.strip() for interval in intervals_str.split(',')]
        
    def get_strategy_config(self) -> Dict:
        """获取策略配置"""
        strategy_params = {}
        
        # 从strategy_params节获取参数
        if self.config.has_section('strategy_params'):
            for key, value in self.config.items('strategy_params'):
                # 尝试转换为数字类型
                try:
                    if '.' in value:
                        strategy_params[key] = float(value)
                    else:
                        strategy_params[key] = int(value)
                except ValueError:
                    strategy_params[key] = value
        
        config = {
            'strategy_name': self.config.get('strategy', 'strategy_name', fallback='default_strategy'),
            'strategy_version': self.config.get('strategy', 'strategy_version', fallback='1.0.0'),
            'trading_pairs': self.get_trading_pairs(),
            'base_currency': self.config.get('trading', 'base_currency', fallback='USDT'),
            'max_position_size': self.config.get('strategy', 'max_position_size', fallback='0.1'),
            'min_order_size': self.config.get('strategy', 'min_order_size', fallback='10'),
            'decision_interval': self.config.getint('strategy', 'decision_interval', fallback=60),
            'data_window': self.config.getint('strategy', 'data_window', fallback=100),
            'strategy_params': strategy_params,
            'max_drawdown': self.config.get('strategy', 'max_drawdown', fallback='0.05'),
            'stop_loss': self.config.get('strategy', 'stop_loss', fallback=None),
            'take_profit': self.config.get('strategy', 'take_profit', fallback=None)
        }
        
        return config
        
    def get_data_collection_config(self) -> Dict:
        """获取数据收集配置"""
        return {
            'orderbook_depth': self.config.getint('data_collection', 'orderbook_depth', fallback=20),
            'trades_limit': self.config.getint('data_collection', 'trades_limit', fallback=100),
            'candles_limit': self.config.getint('data_collection', 'candles_limit', fallback=200),
            'orders_limit': self.config.getint('data_collection', 'orders_limit', fallback=100)
        }
        
    def get_environment_config(self) -> Dict:
        """获取环境配置"""
        return {
            'trading_env': self.config.get('environment', 'trading_env', fallback='test'),
            'debug_mode': self.config.getboolean('environment', 'debug_mode', fallback=True),
            'log_level': self.config.get('environment', 'log_level', fallback='INFO'),
            'enable_trading': self.config.getboolean('environment', 'enable_trading', fallback=False)
        }
        
    def get_risk_config(self) -> Dict:
        """获取风险管理配置"""
        return {
            'max_daily_loss': self.config.get('risk_management', 'max_daily_loss', fallback='0.02'),
            'max_positions': self.config.getint('risk_management', 'max_positions', fallback=3),
            'max_order_amount': self.config.get('risk_management', 'max_order_amount', fallback='100'),
            'risk_threshold_medium': self.config.get('risk_management', 'risk_threshold_medium', fallback='0.5'),
            'risk_threshold_high': self.config.get('risk_management', 'risk_threshold_high', fallback='0.8')
        }
        
    def update_config(self, section: str, key: str, value: str):
        """更新配置"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

def create_strategy_input_manager_from_config(config_file: str = "config.ini") -> StrategyInputManager:
    """从配置文件创建策略输入管理器"""
    
    # 加载配置
    config_manager = ConfigManager(config_file)
    strategy_config = config_manager.get_strategy_config()
    
    # 创建API客户端
    configuration = gate_api.Configuration(host="https://api.gateio.ws/api/v4")
    configuration.key = os.getenv("GATEIO_API_KEY")
    configuration.secret = os.getenv("GATEIO_API_SECRET")
    api_client = gate_api.ApiClient(configuration)
    
    return StrategyInputManager(api_client, strategy_config)


# ===== 使用示例 =====

def create_strategy_input_manager(config: Dict = None) -> StrategyInputManager:
    """创建策略输入管理器的工厂函数（向后兼容）"""
    
    # 默认配置
    if config is None:
        config = {
            'strategy_name': 'demo_strategy',
            'strategy_version': '1.0.0',
            'trading_pairs': ['BTC_USDT', 'ETH_USDT'],
            'base_currency': 'USDT',
            'max_position_size': '0.1',
            'min_order_size': '10',
            'decision_interval': 60,
            'data_window': 100,
            'strategy_params': {
                'rsi_period': 14,
                'ma_period': 20
            },
            'max_drawdown': '0.05',
            'stop_loss': '0.02',
            'take_profit': '0.04'
        }
    
    # 创建API客户端
    configuration = gate_api.Configuration(host="https://api.gateio.ws/api/v4")
    configuration.key = os.getenv("GATEIO_API_KEY")
    configuration.secret = os.getenv("GATEIO_API_SECRET")
    api_client = gate_api.ApiClient(configuration)
    
    return StrategyInputManager(api_client, config)

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 示例使用
    try:
        manager = create_strategy_input_manager_from_config()
        strategy_input = manager.collect_strategy_input(['1m', '5m', '1h'])
        
        # 清洗和验证数据
        clean_input = manager.clean_and_validate_input(strategy_input)
        
        # 生成质量报告
        quality_report = manager.get_data_quality_report(clean_input)
        
        print(f"Strategy Input ID: {clean_input.input_id}")
        print(f"Data Completeness: {clean_input.data_completeness}")
        print(f"Quality Report: {quality_report}")
        
    except Exception as e:
        print(f"Error: {e}") 