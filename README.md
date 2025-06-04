# Module_Validation

基于 [正点原子·潘多拉 IoT 开发板](http://47.111.11.73/docs/boards/iot/zdyz_panduola.html) 的模块验证工程。

## 参考资料

- [RT-Thread 潘多拉 STM32L475 上手指南](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/tutorial/quick-start/iot_board/quick-start)
- [RT-Thread IoT-Board SDK](https://github.com/RT-Thread/IoT_Board)

## 环境搭建

- **Windows 用户**请参考：[使用 VS Code 开发 RT-Thread](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/application-note/setup/qemu/vscode/an0021-qemu-vscode)
- **Ubuntu 用户**请参考：[在 Ubuntu 平台开发 RT-Thread](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/application-note/setup/qemu/ubuntu/an0005-qemu-ubuntu)

> 注：仅在实体板上运行固件时，无需安装 QEMU。

## 烧录说明

1. 推荐使用板载 ST-Link，无需额外硬件即可下载固件。
2. 本仓库采用 Raspberry Pi 作为开发环境，需借助 [st-flash](https://github.com/stlink-org/stlink/tree/testing) 工具烧录 STM32L475。

烧录步骤示例：

```sh
# 进入示例工程目录
cd projects/hello_led

# 编译工程
scons -j8

# 烧录固件到开发板
st-flash --debug write rt-thread.bin 0x08000000
```

## 开始实验

请根据上述步骤完成环境搭建与固件烧录，后续可根据项目需求进行实验与开发。

