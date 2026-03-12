#ifndef F_CPU
#define F_CPU 1000000UL
#endif

#include <avr/io.h>
#include <util/delay.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <stdio.h>

uint8_t sleep_count __attribute__ ((section (".noinit")));

// --- UART & ADC ---
void uart_init(void) {
    UCSRA = (1 << U2X); UBRRH = 0; UBRRL = 12;
    UCSRC = (1 << URSEL) | (3 << UCSZ0); UCSRB = (1 << TXEN);
}
void uart_putstr(const char *s) {
    while (*s) { while (!(UCSRA & (1 << UDRE))); UDR = *s++; }
}
void adc_init(void) { ADMUX = (1 << REFS0); ADCSRA = (1 << ADEN) | (1 << ADPS1) | (1 << ADPS0); }
uint16_t adc_read(uint8_t ch) {
    ADMUX = (ADMUX & 0xF0) | (ch & 0x07); ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC)); return ADC;
}

// --- I2C (安全版) ---
uint8_t i2c_wait(void) {
    uint16_t timeout = 2000;
    while (!(TWCR & (1 << TWINT))) { if (--timeout == 0) return 1; }
    return 0;
}
void i2c_init(void) { TWBR = 32; TWSR = (1 << TWPS0); }
uint8_t i2c_start(void) { TWCR = (1 << TWINT) | (1 << TWSTA) | (1 << TWEN); return i2c_wait(); }
void i2c_stop(void) { TWCR = (1 << TWINT) | (1 << TWSTO) | (1 << TWEN); }
uint8_t i2c_write(uint8_t data) { TWDR = data; TWCR = (1 << TWINT) | (1 << TWEN); return i2c_wait(); }
uint8_t i2c_read(uint8_t ack) { TWCR = (1 << TWINT) | (1 << TWEN) | (ack ? (1 << TWEA) : 0); if (i2c_wait()) return 0; return TWDR; }

uint8_t aht25_read(float *temp, float *humi) {
    uint8_t data[6];
    if (i2c_start()) return 1;
    i2c_write(0x38 << 1); i2c_write(0xAC); i2c_write(0x33); i2c_write(0x00); i2c_stop();
    _delay_ms(80);
    if (i2c_start()) return 1;
    i2c_write((0x38 << 1) | 1);
    for(int i=0; i<5; i++) data[i] = i2c_read(1);
    data[5] = i2c_read(0); i2c_stop();
    if (data[0] & 0x80) return 1;
    uint32_t h_raw = ((uint32_t)data[1] << 12) | ((uint32_t)data[2] << 4) | (data[3] >> 4);
    uint32_t t_raw = ((uint32_t)(data[3] & 0x0F) << 16) | ((uint32_t)data[4] << 8) | data[5];
    *humi = (float)h_raw * 100 / 1048576;
    *temp = (float)t_raw * 200 / 1048576 - 50;
    return 0;
}

int main(void) {
    MCUSR = 0;
    wdt_disable();

    DDRB |= (1 << PB0); // LED
    DDRD |= (1 << PD2) | (1 << PD3); // LoRa Mode
    DDRC |= (1 << PC1); // Moisture Sensor Power

    if (sleep_count > 5) sleep_count = 0;

    if (sleep_count > 0 && sleep_count < 5) {
        PORTD |= (1 << PD2) | (1 << PD3); // LoRa Sleep
        PORTC &= ~(1 << PC1);             // Moisture Sensor Power OFF

        PORTB |= (1 << PB0); _delay_ms(2); PORTB &= ~(1 << PB0); // Heartbeat

        sleep_count++;
        wdt_enable(WDTO_2S);
        set_sleep_mode(SLEEP_MODE_PWR_DOWN);
        sleep_mode();
    }

    sleep_count = 1;

    // --- Wakeup ---
    PORTD &= ~((1 << PD2) | (1 << PD3)); // LoRa Normal
    PORTC |= (1 << PC1);                 // Moisture Sensor Power ON
    _delay_ms(100); // 復帰待ち

    PORTB |= (1 << PB0);

    uart_init();
    adc_init();
    i2c_init();

    float temp, humi;
    uint16_t moisture = adc_read(0);
    if (aht25_read(&temp, &humi) != 0) { temp = -99.9; humi = -99.9; }

    char buffer[64];
    sprintf(buffer, "M:%u,T:%.1f,H:%.1f\r\n", moisture, (double)temp, (double)humi);
    uart_putstr(buffer);

    while (!(UCSRA & (1 << TXC)));

    PORTB &= ~(1 << PB0);

    // --- Sleep Preparation ---
    PORTD |= (1 << PD2) | (1 << PD3); // LoRa Sleep
    PORTC &= ~(1 << PC1);             // Moisture Sensor Power OFF
    ADCSRA &= ~(1 << ADEN); TWCR &= ~(1 << TWEN); UCSRB &= ~(1 << TXEN);

    wdt_enable(WDTO_2S);
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_mode();

    return 0;
}
