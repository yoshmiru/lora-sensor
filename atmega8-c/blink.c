#include <avr/io.h>

int main(void) {
    // 全ポートを出力に設定（PB, PC, PDすべて）
    DDRB = 0xFF;
    DDRC = 0xFF;
    DDRD = 0xFF;

    while (1) {
        // すべてのピンを同時に ON/OFF (トグル)
        PORTB ^= 0xFF;
        PORTC ^= 0xFF;
        PORTD ^= 0xFF;
        
        // 極小のウェイト
        // 正常なら速すぎて点灯に見えるはず
        // 異常に遅いならこれで点滅が見えるはず
        for(volatile long i=0; i<1000; i++); 
    }
    return 0;
}
