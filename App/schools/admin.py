"""
Admin configuration for Schools app.
"""

from django.contrib import admin
from .models import AcademicYear, Term, Section


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['school', 'year', 'start_date', 'end_date', 'is_current']
    list_filter = ['school', 'is_current', 'year']
    search_fields = ['school__name']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'term_number', 'name', 'start_date', 'end_date', 'is_active']
    list_filter = ['academic_year__school', 'term_number', 'is_active']
    ordering = ['academic_year', 'term_number']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['school', 'name', 'order', 'description']
    list_filter = ['school', 'name']
    ordering = ['order', 'name']
