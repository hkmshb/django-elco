from elco.core.registry import register
from ..models import TransformerRating



@register.assignment_tag
def get_rating_xfmr_table_fields_with_model():
    fields = ['code', 'capacity', 'voltage_ratio']
    return (fields, TransformerRating)
