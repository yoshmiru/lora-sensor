#![no_std]
#![no_main]

use panic_halt as _;
use atmega_hal::prelude::*;
use atmega_hal::clock::MHz1;
use atmega_hal::usart::{Baudrate, Usart};
use ufmt::uwriteln;

#[atmega_hal::entry]
fn main() -> ! {
    let dp = atmega_hal::Peripherals::take().unwrap();
    let pins = atmega_hal::pins!(dp);
    
    // E220 制御ピンの設定 (Normal Mode: M0=L, M1=L)
    let mut m0 = pins.pd2.into_output();
    let mut m1 = pins.pd3.into_output();
    m0.set_low();
    m1.set_low();

    // 動作確認用 LED (PB0)
    let mut led = pins.pb0.into_output();
    led.set_low();

    // UART (USART) の初期化 (9600bps)
    // 内部で最適な UBRR と U2X モードが自動選択されます
    let mut serial = Usart::new(
        dp.USART,
        pins.pd0,
        pins.pd1.into_output(),
        Baudrate::<MHz1>::new(9600),
    );

    let mut delay = atmega_hal::delay::Delay::<MHz1>::new();

    loop {
        // 送信開始：LED点灯
        led.set_high();

        // LoRa モジュールへデータを書き込み
        // uwriteln! は自動的に末尾に \r\n を付加します
        let _ = uwriteln!(&mut serial, "Hello LoRa from Rust!");

        // 0.2秒点灯を維持して、送信中であることを視覚化
        delay.delay_ms(200u16);
        led.set_low();

        // 5秒待機
        delay.delay_ms(5000u16);
    }
}
