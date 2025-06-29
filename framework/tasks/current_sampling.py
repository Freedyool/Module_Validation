"""
电流采样任务实现

实现定时电流采样功能，支持高精度定时和数据记录
"""

import time
import threading
import sys
import os
from typing import Dict, Any, List
import logging

# 相对导入父级模块
from ..interfaces import TaskInterface, AdapterInterface, ModuleInterface

logger = logging.getLogger(__name__)


class CurrentSamplingTask(TaskInterface):
    """电流采样任务"""
    
    def __init__(self, adapter: AdapterInterface, module: ModuleInterface):
        super().__init__(adapter, module)
        self.name = "Current Sampling Task"
        self.is_running = False
        self.stop_event = threading.Event()
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行电流采样任务
        
        Args:
            duration_s: 采样持续时间(秒)，默认1秒
            interval_ms: 采样间隔(毫秒)，默认1毫秒
            channels: 采样通道列表，None表示所有通道
            
        Returns:
            Dict[str, Any]: 采样结果
        """
        # 获取参数
        duration_s = kwargs.get("duration_s", 1.0)
        interval_ms = kwargs.get("interval_ms", 1.0)
        channels = kwargs.get("channels", None)
        
        logger.info(f"开始电流采样任务: 持续{duration_s}秒, 间隔{interval_ms}ms")
        
        # 验证参数
        if duration_s <= 0 or interval_ms <= 0:
            return {
                "success": False,
                "error": "无效的采样参数",
                "data": None
            }
        
        # 检查模组是否已初始化
        if not self.module.is_initialized:
            logger.info("初始化模组...")
            if not self.module.initialize():
                return {
                    "success": False,
                    "error": "模组初始化失败",
                    "data": None
                }
        
        # 执行采样
        try:
            self.is_running = True
            self.stop_event.clear()
            
            start_time = time.time()
            end_time = start_time + duration_s
            interval_s = interval_ms / 1000.0
            
            samples = []
            sample_count = 0
            total_samples = int(duration_s / interval_s)
            
            logger.info(f"预计采样 {total_samples} 个数据点")
            
            # 首次采样获取通道信息
            if channels is None:
                first_sample = self.module.read_current()
                if isinstance(first_sample, list):
                    num_channels = len(first_sample)
                    channels = list(range(1, num_channels + 1))
                else:
                    channels = [1]
            
            # 采样循环
            while time.time() < end_time and not self.stop_event.is_set():
                sample_start = time.time()
                
                # 读取数据
                if len(channels) == 1:
                    current = self.module.read_current(channels[0])
                    voltage = self.module.read_voltage(channels[0]) 
                    power = self.module.read_power(channels[0])
                    
                    sample_data = {
                        "timestamp": sample_start,
                        "relative_time": sample_start - start_time,
                        "channel": channels[0],
                        "current": current,
                        "voltage": voltage,
                        "power": power
                    }
                else:
                    # 多通道采样
                    currents = self.module.read_current()
                    voltages = self.module.read_voltage()
                    powers = self.module.read_power()
                    
                    sample_data = {
                        "timestamp": sample_start,
                        "relative_time": sample_start - start_time,
                        "channels": {}
                    }
                    
                    for i, ch in enumerate(channels):
                        if i < len(currents):
                            sample_data["channels"][ch] = {
                                "current": currents[i],
                                "voltage": voltages[i] if i < len(voltages) else None,
                                "power": powers[i] if i < len(powers) else None
                            }
                
                samples.append(sample_data)
                sample_count += 1
                
                # 计算下次采样时间
                next_sample_time = start_time + sample_count * interval_s
                sleep_time = max(0, next_sample_time - time.time())
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                # 进度输出（每100个样本或最后一个样本）
                if sample_count % 100 == 0 or time.time() >= end_time:
                    progress = min(100, (time.time() - start_time) / duration_s * 100)
                    logger.info(f"采样进度: {progress:.1f}% ({sample_count}/{total_samples})")
            
            # 计算统计信息
            actual_duration = time.time() - start_time
            actual_rate = sample_count / actual_duration if actual_duration > 0 else 0
            target_rate = 1000.0 / interval_ms
            
            result = {
                "success": True,
                "error": None,
                "data": {
                    "samples": samples,
                    "statistics": {
                        "total_samples": sample_count,
                        "target_samples": total_samples,
                        "actual_duration": actual_duration,
                        "target_duration": duration_s,
                        "actual_sample_rate": actual_rate,
                        "target_sample_rate": target_rate,
                        "timing_accuracy": actual_rate / target_rate if target_rate > 0 else 0,
                        "channels": channels
                    }
                }
            }
            
            logger.info(f"采样完成: {sample_count}个样本, 平均速率{actual_rate:.1f}Hz")
            return result
            
        except Exception as e:
            logger.error(f"采样过程中出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
        finally:
            self.is_running = False
    
    def stop(self):
        """停止采样任务"""
        if self.is_running:
            logger.info("停止采样任务...")
            self.stop_event.set()
    
    def print_results(self, result: Dict[str, Any]):
        """打印采样结果
        
        Args:
            result: execute方法返回的结果
        """
        if not result["success"]:
            print(f"采样失败: {result['error']}")
            return
        
        data = result["data"]
        samples = data["samples"]
        stats = data["statistics"]
        
        print(f"\n{'='*60}")
        print(f"电流采样结果")
        print(f"{'='*60}")
        
        # 打印统计信息
        print(f"采样统计:")
        print(f"  目标样本数: {stats['target_samples']}")
        print(f"  实际样本数: {stats['total_samples']}")
        print(f"  目标持续时间: {stats['target_duration']:.3f}秒")
        print(f"  实际持续时间: {stats['actual_duration']:.3f}秒")
        print(f"  目标采样率: {stats['target_sample_rate']:.1f}Hz")
        print(f"  实际采样率: {stats['actual_sample_rate']:.1f}Hz")
        print(f"  定时精度: {stats['timing_accuracy']*100:.1f}%")
        print(f"  采样通道: {stats['channels']}")
        
        if not samples:
            print("没有采样数据")
            return
        
        # 判断单通道还是多通道
        is_multi_channel = "channels" in samples[0]
        
        if is_multi_channel:
            # 多通道数据
            channels = stats["channels"]
            
            # 计算每个通道的统计信息
            for ch in channels:
                print(f"\n通道 {ch} 统计:")
                currents = [s["channels"][ch]["current"] for s in samples if s["channels"][ch]["current"] is not None]
                voltages = [s["channels"][ch]["voltage"] for s in samples if s["channels"][ch]["voltage"] is not None]
                powers = [s["channels"][ch]["power"] for s in samples if s["channels"][ch]["power"] is not None]
                
                if currents:
                    print(f"  电流: 最小={min(currents)*1000:.3f}mA, 最大={max(currents)*1000:.3f}mA, 平均={sum(currents)/len(currents)*1000:.3f}mA")
                if voltages:
                    print(f"  电压: 最小={min(voltages):.3f}V, 最大={max(voltages):.3f}V, 平均={sum(voltages)/len(voltages):.3f}V")
                if powers:
                    print(f"  功率: 最小={min(powers)*1000:.3f}mW, 最大={max(powers)*1000:.3f}mW, 平均={sum(powers)/len(powers)*1000:.3f}mW")
            
            # 打印部分样本数据
            print(f"\n前10个样本 (共{len(samples)}个):")
            print(f"{'时间(ms)':>8} {'通道':>4} {'电流(mA)':>10} {'电压(V)':>8} {'功率(mW)':>10}")
            print("-" * 50)
            
            for i, sample in enumerate(samples[:10]):
                time_ms = sample["relative_time"] * 1000
                for ch in channels:
                    ch_data = sample["channels"][ch]
                    current_ma = ch_data["current"] * 1000 if ch_data["current"] is not None else 0
                    voltage_v = ch_data["voltage"] if ch_data["voltage"] is not None else 0
                    power_mw = ch_data["power"] * 1000 if ch_data["power"] is not None else 0
                    
                    print(f"{time_ms:8.1f} {ch:4d} {current_ma:10.3f} {voltage_v:8.3f} {power_mw:10.3f}")
        else:
            # 单通道数据
            channel = samples[0]["channel"]
            currents = [s["current"] for s in samples if s["current"] is not None]
            voltages = [s["voltage"] for s in samples if s["voltage"] is not None]
            powers = [s["power"] for s in samples if s["power"] is not None]
            
            print(f"\n通道 {channel} 统计:")
            if currents:
                print(f"  电流: 最小={min(currents)*1000:.3f}mA, 最大={max(currents)*1000:.3f}mA, 平均={sum(currents)/len(currents)*1000:.3f}mA")
            if voltages:
                print(f"  电压: 最小={min(voltages):.3f}V, 最大={max(voltages):.3f}V, 平均={sum(voltages)/len(voltages):.3f}V")
            if powers:
                print(f"  功率: 最小={min(powers)*1000:.3f}mW, 最大={max(powers)*1000:.3f}mW, 平均={sum(powers)/len(powers)*1000:.3f}mW")
            
            # 打印部分样本数据
            print(f"\n前10个样本 (共{len(samples)}个):")
            print(f"{'时间(ms)':>8} {'电流(mA)':>10} {'电压(V)':>8} {'功率(mW)':>10}")
            print("-" * 40)
            
            for sample in samples[:10]:
                time_ms = sample["relative_time"] * 1000
                current_ma = sample["current"] * 1000 if sample["current"] is not None else 0
                voltage_v = sample["voltage"] if sample["voltage"] is not None else 0
                power_mw = sample["power"] * 1000 if sample["power"] is not None else 0
                
                print(f"{time_ms:8.1f} {current_ma:10.3f} {voltage_v:8.3f} {power_mw:10.3f}")
        
        if len(samples) > 10:
            print(f"... 还有 {len(samples) - 10} 个样本")
        
        print(f"{'='*60}")
