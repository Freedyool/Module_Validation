/*
 * 立创开发板软硬件资料与相关扩展板软硬件资料官网全部开源
 * 开发板官网：www.lckfb.com
 * 技术支持常驻论坛，任何技术问题欢迎随时交流学习
 * 立创论坛：https://oshwhub.com/forum
 * 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
 * 不靠卖板赚钱，以培养中国工程师为己任
 * Change Logs:
 * Date           Author       Notes
 * 2025-05-30     FreedYool    first version
 */
#ifndef __BSP_I2C_H__
#define __BSP_I2C_H__

#include "board.h"

#define RCC_I2C_ENABLE()    __RCC_GPIOB_CLK_ENABLE(); \
                            __RCC_I2C1_CLK_ENABLE()
#define RCC_DBG_ENABLE()    __RCC_GPIOA_CLK_ENABLE()

#define I2C_PORT            CW_I2C1
#define I2C_Deinit()        I2C1_DeInit()

#define GPIO_PORT_I2C       CW_GPIOB
#define GPIO_SCL         	GPIO_PIN_10
#define GPIO_SDA         	GPIO_PIN_11

#define GPIO_PORT_DBG       CW_GPIOA
#define GPIO_DBG            GPIO_PIN_0
#define DBG(BIT)  	        GPIO_WritePin(GPIO_PORT_DBG, GPIO_DBG, BIT?GPIO_Pin_SET:GPIO_Pin_RESET)

void IIC_INIT(void);
void IIC_DEINIT(void);
uint8_t IIC_Read(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len);
uint8_t IIC_Write(uint8_t addr, uint8_t reg, uint8_t *buf, uint16_t len);



#endif
