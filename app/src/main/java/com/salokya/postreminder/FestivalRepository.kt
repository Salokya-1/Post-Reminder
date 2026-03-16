package com.salokya.postreminder

import android.content.Context
import org.apache.poi.ss.usermodel.Cell
import org.apache.poi.ss.usermodel.DataFormatter
import org.apache.poi.ss.usermodel.Row
import org.apache.poi.ss.usermodel.WorkbookFactory
import org.apache.poi.ss.usermodel.DateUtil
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException
import java.util.Locale

object FestivalRepository {
    private const val FESTIVAL_FILE_NAME = "festivals.csv"
    private const val EXCEL_FILE_NAME = "SocialMedia_Calendar_2026.xlsx"

    fun loadFestivals(context: Context): List<Festival> {
        val excelFestivals = loadFromExcel(context)
        if (excelFestivals.isNotEmpty()) {
            return excelFestivals.sortedBy { it.date }
        }

        return loadFromCsv(context).sortedBy { it.date }
    }

    private fun loadFromCsv(context: Context): List<Festival> {
        val lines = try {
            context.assets.open(FESTIVAL_FILE_NAME)
                .bufferedReader()
                .use { it.readLines() }
        } catch (_: Exception) {
            return emptyList()
        }

        return lines
            .drop(1) // Skip CSV header.
            .mapNotNull { line ->
                val parts = line.split(",")
                if (parts.size < 2) {
                    return@mapNotNull null
                }

                val name = parts[0].trim()
                val dateRaw = parts[1].trim()
                val notes = parts.drop(2).joinToString(",").trim()

                if (name.isBlank() || dateRaw.isBlank()) {
                    return@mapNotNull null
                }

                val parsedDate = try {
                    LocalDate.parse(dateRaw)
                } catch (_: DateTimeParseException) {
                    null
                }

                parsedDate?.let { Festival(name = name, date = it, notes = notes) }
            }
    }

    private fun loadFromExcel(context: Context): List<Festival> {
        return try {
            context.assets.open(EXCEL_FILE_NAME).use { input ->
                WorkbookFactory.create(input).use { workbook ->
                    val formatter = DataFormatter(Locale.ENGLISH)
                    val result = mutableListOf<Festival>()

                    for (sheetIndex in 0 until workbook.numberOfSheets) {
                        val sheet = workbook.getSheetAt(sheetIndex) ?: continue
                        val headerRow = sheet.getRow(sheet.firstRowNum) ?: continue

                        val dateColumn = findHeaderColumn(headerRow, formatter, listOf("date", "day"))
                        val nameColumn = findHeaderColumn(headerRow, formatter, listOf("festival", "event", "occasion", "name", "title", "post"))
                        val notesColumn = findHeaderColumn(headerRow, formatter, listOf("note", "caption", "details", "description", "remark", "content"))

                        for (rowIndex in (headerRow.rowNum + 1)..sheet.lastRowNum) {
                            val row = sheet.getRow(rowIndex) ?: continue

                            val date = if (dateColumn != null) {
                                parseDateCell(row.getCell(dateColumn), formatter)
                            } else {
                                findDateInRow(row, formatter)
                            }

                            val name = if (nameColumn != null) {
                                formatter.formatCellValue(row.getCell(nameColumn)).trim()
                            } else {
                                findNameInRow(row, formatter, dateColumn)
                            }

                            if (date == null || name.isBlank()) {
                                continue
                            }

                            val notes = notesColumn
                                ?.let { formatter.formatCellValue(row.getCell(it)).trim() }
                                .orEmpty()

                            result += Festival(name = name, date = date, notes = notes)
                        }
                    }

                    result
                        .distinctBy { "${it.name}_${it.date}" }
                        .sortedBy { it.date }
                }
            }
        } catch (_: Exception) {
            emptyList()
        }
    }

    private fun findHeaderColumn(
        headerRow: Row,
        formatter: DataFormatter,
        keywords: List<String>
    ): Int? {
        val first = headerRow.firstCellNum.toInt().coerceAtLeast(0)
        val last = headerRow.lastCellNum.toInt().coerceAtLeast(first)

        for (index in first until last) {
            val text = formatter.formatCellValue(headerRow.getCell(index)).trim().lowercase(Locale.ENGLISH)
            if (text.isEmpty()) {
                continue
            }

            if (keywords.any { key -> text.contains(key) }) {
                return index
            }
        }

        return null
    }

    private fun findDateInRow(row: Row, formatter: DataFormatter): LocalDate? {
        val first = row.firstCellNum.toInt().coerceAtLeast(0)
        val last = row.lastCellNum.toInt().coerceAtLeast(first)

        for (index in first until last) {
            val parsed = parseDateCell(row.getCell(index), formatter)
            if (parsed != null) {
                return parsed
            }
        }

        return null
    }

    private fun findNameInRow(row: Row, formatter: DataFormatter, dateColumn: Int?): String {
        val first = row.firstCellNum.toInt().coerceAtLeast(0)
        val last = row.lastCellNum.toInt().coerceAtLeast(first)

        for (index in first until last) {
            if (dateColumn != null && index == dateColumn) {
                continue
            }

            val text = formatter.formatCellValue(row.getCell(index)).trim()
            if (text.isBlank()) {
                continue
            }

            if (parseDateText(text) != null) {
                continue
            }

            return text
        }

        return ""
    }

    private fun parseDateCell(cell: Cell?, formatter: DataFormatter): LocalDate? {
        if (cell == null) {
            return null
        }

        if (DateUtil.isCellDateFormatted(cell)) {
            return try {
                cell.localDateTimeCellValue.toLocalDate()
            } catch (_: Exception) {
                try {
                    val excelDate = DateUtil.getJavaDate(cell.numericCellValue)
                    LocalDateTime.ofInstant(excelDate.toInstant(), ZoneId.systemDefault()).toLocalDate()
                } catch (_: Exception) {
                    null
                }
            }
        }

        val text = formatter.formatCellValue(cell).trim()
        return parseDateText(text)
    }

    private fun parseDateText(text: String): LocalDate? {
        if (text.isBlank()) {
            return null
        }

        val normalized = text.replace(".", "-").replace("/", "-").trim()

        val patterns = listOf(
            DateTimeFormatter.ISO_LOCAL_DATE,
            DateTimeFormatter.ofPattern("d-M-uuuu", Locale.ENGLISH),
            DateTimeFormatter.ofPattern("dd-MM-uuuu", Locale.ENGLISH),
            DateTimeFormatter.ofPattern("d MMM uuuu", Locale.ENGLISH),
            DateTimeFormatter.ofPattern("d MMMM uuuu", Locale.ENGLISH),
            DateTimeFormatter.ofPattern("MMM d, uuuu", Locale.ENGLISH),
            DateTimeFormatter.ofPattern("MMMM d, uuuu", Locale.ENGLISH)
        )

        for (formatter in patterns) {
            try {
                return LocalDate.parse(normalized, formatter)
            } catch (_: DateTimeParseException) {
                // Try next date format.
            }
        }

        return null
    }
}
