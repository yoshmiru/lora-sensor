export interface Env {
	DB: D1Database;
	LINE_CHANNEL_ACCESS_TOKEN: string;
}

// 確定したキャリブレーション値
const DRY_VAL = 593;
const WET_VAL = 273;

function toJST(utcString: string): string {
	const date = new Date(utcString + " UTC");
	return date.toLocaleString("ja-JP", {
		timeZone: "Asia/Tokyo",
		month: "2-digit",
		day: "2-digit",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit"
	});
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		const signature = request.headers.get("x-line-signature");
		const isLine = signature !== null;

		// --- A. LoRa 受信処理 ---
		if (request.method === "POST" && !isLine) {
			try {
				const batch = await request.json() as any[];
				const statements = batch.map(entry => {
					const parts = entry.message.split(',');
					const moistureRaw = parseInt(parts[0].split(':')[1]);
					const temperature = parseFloat(parts[1].split(':')[1]);
					const humidity = parseFloat(parts[2].split(':')[1]);

					// 水分量パーセント計算 (593 -> 0%, 273 -> 100%)
					let moisturePercent = ((DRY_VAL - moistureRaw) / (DRY_VAL - WET_VAL)) * 100;
					moisturePercent = Math.max(0, Math.min(100, moisturePercent));

					return env.DB.prepare(
						"INSERT INTO sensor_data (moisture, temp, humi) VALUES (?, ?, ?)"
					).bind(moisturePercent.toFixed(1), temperature, humidity);
				});
				await env.DB.batch(statements);
				return new Response("Batch Logged", { status: 200 });
			} catch (err) {
				return new Response("Batch Error", { status: 400 });
			}
		}

		// --- B. LINE Webhook 処理 ---
		if (request.method === "POST" && isLine) {
			try {
				const body = await request.json() as any;
				const event = body.events[0];
				if (!event || !event.replyToken) return new Response("OK");

				const latest = await env.DB.prepare(
					"SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1"
				).first() as any;

				let replyText = "";
				if (latest) {
					const timeJST = toJST(latest.created_at);
					replyText = `【現在のハウス状況】\n💧水分: ${latest.moisture}%\n🌡温度: ${latest.temp}℃\n☁湿度: ${latest.humi}%\n(計測: ${timeJST})`;
				} else {
					replyText = "データがありません。";
				}

				await fetch("https://api.line.me/v2/bot/message/reply", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}`
					},
					body: JSON.stringify({
						replyToken: event.replyToken,
						messages: [{ type: "text", text: replyText }]
					})
				});
				return new Response("OK");
			} catch (err) {
				return new Response("Error", { status: 500 });
			}
		}

		return new Response("Not Found", { status: 404 });
	},
};
