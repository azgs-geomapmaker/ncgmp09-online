{% load filters %}
#mapunitpolys {
	line-width: 0;
	polygon-opacity: 1;{% for description in dmu_list %}{% if colors|get:description.pk != "#FFFFFF" %}
	["mapunit"="{{ description.mapunit }}"] { polygon-fill: {{ colors|get:description.pk }}; }{% endif %}{% endfor %}
}