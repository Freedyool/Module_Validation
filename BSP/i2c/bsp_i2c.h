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


#define RCC_I2C_ENABLE()  __RCC_GPIOB_CLK_ENABLE()
#define PORT_I2C         	CW_GPIOB

#define GPIO_SCL         	GPIO_PIN_10
#define GPIO_SDA         	GPIO_PIN_11

// 上拉输入模式
#define SDA_IN() 	{	GPIO_InitTypeDef	GPIO_InitStruct; 				\
						GPIO_InitStruct.Pins = GPIO_SDA;					\
						GPIO_InitStruct.Mode = GPIO_MODE_INPUT_PULLUP;		\
						GPIO_InitStruct.Speed = GPIO_SPEED_HIGH;			\
						GPIO_Init(PORT_I2C, &GPIO_InitStruct);				\
					}
// 开漏输出
#define SDA_OUT() 	{	GPIO_InitTypeDef	GPIO_InitStruct; 				\
						GPIO_InitStruct.Pins = GPIO_SDA;					\
						GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;			\
						GPIO_InitStruct.Speed = GPIO_SPEED_HIGH;			\
						GPIO_Init(PORT_I2C, &GPIO_InitStruct);				\
					}

#define SCL(BIT)  	GPIO_WritePin(PORT_I2C, GPIO_SCL, BIT?GPIO_Pin_SET:GPIO_Pin_RESET)
#define SDA(BIT)  	GPIO_WritePin(PORT_I2C, GPIO_SDA, BIT?GPIO_Pin_SET:GPIO_Pin_RESET)
#define SDA_GET() 	GPIO_ReadPin(PORT_I2C, GPIO_SDA)


void I2C_GPIO_INIT(void);
void I2C_GPIO_DEINIT(void);
void IIC_Start(void);
void IIC_Stop(void);
void IIC_Send_Ack(uint8_t ack);
uint8_t IIC_Wait_Ack(void);
void IIC_Write(uint8_t data);
uint8_t IIC_Read(void);



#endif
