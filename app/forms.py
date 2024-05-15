from django import forms
from .models import Evaluation
from .variables import VALUE, INTERPRETED_BY, INTERPRETATION, EVAL_DATE


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [VALUE, INTERPRETED_BY, INTERPRETATION, EVAL_DATE]
        widgets = {
            EVAL_DATE: forms.DateInput(format=("%Y-%m-%d"), attrs={"type": "date"}),
            INTERPRETED_BY: forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super(EvaluationForm, self).__init__(*args, **kwargs)

        if user:
            self.fields[INTERPRETED_BY].initial = f"{user.first_name} {user.last_name}"
            self.fields[INTERPRETED_BY].disabled = True
