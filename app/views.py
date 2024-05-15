from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime
from .models import GenVariant, Sample, Evaluation, Experiment, VariantStatistics
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import EvaluationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q

import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth.views import LoginView
from .variables import (
    VARIANT_ID,
    GENE,
    LIST_PER_PAGE,
    EVAL_DATE,
    SAMPLE_NAME,
    EXPERIMENT,
    ACMG_VALUES,
)


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or self.success_url or "/"


@login_required
def index(request):
    objects_list = GenVariant.objects.all()
    experiments = Experiment.objects.all()

    combined_conditions = Q()

    variant_id = request.GET.get(VARIANT_ID)
    if variant_id:
        combined_conditions &= Q(variant_id__icontains=variant_id)

    gene = request.GET.get(GENE)
    if gene:
        combined_conditions &= Q(gene=gene)

    # gnomad_total_af - could be greater than, less than, or equal
    gnomad_total_af = request.GET.get("gnomad_total_af")
    gnomad_total_af_compare = request.GET.get("gnomad_total_af_compare", "")

    compare_options_gnomad = {
        "selected_gte": gnomad_total_af_compare == "gte",
        "selected_lte": gnomad_total_af_compare == "lte",
    }

    if gnomad_total_af:
        gnomad_total_af = float(gnomad_total_af)
        if gnomad_total_af_compare == "gte":
            combined_conditions &= Q(gnomad_total_af__gte=gnomad_total_af)
        elif gnomad_total_af_compare == "lte":
            combined_conditions &= Q(gnomad_total_af__lte=gnomad_total_af)

    # cadd_phred - could be greater than, less than, or equal
    cadd_phred = request.GET.get("cadd_phred")
    cadd_phred_compare = request.GET.get("cadd_phred_compare", "")

    compare_options_cadd_phred = {
        "selected_gte": cadd_phred_compare == "gte",
        "selected_lte": cadd_phred_compare == "lte",
    }

    if cadd_phred:
        cadd_phred = float(cadd_phred)
        if cadd_phred_compare == "gte":
            combined_conditions &= Q(cadd_phred__gte=cadd_phred)
        elif cadd_phred_compare == "lte":
            combined_conditions &= Q(cadd_phred__lte=cadd_phred)

    # dbsnp_id - exact match
    dbsnp_id = request.GET.get("dbsnp_id")
    if dbsnp_id:
        combined_conditions &= Q(dbsnp_id=dbsnp_id)

    # cosmic_id - exact match
    cosmic_id = request.GET.get("cosmic_id")
    if cosmic_id:
        combined_conditions &= Q(cosmic_id__icontains=cosmic_id)

    # consequence - multiple checkboxes
    unique_consequences = (
        GenVariant.objects.order_by("consequence")
        .values_list("consequence", flat=True)
        .distinct()
    )
    selected_consequences = request.GET.getlist("consequence")

    if selected_consequences:
        combined_conditions &= Q(consequence__in=selected_consequences)

    # evaluation - select from pre-defined ACMG classification values
    selected_evaluations = request.GET.getlist("evaluation")
    selected_evaluation_values = [
        int(ev) for ev in selected_evaluations if ev.isdigit()
    ]
    if selected_evaluation_values:
        evaluated_variant_ids = (
            Evaluation.objects.filter(value__in=selected_evaluation_values)
            .values_list("variant_id_id", flat=True)
            .distinct()
        )

        combined_conditions &= Q(id__in=evaluated_variant_ids)

    interpreted_by = request.GET.get("interpreted_by", "")

    if interpreted_by:
        combined_conditions &= Q(evaluations__interpreted_by__icontains=interpreted_by)

    objects_list = objects_list.filter(combined_conditions).distinct()

    experiment_filter = request.GET.get("experiment_filter")
    frequency_threshold = request.GET.get("frequency_threshold")
    frequency_compare = request.GET.get("frequency_compare")

    compare_options_frequency = {
        "selected_gte": frequency_compare == "gte",
        "selected_lte": frequency_compare == "lte",
    }

    if experiment_filter:
        stats = VariantStatistics.objects.filter(
            experiment__experiment_name=experiment_filter
        )
        if frequency_threshold:
            frequency_threshold = float(frequency_threshold)
            if frequency_compare == "gte":
                stats = stats.filter(frequency__gte=frequency_threshold)
            elif frequency_compare == "lte":
                stats = stats.filter(frequency__lte=frequency_threshold)
            filtered_variant_ids = stats.values_list("variant__variant_id", flat=True)
            objects_list = objects_list.filter(variant_id__in=filtered_variant_ids)

    # Process experiments for template
    for experiment in experiments:
        experiment.is_selected = experiment.experiment_name == experiment_filter

    # Sorting and ordering
    sort_by = request.GET.get("sort_by", VARIANT_ID)
    order = request.GET.get("order", "")
    if order.lower() == "desc":
        sort_by = f"-{sort_by}"

    objects_list = objects_list.order_by(sort_by)

    # Pagination
    paginator = Paginator(objects_list, LIST_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    genvariant_data = []

    for variant in page_obj:
        variant_dict = {
            "variant_id": variant.variant_id,
            "gene": variant.gene,
            "chromosome": variant.chromosome,
            "variant_start": variant.variant_start,
            "variant_end": variant.variant_end,
            "reference": variant.reference,
            "alternate": variant.alternate,
            "zygosity": variant.zygosity,
            "gnomad_total_af": variant.gnomad_total_af,
            "cadd_phred": variant.cadd_phred,
            "dbsnp_id": variant.dbsnp_id,
            "consequence": variant.consequence,
            "cosmic_id": variant.cosmic_id,
            "experiments": [],
        }

        variant_statistics = VariantStatistics.objects.filter(
            variant__variant_id=variant.variant_id
        ).select_related("experiment")

        stats_list = [
            {
                "experiment_name": stat.experiment.experiment_name,
                "count": stat.count,
                "frequency": stat.frequency,
            }
            for stat in variant_statistics
        ]

        stats_dict = {stat["experiment_name"]: stat for stat in stats_list}

        variant_dict["experiments"] = []

        for experiment in experiments:
            if experiment.experiment_name in stats_dict:
                exp_data = stats_dict[experiment.experiment_name]
                exp = {
                    "experiment_name": exp_data["experiment_name"],
                    "sample_count": exp_data["count"],
                    "frequency": exp_data["frequency"],
                }
            else:
                exp = {
                    "experiment_name": experiment.experiment_name,
                    "sample_count": 0,
                    "frequency": 0.0,
                }

            variant_dict["experiments"].append(exp)

        genvariant_data.append(variant_dict)

    if "export_to_csv" in request.POST:
        selected_columns = request.POST.getlist("columns")

        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"genvar_exported-variants_{timestamp}.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response, delimiter="|")

        writer.writerow(selected_columns)

        queryset = objects_list
        for obj in queryset:
            row = [
                getattr(obj, column)
                for column in selected_columns
                if hasattr(obj, column)
            ]
            writer.writerow(row)

        return response

    context = {
        "genvariants": genvariant_data,
        "experiments": experiments,
        "count": objects_list.count(),
        "selected_consequences": selected_consequences,
        "unique_consequences": unique_consequences,
        "selected_evaluations": selected_evaluations,
        "ACMG_VALUES": ACMG_VALUES,
        "compare_options": {
            "gnomad": compare_options_gnomad,
            "cadd_phred": compare_options_cadd_phred,
            "frequency": compare_options_frequency,
        },
        "sort_by": sort_by,
        "order": order,
        "page_obj": page_obj,
    }

    return render(request, "app/index.html", context)


@login_required
def variant_detail(request, variant_id):
    variant = get_object_or_404(GenVariant, variant_id=variant_id)
    evaluations = Evaluation.objects.filter(variant_id=variant).order_by(EVAL_DATE)
    new_evaluation = None

    experiments = Experiment.objects.all()

    if request.method == "POST":
        evaluation_form = EvaluationForm(request.POST, user=request.user)
        if evaluation_form.is_valid():
            new_evaluation = evaluation_form.save(commit=False)
            new_evaluation.variant_id = variant
            new_evaluation.save()
            return redirect("variant_detail", variant_id=variant_id)
    else:
        evaluation_form = EvaluationForm(user=request.user)

    samples_by_experiments = []

    for experiment in experiments:
        samples = []
        samples_filtered = variant.samples_with_variant.filter(experiment=experiment)
        experiment_count = samples_filtered.count()
        total_samples = experiment.samples.count()
        frequency = experiment_count / total_samples if total_samples > 0 else 0

        for sample in samples_filtered:
            sample_name = sample.sample_name
            samples.append(sample_name)

        samples.sort(reverse=True)

        samples_by_experiments.append(
            {
                "experiment_name": experiment,
                "experiment_samples": samples,
                "experiment_counts": experiment_count,
                "variant_freq": frequency,
            }
        )

    context = {
        "variant": variant,
        "samples_by_experiments": samples_by_experiments,
        "experiments": experiments,
        "evaluations": evaluations,
        "evaluation_form": evaluation_form,
    }

    return render(request, "app/variant_detail.html", context)


@login_required
def sample_list(request):
    objects_list = Sample.objects.all()
    combined_conditions = Q()

    sample_name = request.GET.get(SAMPLE_NAME)

    if sample_name:
        combined_conditions &= Q(sample_name=sample_name)

    experiment = request.GET.get(EXPERIMENT)
    if experiment:
        combined_conditions &= Q(experiment__experiment_name=experiment)

    objects_list = objects_list.filter(combined_conditions).distinct()

    sort_by = request.GET.get("sort_by", SAMPLE_NAME)
    order = request.GET.get("order", "")
    if order.lower() == "desc":
        sort_by = f"-{sort_by}"

    objects_list = objects_list.order_by(sort_by)

    paginator = Paginator(objects_list, LIST_PER_PAGE)
    page_number = request.GET.get("page")
    samples = paginator.get_page(page_number)

    context = {
        "samples": samples,
        "sort_by": sort_by,
        "order": order,
    }

    return render(request, "app/sample_list.html", context)


@login_required
def sample_detail(request, sample_name):
    sample = get_object_or_404(Sample, sample_name=sample_name)

    experiment = sample.experiment
    variants = sample.variants.all()
    number_of_variants = variants.count()

    paginator = Paginator(variants, LIST_PER_PAGE)
    page_number = request.GET.get("page")
    variants = paginator.get_page(page_number)

    context = {
        "sample": sample,
        "variants": variants,
        "count": number_of_variants,
        "experiment": experiment,
    }

    return render(
        request,
        "app/sample_detail.html",
        context,
    )


@login_required
def documentation(request):
    return render(request, "app/documentation.html")


@login_required
def about(request):
    return render(request, "app/about.html")


@login_required
def profile(request):
    return render(request, "app/profile.html")
