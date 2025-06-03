/*
 * 立创开发板软硬件资料与相关扩展板软硬件资料官网全部开源
 * 开发板官网：www.lckfb.com
 * 技术支持常驻论坛，任何技术问题欢迎随时交流学习
 * 立创论坛：https://oshwhub.com/forum
 * 关注bilibili账号：【立创开发板】，掌握我们的最新动态！
 * 不靠卖板赚钱，以培养中国工程师为己任
 * 

 Change Logs:
 * Date           Author       Notes
 * 2024-03-07     LCKFB-LP    first version
 */
 
#include "bsp_dbg.h" 
#include "stdio.h"

void dbg_init(void)
{
	GPIO_InitTypeDef GPIO_InitStructure;	

	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);	

	GPIO_StructInit(&GPIO_InitStructure);
	GPIO_InitStructure.GPIO_Pin           = GPIO_Pin_4;//TX引脚
	GPIO_InitStructure.GPIO_Mode          = GPIO_Mode_OUT;//IO口用作串口引脚要配置复用模式
	GPIO_InitStructure.GPIO_Speed         = GPIO_Speed_100MHz;
	GPIO_InitStructure.GPIO_OType         = GPIO_OType_PP;
	GPIO_InitStructure.GPIO_PuPd          = GPIO_PuPd_NOPULL;
	GPIO_Init(GPIOB,&GPIO_InitStructure);
}

void dbg_set(u8 state)
{
    if (state)
    {
        GPIO_SetBits(GPIOB, GPIO_Pin_4);
    }
    else
    {
        GPIO_ResetBits(GPIOB, GPIO_Pin_4);
    }
}