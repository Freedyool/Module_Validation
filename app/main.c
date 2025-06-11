/*
 * ������������Ӳ�������������չ����Ӳ�����Ϲ���ȫ����Դ
 * �����������www.lckfb.com
 * ����֧�ֳ�פ��̳���κμ������⻶ӭ��ʱ����ѧϰ
 * ������̳��https://oshwhub.com/forum
 * ��עbilibili�˺ţ������������塿���������ǵ����¶�̬��
 * ��������׬Ǯ���������й�����ʦΪ����
 * 

 Change Logs:
 * Date           Author       Notes
 * 2024-03-07     LCKFB-LP    first version
 */
#include "board.h"
#include "bsp_uart.h"
#include "bsp_dbg.h"
#include "driver_ina226_basic.h"
#include "driver_ina226_shot.h"
#include <stdio.h>

int32_t ina226_poll(uint32_t times);

int main(void)
{
	
	board_init();
	
	uart1_init(115200U);

	dbg_init();

	GPIO_InitTypeDef  GPIO_InitStructure;
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);

	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
	GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_100MHz;
	GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
	GPIO_Init(GPIOB, &GPIO_InitStructure);

	ina226_basic_init(INA226_ADDRESS_0, 0.1);

	while(1)
	{
		GPIO_SetBits(GPIOB, GPIO_Pin_2);
		// delay_ms(500);

		ina226_poll(10);

		GPIO_ResetBits(GPIOB, GPIO_Pin_2);
		delay_ms(100);
	}
}

int32_t ina226_poll(uint32_t times)
{
	uint32_t i;
	uint8_t res;

	for (i = 0; i < times; i++)
	{
		float mV;
		float mA;
		float mW;

		res = ina226_basic_read(&mV, &mA, &mW);
		if (res != 0)
		{
			(void)ina226_basic_deinit();

			return 1;
		}

		uart1_send_raw((uint8_t *)&mV, sizeof(mV));
		uart1_send_raw((uint8_t *)&mA, sizeof(mA));
		uart1_send_raw((uint8_t *)&mW, sizeof(mW));
		uart1_send_raw((uint8_t *)&i, sizeof(i));
		
		// ina226_interface_delay_ms(50);
	}

	return 0;
}