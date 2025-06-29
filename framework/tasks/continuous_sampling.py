"""
连续采样任务实现

实现连续循环采样功能，支持用户交互终止
"""

import time
import threading
import sys
import os
import select
from typing import Dict, Any, List
import logging

# 相对导入父级模块
from ..interfaces import TaskInterface, AdapterInterface, ModuleInterface

logger = logging.getLogger(__name__)


class ContinuousSamplingTask(TaskInterface):
    """连续采样任务"""
    
    def __init__(self, adapter: AdapterInterface, module: ModuleInterface):
        super().__init__(adapter, module)
        self.name = "Continuous Sampling Task"
        self.is_running = False
        self.stop_event = threading.Event()
        self.sample_count = 0
        self.start_time = None
        
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行连续采样任务
        
        Args:
            interval_ms: 采样间隔(毫秒)，默认1000ms
            channels: 采样通道列表，None表示所有通道
            display_samples: 是否实时显示采样数据，默认True
            
        Returns:
            Dict[str, Any]: 采样结果
        """
        # 获取参数
        interval_ms = kwargs.get("interval_ms", 1000.0)
        channels = kwargs.get("channels", None)
        display_samples = kwargs.get("display_samples", True)
        
        logger.info(f"开始连续采样任务: 间隔{interval_ms}ms")
        
        # 验证参数
        if interval_ms <= 0:
            return {
                "success": False,
                "error": "无效的采样间隔",
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
            self.sample_count = 0
            self.start_time = time.time()
            
            interval_s = interval_ms / 1000.0
            samples = []
            
            # 首次采样获取通道信息
            if channels is None:
                first_sample = self.module.read_current()
                if isinstance(first_sample, list):
                    num_channels = len(first_sample)
                    channels = list(range(1, num_channels + 1))
                else:
                    channels = [1]
            
            print(f"\n{'='*80}")
            print(f"连续采样模式启动 - 采样间隔: {interval_ms}ms")
            print(f"采样通道: {channels}")
            print(f"按 'q' + Enter 停止采样，按 's' + Enter 显示统计信息")
            print(f"{'='*80}")
            
            if display_samples:
                self._print_header(channels)
            
            # 启动用户输入监听线程
            input_thread = threading.Thread(target=self._input_listener, daemon=True)
            input_thread.start()
            
            # 采样循环
            next_sample_time = self.start_time
            
            while not self.stop_event.is_set():
                sample_start = time.time()
                
                # 读取数据
                sample_data = self._read_sample_data(channels, sample_start)
                
                if sample_data:
                    samples.append(sample_data)
                    self.sample_count += 1
                    
                    # 实时显示数据
                    if display_samples:
                        self._print_sample(sample_data, channels)
                    
                    # 限制内存中保存的样本数量
                    if len(samples) > 10000:  # 保留最近10000个样本
                        samples.pop(0)
                
                # 计算下次采样时间
                next_sample_time += interval_s
                sleep_time = max(0, next_sample_time - time.time())
                
                if sleep_time > 0:
                    # 使用较小的睡眠间隔以提高响应性
                    sleep_steps = max(1, int(sleep_time / 0.1))
                    step_sleep = sleep_time / sleep_steps
                    
                    for _ in range(sleep_steps):
                        if self.stop_event.is_set():
                            break
                        time.sleep(step_sleep)
            
            # 计算统计信息
            actual_duration = time.time() - self.start_time
            actual_rate = self.sample_count / actual_duration if actual_duration > 0 else 0
            target_rate = 1000.0 / interval_ms
            
            result = {
                "success": True,
                "error": None,
                "data": {
                    "samples": samples,
                    "statistics": {
                        "total_samples": self.sample_count,
                        "actual_duration": actual_duration,
                        "actual_sample_rate": actual_rate,
                        "target_sample_rate": target_rate,
                        "timing_accuracy": actual_rate / target_rate if target_rate > 0 else 0,
                        "channels": channels
                    }
                }
            }
            
            print(f"\n{'='*80}")
            print(f"连续采样已停止")
            print(f"总采样数: {self.sample_count}, 持续时间: {actual_duration:.1f}秒")
            print(f"平均采样率: {actual_rate:.2f}Hz (目标: {target_rate:.2f}Hz)")
            print(f"{'='*80}")
            
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
    
    def _read_sample_data(self, channels: List[int], timestamp: float) -> Dict[str, Any]:
        """读取单次采样数据"""
        try:
            if len(channels) == 1:
                current = self.module.read_current(channels[0])
                voltage = self.module.read_voltage(channels[0]) 
                power = self.module.read_power(channels[0])
                
                return {
                    "timestamp": timestamp,
                    "relative_time": timestamp - self.start_time,
                    "sample_count": self.sample_count + 1,
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
                    "timestamp": timestamp,
                    "relative_time": timestamp - self.start_time,
                    "sample_count": self.sample_count + 1,
                    "channels": {}
                }
                
                for i, ch in enumerate(channels):
                    if i < len(currents):
                        sample_data["channels"][ch] = {
                            "current": currents[i],
                            "voltage": voltages[i] if i < len(voltages) else None,
                            "power": powers[i] if i < len(powers) else None
                        }
                
                return sample_data
                
        except Exception as e:
            logger.error(f"读取采样数据失败: {e}")
            return None
    
    def _print_header(self, channels: List[int]):
        """打印表头"""
        if len(channels) == 1:
            print(f"{'样本#':>8} {'时间(s)':>10} {'电流(mA)':>12} {'电压(V)':>10} {'功率(mW)':>12}")
            print("-" * 62)
        else:
            header = f"{'样本#':>8} {'时间(s)':>10}"
            for ch in channels:
                header += f" {'CH'+str(ch)+'(mA)':>10} {'CH'+str(ch)+'(V)':>9} {'CH'+str(ch)+'(mW)':>10}"
            print(header)
            print("-" * len(header))
    
    def _print_sample(self, sample_data: Dict[str, Any], channels: List[int]):
        """打印采样数据"""
        if len(channels) == 1:
            current_ma = sample_data["current"] * 1000 if sample_data["current"] is not None else 0
            voltage_v = sample_data["voltage"] if sample_data["voltage"] is not None else 0
            power_mw = sample_data["power"] * 1000 if sample_data["power"] is not None else 0
            
            print(f"{sample_data['sample_count']:8d} {sample_data['relative_time']:10.2f} "
                  f"{current_ma:12.3f} {voltage_v:10.3f} {power_mw:12.3f}")
        else:
            line = f"{sample_data['sample_count']:8d} {sample_data['relative_time']:10.2f}"
            for ch in channels:
                if ch in sample_data["channels"]:
                    ch_data = sample_data["channels"][ch]
                    current_ma = ch_data["current"] * 1000 if ch_data["current"] is not None else 0
                    voltage_v = ch_data["voltage"] if ch_data["voltage"] is not None else 0
                    power_mw = ch_data["power"] * 1000 if ch_data["power"] is not None else 0
                    line += f" {current_ma:10.3f} {voltage_v:9.3f} {power_mw:10.3f}"
                else:
                    line += " " + " "*29
            print(line)
    
    def _input_listener(self):
        """监听用户输入"""
        try:
            while self.is_running and not self.stop_event.is_set():
                try:
                    # 在Windows上使用不同的方法
                    if os.name == 'nt':
                        import msvcrt
                        if msvcrt.kbhit():
                            key = msvcrt.getch().decode('utf-8').lower()
                            if key == 'q':
                                print("\n检测到 'q' 按键，正在停止采样...")
                                self.stop_event.set()
                                break
                            elif key == 's':
                                self._print_current_statistics()
                    else:
                        # Unix/Linux系统
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            line = sys.stdin.readline().strip().lower()
                            if line == 'q':
                                print("检测到 'q' 命令，正在停止采样...")
                                self.stop_event.set()
                                break
                            elif line == 's':
                                self._print_current_statistics()
                    
                    time.sleep(0.1)
                except:
                    # 如果输入监听失败，回退到简单的计时器
                    time.sleep(1)
                    
        except Exception as e:
            logger.debug(f"输入监听线程异常: {e}")
    
    def _print_current_statistics(self):
        """打印当前统计信息"""
        if self.start_time:
            duration = time.time() - self.start_time
            rate = self.sample_count / duration if duration > 0 else 0
            
            print(f"\n--- 当前统计 (运行时间: {duration:.1f}s) ---")
            print(f"采样数: {self.sample_count}")
            print(f"采样率: {rate:.2f} Hz")
            print(f"--- 按 'q' 停止，按 's' 显示统计 ---\n")
    
    def stop(self):
        """停止采样任务"""
        if self.is_running:
            logger.info("停止连续采样任务...")
            self.stop_event.set()
    
    def print_results(self, result: Dict[str, Any]):
        """打印采样结果摘要"""
        if not result["success"]:
            print(f"采样失败: {result['error']}")
            return
        
        data = result["data"]
        samples = data["samples"]
        stats = data["statistics"]
        
        print(f"\n{'='*60}")
        print(f"连续采样结果摘要")
        print(f"{'='*60}")
        
        # 打印统计信息
        print(f"采样统计:")
        print(f"  总采样数: {stats['total_samples']}")
        print(f"  运行时间: {stats['actual_duration']:.3f}秒")
        print(f"  目标采样率: {stats['target_sample_rate']:.1f}Hz")
        print(f"  实际采样率: {stats['actual_sample_rate']:.1f}Hz")
        print(f"  定时精度: {stats['timing_accuracy']*100:.1f}%")
        print(f"  采样通道: {stats['channels']}")
        
        if not samples:
            print("没有采样数据")
            return
        
        # 计算数据统计
        is_multi_channel = "channels" in samples[0]
        
        if is_multi_channel:
            # 多通道数据统计
            channels = stats["channels"]
            
            for ch in channels:
                print(f"\n通道 {ch} 统计 (最近 {len(samples)} 个样本):")
                currents = [s["channels"][ch]["current"] for s in samples 
                           if ch in s["channels"] and s["channels"][ch]["current"] is not None]
                voltages = [s["channels"][ch]["voltage"] for s in samples 
                           if ch in s["channels"] and s["channels"][ch]["voltage"] is not None]
                powers = [s["channels"][ch]["power"] for s in samples 
                         if ch in s["channels"] and s["channels"][ch]["power"] is not None]
                
                if currents:
                    print(f"  电流: 最小={min(currents)*1000:.3f}mA, 最大={max(currents)*1000:.3f}mA, 平均={sum(currents)/len(currents)*1000:.3f}mA")
                if voltages:
                    print(f"  电压: 最小={min(voltages):.3f}V, 最大={max(voltages):.3f}V, 平均={sum(voltages)/len(voltages):.3f}V")
                if powers:
                    print(f"  功率: 最小={min(powers)*1000:.3f}mW, 最大={max(powers)*1000:.3f}mW, 平均={sum(powers)/len(powers)*1000:.3f}mW")
        else:
            # 单通道数据统计
            channel = samples[0]["channel"]
            currents = [s["current"] for s in samples if s["current"] is not None]
            voltages = [s["voltage"] for s in samples if s["voltage"] is not None]
            powers = [s["power"] for s in samples if s["power"] is not None]
            
            print(f"\n通道 {channel} 统计 (最近 {len(samples)} 个样本):")
            if currents:
                print(f"  电流: 最小={min(currents)*1000:.3f}mA, 最大={max(currents)*1000:.3f}mA, 平均={sum(currents)/len(currents)*1000:.3f}mA")
            if voltages:
                print(f"  电压: 最小={min(voltages):.3f}V, 最大={max(voltages):.3f}V, 平均={sum(voltages)/len(voltages):.3f}V")
            if powers:
                print(f"  功率: 最小={min(powers)*1000:.3f}mW, 最大={max(powers)*1000:.3f}mW, 平均={sum(powers)/len(powers)*1000:.3f}mW")
        
        print(f"{'='*60}")
