<artist>
<name>{{name}}</name>
<biography>{%- if biography is defined-%}
{{biography.content}}
{% endif%}
albums: {{albums_count}}
</biography>
{% if image[image_default_size] %}
  <thumb>{{image[image_default_size]}}</thumb>
{% endif %}
{% if image.large %}
  <thumb>{{image.large}}</thumb>
{% endif %}
{% if image.small %}
  <thumb>{{image.small}}</thumb>
{% endif %}
{% if image.thumbnail %}
  <thumb>{{image.thumbnail}}</thumb>
{% endif %}
</artist>
