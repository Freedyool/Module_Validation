# Module_Validation

立创·地文星CW32F030C8T6开发板

## 环境搭建

推荐使用 vscode 打开根目录并安装 [EIDE](https://marketplace.visualstudio.com/items?itemName=CL.eide) 插件打开本项目；

项目预设的编译工具为：AC5 编译器；
项目预设的烧录工具为：DAP-Link + uv4；

烧录注意事项：

1. cw32f030 暂时没有适用于 OpenOCD 的官方 target 脚本，故不支持 OpenOCD 烧录；
2. 本项目使用脚本调用 uv4.exe 实现固件烧录，命令参见 `.eide/eide.json` 中的 `uploadConfig` 字段；
3. 烧录工具使用的是网购的 DAP-Link 模块连接 `CW32F030` 的 `GND`、`CLK`、`DIO` 和 `5V` pin 脚；
4. 更多烧录方式请参考 [LC-DWX](https://wiki.lckfb.com/zh-hans/dwx-cw32f030c8t6/beginner)；
