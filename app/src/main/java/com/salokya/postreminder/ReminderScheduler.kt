package com.salokya.postreminder

import android.content.Context
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

object ReminderScheduler {
    private const val UNIQUE_WORK_NAME = "festival_reminder_worker"

    fun scheduleDailyCheck(context: Context) {
        val request = PeriodicWorkRequestBuilder<FestivalReminderWorker>(1, TimeUnit.DAYS)
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            UNIQUE_WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request
        )
    }
}
