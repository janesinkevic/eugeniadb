from django.db import models
from django.utils import timezone
from app.variables import (
    HEALTH_STATE_VALUES,
    GENDER_VALUES,
    SAMPLE_TYPE_VALUES,
    MUTATION_TYPE_VALUES,
    ACMG_VALUES,
)


class Experiment(models.Model):
    experiment_name = models.CharField(max_length=2048, unique=True)
    path = models.CharField(max_length=2048)

    def __str__(self):
        return self.experiment_name


class Sample(models.Model):
    sample_name = models.CharField(max_length=2048, unique=True)
    experiment = models.ForeignKey(
        Experiment, related_name="samples", on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.sample_name


class GenVariant(models.Model):
    variant_id = models.CharField(max_length=2048, unique=True)

    gene = models.CharField(max_length=2048, null=True, blank=True)

    chromosome = models.CharField(max_length=2048, null=True, blank=True)
    variant_start = models.IntegerField(default=0, null=True, blank=True)
    variant_end = models.IntegerField(default=0, null=True, blank=True)
    reference = models.CharField(max_length=2048, null=True, blank=True)
    alternate = models.CharField(max_length=2048, null=True, blank=True)
    zygosity = models.CharField(max_length=255, null=True, blank=True)

    gnomad_total_af = models.FloatField(default=0, null=True, blank=True)
    cadd_phred = models.FloatField(default=0, null=True, blank=True)
    dbsnp_id = models.CharField(max_length=2048, null=True, blank=True)
    consequence = models.CharField(max_length=2048, null=True, blank=True)
    cosmic_id = models.CharField(max_length=2048, null=True, blank=True)

    samples_with_variant = models.ManyToManyField(
        Sample, related_name="variants", blank=True, default=[]
    )

    def __str__(self):
        return self.variant_id


class Evaluation(models.Model):
    variant_id = models.ForeignKey(
        GenVariant, related_name="evaluations", on_delete=models.CASCADE
    )
    value = models.IntegerField(choices=ACMG_VALUES)
    interpreted_by = models.CharField(max_length=2048, null=True, blank=True)
    interpretation = models.CharField(max_length=2048, null=True, blank=True)
    eval_date = models.DateField(default=timezone.now)

    def __str__(self):
        return dict(self.ACMG_VALUES).get(self.value, "Unknown")


class VariantStatistics(models.Model):
    variant = models.ForeignKey(GenVariant, on_delete=models.CASCADE)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    frequency = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
