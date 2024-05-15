from django.contrib import admin
from .models import (
    GenPanel,
    Experiment,
    Sample,
    GenVariant,
    Evaluation,
)

from .variables import (
    GENVARIANT_COLUMN_NAMES,
    VARIANT_ID,
    GENE,
    LIST_PER_PAGE,
    EVALUATION_COLUMN_NAMES,
    SAMPLE_COLUMN_NAMES,
    EXPERIMENT_COLUMN_NAMES,
)
from django.db.models import Count, Q
from django.core.paginator import Paginator


class EvaluationInline(admin.TabularInline):
    model = Evaluation
    extra = 1


class DiseaseAssociationInline(admin.TabularInline):
    model = DiseaseAssociation
    extra = 1


class GenVariantAdmin(admin.ModelAdmin):

    variant_columns = GENVARIANT_COLUMN_NAMES
    list_display = variant_columns

    list_per_page = LIST_PER_PAGE
    search_fields = [VARIANT_ID, GENE]

    inlines = [EvaluationInline]

    def get_samples_with_variant(self, obj):
        samples = ", ".join(
            [sample.sample_name for sample in obj.samples_with_variant.all()]
        )
        return samples

    get_samples_with_variant.short_description = "Samples with Variant"


class EvaluationAdmin(admin.ModelAdmin):
    list_display = EVALUATION_COLUMN_NAMES


class SampleAdmin(admin.ModelAdmin):
    list_display = SAMPLE_COLUMN_NAMES


class ExperimentAdmin(admin.ModelAdmin):
    list_display = EXPERIMENT_COLUMN_NAMES


admin.site.register(GenVariant, GenVariantAdmin)
admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(Experiment, ExperimentAdmin)
