#ifndef F_CPU
#define F_CPU 1000000UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <stdio.h>

// --- 安全版 I2C Functions ---
// タイムアウト付きの待機処理
uint8_t i2c_wait(void) {
    uint16_t timeout = 2000; // 約数ms
    while (!(TWCR & (1 << TWINT))) {
        if (--timeout == 0) return 1; // 失敗
    }
    return 0;
}

void i2c_init(void) {
    TWBR = 32;
    TWSR = (1 << TWPS0);
}

uint8_t i2c_start(void) {
    TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN);
    return i2c_wait();
}

void i2c_stop(void) {
    TWCR = (1 << TWINT) | (1 << TWSTO) | (1 << TWEN);
}

uint8_t i2c_write(uint8_t data) {
    TWDR = data;
    TWCR = (1 << TWINT) | (1 << TWEN);
    return i2c_wait();
}

uint8_t i2c_read(uint8_t ack) {
    TWCR = (1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0);
    if (i2c_wait()) return 0;
    return TWDR;
}

// --- AHT25 (安全版) ---
uint8_t aht25_read(float *temp, float *humi) {
    uint8_t data[6];

    // 測定開始
    if (i2c_start()) return 1;
    if (i2c_write(0x38 << 1)) { i2c_stop(); return 1; }
    i2c_write(0xAC); i2c_write(0x33); i2c_write(0x00);
    i2c_stop();

    _delay_ms(80);

    // データ読み出し
    if (i2c_start()) return 1;
    if (i2c_write((0x38 << 1) | 1)) { i2c_stop(); return 1; }
    for(int i=0; i<5; i++) data[i] = i2c_read(1);
    data[5] = i2c_read(0);
    i2c_stop();

    // 状態チェック (bit7 が 0 なら測定完了)
    if (data[0] & 0x80) return 1;

    uint32_t h_raw = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
    uint32_t t_raw = ((uint32_t)(data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];
    *humi = (float)h_raw * 100 / 1048576;
    *temp = (float)t_raw * 200 / 1048576 - 50;
    return 0;
}

// --- UART & ADC ---
void uart_init(void) {
    UCSRA = (1 << U2X);
    UBRRH = 0; UBRRL = 12;
    UCSRC = (1 << URSEL) | (3 << UCSZ0);
    UCSRB = (1 << TXEN);
}

void uart_putstr(const char *s) {
    while (*s) {
        while (!(UCSRA & (1 << UDRE)));
        UDR = *s++;
    }
}

void adc_init(void) {
    ADMUX = (1 << REFS0);
    ADCSRA = (1 << ADEN) | (1 << ADPS1) | (1 << ADPS0);
}

uint16_t adc_read(uint8_t ch) {
    ADMUX = (ADMUX & 0xF0) | (ch & 0x07);
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC));
    return ADC;
}

int main(void) {
    DDRD |= (1 << PD2) | (1 << PD3);
    PORTD &= ~((1 << PD2) | (1 << PD3));
    _delay_ms(1000);

    uart_init();
    adc_init();
    i2c_init();

    char buffer[64];
    float temp, humi;

    while (1) {
        uint16_t moisture = adc_read(0);

        // AHT25 の読み取りを試みる
        if (aht25_read(&temp, &humi) != 0) {
            // 失敗時はエラー表示（またはダミー）
            temp = -99.9;
            humi = -99.9;
        }

        sprintf(buffer, "M:%u,T:%.1f,H:%.1f\r\n", moisture, (double)temp, (double)humi);
        uart_putstr(buffer);

        for(int i=0; i<10; i++) _delay_ms(1000);
    }
    return 0;
}
