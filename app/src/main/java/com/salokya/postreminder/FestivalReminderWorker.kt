package com.salokya.postreminder

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import java.time.LocalDate

class FestivalReminderWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        createNotificationChannelIfNeeded(applicationContext)

        val today = LocalDate.now()
        val festivals = FestivalRepository.loadFestivals(applicationContext)
        festivals
            .filter { it.date.minusDays(2) == today }
            .forEach { festival ->
                if (shouldNotifyToday(festival, today)) {
                    sendNotification(festival)
                }
            }

        return Result.success()
    }

    private fun shouldNotifyToday(festival: Festival, today: LocalDate): Boolean {
        val prefs = applicationContext.getSharedPreferences("festival_reminders", Context.MODE_PRIVATE)
        val year = festival.date.year
        val key = "${festival.name}_${year}_$today"
        val notified = prefs.getBoolean(key, false)

        if (!notified) {
            prefs.edit().putBoolean(key, true).apply()
        }

        return !notified
    }

    private fun sendNotification(festival: Festival) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val hasPermission = ContextCompat.checkSelfPermission(
                applicationContext,
                Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
            if (!hasPermission) {
                return
            }
        }

        val manager = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val content = "${festival.name} is on ${festival.date}. Prepare now."

        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("Festival Reminder")
            .setContentText(content)
            .setStyle(NotificationCompat.BigTextStyle().bigText(content))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()

        manager.notify(festival.name.hashCode(), notification)
    }

    private fun createNotificationChannelIfNeeded(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return
        }

        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (manager.getNotificationChannel(CHANNEL_ID) != null) {
            return
        }

        val channel = NotificationChannel(
            CHANNEL_ID,
            "Festival Reminders",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "Reminders for festivals 2 days before the date"
        }
        manager.createNotificationChannel(channel)
    }

    companion object {
        const val CHANNEL_ID = "festival-reminders"
    }
}
