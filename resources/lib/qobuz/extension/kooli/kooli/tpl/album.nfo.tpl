
<album>
  <title>{{title}}</title>
  {% if artist.name is defined %}
    <artist>{{artist.name}}</artist>
  {% endif %}
  {% for genre in genres_list %}
  <genre>{{genre}}</genre>
  {% endfor %}
  <releasedate>{{released_at}}</releasedate>
  <type>{{type}}</type>
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
  <label>{{label.name}}</label>
  {% for track in tracks['items'] %}
    <track>
      <position>{{track.track_number}}</position>
      <title>{{track.title}}</title>
      <duration>{{track.duration}}</duration>
    </track>
  {% endfor %}
<review>
{%- if catchline is defined -%}
{{catchline}}
{%- endif -%}
{%- if description is defined -%}
{{description}}
{%- endif -%}
{% if true %}
Duration : {{(duration / 60)|round}} mn
Tracks   : {{tracks_count}}
Media    : {{media_count}}
HiRes    : {{hires}}
Sales factors (monthly/yearly): {{product_sales_factors_monthly}} / {{product_sales_factors_yearly}}
Copyright: {{copyright}}
{% endif %}
</review>
</album>
