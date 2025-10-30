import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
import pytz

TOKEN = "7637705087:AAGLEf3miUmAeGMtsbetujFj31s9OFo44yc"
CHANNEL_ID = -1002308678665
USER_ID = 7423350654

message_queue = []
current_message_index = 0
is_queue_active = False
stats = {
    'total_renewed': 0,
    'total_deleted': 0,
    'daily_renewed': 0,
    'daily_deleted': 0,
    'renewal_times': {}
}

ASGABAT_TZ = pytz.timezone('Asia/Ashgabat')

async def ask_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == USER_ID:
        await update.message.reply_text(
            "📢 Lütfen 5 mesajı art arda gönderin!\n"
            "Her mesajı ayrı ayrı alıp, 40 dakika aralıklarla otomatik paylaşacağım."
        )
        context.user_data["waiting_for_messages"] = True
        context.user_data["received_messages"] = []

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_queue, is_queue_active

    if context.user_data.get("waiting_for_messages") and update.effective_user.id == USER_ID:
        context.user_data["received_messages"].append(update.message)

        await update.message.reply_text(
            "✅ {}. mesaj başarıyla alındı!\n"
            "5/5 tamamlanınca otomatik başlayacak.".format(
                len(context.user_data["received_messages"])
            )
        )

        if len(context.user_data["received_messages"]) == 5:
            context.user_data["waiting_for_messages"] = False
            message_queue = context.user_data["received_messages"].copy()
            
            await send_next_message(context, update)
            is_queue_active = True
            # Background task'leri başlat
            if 'rotation_task' not in context.application.chat_data:
                context.application.chat_data['rotation_task'] = asyncio.create_task(message_rotation_loop(context, update))
            if 'stats_task' not in context.application.chat_data:
                context.application.chat_data['stats_task'] = asyncio.create_task(daily_stats_report(context, update))

async def send_next_message(context: ContextTypes.DEFAULT_TYPE, update: Update = None):
    global current_message_index, stats

    if not message_queue:
        return

    msg = message_queue[current_message_index]
    
    try:
        # Önceki mesajı sil
        if "last_message_id" in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=CHANNEL_ID,
                    message_id=context.user_data["last_message_id"]
                )
                stats['total_deleted'] += 1
                stats['daily_deleted'] += 1
            except Exception as e:
                print(f"Mesaj silinirken hata: {e}")

        # Yeni mesajı gönder
        sent_msg = await context.bot.copy_message(
            chat_id=CHANNEL_ID,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id
        )
        context.user_data["last_message_id"] = sent_msg.message_id

        # İstatistikleri güncelle
        now = datetime.now(ASGABAT_TZ)
        current_hour = now.hour
        stats['renewal_times'][current_hour] = stats['renewal_times'].get(current_hour, 0) + 1
        
        stats['total_renewed'] += 1
        stats['daily_renewed'] += 1

        next_time = (now + timedelta(minutes=40)).strftime("%H:%M")

        # Kullanıcıya bilgi ver
        if update and hasattr(update, 'message'):
            await update.message.reply_text(
                f"✅ Mesaj başarıyla kanalda Yenilendi!\n"
                f"📅 Yenileme Saati: {now.strftime('%H:%M')}\n"
                f"🔋 Yeniden Yenilenecek Vakti: {next_time}\n"
                f"⏳ 40 dakika sonra yeniden yenilenecek."
            )

        # Bir sonraki mesaja geç
        current_message_index = (current_message_index + 1) % 5

    except Exception as e:
        print(f"Mesaj gönderilirken hata: {e}")
        if update and hasattr(update, 'message'):
            await update.message.reply_text(f"⚠️ Hata: {e}")

async def message_rotation_loop(context: ContextTypes.DEFAULT_TYPE, update: Update = None):
    global is_queue_active
    while is_queue_active:
        try:
            await asyncio.sleep(2400)  # 40 dakika
            if is_queue_active:  # Hala aktif mi kontrol et
                await send_next_message(context, update)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Rotation loop hatası: {e}")
            await asyncio.sleep(60)  # Hata durumunda 1 dakika bekle

async def daily_stats_report(context: ContextTypes.DEFAULT_TYPE, update: Update = None):
    last_report_day = None
    
    while True:
        try:
            now = datetime.now(ASGABAT_TZ)
            current_day = now.day
            
            # Her gün 23:00'de ve gün değiştiyse rapor gönder
            if (now.hour == 23 and now.minute == 0) and current_day != last_report_day:
                report = "📊 Günlük İstatistik Raporu:\n"
                report += f"• Bugünkü Yenilenen Mesaj: {stats['daily_renewed']}\n"
                report += f"• Bugünkü Silinen Mesaj: {stats['daily_deleted']}\n"
                report += f"• Toplam Yenilenen: {stats['total_renewed']}\n"
                report += f"• Toplam Silinen: {stats['total_deleted']}\n"
                
                if stats['renewal_times']:
                    report += "⏰ En Yoğun Saatler:\n"
                    sorted_hours = sorted(stats['renewal_times'].items(), key=lambda x: x[1], reverse=True)[:3]
                    for hour, count in sorted_hours:
                        report += f"- {hour}:00 - {hour+1}:00 → {count} yenileme\n"
                else:
                    report += "⏰ Bugün hiç yenileme yapılmadı.\n"
                
                if update and hasattr(update, 'message'):
                    try:
                        await update.message.reply_text(report)
                    except Exception as e:
                        print(f"Rapor gönderilemedi: {e}")
                
                # Günlük istatistikleri sıfırla
                stats['daily_renewed'] = 0
                stats['daily_deleted'] = 0
                stats['renewal_times'] = {}
                last_report_day = current_day
                
                # Aynı raporun tekrar gönderilmesini engelle
                await asyncio.sleep(60)
            
            # 30 saniye bekleyerek tekrar kontrol et
            await asyncio.sleep(30)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Stats report hatası: {e}")
            await asyncio.sleep(60)

async def stop_tasks(application):
    """Görevleri durdur"""
    global is_queue_active
    is_queue_active = False
    
    if 'rotation_task' in application.chat_data:
        application.chat_data['rotation_task'].cancel()
        try:
            await application.chat_data['rotation_task']
        except asyncio.CancelledError:
            pass
    
    if 'stats_task' in application.chat_data:
        application.chat_data['stats_task'].cancel()
        try:
            await application.chat_data['stats_task']
        except asyncio.CancelledError:
            pass

async def post_init(application):
    """Bot başlatıldıktan sonra çalışacak fonksiyon"""
    print("Bot başarıyla başlatıldı!")

async def post_stop(application):
    """Bot durdurulurken çalışacak fonksiyon"""
    await stop_tasks(application)
    print("Bot durduruldu!")

def main():
    # Application builder ile bot'u oluştur
    app = Application.builder().token(TOKEN).post_init(post_init).post_stop(post_stop).build()
    
    # Handler'ları ekle
    app.add_handler(CommandHandler("start", ask_message))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, receive_message))
    
    print("Bot başlatılıyor...")
    
    try:
        # Bot'u polling modunda çalıştır
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        print("Bot kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"Bot çalışırken hata oluştu: {e}")
    finally:
        # Event loop'u al ve görevleri temizle
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(stop_tasks(app))

if __name__ == "__main__":
    main()