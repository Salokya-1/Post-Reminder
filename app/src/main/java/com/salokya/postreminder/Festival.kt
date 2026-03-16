package com.salokya.postreminder

import java.time.LocalDate

data class Festival(
    val name: String,
    val date: LocalDate,
    val notes: String = ""
)
