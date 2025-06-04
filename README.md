# Module_Validation

[正点原子·潘多拉IoT开发板](http://47.111.11.73/docs/boards/iot/zdyz_panduola.html)

参考资料：
[RT-Thread 潘多拉 STM32L475 上手指南](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/tutorial/quick-start/iot_board/quick-start)
[RT-Thread IoT-Board SDK](https://github.com/RT-Thread/IoT_Board)

## 环境搭建

- Windows 用户请参考：[使用 VS Code 开发 RT-Thread](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/application-note/setup/qemu/vscode/an0021-qemu-vscode)
- Ubuntu 用户请参考：[在 Ubuntu 平台开发 RT-Thread](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/application-note/setup/qemu/ubuntu/an0005-qemu-ubuntu)

注：如果只想在实体板子上运行固件，则无需安装 qemu；

烧录注意事项：

1. 烧录工具推荐使用板载的 stlink，无需其它硬件即可完成固件下载；
2. 由于本仓库使用 raspberry pi 开发环境，需要借助 [st-flash](https://github.com/stlink-org/stlink/tree/testing) 工具以实现对 STM32L475 的烧录；

## 开始实验

